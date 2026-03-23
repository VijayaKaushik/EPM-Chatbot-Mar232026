from google.adk.agents import LlmAgent
from google.adk.tools import skill_toolset

from .tool import analyze_release_data, calculate_tax, get_supported_fields, get_vesting_dates, get_vesting_details

import pathlib
from google.adk.skills import load_skill_from_dir

# Load skills from the file definitions
tax_calculation_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "tax_calculation"
)

welcome_intent_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "welcome_intent"
)

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[tax_calculation_skill, welcome_intent_skill]
)

root_agent = LlmAgent(
    name="releasemanagement_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a Release Management Agent helping users with vesting releases,
    tax calculations, data analysis, and related workflows.

    SKILLS:
    - welcome-intent: Greet users and understand their intent
    - vesting-tax-calculation: Execute vesting tax calculation workflows

    DATA ANALYSIS:
    - When users ask to analyze, slice, dice, filter, group, or aggregate
      release activity data, first call `get_supported_fields` to discover
      available columns, then use `analyze_release_data` with a natural
      language query to perform the analysis.
    - The dataset contains 100 release activity records with employee,
      grant, vesting, tax, and release information.

    APPROACH:
    - Use welcome-intent skill for new users or unclear requests
    - Use vesting-tax-calculation skill for tax calculation workflows
    - For data analysis questions, use get_supported_fields + analyze_release_data
    - Follow the skill instructions for detailed workflow guidance
    - If user states clear intent, proceed directly to the appropriate skill

    COMMUNICATION:
    - Be welcoming, professional, and clear
    - Never expose internal identifiers (e.g., token_id) to users
    - Present results in business-friendly language
    - Focus on outcomes and next steps
    """,
    tools=[analyze_release_data, calculate_tax, get_supported_fields, get_vesting_dates, get_vesting_details, my_skill_toolset],
)
