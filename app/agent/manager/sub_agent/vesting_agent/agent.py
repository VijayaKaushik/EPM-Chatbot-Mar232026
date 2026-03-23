import pathlib

from google.adk.agents import LlmAgent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

from .tool import get_vesting_dates, get_vesting_details

# Load skills from the file definitions
welcome_intent_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "welcome_intent"
)

vesting_schedule_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "vesting_schedule"
)

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[welcome_intent_skill, vesting_schedule_skill]
)

vesting_agent = LlmAgent(
    name="vesting_agent",
    model="gemini-2.5-flash",
    instruction= """
    You are a Vesting Agent helping users view upcoming vesting dates
    and retrieve detailed vesting information for equity compensation plans.

    SKILLS:
    - welcome-intent: Greet users and understand their intent
    - vesting-schedule: Guide users through viewing vesting dates and details

    APPROACH:
    - Use welcome-intent skill for new users or unclear requests
    - Use vesting-schedule skill for vesting date and detail workflows
    - Follow the skill instructions for detailed workflow guidance
    - If user states clear intent, proceed directly to the appropriate skill

    COMMUNICATION:
    - Be welcoming, professional, and clear
    - Never expose internal identifiers (e.g., token_id) to users
    - Present participant data in business-friendly tables or summaries
    - Focus on outcomes and next steps
    """,
    tools=[get_vesting_dates, get_vesting_details, my_skill_toolset],
)

# Required for adk web
root_agent = vesting_agent
