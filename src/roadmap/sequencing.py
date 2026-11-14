"""Foundations first: order the months of an optimal plan without changing its value.

Part B (the knapsack DP) decides WHAT is taken and which activities fit together.
Because the months have different budgets, the DP may put an advanced activity (say a
backend internship) in Month 1 and a basic one in Month 4. This step re-arranges the
SAME activities over the months so the plan reads like a roadmap. In order of importance:

  1. prerequisites: if the learning path to skill X goes through skill Y and the plan has
     an activity for Y, the Y activity must not come after the X one;
  2. depth: basic activities come early (cost = month index x how foundational the
     activity is, so being late hurts the basics most);
  3. free months (nothing scheduled) come last.

How: depth-first branch and bound over every way of placing the activities so each month
stays within its budget, cutting a branch once it cannot beat the best arrangement found
so far. The DP's own arrangement is the starting best, so the result is never worse than it.
The activity set never changes, so total career value and every constraint are untouched.
A node limit keeps it fast on large inputs (it then returns the best arrangement found).
"""
from collections.abc import Callable

from .models import Activity

NODE_LIMIT = 150_000


def order_foundations_first(schedule: dict[int, list[Activity]], budgets: dict[int, int],
                            depth: Callable[[Activity], int],
                            prerequisites: Callable[[Activity], set[str]] = lambda a: set(),
                            node_limit: int = NODE_LIMIT) -> dict[int, list[Activity]]:
    months = sorted(budgets)
    cap = [budgets[m] for m in months]
    n = len(months)
    start = [list(schedule.get(m, [])) for m in months]
    items = sorted((a for g in start for a in g), key=lambda a: (depth(a), -a.hours, a.activity_id))
    ids = [a.activity_id for a in items]
    pre = {a.activity_id: set(prerequisites(a)) & set(ids) for a in items}
    after = {i: {j for j in ids if i in pre[j]} for i in ids}      # who needs i first
    deepest = max((depth(a) for a in items), default=0)
    weight = {a.activity_id: deepest - depth(a) + 1 for a in items}  # basics weigh most

    def final_cost(slot: dict[str, int]):
        broken = sum(1 for i in ids for p in pre[i] if slot[p] > slot[i])
        weighted = sum(slot[i] * weight[i] for i in ids)
        used = set(slot.values())
        return (broken, weighted, -sum(i for i in range(n) if i not in used))

    best_slot = {a.activity_id: i for i, g in enumerate(start) for a in g}
    best = final_cost(best_slot)
    nodes = 0
    slot: dict[str, int] = {}
    load = [0] * n

    def search(k: int, broken: int, weighted: int):
        nonlocal best, best_slot, nodes
        nodes += 1
        if nodes > node_limit or (broken, weighted) > best[:2]:
            return
        if k == len(items):
            c = final_cost(slot)
            if c < best:
                best, best_slot = c, dict(slot)
            return
        a = items[k]
        aid = a.activity_id
        for i in range(n):
            if load[i] + a.hours > cap[i]:
                continue
            new_broken = broken
            new_broken += sum(1 for p in pre[aid] if p in slot and slot[p] > i)
            new_broken += sum(1 for q in after[aid] if q in slot and i > slot[q])
            slot[aid] = i
            load[i] += a.hours
            search(k + 1, new_broken, weighted + i * weight[aid])
            load[i] -= a.hours
            del slot[aid]

    search(0, 0, 0)

    result: dict[int, list[Activity]] = {m: [] for m in months}
    for a in items:
        result[months[best_slot[a.activity_id]]].append(a)
    return {m: sorted(g, key=lambda a: (depth(a), a.activity_id)) for m, g in result.items()}
