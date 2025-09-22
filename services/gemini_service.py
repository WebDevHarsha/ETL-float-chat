from config import gemini_client

def generate_sql(user_query: str, retrieved_meta: list):
    prompt = f"""
    The user asked: "{user_query}".
    You have access to a PostgreSQL table called "ocean_data".
    Relevant metadata from the dataset: {retrieved_meta}
    Generate a PostgreSQL SELECT query using this metadata. Respond ONLY with SQL. 
    Do NOT include markdown code fences.
    """
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    sql_query = response.text.strip()
    return sql_query.replace("```sql", "").replace("```SQL", "").replace("```", "").strip()
