from sqlalchemy import text
from config import engine

def execute_sql(sql_query: str):
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        return [dict(row) for row in result.fetchall()]
