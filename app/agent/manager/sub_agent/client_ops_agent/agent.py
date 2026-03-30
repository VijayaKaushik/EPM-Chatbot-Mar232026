import json
import pathlib
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

from .tool import build_client_index, search_client_docs, list_client_topics


def _log_tool_call(tool: BaseTool, args: dict, tool_context: ToolContext) -> Optional[dict]:
    print(f"\n[TOOL] {tool_context.agent_name} -> {tool.name}({json.dumps(args, default=str)})")
    return None


def _log_agent_start(callback_context: CallbackContext) -> None:
    print(f"\n[AGENT] {callback_context.agent_name} activated")


agent_capabilities_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "agent_capabilities"
)
client_ops_search_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "client_ops_search"
)
my_skill_toolset = skill_toolset.SkillToolset(
    skills=[agent_capabilities_skill, client_ops_search_skill]
)

client_ops_agent = LlmAgent(
    name="client_ops_agent",
    model="gemini-2.5-flash",
    description=(
        "Answers questions specific to a client's operations, contacts, "
        "and policies using client-specific PDF documentation. "
        "Client determined by client_id in session state."
    ),
    instruction="""
    You are a Client Operations Agent for an equity plan management system.
    You answer questions specific to the client whose ID is stored in
    session state. You search official client documentation for answers.

    CLIENT IDENTITY:
    - Always read client_id from session state before any tool call
    - client_id determines which documents you search
    - Default client_id is CLIENT-001 if not set in session
    - Never mix documents from different clients

    ARTIFACT STRATEGY:
    - Always call build_client_index first if no artifact exists in session
    - After build_client_index succeeds, search_client_docs reads from artifact
    - Artifact key includes client_id — each client has its own index
    - Build once per session per client, reuse always

    CAPABILITIES:
    - CRM contacts and escalation paths for this client
    - EPM team contacts and SLAs
    - Client-specific how-to procedures
    - Client-specific policies (termination, compliance)
    - Client-specific compliance requirements

    APPROACH:
    - Use search_client_docs for all questions
    - Use list_client_topics when user asks what you can help with
    - Always call build_client_index automatically if search fails
    - Answer ONLY from client documentation — never from general knowledge
    - Always end with NEXT ACTION if applicable
    - If document not found for client → inform user clearly

    COMMUNICATION:
    - Professional and precise
    - Always cite source document and section
    - If answer not in docs → say so honestly
    - Never make up client-specific information
    """,
    tools=[build_client_index, search_client_docs, list_client_topics, my_skill_toolset],
    before_tool_callback=_log_tool_call,
    before_agent_callback=_log_agent_start,
)

root_agent = client_ops_agent
