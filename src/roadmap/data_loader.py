"""Reads the CSV files in data/ into a Dataset and validates them."""
import csv
import difflib
import re
from pathlib import Path

from .models import Activity, Dataset, Month, Resource, Skill

TOPIC_SEPARATOR = ";"


def _rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def _flag(value: str) -> bool:
    return value.lower() in ("1", "true", "yes", "y")


def _int(row: dict[str, str], column: str, file: str, default: int | None = None) -> int:
    raw = row.get(column, "")
    if raw == "" and default is not None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"{file}: column '{column}' must be a whole number, got '{raw}' in row {row}") from None


def _need(row: dict[str, str], columns: tuple[str, ...], file: str) -> None:
    missing = [c for c in columns if c not in row]
    if missing:
        raise ValueError(f"{file}: missing column(s) {', '.join(missing)}")


def load_dataset(data_dir: str | Path = "data", student_file: str | Path | None = None) -> Dataset:
    d = Path(data_dir)

    skills: dict[str, Skill] = {}
    for r in _rows(d / "skills.csv"):
        _need(r, ("skill_id", "name", "relevance", "demand"), "skills.csv")
        skills[r["skill_id"]] = Skill(
            r["skill_id"], r["name"], _int(r, "relevance", "skills.csv"), _int(r, "demand", "skills.csv"),
            r.get("category") or "General", _int(r, "level", "skills.csv", default=2),
            tuple(t.strip() for t in r.get("topics", "").split(TOPIC_SEPARATOR) if t.strip()),
            r.get("tip", ""))

    resources = []
    for r in _rows(d / "resources.csv"):
        _need(r, ("resource_id", "name", "skill_a", "skill_b", "hours"), "resources.csv")
        resources.append(Resource(r["resource_id"], r["name"], r["skill_a"], r["skill_b"],
                                  _int(r, "hours", "resources.csv"), _flag(r.get("unavailable", "0")),
                                  r.get("provider", "")))
    activities = []
    for r in _rows(d / "activities.csv"):
        _need(r, ("activity_id", "name", "type", "hours", "career_value", "skill_unlocked"), "activities.csv")
        activities.append(Activity(r["activity_id"], r["name"], r["type"], _int(r, "hours", "activities.csv"),
                                   _int(r, "career_value", "activities.csv"), r["skill_unlocked"],
                                   r.get("deliverable", ""),
                                   tuple(t.strip() for t in r.get("syllabus", "").split(TOPIC_SEPARATOR) if t.strip())))
    months = []
    for r in _rows(d / "months.csv"):
        _need(r, ("month", "hour_budget"), "months.csv")
        months.append(Month(_int(r, "month", "months.csv"), _int(r, "hour_budget", "months.csv")))

    student_path = Path(student_file) if student_file else d / "student.csv"
    student_skills = {r["skill_id"] for r in _rows(student_path) if r.get("skill_id")}

    data = Dataset(skills, resources, activities, months, student_skills)
    validate(data)
    return data


def list_presets(data_dir: str | Path = "data") -> dict[str, Path]:
    """Student profile CSVs in data/students/, keyed by a readable label."""
    folder = Path(data_dir) / "students"
    if not folder.is_dir():
        return {}
    return {p.stem.replace("_", " ").title(): p for p in sorted(folder.glob("*.csv"))}


def read_student_file(path: str | Path) -> set[str]:
    return {r["skill_id"] for r in _rows(Path(path)) if r.get("skill_id")}


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def resolve_skills(data: Dataset, tokens: list[str]) -> set[str]:
    """Turn user input ('S01', 'python', 'git', 'aws') into skill ids.

    Accepts an id, an exact name, or a name fragment that matches exactly one skill.
    Raises ValueError with suggestions otherwise.
    """
    found: set[str] = set()
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if token.upper() in data.skills:
            found.add(token.upper())
            continue
        key = _norm(token)
        exact = [s.skill_id for s in data.skills.values() if _norm(s.name) == key]
        if len(exact) == 1:
            found.add(exact[0])
            continue
        partial = [s.skill_id for s in data.skills.values() if key and key in _norm(s.name)]
        if len(partial) == 1:
            found.add(partial[0])
            continue
        if len(partial) > 1:
            names = ", ".join(data.skills[s].name for s in partial)
            raise ValueError(f"'{token}' is ambiguous. It matches: {names}")
        close = difflib.get_close_matches(token.lower(), [s.name.lower() for s in data.skills.values()], n=3, cutoff=0.5)
        hint = f" Did you mean: {', '.join(close)}?" if close else " Use --list-skills to see valid names."
        raise ValueError(f"Unknown skill '{token}'.{hint}")
    return found


def validate(data: Dataset) -> None:
    """Raise ValueError if any row refers to an unknown skill or has bad numbers."""
    errors = []

    def duplicates(label: str, ids: list):
        for x in sorted({i for i in ids if ids.count(i) > 1}):
            errors.append(f"duplicate {label} {x}")

    duplicates("resource id", [r.resource_id for r in data.resources])
    duplicates("activity id", [a.activity_id for a in data.activities])
    duplicates("month", [m.month for m in data.months])
    for s in data.skills.values():
        if not (1 <= s.relevance <= 10 and 1 <= s.demand <= 10):
            errors.append(f"skill {s.skill_id}: relevance/demand must be 1-10")
    for r in data.resources:
        for sid in (r.skill_a, r.skill_b):
            if sid not in data.skills:
                errors.append(f"resource {r.resource_id}: unknown skill {sid}")
        if r.skill_a == r.skill_b:
            errors.append(f"resource {r.resource_id}: connects a skill to itself")
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
