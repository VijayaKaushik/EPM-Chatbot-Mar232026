import math
import os
import pathlib
import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import pandas as pd
from google.adk.tools.tool_context import ToolContext


class VestingDateService:
    """Service to manage vesting dates from CSV, supporting dynamic filtering."""

    def __init__(self, csv_path: pathlib.Path = None):
        """
        Initialize the service with the vesting dates CSV.

        Args:
            csv_path (pathlib.Path, optional): Path to vesting_dates.csv.
                Defaults to vesting_data/vesting_dates.csv.
        """
        if csv_path is None:
            csv_path = pathlib.Path(__file__).parent / "vesting_data" / "vesting_dates.csv"
        self.csv_path = csv_path
        self._df = None

    def _load_csv(self) -> pd.DataFrame:
        """Load and cache the vesting dates CSV."""
        if self._df is None:
            if not self.csv_path.exists():
                raise FileNotFoundError(f"Vesting dates CSV not found: {self.csv_path}")
            self._df = pd.read_csv(self.csv_path, dtype={"client_id": str, "vesting_date": str})
        return self._df

    def get_all_dates(self, client_id: str) -> List[str]:
        """
        Get all vesting dates for a client, sorted ascending.

        Args:
            client_id (str): Client identifier.

        Returns:
            List[str]: Sorted list of vesting dates (YYYY-MM-DD format).
        """
        df = self._load_csv()
        dates = df[df["client_id"] == client_id]["vesting_date"].tolist()
        return sorted(dates)

    def get_next_n_dates(self, client_id: str, count: int = 1) -> List[str]:
        """
        Get the next N vesting dates greater than today for a client.

        Args:
            client_id (str): Client identifier.
            count (int): Number of future dates to return. Defaults to 1.

        Returns:
            List[str]: List of next N vesting dates (or fewer if not enough future dates).
        """
        all_dates = self.get_all_dates(client_id)
        today = datetime.now().date()
        future_dates = [d for d in all_dates if datetime.strptime(d, "%Y-%m-%d").date() > today]
        return future_dates[:count]

    def get_dates_in_month(self, client_id: str, month: int = None, year: int = None) -> List[str]:
        """
        Get all vesting dates in a specific month/year for a client.

        Args:
            client_id (str): Client identifier.
            month (int, optional): Month (1-12). If None, uses current month.
            year (int, optional): Year (YYYY). If None, uses current year.

        Returns:
            List[str]: List of vesting dates in the specified month.
        """
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        all_dates = self.get_all_dates(client_id)
        month_dates = [
            d for d in all_dates
            if datetime.strptime(d, "%Y-%m-%d").month == month
            and datetime.strptime(d, "%Y-%m-%d").year == year
        ]
        return month_dates

    def get_dates_in_range(self, client_id: str, start_date: str, end_date: str) -> List[str]:
        """
        Get all vesting dates between start_date and end_date (inclusive) for a client.

        Args:
            client_id (str): Client identifier.
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.

        Returns:
            List[str]: List of vesting dates in the specified range.
        """
        all_dates = self.get_all_dates(client_id)
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        range_dates = [
            d for d in all_dates
            if start <= datetime.strptime(d, "%Y-%m-%d").date() <= end
        ]
        return range_dates


def _safe_records(df: pd.DataFrame) -> List[Dict]:
    """Convert DataFrame rows to dicts, replacing all NaN/NA with None (valid JSON null)."""
    rows = []
    for record in df.to_dict(orient="records"):
        rows.append({
            k: None if (isinstance(v, float) and math.isnan(v)) else v
            for k, v in record.items()
        })
    return rows

VESTING_DATA_DIR = pathlib.Path(__file__).parent / "vesting_data" / "vesting_details"
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


def get_vesting_dates(
    client_id: str = "CLIENT_001",
    count: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict:
    """
    Returns vesting dates for a client from CSV, with flexible filtering.

    Loads vesting dates from vesting_dates.csv and filters based on the query parameters.
    Supports multiple query patterns through optional parameters.

    Args:
        client_id (str): Client identifier. Defaults to "CLIENT_001".
        count (int, optional): Return the next N future dates. If provided, ignores month/year/range.
        month (int, optional): Filter by month (1-12). If None, uses current month.
        year (int, optional): Filter by year (YYYY). If None, uses current year.
        start_date (str, optional): Start date for range filter (YYYY-MM-DD). Requires end_date.
        end_date (str, optional): End date for range filter (YYYY-MM-DD). Requires start_date.

    LLM Prompt Examples:
        - "Give me next vesting date" → count=1
        - "Give me next 3 vesting dates" → count=3
        - "Show all vesting dates in June" → month=6
        - "Get vesting dates for May 2027" → month=5, year=2027
        - "List vesting dates from 2026-05-01 to 2026-12-31" → start_date="2026-05-01", end_date="2026-12-31"
        - "Get all vesting dates for CLIENT_001" → (no filters, returns all)

    Returns:
        Dict:
            status (str): success or error
            vesting_dates (List[str]): List of matching vesting dates in YYYY-MM-DD format
            client_id (str): The client ID queried
            filter_type (str): Type of filter applied (all, next_n, month, range)
            total_found (int): Number of dates found
            message (str): Status message
    """
    try:
        service = VestingDateService()
        
        # Determine filter type and get dates
        if count is not None:
            # Next N dates
            dates = service.get_next_n_dates(client_id, count)
            filter_type = f"next_{count}"
        elif start_date and end_date:
            # Date range
            dates = service.get_dates_in_range(client_id, start_date, end_date)
            filter_type = f"range_{start_date}_to_{end_date}"
        elif month is not None:
            # Month filter (use provided year or current year)
            dates = service.get_dates_in_month(client_id, month, year)
            month_name = datetime(2000, month, 1).strftime("%B")
            filter_type = f"{month_name}_{year or datetime.now().year}"
        else:
            # All dates for client
            dates = service.get_all_dates(client_id)
            filter_type = "all"

        return {
            "status": "success",
            "vesting_dates": dates,
            "client_id": client_id,
            "filter_type": filter_type,
            "total_found": len(dates),
            "message": f"Retrieved {len(dates)} vesting date(s) for {client_id} ({filter_type})",
        }
    except FileNotFoundError as e:
        return {
            "status": "error",
            "vesting_dates": [],
            "client_id": client_id,
            "message": f"Error loading vesting dates: {str(e)}",
        }
    except Exception as e:
        return {
            "status": "error",
            "vesting_dates": [],
            "client_id": client_id,
            "message": f"Failed to retrieve vesting dates: {str(e)}",
        }


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
    participants: List[Dict] = _safe_records(df)

    # Write employee_ids to state so orchestrator can pick them up reliably
    employee_ids = [p["employee_id"] for p in participants]
    tool_context.state["last_vesting_employee_ids"] = employee_ids

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "token_id": token_id,
        "employee_ids": employee_ids,
        "participant_count": len(participants),
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


def filter_participants(
    vesting_date: str,
    grant_type: Optional[str] = None,
    officer_status: Optional[str] = None,
    tax_method: Optional[str] = None,
    tool_context: ToolContext = None,
) -> Dict:
    """
    Filters unbatched participants for a vesting date by optional criteria.

    Loads the vesting CSV for the given date and returns only rows where
    batch_id is null/empty (unbatched). Applies grant_type, officer_status,
    and tax_method filters using AND logic when provided. Stores the active
    filters and matched employee IDs in session state for use by
    calculate_tax_for_batch and create_batch.

    Args:
        vesting_date (str): Vesting date in YYYY-MM-DD format.
        grant_type (str, optional): Filter by grant type (RSU / PSU / Stock Option).
        officer_status (str, optional): Filter by officer status (Officer / Non-Officer).
        tax_method (str, optional): Filter by tax method (Net Issuance / Sell-to-Cover / Cash Payment).
        tool_context (ToolContext): ADK tool context for session state.

    LLM Prompt Examples:
        - "Filter RSU participants for 2026-05-15"
        - "Show only Officers for the next vesting date"
        - "Filter by Sell-to-Cover tax method"
        - "Show all unbatched participants"

    State Updates:
        tool_context.state["active_filters"]: dict of applied filter values
        tool_context.state["filtered_employee_ids"]: list of matched employee_ids
        tool_context.state["_filtered_tranche_keys"]: list of (employee_id, tranche_id) tuples for row-level matching

    Returns:
        Dict containing:
            status (str): success, no_match, or error
            vesting_date (str): The requested date
            filters_applied (Dict): Active filter values
            total_matched (int): Number of rows matching filters
            total_unbatched (int): Total unbatched rows before filtering
            total_remaining_after_this (int): Unbatched rows that won't be in this batch
            participants (List[Dict]): Matched participant rows
            message (str): Status message
    """
    csv_path = VESTING_DATA_DIR / f"{vesting_date}.csv"
    if not csv_path.exists():
        return {
            "status": "error",
            "vesting_date": vesting_date,
            "message": f"No vesting data found for date {vesting_date}",
        }

    df = pd.read_csv(csv_path, dtype={"employee_id": str})

    # Treat all rows as unbatched if batch_id column doesn't exist yet
    if "batch_id" not in df.columns:
        df["batch_id"] = None

    # Unbatched rows only
    unbatched = df[df["batch_id"].isna() | (df["batch_id"] == "")]
    total_unbatched = len(unbatched)

    filtered = unbatched.copy()

    # Apply AND filters
    if grant_type:
        filtered = filtered[filtered["grant_type"] == grant_type]
    if officer_status and "officer_status" in filtered.columns:
        filtered = filtered[filtered["officer_status"] == officer_status]
    if tax_method:
        filtered = filtered[filtered["tax_method"] == tax_method]

    total_matched = len(filtered)

    if total_matched == 0:
        return {
            "status": "no_match",
            "vesting_date": vesting_date,
            "filters_applied": {
                "grant_type": grant_type,
                "officer_status": officer_status,
                "tax_method": tax_method,
            },
            "total_matched": 0,
            "total_unbatched": total_unbatched,
            "total_remaining_after_this": total_unbatched,
            "participants": [],
            "message": (
                f"No unbatched participants match the given filters for {vesting_date}. "
                f"Total unbatched: {total_unbatched}."
            ),
        }

    # Store filter state and matched IDs
    matched_ids = filtered["employee_id"].tolist()
    has_tranche = "tranche_id" in filtered.columns
    tranche_keys = (
        list(zip(filtered["employee_id"].tolist(), filtered["tranche_id"].tolist()))
        if has_tranche
        else [(eid, None) for eid in matched_ids]
    )

    tool_context.state["active_filters"] = {
        "vesting_date": vesting_date,
        "grant_type": grant_type,
        "officer_status": officer_status,
        "tax_method": tax_method,
    }
    tool_context.state["filtered_employee_ids"] = matched_ids
    tool_context.state["_filtered_tranche_keys"] = tranche_keys

    total_remaining = total_unbatched - total_matched

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "filters_applied": {
            "grant_type": grant_type,
            "officer_status": officer_status,
            "tax_method": tax_method,
        },
        "total_matched": total_matched,
        "total_unbatched": total_unbatched,
        "total_remaining_after_this": total_remaining,
        "participants": _safe_records(filtered),
        "message": (
            f"{total_matched} participants matched filters for {vesting_date}. "
            f"{total_remaining} will remain unbatched after this batch."
        ),
    }


def calculate_tax_for_batch(
    fmv: float,
    sales_price: float,
    tool_context: ToolContext,
) -> Dict:
    """
    Calculates tax for the currently filtered participants using provided FMV and sales price.

    Reads filtered_employee_ids and active_filters from session state (set by
    filter_participants). Computes tax per row using the same logic as calculate_tax.
    Stores results in state for create_batch to consume.

    Args:
        fmv (float): Fair Market Value per share at release.
        sales_price (float): Sale price per share.
        tool_context (ToolContext): ADK tool context for session state.

    LLM Prompt Examples:
        - "Calculate tax with FMV 45.50 and sales price 52.00"
        - "Compute taxes using FMV=50, sales price=60"
        - "Run tax calculation"

    Preconditions:
        - filter_participants must have been called first for this session.

    State Updates:
        tool_context.state["tax_results"]: {employee_id: total_tax_amount}
        tool_context.state["_tax_rows"]: per-row list for create_batch row matching
        tool_context.state["fmv"]: fmv used
        tool_context.state["sales_price"]: sales_price used

    Returns:
        Dict containing:
            status (str): success or error
            vesting_date (str): The vesting date being processed
            fmv (float): FMV used
            sales_price (float): Sales price used
            participants_processed (int): Number of rows processed
            summary (Dict): Aggregate totals
            per_participant (List[Dict]): Row-level tax breakdown
            message (str): Status message
    """
    active_filters = tool_context.state.get("active_filters")
    filtered_ids = tool_context.state.get("filtered_employee_ids")

    if not active_filters or filtered_ids is None:
        return {
            "status": "error",
            "message": "No filtered participants in session. Call filter_participants first.",
        }

    vesting_date = active_filters["vesting_date"]
    csv_path = VESTING_DATA_DIR / f"{vesting_date}.csv"
    if not csv_path.exists():
        return {
            "status": "error",
            "vesting_date": vesting_date,
            "message": f"No vesting data file found for {vesting_date}",
        }

    df = pd.read_csv(csv_path, dtype={"employee_id": str})

    # Match exact rows using tranche keys if available, otherwise employee_id
    tranche_keys = tool_context.state.get("_filtered_tranche_keys")
    has_tranche = "tranche_id" in df.columns and tranche_keys and tranche_keys[0][1] is not None

    if has_tranche:
        key_set = set((eid, tid) for eid, tid in tranche_keys)
        mask = df.apply(lambda r: (r["employee_id"], r["tranche_id"]) in key_set, axis=1)
    else:
        id_set = set(filtered_ids)
        mask = df["employee_id"].isin(id_set)

    matched_df = df[mask].copy()

    if matched_df.empty:
        return {
            "status": "error",
            "vesting_date": vesting_date,
            "message": "Matched rows not found in CSV. Session state may be stale.",
        }

    random.seed(int(vesting_date.replace("-", "")))

    tax_rows = []
    tax_results: Dict[str, float] = {}

    for _, row in matched_df.iterrows():
        tax_amount = _calculate_tax_amount(int(row["shares_released"]), fmv, sales_price)
        emp_id = row["employee_id"]
        tranche_id = row["tranche_id"] if (has_tranche and pd.notna(row.get("tranche_id"))) else None
        net_val = row.get("net_value_delivered", 0)
        net_val = float(net_val) if pd.notna(net_val) else 0.0

        tax_rows.append({
            "employee_id": emp_id,
            "tranche_id": tranche_id,
            "employee_name": row.get("employee_name", "") or "",
            "grant_type": row.get("grant_type", "") or "",
            "shares_released": int(row["shares_released"]),
            "net_value_delivered": net_val,
            "tax_amount": tax_amount,
        })

        # Accumulate per employee for the spec-required tax_results shape
        tax_results[emp_id] = round(tax_results.get(emp_id, 0.0) + tax_amount, 2)

    # Summaries
    total_shares = sum(r["shares_released"] for r in tax_rows)
    total_fmv_value = round(total_shares * fmv, 2)
    total_tax = round(sum(r["tax_amount"] for r in tax_rows), 2)
    total_net = round(sum(r["net_value_delivered"] for r in tax_rows), 2)

    tool_context.state["tax_results"] = tax_results
    tool_context.state["_tax_rows"] = tax_rows
    tool_context.state["fmv"] = fmv
    tool_context.state["sales_price"] = sales_price

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "fmv": fmv,
        "sales_price": sales_price,
        "participants_processed": len(tax_rows),
        "summary": {
            "total_shares_released": total_shares,
            "total_fmv": total_fmv_value,
            "total_tax_withheld": total_tax,
            "net_value_delivered": total_net,
        },
        "per_participant": tax_rows,
        "message": (
            f"Tax calculated for {len(tax_rows)} participant rows. "
            f"Total tax withheld: ${total_tax:,.2f}. Call create_batch to commit."
        ),
    }


def create_batch(tool_context: ToolContext) -> Dict:
    """
    Creates a release batch for the filtered and tax-calculated participants.

    Reads active_filters, filtered_employee_ids, tax_results, fmv, and sales_price
    from session state. Generates a unique batch_id, writes batch fields back into
    the vesting CSV (batch_id, tax_amount, fmv, sales_price, batch_created_at,
    approval_url), then clears batch-related state.

    Args:
        tool_context (ToolContext): ADK tool context for session state.

    LLM Prompt Examples:
        - "Create the batch"
        - "Commit this batch and generate approval URL"
        - "Go ahead and create the batch"
        - "Submit the release batch"

    Preconditions:
        - filter_participants must have been called (active_filters, filtered_employee_ids in state)
        - calculate_tax_for_batch must have been called (tax_results, fmv, sales_price in state)

    Returns:
        Dict containing:
            status (str): success or error
            batch_id (str): Generated batch identifier (e.g. BATCH-A1B2C3D4)
            vesting_date (str): The vesting date processed
            participants_batched (int): Number of rows written to this batch
            remaining_unbatched (int): Rows still unbatched after this commit
            approval_url (str): URL to approve this batch
            summary (Dict): Aggregate totals for this batch
            message (str): Status message
    """
    active_filters = tool_context.state.get("active_filters")
    filtered_ids = tool_context.state.get("filtered_employee_ids")
    tax_results = tool_context.state.get("tax_results")
    tax_rows = tool_context.state.get("_tax_rows")
    fmv = tool_context.state.get("fmv")
    sales_price = tool_context.state.get("sales_price")

    missing = []
    if not active_filters:
        missing.append("active_filters (call filter_participants first)")
    if filtered_ids is None:
        missing.append("filtered_employee_ids (call filter_participants first)")
    if tax_results is None:
        missing.append("tax_results (call calculate_tax_for_batch first)")
    if fmv is None:
        missing.append("fmv (call calculate_tax_for_batch first)")
    if sales_price is None:
        missing.append("sales_price (call calculate_tax_for_batch first)")

    if missing:
        return {
            "status": "error",
            "message": f"Missing required state: {'; '.join(missing)}",
        }

    vesting_date = active_filters["vesting_date"]
    csv_path = VESTING_DATA_DIR / f"{vesting_date}.csv"
    if not csv_path.exists():
        return {
            "status": "error",
            "vesting_date": vesting_date,
            "message": f"No vesting data file found for {vesting_date}",
        }

    batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"
    approval_url = f"https://approval.dummy.com/{batch_id}"

    # EST timestamp
    est = timezone(timedelta(hours=-5))
    batch_created_at = datetime.now(est).strftime("%Y-%m-%d %H:%M:%S EST")

    df = pd.read_csv(csv_path, dtype={"employee_id": str})

    # Ensure batch columns exist
    for col in ["batch_id", "tax_amount", "fmv", "sales_price", "batch_created_at", "approval_url"]:
        if col not in df.columns:
            df[col] = None

    # Build a per-row tax lookup keyed by (employee_id, tranche_id) or employee_id
    has_tranche = "tranche_id" in df.columns and tax_rows and tax_rows[0].get("tranche_id") is not None
    if has_tranche:
        row_tax_map = {(r["employee_id"], r["tranche_id"]): r["tax_amount"] for r in tax_rows}
    else:
        row_tax_map = {r["employee_id"]: r["tax_amount"] for r in tax_rows}

    tranche_keys = tool_context.state.get("_filtered_tranche_keys")
    if has_tranche:
        key_set = set((eid, tid) for eid, tid in tranche_keys)
        match_mask = df.apply(lambda r: (r["employee_id"], r["tranche_id"]) in key_set, axis=1)
    else:
        id_set = set(filtered_ids)
        match_mask = df["employee_id"].isin(id_set) & (df["batch_id"].isna() | (df["batch_id"] == ""))

    participants_batched = match_mask.sum()

    for idx in df[match_mask].index:
        row = df.loc[idx]
        emp_id = row["employee_id"]
        key = (emp_id, row["tranche_id"]) if has_tranche else emp_id
        df.at[idx, "batch_id"] = batch_id
        df.at[idx, "tax_amount"] = row_tax_map.get(key, 0.0)
        df.at[idx, "fmv"] = fmv
        df.at[idx, "sales_price"] = sales_price
        df.at[idx, "batch_created_at"] = batch_created_at
        df.at[idx, "approval_url"] = approval_url

    df.to_csv(csv_path, index=False)

    # Count remaining unbatched rows
    remaining_unbatched = int((df["batch_id"].isna() | (df["batch_id"] == "")).sum())

    # Batch summary
    total_shares = sum(r["shares_released"] for r in tax_rows)
    total_tax = round(sum(r["tax_amount"] for r in tax_rows), 2)
    total_net = round(sum(r["net_value_delivered"] for r in tax_rows), 2)

    # Clear batch-related state
    tool_context.state["active_filters"] = None
    tool_context.state["filtered_employee_ids"] = None
    tool_context.state["tax_results"] = None
    tool_context.state["_tax_rows"] = None
    tool_context.state["_filtered_tranche_keys"] = None
    tool_context.state["fmv"] = None
    tool_context.state["sales_price"] = None

    return {
        "status": "success",
        "batch_id": batch_id,
        "vesting_date": vesting_date,
        "participants_batched": int(participants_batched),
        "remaining_unbatched": remaining_unbatched,
        "approval_url": approval_url,
        "summary": {
            "total_shares_released": total_shares,
            "total_tax_withheld": total_tax,
            "net_value_delivered": total_net,
        },
        "message": (
            f"Batch {batch_id} created for {int(participants_batched)} participant rows. "
            f"{remaining_unbatched} rows remain unbatched. "
            f"Approval URL: {approval_url}"
        ),
    }
