"""
tests/test_budget.py

Unit tests for models/budget.py — Budget dataclass and its methods.
"""

import pytest
from models.budget import Budget


class TestBudgetCreation:
    """Tests for creating Budget objects with valid and invalid inputs."""

    def test_valid_budget_creation(self):
        budget = Budget(income=30000.0, budget_limit=20000.0)
        assert budget.income == 30000.0
        assert budget.budget_limit == 20000.0

    def test_budget_stores_float_values(self):
        budget = Budget(income=15000.5, budget_limit=10000.75)
        assert budget.income == 15000.5
        assert budget.budget_limit == 10000.75


class TestRemainingBudget:
    """Tests for Budget.get_remaining_budget()."""

    def test_remaining_when_under_budget(self):
        budget = Budget(income=30000.0, budget_limit=20000.0)
        assert budget.get_remaining_budget(5000.0) == 15000.0

    def test_remaining_when_exactly_at_budget(self):
        budget = Budget(income=30000.0, budget_limit=20000.0)
        assert budget.get_remaining_budget(20000.0) == 0.0

    def test_remaining_when_over_budget(self):
        budget = Budget(income=30000.0, budget_limit=20000.0)
        assert budget.get_remaining_budget(25000.0) == -5000.0

    def test_remaining_with_zero_spending(self):
        budget = Budget(income=30000.0, budget_limit=20000.0)
        assert budget.get_remaining_budget(0.0) == 20000.0


class TestIsOverBudget:
    """Tests for Budget.is_over_budget()."""

    def test_not_over_budget(self):
        budget = Budget(income=30000.0, budget_limit=20000.0)
        assert budget.is_over_budget(19999.99) is False

    def test_exactly_at_budget_not_over(self):
        budget = Budget(income=30000.0, budget_limit=20000.0)
        assert budget.is_over_budget(20000.0) is False

    def test_over_budget(self):
        budget = Budget(income=30000.0, budget_limit=20000.0)
        assert budget.is_over_budget(20000.01) is True


class TestBudgetSerialisation:
    """Tests for Budget.to_dict() and Budget.from_dict()."""

    def test_to_dict(self):
        budget = Budget(income=30000.0, budget_limit=20000.0)
        d = budget.to_dict()
        assert d == {"income": 30000.0, "budget_limit": 20000.0}

    def test_from_dict(self):
        d = {"income": 25000.0, "budget_limit": 18000.0}
        budget = Budget.from_dict(d)
        assert budget.income == 25000.0
        assert budget.budget_limit == 18000.0

    def test_round_trip(self):
        original = Budget(income=50000.0, budget_limit=35000.0)
        restored = Budget.from_dict(original.to_dict())
        assert restored.income == original.income
        assert restored.budget_limit == original.budget_limit
