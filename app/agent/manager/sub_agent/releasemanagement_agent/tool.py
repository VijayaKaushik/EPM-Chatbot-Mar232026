from typing import Dict
import os
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from faker import Faker
from google.adk.tools.tool_context import ToolContext

RELEASE_ACTIVITY_FIELDS = [
    {
        "column_name": "employee_id",
        "label": "Employee ID",
        "description": "Unique identifier for the employee",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "employee_name",
        "label": "Employee Name",
        "description": "Full name of the employee",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "email",
        "label": "Email",
        "description": "Email address of the employee",
        "data_type": "string",
        "filterable": True,
        "sortable": False,
    },
    {
        "column_name": "department",
        "label": "Department",
        "description": "Department the employee belongs to (e.g. Finance, Sales, Engineering)",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "employee_status",
        "label": "Employee Status",
        "description": "Current employment status (e.g. Active, Terminated)",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "grant_id",
        "label": "Grant ID",
        "description": "Unique identifier for the equity grant",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "grant_date",
        "label": "Grant Date",
        "description": "Date when the equity grant was issued (YYYY-MM-DD)",
        "data_type": "date",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "grant_type",
        "label": "Grant Type",
        "description": "Type of equity grant (e.g. RSU, PSU, Stock Option)",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "total_shares_granted",
        "label": "Total Shares Granted",
        "description": "Total number of shares in the original grant",
        "data_type": "integer",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "vesting_schedule",
        "label": "Vesting Schedule",
        "description": "Schedule type for vesting (e.g. 4-year monthly, 3-year quarterly)",
        "data_type": "string",
        "filterable": True,
        "sortable": False,
    },
    {
        "column_name": "release_date",
        "label": "Release Date",
        "description": "Date when shares were released (YYYY-MM-DD)",
        "data_type": "date",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "release_number",
        "label": "Release Number",
        "description": "Sequential release number for the grant",
        "data_type": "integer",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "shares_released",
        "label": "Shares Released",
        "description": "Number of shares released in this vesting event",
        "data_type": "integer",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "shares_withheld_for_taxes",
        "label": "Shares Withheld for Taxes",
        "description": "Number of shares withheld to cover tax obligations",
        "data_type": "integer",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "net_shares_delivered",
        "label": "Net Shares Delivered",
        "description": "Number of shares delivered to employee after tax withholding",
        "data_type": "integer",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "stock_price_at_release",
        "label": "Stock Price at Release",
        "description": "Market stock price at the time of release",
        "data_type": "float",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "fmv_at_release",
        "label": "FMV at Release",
        "description": "Fair Market Value of released shares at the time of release",
        "data_type": "float",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "tax_withheld_amount",
        "label": "Tax Withheld Amount",
        "description": "Dollar amount of tax withheld from the release",
        "data_type": "float",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "net_value_delivered",
        "label": "Net Value Delivered",
        "description": "Net dollar value delivered to the employee after taxes",
        "data_type": "float",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "tax_method",
        "label": "Tax Method",
        "description": "Method used for tax withholding (e.g. Net Issuance, Sell-to-Cover)",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "brokerage_account",
        "label": "Brokerage Account",
        "description": "Brokerage account identifier for share delivery",
        "data_type": "string",
        "filterable": True,
        "sortable": False,
    },
    {
        "column_name": "release_status",
        "label": "Release Status",
        "description": "Current status of the release (e.g. Completed, Pending, Failed)",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "processed_date",
        "label": "Processed Date",
        "description": "Date when the release was processed (YYYY-MM-DD)",
        "data_type": "date",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "processed_by",
        "label": "Processed By",
        "description": "Name of the person who processed the release",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "country",
        "label": "Country",
        "description": "Country or territory of the employee",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "currency",
        "label": "Currency",
        "description": "Currency code for the transaction (e.g. USD, EUR, GBP)",
        "data_type": "string",
        "filterable": True,
        "sortable": True,
    },
    {
        "column_name": "notes",
        "label": "Notes",
        "description": "Additional notes or comments about the release",
        "data_type": "string",
        "filterable": False,
        "sortable": False,
    },
]


def get_supported_fields() -> Dict:
    """
    Returns all supported fields/columns available in the release activity data.

    Each field includes its column name, human-readable label, description,
    data type, and whether it supports filtering and sorting. This metadata
    is intended for data analyzers to understand the schema and perform
    slicing, dicing, filtering, and aggregation on release activity data.

    Use this tool FIRST before querying or analyzing release activity data,
    so you know which columns are available and their types.

    LLM Prompt Examples:
        - "What fields are available in the release data?"
        - "Show me all supported columns"
        - "What can I filter or sort by?"
        - "Get the schema for release activity data"
        - "Which fields support filtering?"

    Returns:
        Dict containing:
            status (str): success
            total_fields (int): Total number of available fields
            fields (List[Dict]): List of field definitions, each with:
                - column_name (str): Key name used in the data
                - label (str): Human-readable display name
                - description (str): What the field represents
                - data_type (str): Data type (string, integer, float, date)
                - filterable (bool): Whether field supports filtering
                - sortable (bool): Whether field supports sorting
    """
    return {
        "status": "success",
        "total_fields": len(RELEASE_ACTIVITY_FIELDS),
        "fields": RELEASE_ACTIVITY_FIELDS,
    }


fake = Faker()

DEPARTMENTS = ["Finance", "Engineering", "Sales", "Operations", "HR", "Legal", "Marketing"]
EMPLOYEE_STATUSES = ["Active", "Terminated", "On Leave"]
GRANT_TYPES = ["RSU", "PSU", "Stock Option"]
VESTING_SCHEDULES = ["4-year monthly", "3-year quarterly", "4-year annual", "3-year monthly"]
TAX_METHODS = ["Net Issuance", "Sell-to-Cover", "Cash Payment"]
RELEASE_STATUSES = ["Completed", "Pending", "Failed"]
CURRENCIES = ["USD", "EUR", "GBP", "INR", "CAD", "JPY"]
NOTES_OPTIONS = [
    "Tax rate verified",
    "Employee requested hold",
    "Processed on schedule",
    "Manual override applied",
    "Pending compliance review",
    "Standard processing",
    "Expedited release",
    "Audit flagged",
    "Currency conversion applied",
    "Split transaction",
]


def _build_release_activity_dataframe(num_rows: int = 100) -> pd.DataFrame:
    """Generates a DataFrame with realistic release activity sample data."""
    Faker.seed(42)
    random.seed(42)

    rows = []
    for _ in range(num_rows):
        grant_date = fake.date_between(start_date="-5y", end_date="-1y")
        release_date = datetime(2024, 12, 15).date()
        processed_date = release_date + timedelta(days=random.randint(0, 5))
        total_shares = random.randint(500, 10000)
        shares_released = random.randint(100, total_shares // 2)
        stock_price = round(random.uniform(50.0, 500.0), 2)
        tax_pct = round(random.uniform(0.25, 0.45), 2)
        shares_withheld = int(shares_released * tax_pct)
        net_shares = shares_released - shares_withheld
        fmv = round(shares_released * stock_price, 2)
        tax_withheld_amount = round(shares_withheld * stock_price, 2)
        net_value = round(net_shares * stock_price, 2)

        rows.append({
            "employee_id": fake.bothify(text="########").upper(),
            "employee_name": fake.name(),
            "email": fake.email(),
            "department": random.choice(DEPARTMENTS),
            "employee_status": random.choices(EMPLOYEE_STATUSES, weights=[80, 15, 5])[0],
            "grant_id": f"GR-{fake.hexify(text='^^^^^^^^').upper()}-{fake.bothify(text='???').upper()}",
            "grant_date": grant_date.isoformat(),
            "grant_type": random.choice(GRANT_TYPES),
            "total_shares_granted": total_shares,
            "vesting_schedule": random.choice(VESTING_SCHEDULES),
            "release_date": release_date.isoformat(),
            "release_number": random.randint(1, 16),
            "shares_released": shares_released,
            "shares_withheld_for_taxes": shares_withheld,
            "net_shares_delivered": net_shares,
            "stock_price_at_release": stock_price,
            "fmv_at_release": fmv,
            "tax_withheld_amount": tax_withheld_amount,
            "net_value_delivered": net_value,
            "tax_method": random.choice(TAX_METHODS),
            "brokerage_account": f"BR-{random.randint(100000, 999999)}",
            "release_status": random.choices(RELEASE_STATUSES, weights=[70, 20, 10])[0],
            "processed_date": processed_date.isoformat(),
            "processed_by": fake.name(),
            "country": fake.country(),
            "currency": random.choice(CURRENCIES),
            "notes": random.choice(NOTES_OPTIONS),
        })

    return pd.DataFrame(rows)


# Cached DataFrame so it's created once per process
_release_activity_df: Optional[pd.DataFrame] = None


def _get_release_activity_df() -> pd.DataFrame:
    """Returns the cached release activity DataFrame, creating it if needed."""
    global _release_activity_df
    if _release_activity_df is None:
        _release_activity_df = _build_release_activity_dataframe(100)
    return _release_activity_df


def analyze_release_data(query: str) -> Dict:
    """
    Analyzes release activity data using natural language queries powered by PandasAI.

    This tool accepts a natural language question about the release activity data
    and returns the analysis result. It uses a pre-built DataFrame with 100 rows
    of release activity records containing employee, grant, vesting, tax, and
    release information.

    The data analyzer should call `get_supported_fields` first to understand
    available columns, then use this tool with natural language queries for
    slicing, dicing, filtering, grouping, and aggregating the data.

    Args:
        query (str):
            A natural language question about the release activity data.
            Examples:
            - "How many employees are in each department?"
            - "What is the total net value delivered grouped by grant type?"
            - "Show top 5 employees by fmv_at_release"
            - "Average tax withheld amount for active employees by country"
            - "How many releases failed vs completed?"
            - "What is the sum of shares released by department and grant type?"
            - "List employees where net_value_delivered > 500000"
            - "What percentage of releases used Sell-to-Cover tax method?"

    LLM Prompt Examples:
        - "Analyze release data: total shares released by department"
        - "Query release data for top earners"
        - "Break down release status counts"
        - "Show me a summary of tax withholding by country"
        - "Compare RSU vs PSU net value delivered"

    Returns:
        Dict containing:
            status (str): success or error
            query (str): The original query
            result (str): The analysis result from PandasAI
            total_rows (int): Number of rows in the dataset
            message (str): Status or error message
    """
    try:
        from pandasai import SmartDataframe

        df = _get_release_activity_df()

        api_key = os.environ.get("GOOGLE_API_KEY", "")
        sdf = SmartDataframe(
            df,
            config={
                "llm": f"google/gemini-2.0-flash",
                "api_key": api_key,
                "enable_cache": False,
            },
        )

        result = sdf.chat(query)

        # Convert result to string for consistent return
        if isinstance(result, pd.DataFrame):
            result_str = result.to_markdown(index=False)
        elif isinstance(result, pd.Series):
            result_str = result.to_markdown()
        else:
            result_str = str(result)

        return {
            "status": "success",
            "query": query,
            "result": result_str,
            "total_rows": len(df),
            "message": "Analysis completed successfully",
        }
    except Exception as e:
        return {
            "status": "error",
            "query": query,
            "result": None,
            "total_rows": 0,
            "message": f"Analysis failed: {str(e)}",
        }


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
        "2026-12-15",
    ]

    return {"status": "success", "vesting_dates": all_vesting_dates[:count]}


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
        "message": "Token and initial release file created",
    }


def calculate_tax(
    vesting_date: str, fmv: float, sales: float, tool_context: ToolContext
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
            ),
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
            ),
        }

    # Dummy tax calculation
    estimated_tax = 12345.67

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "summary": "Your total tax is $200K for 1,500 participants with sell-to-cover.",
        "approval_url": "https://dummy.com",
        "message": "Tax calculated successfully",
    }
