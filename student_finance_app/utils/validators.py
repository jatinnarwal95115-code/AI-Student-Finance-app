"""
utils/validators.py

All input validation functions for the Student Financial Literacy Assistant.

Each function raises ValueError with a clear, user-readable message when the
input is invalid, and returns silently when the input is acceptable.
"""

from datetime import date, datetime

from models.expense import ALLOWED_CATEGORIES


def validate_positive_float(value: float, field_name: str = "Value") -> None:
    """Raise ValueError if value is not a positive number.

    Args:
        value:      The number to check.
        field_name: Human-readable label used in the error message.

    Raises:
        ValueError: If value is not numeric or is <= 0.
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a number.")
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")


def validate_positive_int(value: int, field_name: str = "Value") -> None:
    """Raise ValueError if value is not a positive integer.

    Args:
        value:      The value to check.
        field_name: Human-readable label used in the error message.

    Raises:
        ValueError: If value is not an integer or is <= 0.
    """
    try:
        int_val = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a whole number.")
    if int_val <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")


def validate_budget_vs_income(budget: float, income: float) -> None:
    """Raise ValueError if the budget exceeds the income.

    Args:
        budget: The proposed budget limit.
        income: The student's monthly income.

    Raises:
        ValueError: If budget > income.
    """
    if budget > income:
        raise ValueError(
            f"Your budget (₹{budget:,.2f}) cannot exceed your income (₹{income:,.2f}). "
            "Please enter a budget that is within your income."
        )


def validate_category(category: str) -> None:
    """Raise ValueError if category is not in the allowed list.

    Args:
        category: The category string to validate.

    Raises:
        ValueError: If category is not one of the six allowed values.
    """
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(
            f"'{category}' is not a valid category. "
            f"Choose from: {', '.join(ALLOWED_CATEGORIES)}."
        )


def validate_date_not_future(date_str: str) -> None:
    """Raise ValueError if the date is in the future.

    Args:
        date_str: ISO format date string (YYYY-MM-DD).

    Raises:
        ValueError: If the date is after today.
    """
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(
            f"'{date_str}' is not a valid date. Please use YYYY-MM-DD format."
        )
    if parsed > date.today():
        raise ValueError(
            "Expense date cannot be in the future. Please enter today's date or an earlier date."
        )


def validate_description_length(text: str, max_len: int = 100) -> None:
    """Raise ValueError if the description is too long.

    Args:
        text:    The description text to validate.
        max_len: Maximum allowed character count (default 100).

    Raises:
        ValueError: If len(text) > max_len.
    """
    if len(text) > max_len:
        raise ValueError(
            f"Description is too long ({len(text)} characters). "
            f"Please keep it under {max_len} characters."
        )


def validate_interest_rate(rate: float) -> None:
    """Raise ValueError if the interest rate is out of the valid range.

    Args:
        rate: Annual interest rate as a percentage (e.g. 8.5 for 8.5%).

    Raises:
        ValueError: If rate < 0 or rate > 100.
    """
    try:
        rate = float(rate)
    except (TypeError, ValueError):
        raise ValueError("Interest rate must be a number.")
    if rate < 0:
        raise ValueError("Interest rate cannot be negative.")
    if rate > 100:
        raise ValueError("Interest rate cannot exceed 100%.")
