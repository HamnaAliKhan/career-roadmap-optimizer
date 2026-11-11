"""Test scenarios from the proposal, printed with their output for the demo/report:
disconnected skills, hours over-demand, oversized activity, and recomputing
when resources become unavailable."""
from .models import Dataset
from .pipeline import build_roadmap, recompute_with_unavailable


def _check(ok: bool, text: str) -> str:
    return f"  [{'PASS' if ok else 'FAIL'}] {text}"


def disconnected_skills(data: Dataset) -> tuple[bool, str]:
    rm = build_roadmap(data)
    a, b = rm.part_a, rm.part_b
    blocked = [act for act in data.activities if act.skill_unlocked in a.unreachable_skills]
    checks = [
        (bool(a.unreachable_skills), f"unreachable skills reported: {sorted(a.unreachable_skills)}"),
        (all(r.skill_a in a.reachable_skills and r.skill_b in a.reachable_skills
             for r in a.chosen_resources), "chosen resources only connect reachable skills"),
        ({x.activity_id for x in blocked} == {x.activity_id for x in b.ineligible},
         f"activities on unreachable skills excluded: {[x.activity_id for x in b.ineligible]}"),
    ]
    return _report("TEST 1 - Disconnected skills", checks)


def hours_over_demand(data: Dataset) -> tuple[bool, str]:
    rm = build_roadmap(data)
    b = rm.part_b
    demand = sum(x.hours for acts in b.schedule.values() for x in acts) + sum(x.hours for x in b.unscheduled)
    budget = sum(b.budgets.values())
    checks = [
        (demand > budget, f"eligible activities need {demand}h but only {budget}h are available"),
        (all(b.hours_used[m] <= b.budgets[m] for m in b.budgets),
         "every month within its budget: "
         + ", ".join(f"M{m} {b.hours_used[m]}/{b.budgets[m]}" for m in b.budgets)),
        (len({x.activity_id for acts in b.schedule.values() for x in acts})
         == sum(len(acts) for acts in b.schedule.values()), "no activity scheduled twice"),
        (bool(b.unscheduled), f"left out: {[x.activity_id for x in b.unscheduled]}"),
    ]
    return _report("TEST 2 - Hours over-demand", checks)


def oversized_activity(data: Dataset) -> tuple[bool, str]:
    rm = build_roadmap(data)
    b = rm.part_b
    biggest = max(b.budgets.values())
    scheduled = {x.activity_id for acts in b.schedule.values() for x in acts}
    checks = [
        (bool(b.oversized), "oversized reported: "
         + ", ".join(f"{x.activity_id} ({x.hours}h > {biggest}h)" for x in b.oversized)),
        (not any(x.activity_id in scheduled for x in b.oversized), "oversized activities not scheduled"),
    ]
    return _report("TEST 3 - Oversized activity", checks)


def resources_become_unavailable(data: Dataset, resource_ids=("R11", "R12")) -> tuple[bool, str]:
    before = build_roadmap(data)
    after = recompute_with_unavailable(data, set(resource_ids))
    used = {r.resource_id for r in after.part_a.chosen_resources}
    lost = after.part_a.unreachable_skills - before.part_a.unreachable_skills
    checks = [
        (not used & set(resource_ids), f"{', '.join(resource_ids)} no longer used"),
        (True, f"newly unreachable skills: {sorted(lost) or 'none'}"),
        (True, f"learning hours {before.part_a.total_hours} -> {after.part_a.total_hours}, "
               f"career value {before.part_b.total_value} -> {after.part_b.total_value}"),
    ]
    return _report(f"TEST 4 - Recompute when {', '.join(resource_ids)} become unavailable", checks)


def _report(title: str, checks) -> tuple[bool, str]:
    lines = [title] + [_check(ok, text) for ok, text in checks]
    return all(ok for ok, _ in checks), "\n".join(lines)


def run_all(data: Dataset) -> tuple[bool, str]:
    results = [disconnected_skills(data), hours_over_demand(data),
               oversized_activity(data), resources_become_unavailable(data)]
    ok = all(r[0] for r in results)
    body = "\n\n".join(r[1] for r in results)
    return ok, f"{body}\n\n{'ALL TESTS PASSED' if ok else 'SOME TESTS FAILED'}"
