"""Part B - Dynamic Programming: Multiple 0/1 Knapsack.

Knapsacks = months (capacity = that month's hour budget).
Items     = eligible activities (weight = hours, value = career value).
Each activity is placed in at most one month, or not taken.

Filtering (before the DP)
-------------------------
- Ineligible: the activity's skill is not reachable (from Part A).
- Oversized:  the activity needs more hours than every month's budget.
Both are excluded and reported.

Recurrence
----------
best(i, caps) = highest career value from activities i..n-1 when the months
                still have `caps` hours left.

    best(n, caps) = 0
    best(i, caps) = max( best(i+1, caps),                                   # skip i
                         value[i] + best(i+1, caps with month m reduced     # put i in m
                                         by hours[i])  for every m with caps[m] >= hours[i] )

The answer is best(0, budgets). Each subproblem is solved once and memoised.
Two state reductions keep the table small without changing the answer:
  * months are interchangeable for the value, so caps is stored sorted;
  * a month with fewer hours left than the smallest remaining activity can
    never be used again, so its capacity is stored as 0.
The month-by-month assignment is recovered by retracing the choices that
achieve best(i, caps) for each i.

Complexity: O(n * S * m) time and O(n * S) memory, where n = activities,
m = months and S = number of distinct capacity states reached
(S <= product of (budget_m + 1)). That is pseudo-polynomial, like 0/1 knapsack.
"""
from dataclasses import dataclass, field

from .models import Activity, Dataset


@dataclass
class PartBResult:
    schedule: dict[int, list[Activity]] = field(default_factory=dict)  # month -> activities
    hours_used: dict[int, int] = field(default_factory=dict)
    budgets: dict[int, int] = field(default_factory=dict)
    total_value: int = 0
    ineligible: list[Activity] = field(default_factory=list)   # skill not reachable
    oversized: list[Activity] = field(default_factory=list)    # longer than every month
    unscheduled: list[Activity] = field(default_factory=list)  # eligible but didn't fit
    states_explored: int = 0


def solve_multiple_knapsack(weights: list[int], values: list[int], capacities: list[int]):
    """Return (best_value, assignment, states) where assignment[i] is the knapsack
    index for item i, or None if item i is not taken."""
    n = len(weights)
    suffix_min = [0] * (n + 1)
    suffix_min[n] = float("inf")
    for i in range(n - 1, -1, -1):
        suffix_min[i] = min(weights[i], suffix_min[i + 1])

    def canon(i, caps):
        smallest = suffix_min[i]
        return tuple(sorted(c if c >= smallest else 0 for c in caps))

    memo: dict[tuple, int] = {}

    def best(i, caps):  # caps is already canonical for i
        if i == n:
            return 0
        key = (i, caps)
        if key in memo:
            return memo[key]
        value = best(i + 1, canon(i + 1, caps))           # skip item i
        w = weights[i]
        seen = set()
        for k, c in enumerate(caps):
            if c >= w and c not in seen:                  # equal capacities give equal results
                seen.add(c)
                new_caps = caps[:k] + (c - w,) + caps[k + 1:]
                value = max(value, values[i] + best(i + 1, canon(i + 1, new_caps)))
        memo[key] = value
        return value

    total = best(0, canon(0, capacities))

    # Retrace the choices on the real (unsorted) month capacities.
    caps = list(capacities)
    assignment: list[int | None] = [None] * n
    for i in range(n):
        target = best(i, canon(i, caps))
        if best(i + 1, canon(i + 1, caps)) == target:
            continue
        for k, c in enumerate(caps):
            if c >= weights[i]:
                trial = caps[:k] + [c - weights[i]] + caps[k + 1:]
                if values[i] + best(i + 1, canon(i + 1, trial)) == target:
                    assignment[i] = k
                    caps = trial
                    break
    return total, assignment, len(memo)


def run_part_b(data: Dataset, reachable_skills: set[str]) -> PartBResult:
    result = PartBResult()
    months = sorted(data.months, key=lambda m: m.month)
    result.budgets = {m.month: m.hour_budget for m in months}
    max_budget = max((m.hour_budget for m in months), default=0)

    candidates: list[Activity] = []
    for a in data.activities:
        if a.skill_unlocked not in reachable_skills:
            result.ineligible.append(a)
        elif a.hours > max_budget:
            result.oversized.append(a)
        else:
            candidates.append(a)

    # Larger activities first: the capacity states shrink faster, fewer states.
    candidates.sort(key=lambda a: (-a.hours, a.activity_id))
    total, assignment, states = solve_multiple_knapsack(
        [a.hours for a in candidates],
        [a.career_value for a in candidates],
        [m.hour_budget for m in months],
    )

    result.schedule = {m.month: [] for m in months}
    for a, k in zip(candidates, assignment):
        if k is None:
            result.unscheduled.append(a)
        else:
            result.schedule[months[k].month].append(a)
    for month, acts in result.schedule.items():
        acts.sort(key=lambda a: a.activity_id)
        result.hours_used[month] = sum(a.hours for a in acts)
    result.total_value = total
    result.states_explored = states
    return result
