import json
import pathlib
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


def _log_tool_call(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
    print(f"\n[TOOL] {tool_context.agent_name} -> {tool.name}({json.dumps(args, default=str)})")
    return None


def _log_agent_start(callback_context: CallbackContext) -> None:
    print(f"\n[AGENT] {callback_context.agent_name} activated")

from .tool import (
    load_grants,
    query_grants,
    get_grant_details,
    get_grants_by_employee_ids,
)

agent_capabilities_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "agent_capabilities"
)
grant_analysis_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "grant_analysis"
)
my_skill_toolset = skill_toolset.SkillToolset(
    skills=[agent_capabilities_skill, grant_analysis_skill]
)

grant_agent = LlmAgent(
    name="grant_agent",
    model="gemini-2.5-flash",
    description=(
        "Handles all questions about equity grants, plans, "
        "unvested shares, grant types, performance conditions, "
        "and grant-participant relationships."
    ),
    instruction="""
    You are a Grant Agent for an equity plan management system.
    You answer all questions about grants, plans, and grant-participant
    relationships using grant data stored in ADK artifacts.

    ARTIFACT STRATEGY — follow strictly:
    - On first query: call load_grants() to load data into artifact
    - After load_grants succeeds: all tools read from artifact automatically
    - NEVER read from disk directly — always go through load_grants first
    - Artifact persists for the entire session — load once, reuse always
    - If any tool returns source = "artifact" the data is already loaded

    CAPABILITIES:
    - Grant summary and analysis via load_grants + query_grants
    - Specific grant lookup via get_grant_details
    - Cross-agent support via get_grants_by_employee_ids

    WORKFLOW:
    - Always call load_grants first if no prior grant interaction in session
    - Use query_grants for any analytical or aggregation question
    - Use get_grant_details only when a specific grant_id is provided
    - Use get_grants_by_employee_ids when orchestrator passes employee_ids

    WHEN RECEIVING IDS FROM ORCHESTRATOR:
    - If request contains employee_ids -> use query_grants
      with those employee_ids as filter
    - If request contains grant_ids -> use query_grants
      with those grant_ids as filter
    - Always decide internally which tool to use
    - Never expect orchestrator to specify tools

    COMMUNICATION:
    - Professional and clear
    - Always show total counts alongside results
    - Present data in tables where possible
    - Never expose internal artifact keys to user
    """,
    tools=[
        load_grants,
        query_grants,
        get_grant_details,
        get_grants_by_employee_ids,
        my_skill_toolset,
    ],
    before_tool_callback=_log_tool_call,
    before_agent_callback=_log_agent_start,
)

root_agent = grant_agent
