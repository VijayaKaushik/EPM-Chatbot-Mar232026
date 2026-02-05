from typing import Dict
import uuid
from typing import Dict, List, Optional

from google.adk.tools.tool_context import ToolContext



def get_vesting_dates(count: Optional[int] = 1) -> Dict:
    """
    Returns the next upcoming vesting dates.

    Args:
        count (int, optional): Number of upcoming vesting dates to return.
            Defaults to 1 if not provided.

    Example user prompts:
        - "Give me next vesting date"
        - "Give me next 3 vesting dates"

    Returns:
        Dict:
            status (str): success or failure
            vesting_dates (List[str]): List of vesting dates in YYYY-MM-DD format
    """

    all_vesting_dates: List[str] = [
        "2026-03-15",
        "2026-06-15",
        "2026-09-15",
        "2026-12-15"
    ]

    return {
        "status": "success",
        "vesting_dates": all_vesting_dates[:count]
    }


def get_vesting_details(vesting_date: str, tool_context: ToolContext) -> Dict:
    """
    Retrieves details for a specific vesting date and creates a release token.

    This tool is used when a user asks for details about one or more vesting dates.
    It generates a token representing the vesting release workflow and stores the
    vesting date and token mapping inside the agent state.

    Args:
        vesting_date (str):
            Vesting date for which details or release workflow needs to be created.
            Expected format: YYYY-MM-DD.

        tool_context (ToolContext):
            ADK tool context used for maintaining workflow state.
            Stores vesting date and token mappings under:
            state["token_vesting_list"]

    LLM Prompt Examples:
        - "Give me details of this vesting date"
        - "Give me details for vesting date 2026-03-15"
        - "Show vesting details for these dates"
        - "Create release workflow for this vesting date"

    State Updates:
        Adds tuple (vesting_date, token_id) to:
        tool_context.state["token_vesting_list"]

    Returns:
        Dict containing:
            status (str): success or failure
            vesting_date (str): Requested vesting date
            token_id (str): Generated workflow token identifier
            message (str): Status message
    """

    token_id = f"token_{uuid.uuid4().hex[:8]}"

    # Fetch from state
    tool_vesting_list = tool_context.state.get("token_vesting_list")
    if tool_vesting_list is None:
        tool_vesting_list = []

    tool_vesting_list.append((vesting_date, token_id))

    # Update state
    tool_context.state["token_vesting_list"] = tool_vesting_list

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "token_id": token_id,
        "message": "Token and initial release file created"
    }



def calculate_tax(
    vesting_date: str,
    fmv: float,
    sales: float,
    tool_context: ToolContext
) -> Dict:
    """
    Simulates a vesting release and calculates tax for a given vesting event.

    This tool is invoked when a user asks to simulate, prepare, or calculate
    tax for a specific vesting date, typically after vesting details have
    already been initialized using the `get_vesting_details` tool.

    The tool validates that the vesting date exists in the agent state,
    performs a simulated update of FMV and sale price, and returns a
    summarized tax outcome and approval workflow link.

    Args:
        vesting_date (str):
            Vesting date for which release simulation or tax calculation
            is requested. Expected format: YYYY-MM-DD.

        fmv (float):
            Fair Market Value per unit used for the vesting tax calculation.

        sales (float):
            Sale price per unit (sell-to-cover or market sale).

        tool_context (ToolContext):
            ADK tool context used to access workflow state.
            Requires vesting details to be present under:
            state["token_vesting_list"].

    LLM Prompt Examples:
        - "Simulate release for this vesting date"
        - "Calculate tax for this date given FMV = 10 and sales price = 11"
        - "Prepare release for this vesting event"
        - "Run tax simulation for vesting date 2026-03-15"

    Preconditions:
        - Vesting details must already exist in state.
        - If missing, the agent should first call `get_vesting_details`.

    Workflow Simulated:
        1. Validate vesting date and retrieve token
        2. Update FMV and sale price (simulated)
        3. Calculate tax (dummy logic)
        4. Generate approval / execution URL

    Returns:
        Dict containing:
            status (str): success or error
            vesting_date (str): Vesting date processed
            summary (str): Human-readable tax summary
            approval_url (str): Approval or execution link
            message (str): Status message
    """

    # Fetch from state
    tool_vesting_list = tool_context.state["token_vesting_list"]
    if tool_vesting_list is None:
        return {
            "status": "error",
            "missing_vesting_detail": vesting_date,
            "reason": (
                "calculate_tax requires vesting details. "
                "Call get_vesting_details first."
            )
        }

    token_id = None
    for tool_vesting_date in tool_vesting_list:
        if tool_vesting_date[0] == vesting_date:
            token_id = tool_vesting_date[1]

    if token_id is None:
        return {
            "status": "error",
            "missing_vesting_detail": vesting_date,
            "reason": (
                "calculate_tax requires vesting details. "
                "Call get_vesting_details first."
            )
        }

    # Dummy tax calculation
    estimated_tax = 12345.67

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "summary": "Your total tax is $200K for 1,500 participants with sell-to-cover.",
        "approval_url": "https://dummy.com",
        "message": "Tax calculated successfully"
    }
