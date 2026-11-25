# GeoChat - Natural Language Map Query Assistant (LLM + RAG)

Ask a question in English -> the app writes a PostGIS SQL query -> runs it -> returns rows + GeoJSON for a map.

## Setup
    docker compose up -d                 # PostGIS on port 5434
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python load_data.py                  # loads data/places.geojson with GeoPandas
    export GEMINI_API_KEY=your_key       # optional; without it a simple rule-based mock is used
    uvicorn app.main:app --reload

Open http://localhost:8000/docs and try POST /ask:
    {"question": "Show restaurants within 1 km of the city centre"}

Evaluate accuracy: `python evaluate.py`

## Flow
    question -> rag.py (find relevant schema/examples in data_dictionary.md)
             -> llm.py (prompt + Gemini -> SQL)
             -> main.py check_sql_is_safe (only one SELECT)
             -> db.py (run on PostGIS, read-only)
             -> Shapely (WKT -> GeoJSON)
