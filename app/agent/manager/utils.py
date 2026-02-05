from dotenv import load_dotenv
import os
from google.adk.models.lite_llm import LiteLlm
load_dotenv()

OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
#OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")

OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")


def get_model():
    # return LiteLlm(
    #     model=f"ollama_chat/{OLLAMA_MODEL}",
    #     api_base=OLLAMA_API_BASE_URL,
    #     extra_params={
    #         "tool_choice":"auto"
    #     },
    # )
    return "gemini-2.5-flash"
