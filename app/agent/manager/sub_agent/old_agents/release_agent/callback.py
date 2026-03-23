from datetime import datetime
from typing import Dict, Any, Optional

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.genai import types


def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    tool_name = tool.name
    print(f"tool_name : {tool_name}")
    print(f"tool_context : {tool_context}")
    if tool_name == "data_analysis":
        if not "vesting_dates_file_name" in tool_context.state:
            print("no vesting_dates_file_name")
            return {
                "status": "error",
                "reason": "file missing for running the data analysis",
            }
    return None


def before_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    state = callback_context.state
    timestamp = datetime.now()
    state["timestamp"] = timestamp
    # get user id from  state and call the api for authtntication , if non 200  then "responsd as  permission denied"
    #feature flag using launch drakly > look into

    return None


def after_agent_callback(
    callback_context: CallbackContext,
):
    state = callback_context.state
    end_timestamp = datetime.now()
    start_timestamp = state["timestamp"]
    print(f"time taken for agen execution : {end_timestamp - start_timestamp}")
    return None
