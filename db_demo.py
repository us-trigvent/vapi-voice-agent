from __future__ import annotations

from sqlalchemy import text
from database import engine

def run_sql(query: str):
    with engine.begin() as conn: 
        result = conn.execute(text(query))
        return result.fetchall() if result.returns_rows else result.rowcount

query = """SELECT * FROM appointments"""

print(run_sql(query))