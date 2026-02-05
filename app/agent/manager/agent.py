from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent

from .sub_agent.data_analysis_agent.agent import data_analysis_agent
from .sub_agent.knowledge_base_agent.agent import knowledge_base_agent
from .sub_agent.reporting_agent.agent import reporting_agent
from .utils import get_model

load_dotenv()


manager_agent = LlmAgent(
    name="Manager",
    #model="gemini-2.5-flash",
    model=get_model(),
    description="Manager agent",
    instruction="Routes tasks to sub agents",
    sub_agents=[reporting_agent,knowledge_base_agent,data_analysis_agent],
)

# uncomment to run via ai_workflow web
# root_agent = LlmAgent(
#     name="Manager",
#     model="gemini-2.5-flash",
#     description="Manager agent",
#     instruction="Routes tasks to sub agents",
#     sub_agents=[reporting_agent],
# )
