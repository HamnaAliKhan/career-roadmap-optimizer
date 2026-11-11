from helpers import dataset, res, skill

from roadmap.part_a_kruskal import DisjointSet, run_part_a


def test_disjoint_set():
    d = DisjointSet("ABCD")
    assert d.union("A", "B")
    assert d.union("C", "D")
    assert not d.union("B", "A")
    assert d.find("A") == d.find("B") != d.find("C")
    assert d.union("B", "D")
    assert len({d.find(x) for x in "ABCD"}) == 1


def test_mst_picks_cheapest_edges():
    # A-B 1, B-C 2, A-C 5, C-D 3 -> MST = AB, BC, CD = 6 hours
    data = dataset([skill(x) for x in "ABCD"],
                   [res("ab", "A", "B", 1), res("bc", "B", "C", 2),
                    res("ac", "A", "C", 5), res("cd", "C", "D", 3)])
    a = run_part_a(data)
    assert {r.resource_id for r in a.chosen_resources} == {"ab", "bc", "cd"}
    assert a.total_hours == 6
    assert a.reachable_skills == set("ABCD")


def test_disconnected_skill_is_reported_unreachable():
    data = dataset([skill(x) for x in "ABCD"],
                   [res("ab", "A", "B", 1), res("cd", "C", "D", 1)])
    a = run_part_a(data)
    assert a.reachable_skills == {"A", "B"}
    assert a.unreachable_skills == {"C", "D"}
    assert [r.resource_id for r in a.chosen_resources] == ["ab"]  # C-D edge not counted


def test_unavailable_resource_is_never_chosen():
    data = dataset([skill(x) for x in "AB"],
                   [res("cheap", "A", "B", 1, unavailable=True), res("dear", "A", "B", 9)])
    a = run_part_a(data)
    assert [r.resource_id for r in a.chosen_resources] == ["dear"]


def test_only_unavailable_link_makes_skill_unreachable():
    data = dataset([skill(x) for x in "AB"], [res("ab", "A", "B", 1, unavailable=True)])
    assert run_part_a(data).unreachable_skills == {"B"}


def test_equal_hours_tie_break_prefers_relevance():
    # A and B are both known. C can be joined from A (low relevance) or B (high), same hours.
    data = dataset([skill("A", 2), skill("B", 9), skill("C", 5)],
                   [res("fromA", "A", "C", 4), res("fromB", "B", "C", 4)],
                   student=("A", "B"))
    a = run_part_a(data)
    assert [r.resource_id for r in a.chosen_resources] == ["fromB"]


def test_equal_hours_and_relevance_tie_break_prefers_demand():
    # Same hours and same relevance; B has higher demand than A.
    data = dataset([skill("A", 5, demand=2), skill("B", 5, demand=9), skill("C", 5)],
                   [res("fromA", "A", "C", 4), res("fromB", "B", "C", 4)],
                   student=("A", "B"))
    a = run_part_a(data)
    assert [r.resource_id for r in a.chosen_resources] == ["fromB"]


def test_relevance_outranks_demand_in_tie_break():
    # A: higher relevance, low demand. B: lower relevance, high demand -> relevance wins.
    data = dataset([skill("A", 9, demand=1), skill("B", 3, demand=10), skill("C", 5)],
                   [res("fromA", "A", "C", 4), res("fromB", "B", "C", 4)],
                   student=("A", "B"))
    a = run_part_a(data)
    assert [r.resource_id for r in a.chosen_resources] == ["fromA"]


def test_known_skills_cost_nothing_to_connect():
    data = dataset([skill(x) for x in "AB"], [res("ab", "A", "B", 7)], student=("A", "B"))
    a = run_part_a(data)
    assert a.chosen_resources == [] and a.total_hours == 0


def test_real_dataset():
    from roadmap.data_loader import load_dataset
    data = load_dataset("data")
    a = run_part_a(data)
    assert a.unreachable_skills == {"S19", "S20"}
    # a spanning tree over the reachable skills, with the student's skills pre-joined
    assert len(a.chosen_resources) == len(a.reachable_skills) - len(data.student_skills)
