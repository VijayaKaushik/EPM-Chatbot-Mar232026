from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, SseConnectionParams

from app.agent.manager.utils import get_model

reporting_agent = LlmAgent(
    name="reporting_agent",
    model=get_model(),
    # model="gemini-2.5-flash",
    instruction="Handles reporting tasks",
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(url="http://localhost:8000/sse")
        )
    ],
)
