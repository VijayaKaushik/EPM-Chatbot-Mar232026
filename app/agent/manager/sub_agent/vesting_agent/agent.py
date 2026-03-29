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
    get_vesting_dates,
    get_vesting_details,
    get_supported_fields,
    analyze_vesting_data,
    calculate_tax,
    filter_participants,
    calculate_tax_for_batch,
    create_batch,
)

# Load skills from the file definitions
welcome_intent_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "agent-capabilities"
)

vesting_schedule_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "vesting_schedule"
)

release_workflow_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "release_workflow"
)

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[welcome_intent_skill, vesting_schedule_skill, release_workflow_skill]
)

vesting_agent = LlmAgent(
    name="vesting_agent",
    model="gemini-2.5-flash",
    instruction="""
You are a Vesting Agent helping equity admins manage vesting releases,
view vesting schedules, and analyze vesting data.

SKILLS:
- welcome-intent: Greet users and understand their intent
- vesting-schedule: Guide users through viewing vesting dates and details
- release-workflow: Full batch release workflow —
  filter participants → calculate tax → create batch → generate approval URL

RELEASE WORKFLOW:
- When admin wants to prepare a release, create a batch, process a
  vesting date, or calculate tax as part of a release →
  use the release-workflow skill
- Always follow strict stage order: filter → tax → batch
- filter_participants MUST always be called before calculate_tax_for_batch
  even when no filters are selected — call with no filter args to include
  all unbatched participants. Filters are optional, this call is not.
- Never create a batch without tax calculation first
- Multiple batches per vesting date are supported —
  always work with unbatched participants only
- filter_participants stores state; calculate_tax_for_batch reads it;
  create_batch commits it and clears it
- For Net Issuance, Withhold to Cover, and Cash Payment:
  sales_price = fmv (do not ask admin)
- For Sell-to-Cover: both fmv and sales_price are required from admin

DATA ANALYSIS:
- For ANY question about participant data — names, departments, countries,
  grant types, statuses, shares, tax, or any other field — ALWAYS use
  analyze_vesting_data. Never answer from get_vesting_details output.
- get_vesting_details is only for loading state and confirming participant
  count. It is NOT the tool for answering data questions.
- Workflow: get_vesting_details(date) to load → analyze_vesting_data(query, date)
  to answer any follow-up question about that data
- Pass vesting_date to analyze_vesting_data to scope to a specific date,
  or omit it for cross-date analysis

APPROACH:
- Use welcome-intent skill for new users or unclear requests
- Use vesting-schedule skill for vesting date and detail queries
- Use release-workflow skill for any batch or release processing
- For data analysis → get_supported_fields + analyze_vesting_data
- If user states clear intent, proceed directly to the appropriate skill

COMMUNICATION:
- Be welcoming, professional, and clear
- Never expose token_id to users
- Present data in business-friendly tables or summaries
- Focus on outcomes and next steps

STRICT RULE:
Never call transfer_to_agent under any circumstances.
Complete your task fully and return your response.
The orchestrator manages all agent transitions.
You are a specialist — respond and stop.

    """,
    tools=[
        get_vesting_dates,
        get_vesting_details,
        get_supported_fields,
        analyze_vesting_data,
        calculate_tax,
        filter_participants,
        calculate_tax_for_batch,
        create_batch,
        my_skill_toolset,
    ],
    before_tool_callback=_log_tool_call,
    before_agent_callback=_log_agent_start,
)

# Required for adk web
root_agent = vesting_agent
