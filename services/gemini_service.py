from config import gemini_client

def generate_sql(user_query: str, retrieved_meta: list):
    prompt = f"""
    The user asked: "{user_query}".
    You have access to a PostgreSQL table called "ocean_data".
    Relevant metadata from the dataset: {retrieved_meta}
    Generate a PostgreSQL SELECT query using this metadata. Respond ONLY with SQL. 
    Do NOT include markdown code fences.
    """
    
    model = gemini_client.GenerativeModel('gemini-2.5-flash-exp')
    response = model.generate_content(prompt)
    
    sql_query = response.text.strip()
    return sql_query.replace("```sql", "").replace("```SQL", "").replace("```", "").strip()

def summarize_results(user_query: str, sql_query: str, rows: list) -> str:
    prompt = f"""
    The user asked: "{user_query}"
    We generated and executed the following SQL query:
    {sql_query}

    Here are the first few rows of the SQL results:
    {rows[:10]}

    Please provide a clear, concise summary of these results for the user.
    - Highlight key insights or patterns.
    - Use plain English.
    - If there is a numeric trend, describe it.
    - If results are empty, say so.
    """

    model = gemini_client.GenerativeModel('gemini-2.5-flash-exp')
    response = model.generate_content(prompt)
    summary = response.text.strip()

    return summary

