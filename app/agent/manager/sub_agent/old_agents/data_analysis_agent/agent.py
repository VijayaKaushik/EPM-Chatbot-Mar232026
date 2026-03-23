from google.adk.agents.llm_agent import LlmAgent
from dotenv import load_dotenv
import pandas as pd
import os
import google.generativeai as genai


load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "models/gemini-2.5-flash"


def call_gemini(prompt: str) -> str:
    # for model in genai.list_models():
    #     print(model.name, model.supported_generation_methods)
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)  # .md format
    return response.text or "(no response 🥺)"


df = pd.read_csv("C:/Users/vijay/PycharmProjects/PythonProject/sample_employees.csv")


def data_analysis(user_query: str) -> dict:
    """
    Convert natural language queries into executable Python code for pandas DataFrame analysis.

    Args:
        user_query: A natural language question about the employee data, such as 'How many employees are there?' or 'What is the average salary?'

    Returns:
        dict: Analysis results including status, DataFrame info, and summary statistics
    """

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


data_analysis_agent = LlmAgent(
    name="data_analysis_agent",
    model="gemini-2.5-flash",
    # model="gemini-2.5-flash",
    instruction="Handles questions on employee dataframes",
    tools=[data_analysis],
)
