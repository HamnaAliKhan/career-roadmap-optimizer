"""Career Roadmap Optimization System - command-line interface.

Examples
  python main.py                          roadmap for data/student.csv
  python main.py --skills S01,S05         roadmap for a student who knows these skills
  python main.py --unavailable R11,R12    recompute with resources made unavailable
  python main.py --trace                  also print Kruskal's step-by-step decisions
  python main.py --tests                  run the proposal's test scenarios
"""
import argparse
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from roadmap.data_loader import load_dataset, validate  # noqa: E402
from roadmap.pipeline import build_roadmap, format_roadmap, with_unavailable  # noqa: E402
from roadmap.scenarios import run_all  # noqa: E402


def _ids(text: str) -> set[str]:
    return {x.strip() for x in text.split(",") if x.strip()}


def main() -> int:
    p = argparse.ArgumentParser(description="Career Roadmap Optimization System")
    p.add_argument("--data", default="data", help="folder containing the CSV files")
    p.add_argument("--student", help="student profile CSV (default: <data>/student.csv)")
    p.add_argument("--skills", default="", help="comma-separated current skill IDs (overrides the profile)")
    p.add_argument("--unavailable", default="", help="comma-separated resource IDs to mark unavailable")
    p.add_argument("--trace", action="store_true", help="print Kruskal's step-by-step decisions")
    p.add_argument("--tests", action="store_true", help="run the test scenarios and print the results")
    args = p.parse_args()

    try:
        data = load_dataset(args.data, args.student)
        if args.skills:
            data = replace(data, student_skills=_ids(args.skills))
            validate(data)
        if args.unavailable:
            data = with_unavailable(data, _ids(args.unavailable))
    except (ValueError, FileNotFoundError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.tests:
        ok, text = run_all(data)
        print(text)
        return 0 if ok else 1

    rm = build_roadmap(data)
    print(format_roadmap(rm))
    if args.trace:
        print("\nKruskal trace (edges in sorted order):")
        print("\n".join("  " + t for t in rm.part_a.trace))
    return 0


if __name__ == "__main__":
    sys.exit(main())
