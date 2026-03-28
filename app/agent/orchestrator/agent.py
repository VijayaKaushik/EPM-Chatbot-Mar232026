import json
from typing import List, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import AgentTool
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


def _log_tool_call(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
    print(f"\n[TOOL] {tool_context.agent_name} -> {tool.name}({json.dumps(args, default=str)})")
    return None


def _log_agent_start(callback_context: CallbackContext) -> None:
    print(f"\n[AGENT] {callback_context.agent_name} activated")

from app.agent.manager.sub_agent.participant_agent.agent import participant_agent
from app.agent.manager.sub_agent.vesting_agent.agent import vesting_agent
from .context_registry import ContextRegistry
from .planner import Planner

planner = Planner()
registry = ContextRegistry()


def route_query(query: str, tool_context: ToolContext) -> dict:
    """
    Main routing tool. Classifies intent and routes to
    the correct agent. Records turn summary in context_registry.

    LLM Prompt Examples:
      - Any user query is passed through this tool
      - Orchestrator uses this for all routing decisions
    """
    # Step 1 — read current context
    context = registry.read_registry(tool_context)
    turn_index = registry.get_turn_index(tool_context)

    print(f"\n📥 ROUTE QUERY CALLED")
    print(f"📝 Query: {query}")
    print(f"📚 Context registry: {json.dumps(context, indent=2)}")

    # Step 2 — classify intent
    plan = planner.classify(query=query, context_registry=context)

    print(f"\n🔍 PLANNER RESULT: {json.dumps(plan, indent=2)}\n")

    # Step 3 — handle context_only (no agent call needed)
    if plan["route"] == "context_only":
        employee_ids = registry.get_latest_employee_ids(tool_context)
        operation = plan.get("operation", "filter")

        if operation == "intersect":
            # Get employee_ids from all turns and intersect
            all_ids = [
                set(turn.get("employee_ids", []))
                for turn in context.values()
                if turn.get("employee_ids")
            ]
            if all_ids:
                result_ids = list(set.intersection(*all_ids))
            else:
                result_ids = []

            registry.write_turn(
                tool_context=tool_context,
                turn_index=turn_index,
                agent_name="context_only",
                intent=plan["intent"],
                employee_ids=result_ids,
                summary={"operation": "intersect", "result_count": len(result_ids)},
            )
            return {
                "status":       "success",
                "route":        "context_only",
                "operation":    "intersect",
                "employee_ids": result_ids,
                "count":        len(result_ids),
                "message":      f"Found {len(result_ids)} common participants",
            }

        return {
            "status":       "success",
            "route":        "context_only",
            "operation":    operation,
            "employee_ids": employee_ids,
            "message":      "Use existing context to answer this query",
        }

    # Step 4 — record routing plan, let sub_agent handle the rest
    registry.write_turn(
        tool_context=tool_context,
        turn_index=turn_index,
        agent_name=plan["route"],
        intent=plan["intent"],
        summary={"plan": plan},
    )

    # Surface any stored employee_ids so orchestrator can pass them to participant_agent
    context_employee_ids = registry.get_latest_employee_ids(tool_context) or \
                           tool_context.state.get("last_vesting_employee_ids", [])

    return {
        "status":               "success",
        "route":                plan["route"],
        "intent":               plan["intent"],
        "cross_agent":          plan["cross_agent"],
        "join_key":             plan.get("join_key"),
        "join_field":           plan.get("join_field"),
        "requires_context":     plan.get("requires_context", False),
        "context_employee_ids": context_employee_ids,
        "message":              f"Routing to {plan['route']}",
    }


def _parse_summary(summary: Optional[str]) -> dict:
    if not summary:
        return {}
    try:
        return json.loads(summary)
    except (json.JSONDecodeError, ValueError):
        return {"note": summary}


def update_context(
    agent_name: str,
    employee_ids: List[str],
    tool_context: ToolContext,
    vesting_date: Optional[str] = None,
    batch_id: Optional[str] = None,
    summary: Optional[str] = None,
) -> dict:
    """
    Called after an agent completes its response.
    Records lightweight turn summary — keys and scalars only.
    Never stores full records.

    LLM Prompt Examples:
      - Called automatically after vesting_agent completes
      - Called automatically after participant_agent completes
    """
    turn_index = registry.get_turn_index(tool_context)

    # Fall back to state-stored ids if LLM passed an empty list
    resolved_ids = employee_ids or tool_context.state.get("last_vesting_employee_ids", [])

    registry.write_turn(
        tool_context=tool_context,
        turn_index=turn_index,
        agent_name=agent_name,
        intent="completed",
        employee_ids=resolved_ids,
        vesting_date=vesting_date,
        batch_id=batch_id,
        summary=_parse_summary(summary),
    )
    return {"status": "success", "turn_recorded": turn_index}


orchestrator = LlmAgent(
    name="orchestrator",
    model="gemini-2.5-flash",
    description="Routes equity management queries to the correct specialist agent.",
    instruction="""
    You are the Orchestrator for an equity plan management system.
    You route user queries to the correct specialist agent and
    maintain conversation context across turns.

    ## Your Workflow — Follow This Strictly

    STEP 1: Always call route_query(query) first for every user message.
    Read the routing plan it returns.

    STEP 2: Act on the routing plan:

      route = "context_only"
      -> Answer is already in session context
      -> Present the result from route_query directly
      -> Do NOT call any sub-agent

      route = "vesting_agent"
      -> Delegate to vesting_agent with the user's query
      -> vesting_agent owns its entire workflow
      -> When vesting_agent completes, call update_context
         with the employee_ids and vesting_date from its response

      route = "participant_agent"
      -> Read context_employee_ids from route_query response
      -> If requires_context = true AND context_employee_ids is non-empty:
         delegate to participant_agent with the user's query AND
         "Filter to employee_ids: <list from context_employee_ids>" appended
      -> If requires_context = false OR context_employee_ids is empty:
         delegate with user's query only
      -> When participant_agent completes, call update_context
         with the employee_ids from its response

      route = "both"
      -> Step 1: Delegate to vesting_agent first
      -> Extract employee_ids from vesting_agent response
      -> Step 2: Delegate to participant_agent
         passing employee_ids as filter context
      -> JOIN results on employee_id (set intersection on keys only)
      -> Call update_context with merged employee_ids

    STEP 3: Present the final result to the user in a
    clear, business-friendly format.

    ## Critical Rules
    - Always call route_query FIRST before anything else
    - Never skip update_context after an agent completes
    - Never pass full records between agents — keys only
    - Never answer vesting questions yourself — delegate to vesting_agent
    - Never answer participant questions yourself — delegate to participant_agent
    - For cross-agent queries, vesting_agent always runs first
    - Context registry is your memory — read it via route_query

    ## What You Know About Your Agents

    vesting_agent handles:
      Vesting dates, release schedules, participant details
      within a release, department/country/email breakdowns,
      employee status, officer status, grant type, FMV, tax,
      batch creation, release workflow end to end
      Columns: employee_id, employee_name, email, department,
      employee_status, officer_status, grant_id, grant_type,
      country, tax_method, shares_released, fmv_at_release,
      net_value_delivered, batch_id, tax_amount, release_status

    participant_agent handles ONLY compliance/profile fields:
      kyc_status, insider_status, blackout_status,
      current_address, office_address, w8_w9_status,
      withholding_rate, ach_status, account_info,
      grant_eligible, broker_code

    ## Cross-Agent Join Rule
    Joins happen on employee_id keys only.
    Never merge full records — only intersect/union id lists.
    """,
    tools=[
        route_query,
        update_context,
        AgentTool(agent=vesting_agent),
        AgentTool(agent=participant_agent),
    ],
    before_tool_callback=_log_tool_call,
    before_agent_callback=_log_agent_start,
)

root_agent = orchestrator
