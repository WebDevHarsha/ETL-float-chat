from sqlalchemy import text
from config import engine

def execute_sql(sql_query: str):
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        rows = result.fetchall()
        
        # Get column names
        columns = result.keys()
        
        # Convert rows to dictionaries using column names
        return [dict(zip(columns, row)) for row in rows]
