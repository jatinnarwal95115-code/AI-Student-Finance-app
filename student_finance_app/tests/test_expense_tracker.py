"""
tests/test_expense_tracker.py

Unit tests for models/expense.py (Expense dataclass) and
services/expense_tracker.py (ExpenseTracker class).
"""

import pytest
from models.expense import Expense, ALLOWED_CATEGORIES
from services.expense_tracker import ExpenseTracker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_expense(amount=500.0, category="Food", description="Lunch", date="2025-06-01"):
    return Expense(amount=amount, category=category, description=description, date=date)


# ---------------------------------------------------------------------------
# Expense dataclass
# ---------------------------------------------------------------------------

class TestExpenseDataclass:
    def test_valid_expense_creation(self):
        e = make_expense()
        assert e.amount == 500.0
        assert e.category == "Food"
        assert e.description == "Lunch"
        assert e.date == "2025-06-01"

    def test_expense_default_description_is_empty(self):
        e = Expense(amount=100.0, category="Travel", date="2025-06-01")
        assert e.description == ""

    def test_expense_to_dict(self):
        e = make_expense()
        d = e.to_dict()
        assert d["amount"] == 500.0
        assert d["category"] == "Food"
        assert d["description"] == "Lunch"
        assert d["date"] == "2025-06-01"

    def test_expense_from_dict(self):
        d = {"amount": 200.0, "category": "Travel", "description": "Bus", "date": "2025-05-10"}
        e = Expense.from_dict(d)
        assert e.amount == 200.0
        assert e.category == "Travel"

    def test_expense_round_trip(self):
        original = make_expense(amount=750.0, category="Shopping")
        restored = Expense.from_dict(original.to_dict())
        assert restored.amount == original.amount
        assert restored.category == original.category


# ---------------------------------------------------------------------------
# ExpenseTracker — Add and retrieve
# ---------------------------------------------------------------------------

class TestExpenseTrackerAdd:
    def test_add_single_expense(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense())
        assert len(tracker.get_all_expenses()) == 1

    def test_add_multiple_expenses(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense(amount=100.0))
        tracker.add_expense(make_expense(amount=200.0, category="Travel"))
        tracker.add_expense(make_expense(amount=300.0, category="Shopping"))
        assert len(tracker.get_all_expenses()) == 3

    def test_get_all_returns_copy(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense())
        copy = tracker.get_all_expenses()
        copy.clear()
        assert len(tracker.get_all_expenses()) == 1  # original unchanged


# ---------------------------------------------------------------------------
# ExpenseTracker — Total spending
# ---------------------------------------------------------------------------

class TestTotalSpending:
    def test_total_spending_empty_list(self):
        tracker = ExpenseTracker()
        assert tracker.get_total_spending() == 0.0

    def test_total_spending_single_expense(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense(amount=500.0))
        assert tracker.get_total_spending() == 500.0

    def test_total_spending_multiple_expenses(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense(amount=100.0))
        tracker.add_expense(make_expense(amount=250.0))
        tracker.add_expense(make_expense(amount=150.0))
        assert tracker.get_total_spending() == 500.0


# ---------------------------------------------------------------------------
# ExpenseTracker — Category breakdown
# ---------------------------------------------------------------------------

class TestCategoryBreakdown:
    def test_category_breakdown_empty(self):
        tracker = ExpenseTracker()
        breakdown = tracker.get_category_breakdown()
        assert all(v == 0.0 for v in breakdown.values())

    def test_category_breakdown_single_category(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense(amount=300.0, category="Food"))
        tracker.add_expense(make_expense(amount=200.0, category="Food"))
        breakdown = tracker.get_category_breakdown()
        assert breakdown["Food"] == 500.0
        assert breakdown["Travel"] == 0.0

    def test_category_breakdown_multiple_categories(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense(amount=400.0, category="Food"))
        tracker.add_expense(make_expense(amount=600.0, category="Travel"))
        breakdown = tracker.get_category_breakdown()
        assert breakdown["Food"] == 400.0
        assert breakdown["Travel"] == 600.0

    def test_breakdown_includes_all_categories(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense(category="Food"))
        breakdown = tracker.get_category_breakdown()
        assert set(breakdown.keys()) == set(ALLOWED_CATEGORIES)


# ---------------------------------------------------------------------------
# ExpenseTracker — Top category
# ---------------------------------------------------------------------------

class TestTopCategory:
    def test_top_category_empty_list_returns_none(self):
        tracker = ExpenseTracker()
        assert tracker.get_top_category() is None

    def test_top_category_single_category(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense(amount=500.0, category="Shopping"))
        assert tracker.get_top_category() == "Shopping"

    def test_top_category_multiple(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense(amount=200.0, category="Food"))
        tracker.add_expense(make_expense(amount=800.0, category="Travel"))
        tracker.add_expense(make_expense(amount=100.0, category="Entertainment"))
        assert tracker.get_top_category() == "Travel"


# ---------------------------------------------------------------------------
# ExpenseTracker — Clear
# ---------------------------------------------------------------------------

class TestClear:
    def test_clear_empties_list(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense())
        tracker.add_expense(make_expense())
        tracker.clear()
        assert tracker.get_all_expenses() == []
        assert tracker.get_total_spending() == 0.0


# ---------------------------------------------------------------------------
# ExpenseTracker — Serialisation
# ---------------------------------------------------------------------------

class TestSerialisation:
    def test_to_dict_list_empty(self):
        tracker = ExpenseTracker()
        assert tracker.to_dict_list() == []

    def test_round_trip(self):
        tracker = ExpenseTracker()
        tracker.add_expense(make_expense(amount=100.0, category="Food"))
        tracker.add_expense(make_expense(amount=200.0, category="Travel"))
        data = tracker.to_dict_list()
        tracker2 = ExpenseTracker()
        tracker2.from_dict_list(data)
        assert tracker2.get_total_spending() == tracker.get_total_spending()
        assert len(tracker2.get_all_expenses()) == 2
