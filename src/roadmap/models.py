"""Plain data classes shared by every part of the pipeline."""
from dataclasses import dataclass

<<<<<<< HEAD
LEVEL_NAMES = {1: "Foundation", 2: "Core", 3: "Intermediate", 4: "Advanced", 5: "Specialist"}

=======
>>>>>>> origin/main

@dataclass(frozen=True)
class Skill:
    skill_id: str
    name: str
    relevance: int  # 1-10
    demand: int     # 1-10
<<<<<<< HEAD
    category: str = "General"
    level: int = 2                 # 1 foundation ... 5 specialist (used only to order the plan)
    topics: tuple[str, ...] = ()   # syllabus key points
    tip: str = ""                  # one-line study tip

    @property
    def level_name(self) -> str:
        return LEVEL_NAMES.get(self.level, "Core")
=======
>>>>>>> origin/main


@dataclass(frozen=True)
class Resource:
    """An undirected edge between two skills, weighted by hours."""
    resource_id: str
    name: str
    skill_a: str
    skill_b: str
    hours: int
    unavailable: bool
<<<<<<< HEAD
    provider: str = ""
=======
>>>>>>> origin/main


@dataclass(frozen=True)
class Activity:
    activity_id: str
    name: str
    type: str          # course | project | internship
    hours: int
    career_value: int
    skill_unlocked: str
<<<<<<< HEAD
    deliverable: str = ""   # what the student should have at the end
    syllabus: tuple[str, ...] = ()   # the modules/milestones of THIS course, project or internship
=======
>>>>>>> origin/main


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
