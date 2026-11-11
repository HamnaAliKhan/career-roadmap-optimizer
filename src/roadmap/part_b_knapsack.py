"""Part B - Dynamic Programming: Multiple 0/1 Knapsack.

Knapsacks = months (capacity = hour_budget), items = eligible activities
(weight = hours, value = career_value). Each activity goes in at most one month.

Before the DP
-------------
- Eligible = activities whose skill_unlocked is in Part A's reachable_skills.
- Activities with hours > max(month budgets) are excluded and REPORTED.

DP design (decide as a group, and justify it in the report)
-----------------------------------------------------------
Option 1 (exact): recursion over items with memoisation.
    state = (item index i, tuple of remaining hours per month)
    choice for item i = skip it, or put it in month m if it fits.
    Optimal, but the state space grows with the budgets - fine for 15 items / 6 months.
Option 2 (month-by-month): run a classic 1-D 0/1 knapsack table for month 1,
    remove the chosen items, repeat for month 2..6. Fast and easy to show as a
    DP table, but NOT guaranteed optimal overall - say so if you use it.

Either way, keep enough info (choice table / parent pointers) to backtrack
which activity went in which month.
"""
from dataclasses import dataclass, field

from .models import Activity, Dataset


@dataclass
class PartBResult:
    schedule: dict[int, list[Activity]] = field(default_factory=dict)  # month -> activities
    hours_used: dict[int, int] = field(default_factory=dict)
    total_value: int = 0
    ineligible: list[Activity] = field(default_factory=list)   # skill not reachable
    oversized: list[Activity] = field(default_factory=list)    # longer than every month
    unscheduled: list[Activity] = field(default_factory=list)  # eligible but didn't fit


def run_part_b(data: Dataset, reachable_skills: set[str]) -> PartBResult:
    # TODO: filter activities, then run the DP and backtrack.
    raise NotImplementedError
