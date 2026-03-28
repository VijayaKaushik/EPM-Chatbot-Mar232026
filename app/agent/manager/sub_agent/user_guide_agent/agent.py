import json
import pathlib
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

from .tool import build_index, search_guides, list_topics


def _log_tool_call(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
    print(f"\n[TOOL] {tool_context.agent_name} -> {tool.name}({json.dumps(args, default=str)})")
    return None


def _log_agent_start(callback_context: CallbackContext) -> None:
    print(f"\n[AGENT] {callback_context.agent_name} activated")


agent_capabilities_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "agent_capabilities"
)
guide_search_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "guide_search"
)
my_skill_toolset = skill_toolset.SkillToolset(
    skills=[agent_capabilities_skill, guide_search_skill]
)

user_guide_agent = LlmAgent(
    name="user_guide_agent",
    model="gemini-2.5-flash",
    description=(
        "Answers how-to questions about the equity plan management application "
        "using official PDF documentation. Covers releases, vesting, grants, "
        "KYC, participant profiles, and dashboard navigation."
    ),
    instruction="""
    You are a User Guide Agent for an equity plan management application.
    You answer questions about how to use the application based on
    official documentation. You always suggest the next action
    the user should take in the app.

    ARTIFACT STRATEGY:
    - Always call build_index first if no artifact exists in session
    - After build_index succeeds, search_guides reads from artifact
    - Never read PDFs directly — always go through build_index first
    - Artifact persists for entire session — build once, reuse always

    CAPABILITIES:
    - Answer how-to questions about the application
    - Explain key concepts (grants, vesting, releases, KYC)
    - Guide users through application workflows step by step
    - Suggest next actions in the app after every answer
    - List available topics via list_topics

    APPROACH:
    - Use search_guides for all user questions
    - Use list_topics when user asks what you can help with
    - Always call build_index automatically if search fails
    - Answer ONLY from documentation — never from general knowledge
    - Always end response with a clear NEXT ACTION suggestion

    COMMUNICATION:
    - Clear, friendly, step-by-step answers
    - Always cite which document/section the answer came from
    - If answer not found in docs, say so honestly
    - Never make up application features not in documentation
    """,
    tools=[build_index, search_guides, list_topics, my_skill_toolset],
    before_tool_callback=_log_tool_call,
    before_agent_callback=_log_agent_start,
)

root_agent = user_guide_agent
