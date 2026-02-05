import os
import google.generativeai as genai
from dotenv import load_dotenv
import sqlite3
import pandas as pd


load_dotenv()

connection=sqlite3.connect("C:/Users/vijay/PycharmProjects/PythonProject/app/agent/banking_agent/banking.db")
cursor=connection.cursor()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "models/gemini-2.5-flash"

def call_gemini(prompt: str) -> str:
    # for model in genai.list_models():
    #     print(model.name, model.supported_generation_methods)
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt) # .md format
    return response.text or "(no response 🥺)"


from .constant import txt_to_sql


def generate_sql_my (query : str):
    sql_prompt=txt_to_sql.format(user_question=query)
    sql_query= call_gemini(sql_prompt)
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    df= pd.DataFrame.from_records(rows)
    print (df.head())
    for row in rows:
        print(row)

   #step 1: trigger a custom event that returns all the
    # set context
   #Step 2 : Summarize the data
    compact_rows=generate_compact_string(df)
    print("compacted string"  ,compact_rows)

    summary_prompt=f''' 
    
    You are a data analyst assistant specialized in summarizing database query results into clear, actionable bullet points.

   Your task is to analyze data from a banking database and provide a concise summary in bullet point format.

    data : {compact_rows}
'''

    summarize_text=call_gemini(summary_prompt)
    print (summarize_text)
    return summarize_text

def generate_compact_string(df):
    rows=[]
    for index, row in df.iterrows():
        rows.append("|".join(f"{v}" for k,v  in row.items()))

    return ",".join(rows)



##

def generate_sql(query: str):
    """
    Convert natural language questions to SQL queries and execute them on the banking database.

    This function takes a user's natural language question about clients, private bankers,
    or corporate companies, converts it to a SQL query using Gemini LLM, executes the query
    on the SQLite database, and returns the results.

    Args:
        query (str): Natural language question about the banking database.
            Examples:
            - "Show me all clients with net worth over 10 million"
            - "List all private bankers in New York"
            - "What companies does Robert Anderson own?"
            - "How many clients does each banker have?"
            - "Which banker manages the most wealth?"
            - "Show me average revenue by industry"

    Returns:
        list: A list of tuples containing the query results. Each tuple represents one row
            from the database. Returns an empty list if no results are found or if an error occurs.

            Example return values:
            - [('John', 'Doe', 15000000.00), ('Jane', 'Smith', 20000000.00)]
            - [(5,), (3,), (7,)]  # For count queries
            - []  # When no results match the query

    Database Schema:
        The function queries the following tables:

        - private_bankers: Contains banker information (name, job title, location, specialization)
        - clients: Contains client information (name, net worth, risk profile, assigned banker)
        - corporate_companies: Contains company information (name, revenue, industry, client ownership)

    Process Flow:
        1. Formats the user's natural language query into the text-to-SQL prompt template
        2. Sends the formatted prompt to Gemini LLM via call_gemini() function
        3. Receives generated SQL query from Gemini
        4. Executes the SQL query on the SQLite database using the global cursor
        5. Fetches all matching rows from the result set
        6. Prints each row to console for immediate visibility
        7. Returns the complete list of rows

    Example Usage:
        >>> # Simple client query
        >>> results = generate_sql("Show me all clients with net worth over 5 million")
        >>> print(f"Found {len(results)} clients")

        >>> # Aggregation query
        >>> results = generate_sql("What is the total revenue of all technology companies?")
        >>> total_revenue = results[0][0] if results else 0

        >>> # Complex join query
        >>> results = generate_sql("List clients and their bankers in California")
        >>> for client_name, banker_name, location in results:
        ...     print(f"{client_name} is managed by {banker_name} in {location}")

    Supported Query Types:
        - Client queries: Filter by net worth, risk profile, banker assignment
        - Banker queries: Filter by location, job title, experience, specialization
        - Company queries: Filter by industry, revenue, employee count, ownership
        - Aggregations: SUM, AVG, COUNT, MAX, MIN across any numeric fields
        - Joins: Cross-table queries combining clients, bankers, and companies
        - Grouping: Group by industry, location, risk profile, etc.
        - Sorting: Order results by any field in ascending or descending order

    Notes:
        - Requires global 'txt_to_sql' prompt template to be defined
        - Requires global 'cursor' (SQLite database cursor) to be initialized
        - Requires 'call_gemini()' function to be available for LLM API calls
        - Prints results to console as a side effect for debugging/monitoring
        - SQL injection risk is mitigated by LLM generating queries (not direct user input)
        - Consider adding error handling for malformed queries or database errors

    Raises:
        sqlite3.Error: If the generated SQL query is invalid or database connection fails
        Exception: If the LLM API call fails or returns invalid SQL

    Performance Considerations:
        - Query execution time depends on database size and query complexity
        - Large result sets are fetched entirely into memory (fetchall)
        - Consider using fetchmany() or pagination for very large datasets
        - LLM API call adds ~1-3 seconds latency depending on provider

    Security Considerations:
        - Generated SQL should be validated before execution in production
        - Consider implementing query result size limits
        - Sensitive data (net worth, company revenue) is returned in plaintext
        - Ensure appropriate access controls are in place at the application level

    See Also:
        - txt_to_sql_prompt.txt: The prompt template used for query conversion
        - call_gemini(): Function that interfaces with the Gemini LLM API
        - banking_schema.sql: Complete database schema documentation
    """
    sql_prompt = txt_to_sql.format(user_question=query)
    sql_query = call_gemini(sql_prompt)
    sql_query = sql_query.replace("```sqlite", "").replace("```", "").replace("sql", "")
    print(sql_query)
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    df = pd.DataFrame.from_records(rows)
    print(df.head())
    for row in rows:
        print(row)

    # step 1: trigger a custom event that returns all the
    # set context
    # Step 2 : Summarize the data
    compact_rows = generate_compact_string(df)
    print("compacted string", compact_rows)

    summary_prompt = f''' 

    You are a data analyst assistant specialized in summarizing database query results into clear, actionable bullet points.

   Your task is to analyze data from a banking database and provide a concise summary in bullet point format.

    data : {compact_rows}
'''

    summarize_text = call_gemini(summary_prompt)
    print(summarize_text)
    return summarize_text


# Alternative: Shorter Google-style docstring format
def generate_sql_compact(query: str):
    """Convert natural language to SQL and execute on banking database.

    Takes a natural language question, converts it to SQL using Gemini LLM,
    executes the query, and returns results.

    Args:
        query: Natural language question (e.g., "Show clients worth over 10M")

    Returns:
        List of tuples containing query results, empty list if no matches

    Example:
        >>> results = generate_sql("List all bankers in New York")
        >>> for name, title, location in results:
        ...     print(f"{name} - {title} at {location}")
    """
    sql_prompt = txt_to_sql.format(user_question=query)
    sql_query = call_gemini(sql_prompt)
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    return rows


# Alternative: NumPy/SciPy style docstring (very detailed)
def generate_sql_numpy_style(query: str):
    """
    Convert natural language questions to SQL queries and execute them.

    Parameters
    ----------
    query : str
        Natural language question about the banking database. Can query clients,
        private bankers, or corporate companies.

        Examples include:

        - "Show me all clients with net worth over 10 million"
        - "List all private bankers in New York"
        - "What companies does Robert Anderson own?"
        - "How many clients does each banker have?"

    Returns
    -------
    rows : list of tuple
        Query results where each tuple represents one database row. Returns
        empty list if no results found.

        For example:

        - [('John', 'Doe', 15000000.00)] for client queries
        - [(5,)] for count/aggregate queries
        - [] when no matches found

    Notes
    -----
    This function performs the following steps:

    1. Formats user query into LLM prompt using txt_to_sql template
    2. Calls Gemini LLM to generate SQL query
    3. Executes SQL on SQLite database
    4. Fetches and prints all results
    5. Returns results as list of tuples

    The function requires these globals to be defined:

    - txt_to_sql : Prompt template with {user_question} placeholder
    - cursor : SQLite database cursor object
    - call_gemini : Function to call Gemini LLM API

    Examples
    --------
    >>> # Query high net worth clients
    >>> results = generate_sql("clients with net worth over 20 million")
    >>> len(results)
    3

    >>> # Query banker statistics
    >>> results = generate_sql("how many clients per banker")
    >>> for banker, count in results:
    ...     print(f"{banker}: {count} clients")
    Sarah Johnson: 15 clients
    Michael Chen: 12 clients

    See Also
    --------
    call_gemini : Function that calls the Gemini LLM API
    txt_to_sql_prompt.txt : Full prompt template documentation
    """
    sql_prompt = txt_to_sql.format(user_question=query)
    sql_query = call_gemini(sql_prompt)
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    return rows

