"""Reads the five CSV files in data/ into a Dataset and validates them."""
import csv
from pathlib import Path

from .models import Activity, Dataset, Month, Resource, Skill


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return [{k.strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def _flag(value: str) -> bool:
    return value.lower() in ("1", "true", "yes", "y")


def load_dataset(data_dir: str | Path = "data", student_file: str | Path | None = None) -> Dataset:
    d = Path(data_dir)

    skills = {
        r["skill_id"]: Skill(r["skill_id"], r["name"], int(r["relevance"]), int(r["demand"]))
        for r in _rows(d / "skills.csv")
    }
    resources = [
        Resource(r["resource_id"], r["name"], r["skill_a"], r["skill_b"],
                 int(r["hours"]), _flag(r["unavailable"]))
        for r in _rows(d / "resources.csv")
    ]
    activities = [
        Activity(r["activity_id"], r["name"], r["type"], int(r["hours"]),
                 int(r["career_value"]), r["skill_unlocked"])
        for r in _rows(d / "activities.csv")
    ]
    months = [Month(int(r["month"]), int(r["hour_budget"])) for r in _rows(d / "months.csv")]
    student_path = Path(student_file) if student_file else d / "student.csv"
    student_skills = {r["skill_id"] for r in _rows(student_path)}

    data = Dataset(skills, resources, activities, months, student_skills)
    validate(data)
    return data


def validate(data: Dataset) -> None:
    """Raise ValueError if any row refers to an unknown skill or has bad numbers."""
    errors = []
    for s in data.skills.values():
        if not (1 <= s.relevance <= 10 and 1 <= s.demand <= 10):
            errors.append(f"skill {s.skill_id}: relevance/demand must be 1-10")
    for r in data.resources:
        for sid in (r.skill_a, r.skill_b):
            if sid not in data.skills:
                errors.append(f"resource {r.resource_id}: unknown skill {sid}")
        if r.hours <= 0:
            errors.append(f"resource {r.resource_id}: hours must be positive")
    for a in data.activities:
        if a.skill_unlocked not in data.skills:
            errors.append(f"activity {a.activity_id}: unknown skill {a.skill_unlocked}")
        if a.hours <= 0 or a.career_value < 0:
            errors.append(f"activity {a.activity_id}: bad hours or career value")
    for m in data.months:
        if m.hour_budget < 0:
            errors.append(f"month {m.month}: budget cannot be negative")
    for sid in data.student_skills:
        if sid not in data.skills:
            errors.append(f"student profile: unknown skill {sid}")
    if errors:
        raise ValueError("Invalid dataset:\n  " + "\n  ".join(errors))
