"""CLI entry point: python main.py [--data data] [--unavailable R01,R05]"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from roadmap.data_loader import load_dataset  # noqa: E402
from roadmap.pipeline import build_roadmap, format_roadmap, recompute_with_unavailable  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="Career Roadmap Optimization System")
    p.add_argument("--data", default="data", help="folder containing the CSV files")
    p.add_argument("--unavailable", default="", help="comma-separated resource IDs to disable")
    args = p.parse_args()

    data = load_dataset(args.data)
    if args.unavailable:
        a, b = recompute_with_unavailable(data, set(args.unavailable.split(",")))
    else:
        a, b = build_roadmap(data)
    print(format_roadmap(a, b))


if __name__ == "__main__":
    main()
