"""A very small RAG: split the data dictionary into chunks and retrieve the ones
most related to the question using word overlap."""
import re
from pathlib import Path

DICT_PATH = Path(__file__).resolve().parent.parent / "data" / "data_dictionary.md"


def load_chunks():
    text = DICT_PATH.read_text(encoding="utf-8")
    return [c.strip() for c in text.split("\n\n") if c.strip()]


def words(text: str):
    return set(re.findall(r"[a-z]+", text.lower()))


def retrieve(question: str, top_k: int = 4):
    chunks = load_chunks()
    q = words(question)
    always = [c for c in chunks if c.startswith("## Schema") or c.startswith("## Output rules")]
    others = [c for c in chunks if c not in always]
    others.sort(key=lambda c: len(q & words(c)), reverse=True)   # most overlap first
    return always + others[:top_k]
