import pytest

from roadmap.data_loader import load_dataset
from roadmap.pipeline import build_roadmap, format_roadmap, recompute_with_unavailable
from roadmap.scenarios import run_all


@pytest.fixture
def data():
    return load_dataset("data")


def test_part_a_feeds_part_b(data):
    rm = build_roadmap(data)
    for acts in rm.part_b.schedule.values():
        for a in acts:
            assert a.skill_unlocked in rm.part_a.reachable_skills


def test_recompute_routes_around_unavailable_resources(data):
    before = build_roadmap(data)
    after = recompute_with_unavailable(data, {"R11", "R12"})
    used = {r.resource_id for r in after.part_a.chosen_resources}
    assert not {"R11", "R12"} & used
    assert {"R13", "R14"} <= used                              # Docker now reached via AWS
    assert "S12" in after.part_a.reachable_skills
    assert after.part_a.total_hours > before.part_a.total_hours


def test_recompute_when_skill_gets_cut_off(data):
    before = build_roadmap(data)
    after = recompute_with_unavailable(data, {"R11", "R12", "R13"})
    assert "S12" not in before.part_a.unreachable_skills
    assert "S12" in after.part_a.unreachable_skills            # Docker cut off
    assert "A07" in {a.activity_id for a in after.part_b.ineligible}


def _plan(data, skills):
    from dataclasses import replace
    rm = build_roadmap(replace(data, student_skills=set(skills)))
    return rm, {m: [a.activity_id for a in acts] for m, acts in rm.part_b.schedule.items()}


def test_roadmap_depends_on_starting_skills(data):
    full, plan_full = _plan(data, {"S01", "S02", "S05"})     # programming + SQL
    prog, plan_prog = _plan(data, {"S01", "S02"})            # data cluster cut off
    stats, plan_stats = _plan(data, {"S14"})                 # data cluster only
    assert len(full.part_a.reachable_skills) > len(prog.part_a.reachable_skills) > len(stats.part_a.reachable_skills)
    assert plan_full != plan_prog != plan_stats
    assert "S15" in prog.part_a.unreachable_skills           # ML needs the data cluster
    assert "S10" in stats.part_a.unreachable_skills          # backend not reachable from stats


def test_known_skills_free_hours_for_new_activities(data):
    rm, plan = _plan(data, {"S01", "S03", "S04", "S10"})
    scheduled = {a for acts in plan.values() for a in acts}
<<<<<<< HEAD
    known_acts = {"A01", "A02", "A06", "A12"}                  # A12 = Python course (S01 is known)
    assert {a.activity_id for a in rm.part_b.already_known} == known_acts
    assert not scheduled & known_acts
=======
    assert {a.activity_id for a in rm.part_b.already_known} == {"A01", "A02", "A06"}
    assert not scheduled & {"A01", "A02", "A06"}
>>>>>>> origin/main


def test_unknown_resource_id_is_rejected(data):
    with pytest.raises(ValueError):
        recompute_with_unavailable(data, {"R99"})


def test_report_contains_required_fields(data):
    text = format_roadmap(build_roadmap(data))
    for needle in ("Month 1", "Month 6", "TOTAL CAREER VALUE", "Unreachable skills",
                   "Skills unlocked", "hours"):
        assert needle in text


def test_proposal_scenarios_pass(data):
    ok, text = run_all(data)
    assert ok, text
