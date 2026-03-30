import json
import re
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


from app.agent.manager.sub_agent.client_ops_agent.agent import client_ops_agent
from app.agent.manager.sub_agent.grant_agent.agent import grant_agent
from app.agent.manager.sub_agent.participant_agent.agent import participant_agent
from app.agent.manager.sub_agent.user_guide_agent.agent import user_guide_agent
from app.agent.manager.sub_agent.vesting_agent.agent import vesting_agent
from .context_registry import ContextRegistry
from .planner import Planner
from .rag_registry import is_rag_agent

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

    split_type = plan.get("split_type", "operational")

    print(f"🔀 SPLIT_TYPE: {split_type} | ROUTE: {plan['route']}")

    # SINGLE GENERIC RAG HANDLER — works for all RAG agents
    if split_type == "rag":
        rag_agent_name = plan["route"]
        print(f"📖 RAG → {rag_agent_name} | query: {query}")
        registry.write_turn(
            tool_context=tool_context,
            turn_index=turn_index,
            agent_name=rag_agent_name,
            intent=plan["intent"],
            summary={"plan": plan},
        )
        return {
            "status":     "success",
            "route":      rag_agent_name,
            "split_type": "rag",
            "intent":     plan["intent"],
            "rag_query":  plan.get("rag_query") or query,
            "message":    f"Routing to {rag_agent_name} for documentation search",
        }

    # SINGLE GENERIC COMBO HANDLER
    if split_type == "combo":
        rag_agent_name = plan.get("rag_agent", "user_guide_agent")
        print(f"🔀 COMBO → rag_agent: {rag_agent_name} | rag_query: {plan.get('rag_query')} | operational_query: {plan.get('operational_query')}")
        registry.write_turn(
            tool_context=tool_context,
            turn_index=turn_index,
            agent_name="combo",
            intent=plan["intent"],
            summary={
                "rag_agent":         rag_agent_name,
                "rag_query":         plan.get("rag_query"),
                "operational_query": plan.get("operational_query"),
            },
        )
        return {
            "status":            "success",
            "route":             "combo",
            "split_type":        "combo",
            "intent":            plan["intent"],
            "rag_agent":         rag_agent_name,
            "rag_query":         plan.get("rag_query") or query,
            "operational_query": plan.get("operational_query") or query,
            "message":           f"Combo — {rag_agent_name} + operational agent",
        }

    # OPERATIONAL: record routing plan, let sub_agent handle the rest
    print(f"⚙️  OPERATIONAL → {plan['route']} | intent: {plan['intent']}")
    registry.write_turn(
        tool_context=tool_context,
        turn_index=turn_index,
        agent_name=plan["route"],
        intent=plan["intent"],
        summary={"plan": plan},
    )

    context_employee_ids = registry.get_latest_employee_ids(tool_context) or \
                           tool_context.state.get("last_vesting_employee_ids", [])

    return {
        "status":               "success",
        "route":                plan["route"],
        "intent":               plan["intent"],
        "split_type":           "operational",
        "cross_agent":          plan.get("cross_agent", False),
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
    For participant_agent: automatically detects and returns concerns.

    LLM Prompt Examples:
      - Called automatically after vesting_agent completes
      - Called automatically after participant_agent completes
    """
    import pathlib
    import pandas as pd
    from app.agent.manager.sub_agent.participant_agent.tool import _detect_concerns

    turn_index = registry.get_turn_index(tool_context)
    resolved_ids = employee_ids or tool_context.state.get(
        "last_vesting_employee_ids", []
    )

    # AUTO CONCERN DETECTION — runs whenever participant_agent completes
    concerns = []
    if agent_name == "participant_agent":
        try:
            participant_data = json.loads(
                (pathlib.Path(__file__).parent.parent /
                 "manager/sub_agent/participant_agent/participant_data/participants.json")
                .read_text()
            )
            df = pd.DataFrame(participant_data)

            # If we have specific employee_ids, filter to those
            if resolved_ids:
                df = df[df["employee_id"].isin(resolved_ids)]

            concerns = _detect_concerns(df)

            if concerns:
                print(f"\n🔔 CONCERNS DETECTED: {len(concerns)}")
                for c in concerns:
                    print(f"  ⚠️  {c['type']} | {c['severity']} | count={c['count']}")
            else:
                print(f"\n✅ NO CONCERNS — participant data is clean")

        except Exception as e:
            print(f"\n⚠️ Concern detection failed: {e}")

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

    return {
        "status":        "success",
        "turn_recorded": turn_index,
        "concerns":      concerns,
        "has_concerns":  len(concerns) > 0,
    }


def _extract_concerns_from_response(response_text: str) -> list:
    """Extract concerns JSON from participant_agent text response."""
    match = re.search(r'CONCERNS_JSON:\s*(\[.*?\])', response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            return []
    return []


def enrich_from_concerns(
    concerns: str,
    tool_context: ToolContext,
    response_text: str = "",
) -> dict:
    """
    Called after participant_agent completes.
    Reads concerns from agent result (pass as JSON string).
    Falls back to extracting CONCERNS_JSON line from response_text.
    Returns enrichment instructions per concern.

    LLM Prompt Examples:
      - Called automatically after participant_agent returns concerns
    """
    parsed: list = []
    if concerns:
        try:
            parsed = json.loads(concerns) if isinstance(concerns, str) else concerns
        except (json.JSONDecodeError, ValueError):
            parsed = []

    if not parsed and response_text:
        parsed = _extract_concerns_from_response(response_text)

    if not parsed:
        return {
            "status":      "success",
            "enrichments": [],
            "message":     "No concerns — data is clean",
        }

    print(f"\n🔔 ENRICHMENT TRIGGERED: {len(parsed)} concerns\n")
    for c in parsed:
        print(f"  ⚠️  {c['type']} | {c['severity']} | count: {c['count']}")

    return {
        "status":      "success",
        "enrichments": [
            {
                "type":         c["type"],
                "description":  c.get("description", c["type"]),
                "severity":     c["severity"],
                "count":        c["count"],
                "employees":    c.get("employees", []),
                "enrich_agent": c["enrich_agent"],
                "enrich_query": c["enrich_query"],
            }
            for c in parsed
        ],
        "message": f"{len(parsed)} concerns need enrichment",
    }


orchestrator = LlmAgent(
    name="orchestrator",
    model="gemini-2.5-flash",
    description="Routes equity management queries to the correct specialist agent.",
    instruction="""
    You are the Orchestrator for an equity plan management system.
    You route user queries to the correct specialist agent and
    maintain conversation context across turns.

    INTENT SPLITTING — CHECK SPLIT_TYPE FIRST:
    route_query returns split_type. Act on it strictly:

    split_type = "rag"
    → route field contains the specific RAG agent name
    → delegate ONLY to that agent
    → do NOT call any data agent
    → present response directly
    → Examples of RAG agents: user_guide_agent, client_ops_agent
      (more may be added — always use route field, never hardcode)

    split_type = "operational"
    → use existing routing rules
    → delegate to vesting/participant/grant agent
    → do NOT call any RAG agent

    split_type = "combo"
    → route_query returns: rag_agent, rag_query, operational_query
    → Step 1: delegate rag_query to the rag_agent in the response
    → Step 2: delegate operational_query to correct data agent
               using existing operational routing rules
    → Present BOTH with clear section labels:

      ## [Guide Answer]
      [RAG agent response]

      ---

      ## [Data Answer]
      [data agent response]

    CRITICAL: For RAG routing — ALWAYS use the route field from
    route_query. NEVER hardcode agent names in your reasoning.
    New RAG agents may be added without changing your instruction.

    ## Your Workflow — Follow This Strictly

    STEP 1: Always call route_query(query) first for every user message.
    Read the routing plan it returns.

    STEP 2: Act on the routing plan:

      route = "context_only"
      -> Answer is already in session context
      -> Present the result from route_query directly
      -> Do NOT call any sub-agent

      route = [any RAG agent]  (split_type = "rag")
      -> Delegate to that agent with the rag_query from route_query
      -> Present the documentation answer with source and next action
      -> Do NOT call update_context

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

      POST-RESPONSE CONCERN CHECK:
      update_context automatically detects concerns when
      participant_agent completes. Always check its return value:

      result = update_context(agent_name="participant_agent", ...)

      IF result["has_concerns"] is True:
        → call enrich_from_concerns(concerns=result["concerns"])
        → for each enrichment returned:
            → call enrich_agent with enrich_query
        → present:

          ## Participant Data
          [data table]

          ---

          ## ⚠️ [description] ([count] participants)
          [RAG guidance]
          Next Action: [step]

      IF result["has_concerns"] is False:
        → present data directly, no enrichment

      SEVERITY ICONS: critical=🚨 high=⚠️ medium=📋 info=ℹ️

      route = "grant_agent"
      -> Delegate to grant_agent with the user's query
      -> grant_agent loads data into artifact automatically
      -> When grant_agent completes, call update_context
         with the employee_ids from its response

      route = "combo"  (split_type = "combo")
      -> Step 1: Delegate rag_query to rag_agent from route_query response
      -> Step 2: Delegate operational_query to the appropriate data agent
      -> Present both answers with section labels
      -> Call update_context after the data agent completes

      COMBO — EMAIL/COMMUNICATION DRAFTING:
      When combo intent contains "email", "draft", "notification",
      "notify", "letter", or "communication":
      -> Step 1: get operational data (vesting/release/batch details)
      -> Step 2: get EPM/CRM contacts from client_ops_agent
      -> Step 3: draft the email combining both:

        Subject: [relevant subject]

        Dear [CRM contact name],

        [Email body using operational data]

        [Sign off with EPM lead name and contact details]

        Best regards,
        [EPM Lead name]
        [EPM email]
        [Working hours]

      route = "both"  (split_type = "operational")
      -> Step 1: Delegate to vesting_agent first
      -> Extract employee_ids from vesting_agent response
      -> Step 2: Delegate to participant_agent or grant_agent
         passing employee_ids as filter context
      -> JOIN results on employee_id (set intersection on keys only)
      -> Call update_context with merged employee_ids

    STEP 3: Present the final result to the user in a
    clear, business-friendly format.

    ## Critical Rules
    - Always call route_query FIRST before anything else
    - Never skip update_context after a data agent completes
    - Never pass full records between agents — keys only
    - Never answer vesting questions yourself — delegate to vesting_agent
    - Never answer participant questions yourself — delegate to participant_agent
    - Never answer grant questions yourself — delegate to grant_agent
    - For cross-agent queries, vesting_agent always runs first
    - Context registry is your memory — read it via route_query

    ## AGENT CAPABILITIES SUMMARY

    user_guide_agent  → generic how-to, concepts, app navigation
    client_ops_agent  → client contacts, SLAs, client policies
                        client_id read from session state automatically
    vesting_agent     → vesting data, release workflow, batch creation
    participant_agent → KYC, insider, blackout, address, account info
    grant_agent       → grants, plans, unvested shares, grant analysis

    ## STRICT ROUTING ENFORCEMENT
    - When route_query returns route = "grant_agent" you MUST
      delegate to grant_agent. NEVER answer grant questions yourself.
      grant_id, unvested_shares, plan_id, performance_conditions,
      grant_value_at_grant_date DO NOT EXIST in vesting or
      participant data. Only grant_agent can answer these.

    ## CROSS-AGENT JOIN RULES
    - Pass natural language requests to agents — never specify
      which internal tool they should use
    - When join_key = employee_id:
      pass: 'show [requested data] for these employees: [ids]'
    - When join_key = grant_id:
      pass: 'show [requested data] for these grant_ids: [ids]'
    - The receiving agent decides how to answer internally
    """,
    tools=[
        route_query,
        update_context,
        enrich_from_concerns,
        AgentTool(agent=vesting_agent),
        AgentTool(agent=participant_agent),
        AgentTool(agent=grant_agent),
        AgentTool(agent=user_guide_agent),
        AgentTool(agent=client_ops_agent),
    ],
    before_tool_callback=_log_tool_call,
    before_agent_callback=_log_agent_start,
)

root_agent = orchestrator
