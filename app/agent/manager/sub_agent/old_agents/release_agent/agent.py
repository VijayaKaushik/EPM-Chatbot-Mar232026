from typing import List, Dict
import pandas as pd
import google.generativeai as genai
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from dotenv import load_dotenv

from .callback import before_tool_callback, before_agent_callback, after_agent_callback

load_dotenv()
import os

from .relese_api import generate_release_activity

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "models/gemini-2.5-flash"


def call_gemini(prompt: str) -> str:
    # for model in genai.list_models():
    #     print(model.name, model.supported_generation_methods)
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)  # .md format
    return response.text or "(no response 🥺)"


def get_vesting_dates() -> List[str]:
    """
    Retrieve a list of upcoming vesting dates for equity release events.

    This function returns a predefined list of quarterly vesting dates spanning
    two years. These dates represent when equity grants (RSUs, stock options, etc.)
    will vest and be released to employees.

    Returns:
        List[str]: A list of vesting dates in ISO 8601 format (YYYY-MM-DD).
                   Dates are arranged chronologically and typically occur quarterly.

    Example:
        >>> dates = get_vesting_dates()
        >>> print(dates[0])
        '2025-01-15'

    Note:
        This function is used by the ADK agent to understand available vesting
        dates before processing release activities or tax calculations.
    """
    vesting_dates = [
        "2025-01-15",
        "2025-04-15",
        "2025-07-15",
        "2025-10-15",
        "2026-01-15",
        "2026-04-15",
        "2026-07-15",
        "2026-10-15",
    ]
    return vesting_dates


def get_details_for_vesting_date(dates: List[str], tool_context: ToolContext) -> Dict:
    """
    Generate and retrieve equity release activity details for specified vesting dates.

    This function processes multiple vesting dates by:
    1. Generating release activity data via API calls for each date
    2. Reading the generated JSON files into pandas DataFrames
    3. Storing file references in the tool context state for later use
    4. Returning a summary with participant counts per vesting date

    Args:
        dates (List[str]): List of vesting dates in YYYY-MM-DD format to process.
        tool_context (ToolContext): ADK tool context for maintaining state across
                                    agent interactions. Used to store generated
                                    file names for downstream processing.

    Returns:
        Dict: A dictionary containing:
            - status (str): Operation status, typically "Success"
            - records (List[str]): List of summary strings showing date and
                                   participant count for each vesting date

    Side Effects:
        - Generates JSON files named "release_activity_{date}.json" for each date
        - Updates tool_context.state['vesting_dates_file_name'] with list of
          generated file names

    Example:
        >>> context = ToolContext()
        >>> result = get_details_for_vesting_date(["2025-01-15", "2025-04-15"], context)
        >>> print(result)
        {
            "status": "Success",
            "records": [
                "2025-01-15 : Total participant count 50",
                "2025-04-15 : Total participant count 48"
            ]
        }

    Note:
        This tool is designed for ADK agents to understand the scope of release
        activities across multiple vesting dates before performing detailed analysis.
    """
    # we call the API that created the json file in S3
    for date in dates:
        generate_release_activity(release_date=date)

    list_df = []
    map_df = {}
    for date in dates:
        df = pd.read_json(
            f"C:/Users/vijay/PycharmProjects/PythonProject/app/agent/manager/sub_agent/release_activities_{date}.json"
        )
        list_df.append(df)
        map_df[date] = df

    tool_context.state["vesting_dates_file_name"] = [
        f"C:/Users/vijay/PycharmProjects/PythonProject/app/agent/manager/sub_agent/release_activities_{date}.json"
        for date in dates
    ]
    return {
        "status": "Success",
        "records": [
            f" {date} : Total participant count {len(df)}"
            for date, df in map_df.items()
        ],
    }


def calculate_tax(date: str, fmv: float, sale_price: float) -> dict:
    """
    Calculate total tax withholding for equity releases on a specific vesting date.

    This function generates release activity data with specified financial parameters
    (fair market value and sale price) and calculates the aggregate tax withholding
    amount for all participants on the given vesting date.

    Args:
        date (str): The vesting date in YYYY-MM-DD format for which to calculate taxes.
        fmv (float): Fair Market Value per share at the time of release (in dollars).
                     This is typically the closing stock price on the release date.
        sale_price (float): The price per share at which shares are sold to cover taxes
                           (in dollars). May differ from FMV depending on timing.

    Returns:
        dict: A dictionary containing:
            - status (str): Operation status, typically "Success"
            - result (str): Human-readable message with the total tax amount for
                           the vesting date

    Side Effects:
        - Generates a JSON file named "release_activity_{date}.json" containing
          detailed release records with tax calculations

    Example:
        >>> tax_info = calculate_tax("2025-01-15", fmv=150.50, sale_price=151.00)
        >>> print(tax_info)
        {
            "status": "Success",
            "result": "The total tax for the vesting date 2025-01-15 is 125430.50."
        }

    Note:
        This tool enables ADK agents to perform tax analysis and reporting for
        equity release events. The tax_withheld_amount field in the generated
        data reflects withholding based on employee tax rates and share values.
    """
    generate_release_activity(release_date=date, fmv=fmv, sale_price=sale_price)
    df = pd.read_json(
        f"C:/Users/vijay/PycharmProjects/PythonProject/app/agent/manager/sub_agent/release_activities_{date}.json"
    )
    amount = df["tax_withheld_amount"].sum()
    return {
        "status": "Success",
        "result": f"The total tax for the vesting date {date} is {amount}.",
    }


def data_analysis(user_query: str, tool_context: ToolContext) -> dict:
    """
    Convert natural language queries into executable Python code for pandas DataFrame analysis.

    Args:
        user_query: A natural language question about the employee data, such as 'How many employees are there?' or 'What is the average salary?'

    Returns:
        dict: Analysis results including status, DataFrame info, and summary statistics
    """

    df_files = tool_context.state["vesting_dates_file_name"]
    df = pd.DataFrame()

    for file in df_files:
        df = pd.concat([df, pd.read_json(file)], ignore_index=True)

    prompt = f"""
    You are an expert Python data analyst specializing in pandas DataFrame operations. Your task is to convert natural language queries into executable Python code that operates on a pandas DataFrame named `df`.

## Your Role
- Analyze user queries about data and generate clean, efficient Python code
- The code must work with a DataFrame variable named `df`
- Output ONLY executable Python code, no explanations or markdown
- Store final results in a variable named `result`

## Code Requirements
1. **Direct Execution**: Code must be ready for `exec()` - no function definitions unless necessary
2. **Error Handling**: Include try-except blocks for robust execution
3. **Output Variable**: Always store the final answer in a variable called `result`
4. **Print Statement**: Include `print(result)` at the end
5. **Imports**: Include necessary imports (pandas, numpy, etc.) at the top
6. **Efficiency**: Use vectorized pandas operations when possible

## Common Operations to Handle
- **Filtering**: Filter rows based on conditions
- **Aggregation**: Sum, mean, count, groupby operations
- **Sorting**: Sort by columns
- **Column operations**: Create new columns, modify existing ones
- **Statistical analysis**: Describe, correlations, value counts
- **Data inspection**: Shape, columns, dtypes, head/tail, info
- **Missing data**: Check for nulls, handle missing values
- **Merging/Joining**: Combine DataFrames if multiple are referenced


## Important Guidelines
- Assume `df` exists in the execution context
- Use proper pandas syntax and methods
- Handle potential column name issues (case sensitivity, spaces)
- For ambiguous queries, make reasonable assumptions about column names
- Keep code concise but readable
- Avoid hardcoding values unless specified in the query
- Use appropriate data types for operations

## What NOT to Do
- Don't include markdown code fences (```)
- Don't add explanatory comments unless they're critical
- Don't define functions unless the operation is complex
- Don't modify the original DataFrame unless explicitly asked
- Don't use deprecated pandas methods

Now, convert the following user query into executable Python code:

USER QUERY: {user_query}

SAMPLE DATA:{df.head(5).to_string()}

OUTPUT (Python code only):
    """

    response_python_code = call_gemini(prompt)
    print(response_python_code)
    allowed_globals = {
        "__builtins__": __builtins__,
        "df": df,
    }
    allowed_locals = {}

    exec(response_python_code, allowed_globals, allowed_locals)
    if "result" not in allowed_locals:
        return {"Status": "error"}
    result = allowed_locals["result"]
    return {
        "status": "Success",
        "response": str(result),
    }


root_agent = LlmAgent(
    name="release_agent",
    model="gemini-2.5-flash",
    instruction="Release agent for vesting events",
    tools=[
        calculate_tax,
        get_vesting_dates,
        get_details_for_vesting_date,
        data_analysis,
    ],
    before_tool_callback=before_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)
