"""
Tools for release management with filtering and planning capabilities.

Provides:
- Vesting date retrieval
- Vesting detail fetching with data loading
- Execution plan creation
- Filter extraction from natural language
- Filter application to tranche data
- Tax calculation with filters
- Batch creation with metadata
"""

from typing import Dict, List, Optional
import uuid
import json
import pathlib
import os
from datetime import datetime
import random

from google.adk.tools.tool_context import ToolContext
import google.generativeai as genai
from dotenv import load_dotenv

from .models import (
    FilterCondition,
    FilterConditions,
    PlanStep,
    ExecutionPlan,
    TaxResult,
    BatchMetadata,
    BatchRecord,
    Batch,
    FilterOperator,
    PlanStepStatus,
    BatchStatus
)

# Load environment variables
load_dotenv()

# Configure Gemini for LLM-based filter extraction
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"


def call_gemini(prompt: str) -> str:
    """Call Gemini LLM for text generation."""
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text or ""


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


def generate_mock_tranche_data(vesting_date: str, count: int = 50) -> List[Dict]:
    """
    Generate comprehensive mock tranche data for testing.

    Generates diverse data across:
    - Grant types: RSU (40%), Stock Options (30%), Restricted Stock (20%), PSU (10%)
    - Shares: 1000-15000 range
    - Departments: Engineering (40%), Sales (25%), Finance (15%), Marketing (10%), HR (10%)
    - Countries: US (60%), UK (20%), CA (15%), Other (5%)
    - Status: Active (90%), Terminated (10%)
    """
    grant_types = ["RSU", "Stock Option", "Restricted Stock", "PSU"]
    grant_weights = [0.4, 0.3, 0.2, 0.1]

    departments = ["Engineering", "Sales", "Finance", "Marketing", "HR"]
    dept_weights = [0.4, 0.25, 0.15, 0.1, 0.1]

    countries = ["United States", "United Kingdom", "Canada", "Germany", "France", "Australia"]
    country_weights = [0.6, 0.2, 0.15, 0.02, 0.02, 0.01]

    statuses = ["Active", "Terminated"]
    status_weights = [0.9, 0.1]

    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa",
                   "William", "Jennifer", "James", "Amanda", "Richard", "Jessica", "Thomas"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                  "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor", "Thomas", "Moore"]

    tranches = []

    for i in range(count):
        employee_id = f"{uuid.uuid4().hex[:8].upper()}"
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        grant_type = random.choices(grant_types, weights=grant_weights)[0]
        department = random.choices(departments, weights=dept_weights)[0]
        country = random.choices(countries, weights=country_weights)[0]
        status = random.choices(statuses, weights=status_weights)[0]

        # Vary shares from 1000 to 15000
        shares_released = random.randint(1000, 15000)

        tranche = {
            "employee_id": employee_id,
            "employee_name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "department": department,
            "employee_status": status,
            "grant_id": f"GR-{uuid.uuid4().hex[:8].upper()}",
            "grant_date": "2024-01-15",
            "grant_type": grant_type,
            "total_shares_granted": shares_released * 2,
            "vesting_schedule": "4-year quarterly",
            "release_date": vesting_date,
            "release_number": random.randint(1, 16),
            "shares_released": shares_released,
            "shares_withheld_for_taxes": 0,
            "net_shares_delivered": 0,
            "stock_price_at_release": None,
            "fmv_at_release": None,
            "sale_price_at_release": None,
            "tax_withheld_amount": None,
            "tax_method": "Sell-to-Cover",
            "brokerage_account": f"BR-{random.randint(100000, 999999)}",
            "release_status": "Pending",
            "processed_date": vesting_date,
            "processed_by": f"{random.choice(first_names)} {random.choice(last_names)}",
            "country": country,
            "currency": "USD",
            "notes": ""
        }

        tranches.append(tranche)

    return tranches


def get_vesting_details_with_data(vesting_date: str, tool_context: ToolContext) -> Dict:
    """
    Retrieves details for a specific vesting date and loads tranche data.

    Attempts to load data from JSON file (release_activities_{vesting_date}.json).
    If file not found, generates comprehensive mock data.

    Stores data in state under:
    - state["tranche_data"][vesting_date]: Full tranche data
    - state["token_vesting_list"]: Appends (vesting_date, token_id) tuple

    Args:
        vesting_date (str): Vesting date in YYYY-MM-DD format
        tool_context (ToolContext): ADK tool context for state management

    Returns:
        Dict containing:
            status (str): success or error
            vesting_date (str): Requested vesting date
            token_id (str): Generated workflow token
            tranche_count (int): Number of tranches loaded
            message (str): Status message
    """
    token_id = f"token_{uuid.uuid4().hex[:8]}"

    # Initialize state structures if needed
    if "tranche_data" not in tool_context.state:
        tool_context.state["tranche_data"] = {}

    if "token_vesting_list" not in tool_context.state:
        tool_context.state["token_vesting_list"] = []

    # Try to load from JSON file
    current_dir = pathlib.Path(__file__).parent.parent
    json_file = current_dir / f"release_activities_{vesting_date}.json"

    if json_file.exists():
        with open(json_file, 'r') as f:
            tranche_data = json.load(f)
        message = f"Loaded {len(tranche_data)} tranches from file"
    else:
        # Generate mock data
        tranche_data = generate_mock_tranche_data(vesting_date, count=50)
        message = f"Generated {len(tranche_data)} mock tranches (file not found)"

    # Store in state
    tool_context.state["tranche_data"][vesting_date] = tranche_data
    tool_context.state["token_vesting_list"].append((vesting_date, token_id))

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "token_id": token_id,
        "tranche_count": len(tranche_data),
        "message": message
    }


def create_execution_plan(vesting_date: str, user_query: str, tool_context: ToolContext) -> Dict:
    """
    Creates a structured execution plan before workflow execution.

    Analyzes user query to detect:
    - Filter conditions (grant type, amount ranges, departments, etc.)
    - FMV and sales price parameters

    Builds step-by-step plan with proper sequencing.

    Args:
        vesting_date (str): Vesting date to process
        user_query (str): User's natural language query
        tool_context (ToolContext): ADK tool context

    Returns:
        Dict containing:
            status (str): success or error
            plan_id (str): Unique plan identifier
            steps (List[Dict]): Ordered execution steps
            has_filters (bool): Whether filters were detected
            message (str): Status message
    """
    plan_id = f"PLAN_{uuid.uuid4().hex[:8].upper()}"

    # Detect filters in query
    filter_keywords = ["RSU", "option", "restricted", "PSU", "above", "below", "greater",
                       "less", "department", "engineering", "sales", "finance", "marketing",
                       "country", "terminated", "active"]
    has_filters = any(keyword.lower() in user_query.lower() for keyword in filter_keywords)

    # Detect FMV/sales parameters
    fmv_detected = "fmv" in user_query.lower() or "fair market value" in user_query.lower()
    sales_detected = "sales" in user_query.lower() or "sale price" in user_query.lower()

    # Extract numeric values if present
    import re
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', user_query)
    fmv_value = None
    sales_value = None

    if fmv_detected and len(numbers) >= 1:
        fmv_value = float(numbers[0])
    if sales_detected and len(numbers) >= 2:
        sales_value = float(numbers[1])
    elif sales_detected and len(numbers) >= 1 and not fmv_detected:
        sales_value = float(numbers[0])

    # Build execution steps
    steps = []
    step_num = 1

    # Step 1: Always fetch vesting details
    steps.append({
        "step_number": step_num,
        "action": "get_vesting_details_with_data",
        "description": f"Fetch vesting details and tranche data for {vesting_date}",
        "required_inputs": ["vesting_date"],
        "expected_output": "Tranche data loaded into state",
        "status": "pending"
    })
    step_num += 1

    # Steps 2-3: If filters detected, add filter extraction and application
    if has_filters:
        steps.append({
            "step_number": step_num,
            "action": "extract_filters_from_query",
            "description": "Extract filter conditions from user query",
            "required_inputs": ["user_query"],
            "expected_output": "Structured filter conditions",
            "status": "pending"
        })
        step_num += 1

        steps.append({
            "step_number": step_num,
            "action": "apply_filter",
            "description": "Apply filters to subset tranche data",
            "required_inputs": ["vesting_date", "filter_conditions"],
            "expected_output": "Filtered tranche dataset",
            "status": "pending"
        })
        step_num += 1

    # Step N-1: Calculate tax
    steps.append({
        "step_number": step_num,
        "action": "calculate_tax_with_filters",
        "description": "Calculate tax for tranches using FMV and sales price",
        "required_inputs": ["vesting_date", "fmv", "sales"],
        "expected_output": "Tax results for each tranche",
        "status": "pending"
    })
    step_num += 1

    # Step N: Create batch
    steps.append({
        "step_number": step_num,
        "action": "create_batch",
        "description": "Generate release batch with metadata and approval URL",
        "required_inputs": ["vesting_date"],
        "expected_output": "Batch file and approval URL",
        "status": "pending"
    })

    # Create execution plan
    plan = {
        "plan_id": plan_id,
        "vesting_date": vesting_date,
        "steps": steps,
        "has_filters": has_filters,
        "fmv_value": fmv_value,
        "sales_value": sales_value
    }

    # Store in state
    tool_context.state["execution_plan"] = plan

    return {
        "status": "success",
        "plan_id": plan_id,
        "steps": steps,
        "has_filters": has_filters,
        "message": f"Created execution plan with {len(steps)} steps"
    }


def extract_filters_from_query(user_query: str, tool_context: ToolContext) -> Dict:
    """
    Extracts structured filter conditions from natural language query.

    Uses Gemini LLM to parse user intent and convert to FilterCondition objects.

    CRITICAL: FMV and sales price are NOT filters - they are parameters.
    Only extract conditions that subset the data.

    Args:
        user_query (str): User's natural language query
        tool_context (ToolContext): ADK tool context

    Returns:
        Dict containing:
            status (str): success or error
            has_filters (bool): Whether filters were found
            filter_conditions (List[Dict]): Structured filter conditions
            filter_summary (str): Human-readable summary
            message (str): Status message
    """
    # LLM prompt for filter extraction
    prompt = f"""
You are a filter extraction expert. Extract filter conditions from the user query.

CRITICAL RULES:
1. FMV (Fair Market Value) and sales price are PARAMETERS, NOT FILTERS - IGNORE them completely
2. Only extract conditions that SUBSET the data (reduce the number of records)
3. Return ONLY valid JSON, no markdown formatting

SUPPORTED FILTER FIELDS:
- grant_type: Text equality (RSU, Stock Option, Restricted Stock, PSU)
- shares_released: Numeric comparison (>, <, >=, <=, =)
- department: Text equality (Engineering, Sales, Finance, Marketing, HR, Product, Operations)
- country: Text equality
- employee_status: Text equality (Active, Terminated)

EXAMPLES:

Query: "Simulate RSUs"
Output: {{
  "has_filters": true,
  "conditions": [
    {{"field": "grant_type", "operator": "=", "value": "RSU"}}
  ],
  "filter_summary": "Grant type is RSU"
}}

Query: "Process grants above 10000 shares"
Output: {{
  "has_filters": true,
  "conditions": [
    {{"field": "shares_released", "operator": ">", "value": 10000}}
  ],
  "filter_summary": "Shares released greater than 10000"
}}

Query: "Engineering RSUs with FMV 10"
Output: {{
  "has_filters": true,
  "conditions": [
    {{"field": "department", "operator": "=", "value": "Engineering"}},
    {{"field": "grant_type", "operator": "=", "value": "RSU"}}
  ],
  "filter_summary": "Department is Engineering AND Grant type is RSU"
}}

Query: "Simulate next vesting with FMV 10 and sales 12"
Output: {{
  "has_filters": false,
  "conditions": [],
  "filter_summary": "No filters (FMV and sales are parameters, not filters)"
}}

Query: "Stock options below 5000"
Output: {{
  "has_filters": true,
  "conditions": [
    {{"field": "grant_type", "operator": "=", "value": "Stock Option"}},
    {{"field": "shares_released", "operator": "<", "value": 5000}}
  ],
  "filter_summary": "Grant type is Stock Option AND Shares released less than 5000"
}}

USER QUERY: {user_query}

Return ONLY the JSON output, no other text:
"""

    try:
        response = call_gemini(prompt)

        # Clean response - remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join([line for line in lines if not line.startswith("```")])
        response = response.replace("```json", "").replace("```", "").strip()

        # Parse JSON
        result = json.loads(response)

        # Store in state
        tool_context.state["filter_conditions"] = result

        return {
            "status": "success",
            "has_filters": result.get("has_filters", False),
            "filter_conditions": result.get("conditions", []),
            "filter_summary": result.get("filter_summary", "No filters"),
            "message": "Filters extracted successfully"
        }

    except json.JSONDecodeError as e:
        # Fallback - no filters
        fallback_result = {
            "has_filters": False,
            "conditions": [],
            "filter_summary": "Could not parse filters from query"
        }
        tool_context.state["filter_conditions"] = fallback_result

        return {
            "status": "success",
            "has_filters": False,
            "filter_conditions": [],
            "filter_summary": "Could not parse filters from query",
            "message": f"Filter extraction failed, proceeding without filters. Error: {str(e)}"
        }


def apply_filter(vesting_date: str, tool_context: ToolContext) -> Dict:
    """
    Applies filter conditions to tranche data.

    Evaluates each tranche against filter conditions using AND logic.
    Stores filtered results in state.

    Prerequisite: tranche_data must exist in state for vesting_date

    Args:
        vesting_date (str): Vesting date to filter
        tool_context (ToolContext): ADK tool context

    Returns:
        Dict containing:
            status (str): success or error
            vesting_date (str): Vesting date processed
            original_count (int): Count before filtering
            filtered_count (int): Count after filtering
            filter_summary (str): Description of filters applied
    """
    # Validate prerequisite
    if "tranche_data" not in tool_context.state or vesting_date not in tool_context.state["tranche_data"]:
        return {
            "status": "error",
            "message": f"Error: Vesting details not loaded for {vesting_date}. Call get_vesting_details_with_data first."
        }

    tranche_data = tool_context.state["tranche_data"][vesting_date]
    original_count = len(tranche_data)

    # Get filter conditions from state
    filter_state = tool_context.state.get("filter_conditions", {})
    conditions = filter_state.get("conditions", [])
    filter_summary = filter_state.get("filter_summary", "No filters")

    # If no filters, pass through all data
    if not conditions:
        if "filtered_tranches" not in tool_context.state:
            tool_context.state["filtered_tranches"] = {}
        tool_context.state["filtered_tranches"][vesting_date] = tranche_data

        return {
            "status": "success",
            "vesting_date": vesting_date,
            "original_count": original_count,
            "filtered_count": original_count,
            "filter_summary": "No filters applied - all records included"
        }

    # Define operator functions
    operators = {
        "=": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">": lambda a, b: float(a) > float(b),
        "<": lambda a, b: float(a) < float(b),
        ">=": lambda a, b: float(a) >= float(b),
        "<=": lambda a, b: float(a) <= float(b),
        "contains": lambda a, b: str(b).lower() in str(a).lower()
    }

    # Filter tranches
    filtered_tranches = []

    for tranche in tranche_data:
        # Evaluate all conditions with AND logic
        matches_all = True

        for condition in conditions:
            field = condition["field"]
            operator = condition["operator"]
            value = condition["value"]

            # Get tranche value for field
            if field not in tranche:
                matches_all = False
                break

            tranche_value = tranche[field]

            # Evaluate condition
            try:
                if not operators[operator](tranche_value, value):
                    matches_all = False
                    break
            except (ValueError, TypeError):
                # Type conversion failed, skip this tranche
                matches_all = False
                break

        if matches_all:
            filtered_tranches.append(tranche)

    # Store filtered results
    if "filtered_tranches" not in tool_context.state:
        tool_context.state["filtered_tranches"] = {}
    tool_context.state["filtered_tranches"][vesting_date] = filtered_tranches

    filtered_count = len(filtered_tranches)

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "original_count": original_count,
        "filtered_count": filtered_count,
        "filter_summary": filter_summary
    }


def calculate_tax_with_filters(vesting_date: str, fmv: float, sales: float, tool_context: ToolContext) -> Dict:
    """
    Calculates tax for tranches (filtered or unfiltered).

    Tax calculation logic:
    - gross_value = shares_released × fmv
    - tax_amount = gross_value × 0.35 (35% tax rate)
    - net_proceeds = (shares_released × sales) - tax_amount

    Prerequisite: tranche_data or filtered_tranches must exist for vesting_date

    Args:
        vesting_date (str): Vesting date to process
        fmv (float): Fair Market Value per share
        sales (float): Sale price per share
        tool_context (ToolContext): ADK tool context

    Returns:
        Dict containing:
            status (str): success or error
            vesting_date (str): Vesting date processed
            records_processed (int): Number of records
            total_shares (int): Total shares released
            total_tax (float): Total tax withheld
            summary (str): Human-readable summary
    """
    # Get data from filtered_tranches if exists, else tranche_data
    if "filtered_tranches" in tool_context.state and vesting_date in tool_context.state["filtered_tranches"]:
        data_source = tool_context.state["filtered_tranches"][vesting_date]
        data_type = "filtered"
    elif "tranche_data" in tool_context.state and vesting_date in tool_context.state["tranche_data"]:
        data_source = tool_context.state["tranche_data"][vesting_date]
        data_type = "unfiltered"
    else:
        return {
            "status": "error",
            "message": f"Error: No tranche data found for {vesting_date}. Call get_vesting_details_with_data first."
        }

    tax_results = []
    total_shares = 0
    total_tax = 0.0

    TAX_RATE = 0.35  # 35% tax rate

    for tranche in data_source:
        shares = tranche["shares_released"]

        # Calculate tax
        gross_value = shares * fmv
        tax_amount = gross_value * TAX_RATE
        net_proceeds = (shares * sales) - tax_amount

        # Update totals
        total_shares += shares
        total_tax += tax_amount

        # Create tax result
        tax_result = {
            "employee_id": tranche["employee_id"],
            "employee_name": tranche["employee_name"],
            "grant_type": tranche["grant_type"],
            "vesting_date": vesting_date,
            "shares_released": shares,
            "fmv_at_release": fmv,
            "sale_price_at_release": sales,
            "tax_withheld_amount": round(tax_amount, 2),
            "net_proceeds": round(net_proceeds, 2),
            "gross_value": round(gross_value, 2)
        }

        tax_results.append(tax_result)

        # Also update the original tranche data
        tranche["fmv_at_release"] = fmv
        tranche["sale_price_at_release"] = sales
        tranche["tax_withheld_amount"] = round(tax_amount, 2)

    # Store results in state
    if "tax_results" not in tool_context.state:
        tool_context.state["tax_results"] = {}
    tool_context.state["tax_results"][vesting_date] = tax_results

    summary = f"Processed {len(tax_results)} {data_type} records. Total shares: {total_shares:,}, Total tax: ${total_tax:,.2f}"

    return {
        "status": "success",
        "vesting_date": vesting_date,
        "records_processed": len(tax_results),
        "total_shares": total_shares,
        "total_tax": round(total_tax, 2),
        "summary": summary
    }


def create_batch(vesting_date: str, tool_context: ToolContext, save_to_file: bool = True) -> Dict:
    """
    Creates a release batch with metadata from tax calculation results.

    Generates:
    - Unique batch_id
    - Batch metadata (counts, totals, filter info)
    - Batch records from tax results
    - JSON file (if save_to_file=True)
    - Approval URL

    Prerequisite: tax_results must exist for vesting_date

    Args:
        vesting_date (str): Vesting date to create batch for
        tool_context (ToolContext): ADK tool context
        save_to_file (bool): Whether to save batch to JSON file

    Returns:
        Dict containing:
            status (str): success or error
            batch_id (str): Unique batch identifier
            vesting_date (str): Vesting date
            record_count (int): Number of records
            total_shares_released (int): Total shares
            total_tax_withheld (float): Total tax
            file_path (str): Path to saved file (if saved)
            approval_url (str): URL for batch approval
            message (str): Status message
    """
    # Validate prerequisite
    if "tax_results" not in tool_context.state or vesting_date not in tool_context.state["tax_results"]:
        return {
            "status": "error",
            "message": f"Error: Tax results not found for {vesting_date}. Call calculate_tax_with_filters first."
        }

    tax_results = tool_context.state["tax_results"][vesting_date]

    # Generate batch_id
    batch_id = f"BATCH_{uuid.uuid4().hex[:8].upper()}"

    # Calculate totals
    record_count = len(tax_results)
    total_shares = sum(r["shares_released"] for r in tax_results)
    total_tax = sum(r["tax_withheld_amount"] for r in tax_results)

    # Check if filters were applied
    filter_applied = "filter_conditions" in tool_context.state and tool_context.state["filter_conditions"].get("has_filters", False)
    filter_summary = tool_context.state.get("filter_conditions", {}).get("filter_summary", "No filters applied") if filter_applied else None

    # Create metadata
    metadata = {
        "batch_id": batch_id,
        "vesting_date": vesting_date,
        "creation_timestamp": datetime.utcnow().isoformat() + "Z",
        "record_count": record_count,
        "total_shares_released": total_shares,
        "total_tax_withheld": round(total_tax, 2),
        "filter_applied": filter_applied,
        "filter_summary": filter_summary,
        "status": "pending_approval"
    }

    # Create batch records
    records = []
    for tax_result in tax_results:
        # Calculate net shares delivered (shares - shares sold for tax)
        shares_sold_for_tax = int(tax_result["tax_withheld_amount"] / tax_result["sale_price_at_release"])
        net_shares = tax_result["shares_released"] - shares_sold_for_tax

        record = {
            "employee_id": tax_result["employee_id"],
            "employee_name": tax_result["employee_name"],
            "grant_type": tax_result["grant_type"],
            "shares_released": tax_result["shares_released"],
            "fmv_at_release": tax_result["fmv_at_release"],
            "sale_price_at_release": tax_result["sale_price_at_release"],
            "tax_withheld_amount": tax_result["tax_withheld_amount"],
            "net_shares_delivered": net_shares,
            "net_proceeds": tax_result["net_proceeds"]
        }
        records.append(record)

    # Create batch
    batch = {
        "metadata": metadata,
        "records": records
    }

    # Store in state
    if "batches" not in tool_context.state:
        tool_context.state["batches"] = {}
    tool_context.state["batches"][batch_id] = batch

    # Save to file if requested
    file_path = None
    if save_to_file:
        current_dir = pathlib.Path(__file__).parent.parent
        file_name = f"batch_{batch_id}_{vesting_date}.json"
        file_path = current_dir / file_name

        with open(file_path, 'w') as f:
            json.dump(batch, f, indent=2)

    # Generate approval URL
    approval_url = f"https://dummy.com/batches/{batch_id}/approve"

    return {
        "status": "success",
        "batch_id": batch_id,
        "vesting_date": vesting_date,
        "record_count": record_count,
        "total_shares_released": total_shares,
        "total_tax_withheld": round(total_tax, 2),
        "file_path": str(file_path) if file_path else None,
        "approval_url": approval_url,
        "message": f"Batch {batch_id} created successfully with {record_count} records"
    }
