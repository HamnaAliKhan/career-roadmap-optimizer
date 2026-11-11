"""Reads the five CSV files in data/ into a Dataset."""
import csv
from pathlib import Path

from .models import Activity, Dataset, Month, Resource, Skill


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_dataset(data_dir: str | Path = "data") -> Dataset:
    d = Path(data_dir)

    skills = {
        r["skill_id"]: Skill(r["skill_id"], r["name"], int(r["relevance"]), int(r["demand"]))
        for r in _rows(d / "skills.csv")
    }
    resources = [
        Resource(r["resource_id"], r["name"], r["skill_a"], r["skill_b"],
                 int(r["hours"]), r["unavailable"].strip() in ("1", "true", "True"))
        for r in _rows(d / "resources.csv")
    ]
    activities = [
        Activity(r["activity_id"], r["name"], r["type"], int(r["hours"]),
                 int(r["career_value"]), r["skill_unlocked"])
        for r in _rows(d / "activities.csv")
    ]
    months = [Month(int(r["month"]), int(r["hour_budget"])) for r in _rows(d / "months.csv")]
    student_skills = {r["skill_id"] for r in _rows(d / "student.csv")}

    return Dataset(skills, resources, activities, months, student_skills)
