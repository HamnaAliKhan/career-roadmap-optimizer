"""Part C - Integration: Part A's reachable skills decide what Part B may schedule."""
from dataclasses import replace

from .models import Dataset
from .part_a_kruskal import PartAResult, run_part_a
from .part_b_knapsack import PartBResult, run_part_b


def build_roadmap(data: Dataset) -> tuple[PartAResult, PartBResult]:
    a = run_part_a(data)
    b = run_part_b(data, a.reachable_skills)
    return a, b


def recompute_with_unavailable(data: Dataset, resource_ids: set[str]):
    """'Updates' requirement: mark resources unavailable and re-run the whole plan."""
    resources = [replace(r, unavailable=True) if r.resource_id in resource_ids else r
                 for r in data.resources]
    return build_roadmap(replace(data, resources=resources))


def format_roadmap(a: PartAResult, b: PartBResult) -> str:
    # TODO: month-by-month table: activities, skills unlocked, hours used / budget,
    # total career value, unreachable skills, excluded activities.
    raise NotImplementedError
