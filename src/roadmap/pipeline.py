"""Part C - Integration: Part A's reachable skills decide what Part B may schedule."""
from dataclasses import dataclass, replace

from .models import Dataset
from .part_a_kruskal import PartAResult, run_part_a
from .part_b_knapsack import PartBResult, run_part_b


@dataclass
class Roadmap:
    data: Dataset
    part_a: PartAResult
    part_b: PartBResult


def build_roadmap(data: Dataset) -> Roadmap:
    a = run_part_a(data)
    b = run_part_b(data, a.reachable_skills)
    return Roadmap(data, a, b)


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
