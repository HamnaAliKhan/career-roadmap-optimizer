import pytest

from roadmap.data_loader import load_dataset, validate
from roadmap.models import Resource


def test_dataset_meets_proposal_sizes():
    data = load_dataset("data")
    assert len(data.skills) == 20
    assert len(data.resources) == 30
    assert len(data.activities) == 15
    assert len(data.months) == 6
    assert len({m.hour_budget for m in data.months}) == 6  # distinct budgets
    assert data.student_skills == {"S01", "S02", "S05"}
    assert any(r.unavailable for r in data.resources)


def test_validation_rejects_unknown_skill():
    data = load_dataset("data")
    data.resources.append(Resource("RX", "bad", "S01", "S99", 5, False))
    with pytest.raises(ValueError, match="unknown skill S99"):
        validate(data)
