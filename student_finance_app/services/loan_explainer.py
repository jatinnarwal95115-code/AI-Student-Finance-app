"""
services/loan_explainer.py

Provides EMI calculations and loan concept lookups for the Student
Financial Literacy Assistant.

All functions in this module are stateless. No Streamlit imports.
"""

import json
import math
import os
from typing import Optional

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_CONCEPTS_FILE = os.path.join(_DATA_DIR, "loan_concepts.json")

# Cache the concepts list so the file is read only once.
_concepts_cache: Optional[list[dict]] = None


def _load_concepts() -> list[dict]:
    """Load and cache loan concept definitions from loan_concepts.json."""
    global _concepts_cache
    if _concepts_cache is not None:
        return _concepts_cache
    try:
        with open(_CONCEPTS_FILE, "r", encoding="utf-8") as f:
            _concepts_cache = json.load(f)
    except (IOError, json.JSONDecodeError):
        _concepts_cache = []
    return _concepts_cache


def get_all_concepts() -> list[dict]:
    """Return all loan concept records.

    Returns:
        List of dicts, each with keys: term, definition, example.
    """
    return _load_concepts()


def get_concept(term: str) -> Optional[dict]:
    """Look up a loan concept by its term name (case-insensitive).

    Args:
        term: The concept name, e.g. "EMI", "Principal".

    Returns:
        The matching concept dict, or None if not found.
    """
    for concept in _load_concepts():
        if concept.get("term", "").lower() == term.lower():
            return concept
    return None


def calculate_emi(principal: float, annual_rate_pct: float, months: int) -> float:
    """Calculate the monthly EMI using the standard reducing-balance formula.

    Formula:
        r   = (annual_rate_pct / 100) / 12        (monthly rate as decimal)
        EMI = P * r * (1+r)^n / ((1+r)^n - 1)

    Special case:
        If annual_rate_pct == 0, EMI = principal / months  (no interest).

    Args:
        principal:       Original loan amount (must be > 0).
        annual_rate_pct: Annual interest rate as a percentage (0 – 100).
        months:          Repayment period in months (must be >= 1).

    Returns:
        Monthly EMI amount rounded to two decimal places.

    Raises:
        ValueError: If principal <= 0 or months < 1.
    """
    if principal <= 0:
        raise ValueError("Principal must be greater than zero.")
    if months < 1:
        raise ValueError("Repayment period must be at least 1 month.")

    if annual_rate_pct == 0:
        return round(principal / months, 2)

    r = (annual_rate_pct / 100) / 12
    emi = principal * r * math.pow(1 + r, months) / (math.pow(1 + r, months) - 1)
    return round(emi, 2)


def get_repayment_summary(principal: float, annual_rate_pct: float, months: int) -> dict:
    """Return a summary of total repayment and total interest.

    Args:
        principal:       Original loan amount.
        annual_rate_pct: Annual interest rate as a percentage.
        months:          Repayment period in months.

    Returns:
        Dict with keys:
            emi            – monthly EMI amount
            total_payable  – EMI * months
            total_interest – total_payable - principal
    """
    emi = calculate_emi(principal, annual_rate_pct, months)
    total_payable = round(emi * months, 2)
    total_interest = round(total_payable - principal, 2)
    return {
        "emi": emi,
        "total_payable": total_payable,
        "total_interest": total_interest,
    }
