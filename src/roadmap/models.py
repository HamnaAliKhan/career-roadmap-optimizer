"""Plain data classes shared by every part of the pipeline."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    skill_id: str
    name: str
    relevance: int  # 1-10
    demand: int     # 1-10


@dataclass(frozen=True)
class Resource:
    """An undirected edge between two skills, weighted by hours."""
    resource_id: str
    name: str
    skill_a: str
    skill_b: str
    hours: int
    unavailable: bool


@dataclass(frozen=True)
class Activity:
    activity_id: str
    name: str
    type: str          # course | project | internship
    hours: int
    career_value: int
    skill_unlocked: str


@dataclass(frozen=True)
class Month:
    month: int
    hour_budget: int


@dataclass
class Dataset:
    skills: dict[str, Skill]
    resources: list[Resource]
    activities: list[Activity]
    months: list[Month]
    student_skills: set[str]
