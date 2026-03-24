import os
import pathlib
import random
import uuid
from typing import Dict, List, Optional

import pandas as pd
from google.adk.tools.tool_context import ToolContext

VESTING_DATA_DIR = pathlib.Path(__file__).parent / "vesting_data"
TAX_DATA_DIR = pathlib.Path(__file__).parent / "tax_data"

VESTING_FIELDS = [
    {"column_name": "employee_id", "label": "Employee ID", "description": "Unique identifier for the employee", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "employee_name", "label": "Employee Name", "description": "Full name of the employee", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "email", "label": "Email", "description": "Email address of the employee", "data_type": "string", "filterable": True, "sortable": False},
    {"column_name": "department", "label": "Department", "description": "Department the employee belongs to (e.g. Finance, Sales, Engineering)", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "employee_status", "label": "Employee Status", "description": "Current employment status (e.g. Active, Terminated, On Leave)", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "grant_id", "label": "Grant ID", "description": "Unique identifier for the equity grant", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "grant_date", "label": "Grant Date", "description": "Date when the equity grant was issued (YYYY-MM-DD)", "data_type": "date", "filterable": True, "sortable": True},
    {"column_name": "grant_type", "label": "Grant Type", "description": "Type of equity grant (e.g. RSU, PSU, Stock Option)", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "total_shares_granted", "label": "Total Shares Granted", "description": "Total number of shares in the original grant", "data_type": "integer", "filterable": True, "sortable": True},
    {"column_name": "vesting_schedule", "label": "Vesting Schedule", "description": "Schedule type for vesting (e.g. 4-year monthly, 3-year quarterly)", "data_type": "string", "filterable": True, "sortable": False},
    {"column_name": "release_date", "label": "Release Date", "description": "Date when shares were released (YYYY-MM-DD)", "data_type": "date", "filterable": True, "sortable": True},
    {"column_name": "release_number", "label": "Release Number", "description": "Sequential release number for the grant", "data_type": "integer", "filterable": True, "sortable": True},
    {"column_name": "shares_released", "label": "Shares Released", "description": "Number of shares released in this vesting event", "data_type": "integer", "filterable": True, "sortable": True},
    {"column_name": "net_shares_delivered", "label": "Net Shares Delivered", "description": "Number of shares delivered to employee after tax withholding", "data_type": "integer", "filterable": True, "sortable": True},
    {"column_name": "stock_price_at_release", "label": "Stock Price at Release", "description": "Market stock price at the time of release", "data_type": "float", "filterable": True, "sortable": True},
    {"column_name": "fmv_at_release", "label": "FMV at Release", "description": "Fair Market Value of released shares at the time of release", "data_type": "float", "filterable": True, "sortable": True},
    {"column_name": "net_value_delivered", "label": "Net Value Delivered", "description": "Net dollar value delivered to the employee after taxes", "data_type": "float", "filterable": True, "sortable": True},
    {"column_name": "tax_method", "label": "Tax Method", "description": "Method used for tax withholding (e.g. Net Issuance, Sell-to-Cover)", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "brokerage_account", "label": "Brokerage Account", "description": "Brokerage account identifier for share delivery", "data_type": "string", "filterable": True, "sortable": False},
    {"column_name": "release_status", "label": "Release Status", "description": "Current status of the release (e.g. Completed, Pending, Failed)", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "processed_date", "label": "Processed Date", "description": "Date when the release was processed (YYYY-MM-DD)", "data_type": "date", "filterable": True, "sortable": True},
    {"column_name": "processed_by", "label": "Processed By", "description": "Name of the person who processed the release", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "country", "label": "Country", "description": "Country or territory of the employee", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "currency", "label": "Currency", "description": "Currency code for the transaction (e.g. USD, EUR, GBP)", "data_type": "string", "filterable": True, "sortable": True},
    {"column_name": "notes", "label": "Notes", "description": "Additional notes or comments about the release", "data_type": "string", "filterable": False, "sortable": False},
]


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
        #"participants": participants,
        "message": f"Retrieved {len(participants)} participant records for {vesting_date}",
    }


def get_supported_fields() -> Dict:
    """
    Returns all supported fields/columns available in the vesting data.

    Each field includes its column name, human-readable label, description,
    data type, and whether it supports filtering and sorting. Use this tool
    FIRST before calling analyze_vesting_data, so you know which columns
    are available and their types.

    LLM Prompt Examples:
        - "What fields are available in the vesting data?"
        - "Show me all supported columns"
        - "What can I filter or sort by?"
        - "Get the schema for vesting data"

    Returns:
        Dict containing:
            status (str): success
            total_fields (int): Total number of available fields
            fields (List[Dict]): List of field definitions
    """
    return {
        "status": "success",
        "total_fields": len(VESTING_FIELDS),
        "fields": VESTING_FIELDS,
    }


def _load_all_vesting_data() -> pd.DataFrame:
    """Loads and concatenates all vesting CSV files into a single DataFrame."""
    all_dfs = []
    for csv_file in sorted(VESTING_DATA_DIR.glob("*.csv")):
        df = pd.read_csv(csv_file, dtype={"employee_id": str})
        all_dfs.append(df)
    if not all_dfs:
        return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)


from pandasai.llm.base import LLM as _PaiLLM


class GeminiLLM(_PaiLLM):
    """PandasAI-compatible LLM wrapper using Google Gemini via google-genai."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        super().__init__(api_key=api_key)
        from google import genai

        self.model = model
        self._client = genai.Client(api_key=api_key)

    @property
    def type(self) -> str:
        return "google-gemini"

    def call(self, instruction, context=None) -> str:
        prompt = instruction.to_string() if hasattr(instruction, "to_string") else str(instruction)
        self.last_prompt = prompt
        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text


def analyze_vesting_data(query: str, vesting_date: Optional[str] = None) -> Dict:
    """
    Analyzes vesting data using natural language queries powered by PandasAI.

    This tool accepts a natural language question about the vesting data
    and returns the analysis result. If a vesting_date is provided, only
    data for that date is analyzed. Otherwise, all vesting dates are
    combined into a single dataset for cross-date analysis.

    Call `get_supported_fields` first to understand the available columns,
    then use this tool with natural language queries for slicing, dicing,
    filtering, grouping, and aggregating the data.

    Args:
        query (str):
            A natural language question about the vesting data.
            Examples:
            - "How many employees are in each department?"
            - "What is the total net value delivered grouped by grant type?"
            - "Show top 5 employees by fmv_at_release"
            - "Average shares released for active employees by country"
            - "How many releases failed vs completed?"
            - "Compare RSU vs PSU net value delivered"
            - "List employees where net_value_delivered > 300000"
            - "What percentage of releases used Sell-to-Cover tax method?"

        vesting_date (str, optional):
            If provided, analyze only data for this specific vesting date
            (YYYY-MM-DD). If omitted, all vesting dates are combined.

    LLM Prompt Examples:
        - "Analyze vesting data: total shares released by department"
        - "Query vesting data for top earners"
        - "Break down release status counts"
        - "Show me a summary of net value by country"
        - "Compare RSU vs PSU vs Stock Option grants"

    Returns:
        Dict containing:
            status (str): success or error
            query (str): The original query
            result (str): The analysis result from PandasAI
            total_rows (int): Number of rows in the dataset
            message (str): Status or error message
    """
    try:
        from pandasai.agent import Agent as PaiAgent

        if vesting_date:
            csv_path = VESTING_DATA_DIR / f"{vesting_date}.csv"
            if not csv_path.exists():
                return {
                    "status": "error",
                    "query": query,
                    "result": None,
                    "total_rows": 0,
                    "message": f"No vesting data found for date {vesting_date}",
                }
            df = pd.read_csv(csv_path, dtype={"employee_id": str})

            # Join tax data if available for this date
            tax_path = TAX_DATA_DIR / f"{vesting_date}.csv"
            if tax_path.exists():
                tax_df = pd.read_csv(tax_path, dtype={"employee_id": str})
                df = df.merge(tax_df, on="employee_id", how="left", suffixes=("", "_tax"))
        else:
            df = _load_all_vesting_data()
            if df.empty:
                return {
                    "status": "error",
                    "query": query,
                    "result": None,
                    "total_rows": 0,
                    "message": "No vesting data files found",
                }

            # Join all available tax data
            tax_dfs = []
            for tax_file in sorted(TAX_DATA_DIR.glob("*.csv")):
                tdf = pd.read_csv(tax_file, dtype={"employee_id": str})
                # Add release_date so the join is unique per employee+date
                tdf["release_date"] = tax_file.stem
                tax_dfs.append(tdf)
            if tax_dfs:
                all_tax = pd.concat(tax_dfs, ignore_index=True)
                df = df.merge(all_tax, on=["employee_id", "release_date"], how="left", suffixes=("", "_tax"))

        tax_included = "tax_amount" in df.columns
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        llm = GeminiLLM(api_key=api_key, model="gemini-2.5-flash")

        agent = PaiAgent(df, config={"llm": llm})
        result = agent.chat(query)

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
            "tax_data_included": tax_included,
            "message": f"Analysis completed successfully. {'Tax data joined.' if tax_included else 'No tax data available.'}",
        }
    except Exception as e:
        return {
            "status": "error",
            "query": query,
            "result": None,
            "total_rows": 0,
            "message": f"Analysis failed: {str(e)}",
        }


def _calculate_tax_amount(shares_released: int, fmv: float, sales_price: float) -> float:
    """Random tax calculation: base tax + random supplemental rate."""
    base_tax_rate = random.uniform(0.22, 0.37)
    supplemental_rate = random.uniform(0.01, 0.08)
    taxable_income = shares_released * fmv
    capital_gain = shares_released * max(sales_price - fmv, 0)
    tax = (taxable_income * base_tax_rate) + (capital_gain * supplemental_rate)
    return round(tax, 2)


def calculate_tax(vesting_date: str, tool_context: ToolContext) -> Dict:
    """
    Calculates tax for all participants on a given vesting date.

    Loads the vesting detail CSV for the specified date, computes tax for each
    participant using FMV=10 and sales_price=20, and saves the results as a
    CSV in the tax_data folder. The vesting date must already exist in the
    agent state (call get_vesting_details first).

    Args:
        vesting_date (str):
            Vesting date for which to calculate tax. Format: YYYY-MM-DD.

        tool_context (ToolContext):
            ADK tool context. Requires vesting details to be present under
            state["token_vesting_list"]. If missing, the agent should first
            call get_vesting_details.

    LLM Prompt Examples:
        - "Calculate tax for vesting date 2026-05-15"
        - "Run tax calculation for next vesting date"
        - "Compute taxes for this vesting event"
        - "Generate tax report for 2026-06-15"

    Preconditions:
        - Vesting details must already exist in state for this date.
        - If missing, the agent should first call get_vesting_details.

    Returns:
        Dict containing:
            status (str): success or error
            vesting_date (str): The vesting date processed
            fmv (float): FMV used for calculation (10)
            sales_price (float): Sales price used for calculation (20)
            participants_processed (int): Number of participants
            output_file (str): Path to the generated tax CSV
            summary (List[Dict]): Preview of tax results
            message (str): Status message
    """
    # Validate that vesting details exist in state
    tool_vesting_list = tool_context.state.get("token_vesting_list")
    if tool_vesting_list is None:
        return {
            "status": "error",
            "vesting_date": vesting_date,
            "message": "No vesting details in state. Call get_vesting_details first.",
        }

    token_id = None
    for vd, tid in tool_vesting_list:
        if vd == vesting_date:
            token_id = tid
            break

    if token_id is None:
        return {
            "status": "error",
            "vesting_date": vesting_date,
            "message": f"Vesting details not found for {vesting_date}. Call get_vesting_details first.",
        }

    # Load vesting data
    csv_path = VESTING_DATA_DIR / f"{vesting_date}.csv"
    if not csv_path.exists():
        return {
            "status": "error",
            "vesting_date": vesting_date,
            "message": f"No vesting data file found for {vesting_date}",
        }

    vesting_df = pd.read_csv(csv_path, dtype={"employee_id": str})

    # Fixed FMV and sales price
    fmv = 10.0
    sales_price = 20.0

    # Calculate tax for each participant
    random.seed(int(vesting_date.replace("-", "")))  # deterministic per date
    tax_rows = []
    for _, row in vesting_df.iterrows():
        tax_amount = _calculate_tax_amount(row["shares_released"], fmv, sales_price)
        tax_rows.append({
            "employee_id": row["employee_id"],
            "tax_amount": tax_amount,
            "fmv": fmv,
            "sales_price": sales_price,
        })

    tax_df = pd.DataFrame(tax_rows)

    # Save to tax_data folder
    TAX_DATA_DIR.mkdir(exist_ok=True)
    output_path = TAX_DATA_DIR / f"{vesting_date}.csv"
    tax_df.to_csv(output_path, index=False)

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "fmv": fmv,
        "sales_price": sales_price,
        "participants_processed": len(tax_df),
        "output_file": str(output_path),
        #"summary": tax_df.to_dict(orient="records"),
        "message": f"Tax calculated for {len(tax_df)} participants. Output saved to tax_data/{vesting_date}.csv",
    }
