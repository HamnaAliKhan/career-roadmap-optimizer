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
