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

from .tool import get_all_participants, get_participant_details, analyze_participant_data

# Load skills from file definitions
participant_lookup_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "participant_lookup"
)

data_analysis_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "data_analysis"
)

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[participant_lookup_skill, data_analysis_skill]
)

participant_agent = LlmAgent(
    name="participant_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a Participant Agent helping users look up equity plan participants,
    retrieve detailed participant information, and analyze participant data
    across dimensions like country, department, KYC status, insider status, and more.

    SKILLS:
    - participant-lookup: Look up specific participants by name or employee ID
    - participant-data-analysis: Analyze, group, count, and filter participant data

    ROUTING RULES:

    AGGREGATION / FILTER / COUNT / GROUP queries:
    → Use analyze_participant_data directly
    Examples: "how many in US", "group by KYC", "list insiders",
              "count by department", "breakdown by employment status",
              "show participants with unverified ACH", "average withholding rate by country"

    SPECIFIC PARTICIPANT DETAIL:
    → Use get_all_participants to find employee_id if not provided
    → Then use get_participant_details(employee_id)
    Examples: "show me Taylor Randolph's details",
              "get address for employee 74069291",
              "what is the tax info for Marcus Chen"

    SIMPLE LIST / SUMMARY queries:
    → Use get_all_participants and summarize directly
    Examples: "list all participants", "who is in blackout?", "show all insiders"

    APPROACH:
    - For aggregation, grouping, counting, or filtering across the full dataset → analyze_participant_data
    - For a specific named person or employee ID → get_participant_details (after lookup if needed)
    - For listing or summarizing all participants → get_all_participants
    - Follow skill instructions for detailed workflow guidance

    COMMUNICATION:
    - Be professional, clear, and concise
    - Present participant data in business-friendly tables or summaries
    - Always mask tax_id as XXX-XX-XXXX in responses
    - Only show broker_code / officer_code when explicitly requested

    CONCERN REPORTING — CRITICAL:
    After any tool call that returns a "concerns" list:
      → If concerns list is non-empty, you MUST include this
        at the END of your response in exactly this format:

      CONCERNS_JSON: [{"type":"...","severity":"...","count":N,
      "enrich_agent":"...","enrich_query":"..."}]

      This line must appear verbatim — orchestrator reads it.
      Never omit it when concerns exist.
      Never paraphrase it.
    """,
    tools=[
        get_all_participants,
        get_participant_details,
        analyze_participant_data,
        my_skill_toolset,
    ],
    before_tool_callback=_log_tool_call,
    before_agent_callback=_log_agent_start,
)

# Required for adk web
root_agent = participant_agent
