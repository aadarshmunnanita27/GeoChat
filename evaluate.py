"""Measures query accuracy: runs the generated SQL and the expected SQL and compares the results."""
import json
from app.db import run_select
from app.llm import generate_sql
from app.rag import retrieve


def normalise(rows):
    """Compare by 'name' values if present, otherwise by the first column values."""
    if rows and "name" in rows[0]:
        return sorted(r["name"] for r in rows)
    return sorted(str(list(r.values())[0]) for r in rows)


tests = json.load(open("eval/test_set.json"))
correct = 0
for t in tests:
    try:
        got = normalise(run_select(generate_sql(t["question"], retrieve(t["question"]))))
        want = normalise(run_select(t["expected_sql"]))
        ok = got == want
    except Exception as e:
        ok = False
        print("  error:", e)
    correct += ok
    print(("PASS" if ok else "FAIL"), "-", t["question"])

print(f"\nAccuracy: {correct}/{len(tests)} = {100 * correct / len(tests):.0f}%")
