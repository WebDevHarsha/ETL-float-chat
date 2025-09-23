from config import gemini_client

def generate_sql(user_query: str, retrieved_meta: list):
    prompt = f"""
    The user asked: "{user_query}".
    You have access to a PostgreSQL table called "ocean_data".
    Relevant metadata from the dataset: {retrieved_meta}
    Generate a PostgreSQL SELECT query using this metadata. Respond ONLY with SQL. 
    Do NOT include markdown code fences.
    """
    
    model = gemini_client.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(prompt)
    
    sql_query = response.text.strip()
    return sql_query.replace("```sql", "").replace("```SQL", "").replace("```", "").strip()
