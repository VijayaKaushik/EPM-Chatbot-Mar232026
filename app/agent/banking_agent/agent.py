from google.adk.agents import LlmAgent

from .tool import generate_sql

root_agent = LlmAgent(
    name="banking_agent",
    model="gemini-2.5-flash",
    #model="gemini-2.5-flash",
    instruction="Handles questions for corporate and bankers and individual clients",
    tools=[generate_sql]
)
