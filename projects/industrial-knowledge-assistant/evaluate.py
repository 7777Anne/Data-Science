"""Small qualitative retrieval regression set for the fictional SOP corpus.

This is not a production benchmark; expand with manually annotated queries and failure cases.
"""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app import Assistant

CASES = [
    ("What do we do when conveyor bearings exceed 75 C?", "conveyor-maintenance.md"),
    ("How do operators prepare for a line changeover?", "line-changeover.md"),
    ("What happens when visual inspection finds a defect?", "quality-inspection.md"),
    ("What is the current Bitcoin price?", None),
]


def main():
    engine = Assistant()
    passed = 0
    rows = []
    for question, expected in CASES:
        response = engine.ask(question)
        observed = [c["source"] for c in response["citations"]]
        correct = expected in observed if expected else not response["grounded"]
        passed += int(correct)
        rows.append({"question": question, "expected": expected, "retrieved": observed, "pass": correct})
    print(json.dumps({"pass_count": passed, "case_count": len(CASES), "cases": rows}, indent=2))


if __name__ == "__main__":
    main()
