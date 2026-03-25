import pathlib

from google.adk.agents import LlmAgent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

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
- When users ask to analyze, slice, dice, filter, group, or aggregate
  vesting data, first call get_supported_fields to discover available
  columns, then use analyze_vesting_data with a natural language query
- Analyze a specific vesting date by passing vesting_date,
  or all dates combined by omitting it

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
)

# Required for adk web
root_agent = vesting_agent
