"""Part C - Integration: Part A's reachable skills decide what Part B may schedule.

On top of the two algorithms this module assembles the *roadmap* a student reads:
  * for every scheduled activity, the learning resources to study first (the path
    through Part A's minimum spanning tree from the skills the student already has);
  * foundations-first ordering of the months (see sequencing.py), which never changes
    the total career value Part B found;
"""
from dataclasses import dataclass, field, replace

from .models import Activity, Dataset, Resource, Skill
from .part_a_kruskal import PartAResult, run_part_a
from .part_b_knapsack import PartBResult, run_part_b
from .sequencing import order_foundations_first


@dataclass
class PlanItem:
    activity: Activity
    skill: Skill
    prep: list[Resource] = field(default_factory=list)      # study these first
    reused: list[Resource] = field(default_factory=list)    # on the path, but already studied earlier
    path_skills: list[str] = field(default_factory=list)    # skills passed on the way (excl. the target)


@dataclass
class PlanMonth:
    month: int
    budget: int
    hours_used: int
    items: list[PlanItem] = field(default_factory=list)

    @property
    def prep_hours(self) -> int:
        """Reading/course hours of the study-first resources. Part A's cost, on top of the activity hours."""
        return sum(r.hours for i in self.items for r in i.prep)


@dataclass
class Roadmap:
    data: Dataset
    part_a: PartAResult
    part_b: PartBResult
    months: list[PlanMonth] = field(default_factory=list)
    extra_resources: list[Resource] = field(default_factory=list)   # on the MST, not needed by the plan


# --------------------------------------------------------------------------- paths in the MST
def tree_paths(data: Dataset, a: PartAResult) -> dict[str, tuple[list[str], list[Resource]]]:
    """For every reachable skill: (skills on the way from what the student knows, resources used).

    A breadth-first walk over the chosen resources (a tree), starting from all known skills at once.
    """
    adjacency: dict[str, list[tuple[str, Resource]]] = {}
    for r in a.chosen_resources:
        adjacency.setdefault(r.skill_a, []).append((r.skill_b, r))
        adjacency.setdefault(r.skill_b, []).append((r.skill_a, r))
    roots = sorted(s for s in data.student_skills if s in a.reachable_skills)
    paths: dict[str, tuple[list[str], list[Resource]]] = {s: ([s], []) for s in roots}
    queue = list(roots)
    while queue:
        cur = queue.pop(0)
        nodes, rs = paths[cur]
        for nxt, r in adjacency.get(cur, []):
            if nxt not in paths:
                paths[nxt] = (nodes + [nxt], rs + [r])
                queue.append(nxt)
    return paths


# --------------------------------------------------------------------------- the pipeline
def build_roadmap(data: Dataset, sequence: bool = True) -> Roadmap:
    a = run_part_a(data)                                # Part A: greedy, Kruskal
    b = run_part_b(data, a.reachable_skills)            # Part B: DP, multiple knapsack
    paths = tree_paths(data, a)

    scheduled = [x for acts in b.schedule.values() for x in acts]
    acts_of_skill: dict[str, list[str]] = {}
    for x in scheduled:
        acts_of_skill.setdefault(x.skill_unlocked, []).append(x.activity_id)

    def prerequisites(x: Activity) -> set[str]:
        nodes = paths.get(x.skill_unlocked, ([], []))[0]
        return {aid for s in nodes[:-1] for aid in acts_of_skill.get(s, []) if aid != x.activity_id}

    if sequence and scheduled:
        b.schedule = order_foundations_first(
            b.schedule, b.budgets, lambda x: data.skills[x.skill_unlocked].level, prerequisites)
        b.hours_used = {m: sum(x.hours for x in acts) for m, acts in b.schedule.items()}

    studied: set[str] = set()
    months: list[PlanMonth] = []
    for month, acts in b.schedule.items():
        # inside a month, shorter learning paths (the basics) first
        ordered = sorted(acts, key=lambda x: (len(paths.get(x.skill_unlocked, ([], []))[1]),
                                              data.skills[x.skill_unlocked].level, x.activity_id))
        pm = PlanMonth(month, b.budgets[month], b.hours_used[month])
        for x in ordered:
            nodes, rs = paths.get(x.skill_unlocked, ([x.skill_unlocked], []))
            pm.items.append(PlanItem(
                x, data.skills[x.skill_unlocked],
                prep=[r for r in rs if r.resource_id not in studied],
                reused=[r for r in rs if r.resource_id in studied],
                path_skills=nodes[:-1]))
            studied.update(r.resource_id for r in rs)
        months.append(pm)

    extra = [r for r in a.chosen_resources if r.resource_id not in studied]
    return Roadmap(data, a, b, months, extra)


def with_unavailable(data: Dataset, resource_ids: set[str]) -> Dataset:
    """Copy of the dataset with the given resources marked unavailable."""
    unknown = resource_ids - {r.resource_id for r in data.resources}
    if unknown:
        raise ValueError(f"Unknown resource id(s): {', '.join(sorted(unknown))}")
    resources = [replace(r, unavailable=True) if r.resource_id in resource_ids else r
                 for r in data.resources]
    return replace(data, resources=resources)


def recompute_with_unavailable(data: Dataset, resource_ids: set[str]) -> Roadmap:
    """'Updates' requirement: mark resources unavailable and recompute the whole plan."""
    return build_roadmap(with_unavailable(data, resource_ids))


def format_roadmap(rm: Roadmap) -> str:
    from .report import format_roadmap as _format      # imported late: report imports this module
    return _format(rm)
