import itertools
import random

from helpers import act, dataset, skill

from roadmap.part_b_knapsack import run_part_b, solve_multiple_knapsack


def brute_force(weights, values, caps):
    best = 0
    for choice in itertools.product(range(len(caps) + 1), repeat=len(weights)):
        used = [0] * len(caps)
        value = 0
        for i, k in enumerate(choice):
            if k < len(caps):
                used[k] += weights[i]
                value += values[i]
        if all(u <= c for u, c in zip(used, caps)):
            best = max(best, value)
    return best


def test_dp_matches_brute_force_on_random_cases():
    rng = random.Random(363)
    for _ in range(150):
        n, m = rng.randint(1, 6), rng.randint(1, 3)
        w = [rng.randint(1, 12) for _ in range(n)]
        v = [rng.randint(1, 10) for _ in range(n)]
        caps = [rng.randint(0, 15) for _ in range(m)]
        total, assignment, _ = solve_multiple_knapsack(w, v, caps)
        assert total == brute_force(w, v, caps)
        # the assignment must be valid and add up to the reported value
        used = [0] * m
        for i, k in enumerate(assignment):
            if k is not None:
                used[k] += w[i]
        assert all(u <= c for u, c in zip(used, caps))
        assert sum(v[i] for i, k in enumerate(assignment) if k is not None) == total


def test_hours_over_demand_respects_month_budgets():
    acts = [act(f"X{i}", 6, i + 1, "A") for i in range(5)]  # 30h demand
    data = dataset([skill("A")], activities=acts, budgets=(10, 7))  # 17h supply
    b = run_part_b(data, {"A"})
    assert all(b.hours_used[m] <= b.budgets[m] for m in b.budgets)
    assert b.total_value == 5 + 4  # only two 6h items fit, one per month
    assert len(b.unscheduled) == 3


def test_oversized_activity_is_excluded_and_reported():
    data = dataset([skill("A")], activities=[act("big", 50, 99, "A"), act("ok", 5, 1, "A")],
                   budgets=(20, 30))
    b = run_part_b(data, {"A"})
    assert [x.activity_id for x in b.oversized] == ["big"]
    assert b.total_value == 1


def test_unreachable_skill_makes_activity_ineligible():
    data = dataset([skill("A"), skill("B")],
                   activities=[act("x", 5, 9, "B"), act("y", 5, 1, "A")])
    b = run_part_b(data, {"A"})
    assert [x.activity_id for x in b.ineligible] == ["x"]
    assert b.total_value == 1


def test_each_activity_in_at_most_one_month():
    data = dataset([skill("A")], activities=[act("x", 5, 9, "A")], budgets=(10, 10, 10))
    b = run_part_b(data, {"A"})
    assert sum(len(v) for v in b.schedule.values()) == 1


def test_month_with_zero_budget():
    data = dataset([skill("A")], activities=[act("x", 5, 9, "A")], budgets=(0, 5))
    b = run_part_b(data, {"A"})
    assert b.schedule[1] == [] and [x.activity_id for x in b.schedule[2]] == ["x"]
