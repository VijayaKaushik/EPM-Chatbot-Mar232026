import pathlib
import uuid
from typing import Dict, List, Optional

import pandas as pd
from google.adk.tools.tool_context import ToolContext

VESTING_DATA_DIR = pathlib.Path(__file__).parent / "vesting_data"


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
            status (str): success
            vesting_dates (List[str]): List of vesting dates in YYYY-MM-DD format
    """
    all_vesting_dates = [
        "2026-05-15",
        "2026-06-15",
        "2026-09-15",
        "2026-09-15",
        "2026-12-15",
    ]
    return {"status": "success", "vesting_dates": all_vesting_dates[:count]}


def get_vesting_details(vesting_date: str, tool_context: ToolContext) -> Dict:
    """
    Retrieves participant details for a specific vesting date and creates a release token.

    Generates a token representing the vesting release workflow and stores the
    vesting date and token mapping inside the agent state. Returns a list of
    sample participant records for the given vesting date.

    Args:
        vesting_date (str):
            Vesting date for which details are requested.
            Expected format: YYYY-MM-DD.

        tool_context (ToolContext):
            ADK tool context used for maintaining workflow state.
            Stores vesting date and token mappings under:
            state["token_vesting_list"]

    LLM Prompt Examples:
        - "Give me details of this vesting date"
        - "Give me details for vesting date 2026-03-15"
        - "Show vesting details for these dates"

    State Updates:
        Adds tuple (vesting_date, token_id) to:
        tool_context.state["token_vesting_list"]

    Returns:
        Dict containing:
            status (str): success
            vesting_date (str): Requested vesting date
            token_id (str): Generated workflow token identifier (internal only)
            participants (List[Dict]): List of participant vesting records
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

    # Load participant data from CSV
    csv_path = VESTING_DATA_DIR / f"{vesting_date}.csv"
    if not csv_path.exists():
        return {
            "status": "error",
            "vesting_date": vesting_date,
            "message": f"No vesting data found for date {vesting_date}",
        }

    df = pd.read_csv(csv_path, dtype={"employee_id": str})
    participants: List[Dict] = df.to_dict(orient="records")

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "token_id": token_id,
        "participants": participants,
        "message": f"Retrieved {len(participants)} participant records for {vesting_date}",
    }
