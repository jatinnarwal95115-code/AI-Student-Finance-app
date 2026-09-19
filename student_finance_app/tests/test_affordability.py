"""
tests/test_affordability.py

Unit tests for services/affordability.py — "Can I Afford This?" logic.
"""

import pytest
from services.affordability import check_affordability


class TestAffordabilityWithinBudget:
    def test_purchase_within_budget_returns_yes(self):
        response = check_affordability("Headphones", 500.0, 2000.0)
        assert "✅" in response
        assert "can likely afford" in response.lower()

    def test_purchase_exactly_at_remaining_returns_yes(self):
        response = check_affordability("Book", 1000.0, 1000.0)
        assert "✅" in response

    def test_response_contains_item_name(self):
        response = check_affordability("Laptop", 30000.0, 50000.0)
        assert "Laptop" in response

    def test_response_contains_remaining_after_purchase(self):
        response = check_affordability("Shoes", 500.0, 2000.0)
        # After buying ₹500 item with ₹2000 remaining, ₹1500 should remain
        assert "1,500.00" in response


class TestAffordabilitySlightlyOver:
    def test_slightly_over_budget_returns_warning(self):
        # price = 1050, remaining = 1000 → 5% over (within 20% threshold)
        response = check_affordability("Jacket", 1050.0, 1000.0)
        assert "⚠️" in response
        assert "slightly over" in response.lower()

    def test_exactly_20_percent_over_returns_warning(self):
        # price = 1200, remaining = 1000 → exactly 20% over
        response = check_affordability("Watch", 1200.0, 1000.0)
        assert "⚠️" in response


class TestAffordabilitySignificantlyOver:
    def test_significantly_over_budget_returns_no(self):
        # price = 5000, remaining = 1000 → 400% over
        response = check_affordability("iPhone", 5000.0, 1000.0)
        assert "❌" in response
        assert "significantly" in response.lower()


class TestAffordabilityNoRemainingBudget:
    def test_zero_remaining_returns_no_budget_message(self):
        response = check_affordability("Coffee", 50.0, 0.0)
        assert "❌" in response
        assert "no remaining budget" in response.lower()

    def test_negative_remaining_returns_no_budget_message(self):
        response = check_affordability("Coffee", 50.0, -200.0)
        assert "❌" in response


class TestAffordabilityDisclaimer:
    def test_disclaimer_always_appended(self):
        for remaining, price in [(2000.0, 500.0), (500.0, 1000.0), (0.0, 50.0)]:
            response = check_affordability("Item", price, remaining)
            assert "educational purposes only" in response.lower()

    def test_empty_item_name_uses_fallback(self):
        response = check_affordability("", 500.0, 2000.0)
        assert "this item" in response.lower()
