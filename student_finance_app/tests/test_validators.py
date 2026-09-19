"""
tests/test_validators.py

Unit tests for utils/validators.py — all input validation functions.
"""

import pytest
from datetime import date, timedelta
from utils.validators import (
    validate_positive_float,
    validate_positive_int,
    validate_budget_vs_income,
    validate_category,
    validate_date_not_future,
    validate_description_length,
    validate_interest_rate,
)


class TestValidatePositiveFloat:
    def test_valid_positive_float(self):
        validate_positive_float(100.0, "Amount")  # no error

    def test_valid_integer_passes(self):
        validate_positive_float(50, "Amount")  # integers are also acceptable

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="greater than zero"):
            validate_positive_float(0.0, "Amount")

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="greater than zero"):
            validate_positive_float(-10.0, "Amount")

    def test_string_raises(self):
        with pytest.raises(ValueError, match="must be a number"):
            validate_positive_float("abc", "Amount")

    def test_none_raises(self):
        with pytest.raises(ValueError, match="must be a number"):
            validate_positive_float(None, "Amount")


class TestValidatePositiveInt:
    def test_valid_positive_int(self):
        validate_positive_int(12, "Months")  # no error

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="greater than zero"):
            validate_positive_int(0, "Months")

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="greater than zero"):
            validate_positive_int(-5, "Months")

    def test_string_raises(self):
        with pytest.raises(ValueError, match="whole number"):
            validate_positive_int("xyz", "Months")


class TestValidateBudgetVsIncome:
    def test_budget_less_than_income_is_valid(self):
        validate_budget_vs_income(15000.0, 30000.0)  # no error

    def test_budget_equal_to_income_is_valid(self):
        validate_budget_vs_income(30000.0, 30000.0)  # no error

    def test_budget_exceeds_income_raises(self):
        with pytest.raises(ValueError, match="cannot exceed your income"):
            validate_budget_vs_income(35000.0, 30000.0)


class TestValidateCategory:
    def test_valid_categories(self):
        valid = ["Food", "Travel", "Shopping", "Education", "Entertainment", "Other"]
        for cat in valid:
            validate_category(cat)  # no error for any

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError, match="not a valid category"):
            validate_category("Groceries")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="not a valid category"):
            validate_category("")

    def test_lowercase_raises(self):
        with pytest.raises(ValueError, match="not a valid category"):
            validate_category("food")  # case-sensitive


class TestValidateDateNotFuture:
    def test_today_is_valid(self):
        validate_date_not_future(date.today().isoformat())  # no error

    def test_past_date_is_valid(self):
        past = (date.today() - timedelta(days=30)).isoformat()
        validate_date_not_future(past)  # no error

    def test_future_date_raises(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        with pytest.raises(ValueError, match="cannot be in the future"):
            validate_date_not_future(future)

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="not a valid date"):
            validate_date_not_future("01-01-2025")  # wrong format


class TestValidateDescriptionLength:
    def test_empty_string_is_valid(self):
        validate_description_length("")  # no error

    def test_exactly_100_chars_is_valid(self):
        validate_description_length("x" * 100)  # no error

    def test_101_chars_raises(self):
        with pytest.raises(ValueError, match="too long"):
            validate_description_length("x" * 101)


class TestValidateInterestRate:
    def test_zero_rate_is_valid(self):
        validate_interest_rate(0.0)  # no error — interest-free loan

    def test_typical_rate_is_valid(self):
        validate_interest_rate(8.5)  # no error

    def test_100_percent_is_valid(self):
        validate_interest_rate(100.0)  # no error

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            validate_interest_rate(-1.0)

    def test_above_100_raises(self):
        with pytest.raises(ValueError, match="cannot exceed 100"):
            validate_interest_rate(101.0)

    def test_string_raises(self):
        with pytest.raises(ValueError, match="must be a number"):
            validate_interest_rate("high")
