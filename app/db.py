import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5434/geochat")


def run_select(sql: str):
    """Run a SELECT in a read-only transaction and return rows as dicts."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        conn.set_session(readonly=True)   # extra safety: DB itself blocks writes
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SET statement_timeout = 5000")
            cur.execute(sql)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
