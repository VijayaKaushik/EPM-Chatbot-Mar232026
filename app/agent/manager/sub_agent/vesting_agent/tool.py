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
            status (str): success
            vesting_dates (List[str]): List of vesting dates in YYYY-MM-DD format
    """
    all_vesting_dates = [
        "2026-03-15",
        "2026-06-15",
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

    participants: List[Dict] = [
        {
            "employee_id": "74069291",
            "employee_name": "Taylor Randolph",
            "email": "ubutler@example.net",
            "department": "Finance",
            "employee_status": "Active",
            "grant_id": "GR-8FE49167-861",
            "grant_date": "2021-04-13",
            "grant_type": "RSU",
            "total_shares_granted": 3044,
            "vesting_schedule": "4-year monthly",
            "release_date": "2024-12-15",
            "release_number": 10,
            "shares_released": 1522,
            "net_shares_delivered": 993,
            "stock_price_at_release": 345.66,
            "fmv_at_release": 526094.52,
            "net_value_delivered": 343240.38,
            "tax_method": "Net Issuance",
            "brokerage_account": "BR-610056",
            "release_status": "Completed",
            "processed_date": "2024-12-15",
            "processed_by": "Erika Jones",
            "country": "Puerto Rico",
            "currency": "EUR",
            "notes": "Tax rate verified",
        },
        {
            "employee_id": "31582740",
            "employee_name": "Marcus Chen",
            "email": "mchen@example.com",
            "department": "Engineering",
            "employee_status": "Active",
            "grant_id": "GR-2AB73C91-445",
            "grant_date": "2022-01-20",
            "grant_type": "PSU",
            "total_shares_granted": 5000,
            "vesting_schedule": "3-year quarterly",
            "release_date": "2024-12-15",
            "release_number": 6,
            "shares_released": 834,
            "net_shares_delivered": 517,
            "stock_price_at_release": 289.43,
            "fmv_at_release": 241384.62,
            "net_value_delivered": 149634.31,
            "tax_method": "Sell-to-Cover",
            "brokerage_account": "BR-442891",
            "release_status": "Completed",
            "processed_date": "2024-12-16",
            "processed_by": "Diana Patel",
            "country": "United States",
            "currency": "USD",
            "notes": "Standard processing",
        },
        {
            "employee_id": "58203617",
            "employee_name": "Sophia Alvarez",
            "email": "salvarez@example.org",
            "department": "Sales",
            "employee_status": "On Leave",
            "grant_id": "GR-D4F10E82-773",
            "grant_date": "2020-09-05",
            "grant_type": "Stock Option",
            "total_shares_granted": 8000,
            "vesting_schedule": "4-year annual",
            "release_date": "2024-12-15",
            "release_number": 4,
            "shares_released": 2000,
            "net_shares_delivered": 1240,
            "stock_price_at_release": 312.50,
            "fmv_at_release": 625000.00,
            "net_value_delivered": 387500.00,
            "tax_method": "Net Issuance",
            "brokerage_account": "BR-887234",
            "release_status": "Pending",
            "processed_date": "2024-12-17",
            "processed_by": "James Wu",
            "country": "Canada",
            "currency": "CAD",
            "notes": "Employee requested hold",
        },
    ]

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "token_id": token_id,
        "participants": participants,
        "message": "Token and participant details retrieved successfully",
    }
