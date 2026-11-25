import os
import re
import requests

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")   # change if Google renames the model
CENTER = "ST_SetSRID(ST_MakePoint(91.2868, 23.8315), 4326)::geography"


def build_prompt(question: str, context_chunks) -> str:
    context = "\n\n".join(context_chunks)
    return (
        "You are an assistant that writes PostgreSQL/PostGIS SQL.\n"
        "Use ONLY the information in the context below. Return ONE SELECT statement and nothing else "
        "(no explanation, no markdown).\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION: {question}\nSQL:"
    )


def clean_sql(text: str) -> str:
    text = re.sub(r"```(?:sql)?", "", text, flags=re.IGNORECASE).strip()
    return text.rstrip(";").strip()


def ask_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    resp = requests.post(
        url,
        params={"key": API_KEY},
        json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0}},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def mock_sql(question: str) -> str:
    """Rule-based fallback so the demo works without an API key."""
    q = question.lower()
    category = next((c for c in ["hospital", "school", "park", "restaurant"] if c in q), None)
    where = f"category = '{category}'" if category else "TRUE"
    km = re.search(r"(\d+(?:\.\d+)?)\s*km", q)
    if km:
        where += f" AND ST_DWithin(geom::geography, {CENTER}, {float(km.group(1)) * 1000})"
    if "how many" in q or "count" in q:
        return f"SELECT COUNT(*) AS total FROM places WHERE {where}"
    if "nearest" in q or "closest" in q:
        return (f"SELECT name, category, ST_AsText(geom) AS wkt FROM places WHERE {where} "
                f"ORDER BY geom::geography <-> {CENTER} LIMIT 1")
    return f"SELECT name, category, ST_AsText(geom) AS wkt FROM places WHERE {where}"


def generate_sql(question: str, context_chunks) -> str:
    if not API_KEY:
        return mock_sql(question)
    return clean_sql(ask_gemini(build_prompt(question, context_chunks)))
