"""Career Roadmap Optimization System - command-line interface.

Examples
  python main.py                              roadmap for data/student.csv
  python main.py --skills python,git          roadmap for a student who knows these skills
  python main.py --unavailable R11,R12        recompute with resources made unavailable
  python main.py --trace                      also print Kruskal's step-by-step decisions
  python main.py --tests                      run the proposal's test scenarios
  python main.py --list-skills                show valid skill names
"""
import argparse
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from roadmap.data_loader import load_dataset, resolve_skills, validate  # noqa: E402
from roadmap.pipeline import build_roadmap, with_unavailable  # noqa: E402
from roadmap.report import format_roadmap  # noqa: E402
from roadmap.scenarios import run_all  # noqa: E402


def _tokens(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Career Roadmap Optimization System",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--data", default=str(Path(__file__).parent / "data"), help="folder containing the CSV files")
    p.add_argument("--student", help="student profile CSV (default: <data>/student.csv)")
    p.add_argument("--skills", default="", help="current skills, by id or name: S01,S02 or python,git (overrides the profile)")
    p.add_argument("--unavailable", default="", help="comma-separated resource IDs to mark unavailable")
    p.add_argument("--trace", action="store_true", help="print Kruskal's step-by-step decisions")
    p.add_argument("--tests", action="store_true", help="run the test scenarios and print the results")
    p.add_argument("--list-skills", action="store_true", help="list all skills and exit")
    p.add_argument("--list-resources", action="store_true", help="list all learning resources and exit")
    args = p.parse_args(argv)

    try:
        data = load_dataset(args.data, args.student)
        if args.skills:
            data = replace(data, student_skills=resolve_skills(data, _tokens(args.skills)))
            validate(data)
        if args.unavailable:
            data = with_unavailable(data, {x.upper() for x in _tokens(args.unavailable)})
    except (ValueError, FileNotFoundError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.list_skills:
        for s in data.skills.values():
            print(f"{s.skill_id}  {s.name:<20} {s.category:<16} {s.level_name:<12} relevance {s.relevance}  demand {s.demand}")
        return 0
    if args.list_resources:
        for r in data.resources:
            flag = "  [UNAVAILABLE]" if r.unavailable else ""
            print(f"{r.resource_id}  {r.name:<40} {data.skills[r.skill_a].name} <-> {data.skills[r.skill_b].name}  {r.hours} h{flag}")
        return 0
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
