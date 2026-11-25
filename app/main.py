import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shapely import wkt
from shapely.geometry import mapping

from app.db import run_select
from app.llm import generate_sql, API_KEY
from app.rag import retrieve

app = FastAPI(title="GeoChat - Natural Language Map Query Assistant")

FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy)\b", re.I)


class Question(BaseModel):
    question: str


def check_sql_is_safe(sql: str):
    """Only allow a single read-only SELECT statement."""
    if not sql.lower().lstrip().startswith(("select", "with")):
        raise HTTPException(400, "Only SELECT queries are allowed")
    if ";" in sql or FORBIDDEN.search(sql):
        raise HTTPException(400, "Unsafe SQL blocked")


@app.get("/health")
def health():
    return {"status": "ok", "mode": "gemini" if API_KEY else "mock (no GEMINI_API_KEY set)"}


@app.post("/ask")
def ask(body: Question):
    context = retrieve(body.question)               # 1. RAG: find relevant schema / examples
    sql = generate_sql(body.question, context)      # 2. LLM: question -> SQL
    check_sql_is_safe(sql)                          # 3. Guard: only safe SELECTs
    try:
        rows = run_select(sql)                      # 4. Run on PostGIS
    except Exception as e:
        raise HTTPException(400, f"SQL failed: {e}")

    features = []                                   # 5. Shapely: WKT -> GeoJSON for the map
    for r in rows:
        if r.get("wkt"):
            geom = mapping(wkt.loads(r["wkt"]))
            props = {k: v for k, v in r.items() if k != "wkt"}
            features.append({"type": "Feature", "geometry": geom, "properties": props})

    return {
        "question": body.question,
        "sql": sql,
        "rows": [{k: v for k, v in r.items() if k != "wkt"} for r in rows],
        "geojson": {"type": "FeatureCollection", "features": features},
    }
