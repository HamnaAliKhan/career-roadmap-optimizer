from roadmap.data_loader import load_dataset


def test_loads_sample_data():
    data = load_dataset("data")
    assert "S01" in data.skills
    assert len(data.months) == 6
    assert data.student_skills == {"S01"}
    assert any(r.unavailable for r in data.resources)


# TODO (required by the proposal's Testing section):
# - test_disconnected_skill_is_reported_unreachable   (Part A)
# - test_unavailable_resource_is_never_chosen          (Part A)
# - test_equal_hours_tie_break_prefers_relevance       (Part A)
# - test_hours_over_demand_respects_month_budgets      (Part B)
# - test_oversized_activity_is_excluded_and_reported   (Part B)
# - test_recompute_when_resource_becomes_unavailable   (Pipeline)
