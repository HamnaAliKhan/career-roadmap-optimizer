<<<<<<< HEAD
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
=======
"""Part C - Integration: Part A's reachable skills decide what Part B may schedule."""
from dataclasses import dataclass, replace

from .models import Dataset
from .part_a_kruskal import PartAResult, run_part_a
from .part_b_knapsack import PartBResult, run_part_b
>>>>>>> origin/main


@dataclass
class Roadmap:
    data: Dataset
    part_a: PartAResult
    part_b: PartBResult
<<<<<<< HEAD
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
=======


def build_roadmap(data: Dataset) -> Roadmap:
    a = run_part_a(data)
    b = run_part_b(data, a.reachable_skills)
    return Roadmap(data, a, b)
>>>>>>> origin/main


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


<<<<<<< HEAD
def format_roadmap(rm: Roadmap) -> str:
    from .report import format_roadmap as _format      # imported late: report imports this module
    return _format(rm)
=======
def _skill_names(data: Dataset, ids) -> str:
    return ", ".join(f"{data.skills[s].name} ({s})" for s in sorted(ids)) or "none"


def format_roadmap(rm: Roadmap) -> str:
    data, a, b = rm.data, rm.part_a, rm.part_b
    line = "=" * 72
    out = [line, "CAREER ROADMAP", line,
           f"Current skills: {_skill_names(data, data.student_skills)}", ""]

    out.append("PART A - Learning resources (Greedy, Kruskal MST)")
    out.append("-" * 72)
    for r in a.chosen_resources:
        out.append(f"  {r.resource_id}  {r.name:<36} {data.skills[r.skill_a].name} <-> "
                   f"{data.skills[r.skill_b].name}  {r.hours}h")
    out.append(f"  Total learning hours: {a.total_hours}")
    out.append(f"  Reachable skills ({len(a.reachable_skills)}): {_skill_names(data, a.reachable_skills)}")
    out.append(f"  Unreachable skills ({len(a.unreachable_skills)}): {_skill_names(data, a.unreachable_skills)}")
    if a.skipped_unavailable:
        out.append("  Unavailable resources (not used): "
                   + ", ".join(r.resource_id for r in a.skipped_unavailable))
    out.append("")

    out.append("PART B - Month-by-month plan (DP, Multiple 0/1 Knapsack)")
    out.append("-" * 72)
    for month, acts in b.schedule.items():
        out.append(f"  Month {month}  [{b.hours_used[month]}/{b.budgets[month]} hours]")
        if not acts:
            out.append("    (free month - no activity fits)")
        for act in acts:
            out.append(f"    {act.activity_id}  {act.name:<38} {act.type:<10} {act.hours:>3}h  "
                       f"value {act.career_value:>2}  unlocks {data.skills[act.skill_unlocked].name}")
    used, budget = sum(b.hours_used.values()), sum(b.budgets.values())
    out.append(f"  Hours used: {used}/{budget}")
    out.append(f"  TOTAL CAREER VALUE: {b.total_value}")
    unlocked = {act.skill_unlocked for acts in b.schedule.values() for act in acts}
    out.append(f"  Skills unlocked: {_skill_names(data, unlocked)}")
    out.append("")

    out.append("EXCLUDED ACTIVITIES")
    out.append("-" * 72)
    for act in b.already_known:
        out.append(f"  {act.activity_id}  {act.name}: student already knows {data.skills[act.skill_unlocked].name}")
    for act in b.ineligible:
        out.append(f"  {act.activity_id}  {act.name}: skill {data.skills[act.skill_unlocked].name} is unreachable")
    for act in b.oversized:
        out.append(f"  {act.activity_id}  {act.name}: needs {act.hours}h, more than every month's budget")
    for act in b.unscheduled:
        out.append(f"  {act.activity_id}  {act.name}: did not fit in the optimal plan ({act.hours}h)")
    if not (b.already_known or b.ineligible or b.oversized or b.unscheduled):
        out.append("  none")
    out.append(line)
    return "\n".join(out)
>>>>>>> origin/main
