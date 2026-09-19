"""
services/scholarship_advisor.py

Provides scholarship data loading and eligibility-based matching for the
Student Financial Literacy Assistant.

Matching is done through keyword overlap and numeric eligibility checks.
No external APIs are used — all data comes from data/scholarships.json.
"""

import json
import os
from typing import Optional

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_SCHOLARSHIPS_FILE = os.path.join(_DATA_DIR, "scholarships.json")

# Words to ignore when building a keyword set from the student's input.
_STOP_WORDS: set[str] = {
    "i", "am", "a", "an", "the", "and", "or", "for", "in", "of",
    "to", "is", "my", "me", "we", "are", "from", "with", "have",
    "has", "been", "be", "as", "at", "on", "it", "this", "that",
    "do", "not", "can", "also", "very", "just",
}

# Cache the scholarship list.
_scholarships_cache: Optional[list[dict]] = None


def _load_scholarships() -> list[dict]:
    """Load and cache scholarship records from scholarships.json."""
    global _scholarships_cache
    if _scholarships_cache is not None:
        return _scholarships_cache
    try:
        with open(_SCHOLARSHIPS_FILE, "r", encoding="utf-8") as f:
            _scholarships_cache = json.load(f)
    except (IOError, json.JSONDecodeError):
        _scholarships_cache = []
    return _scholarships_cache


def get_all_scholarships() -> list[dict]:
    """Return the full list of scholarship records.

    Returns:
        List of scholarship dicts. Empty list if file is unavailable.
    """
    return list(_load_scholarships())


def match_scholarships(
    percentage: float,
    family_income: float,
    keywords_input: str,
) -> list[dict]:
    """Return scholarships that match the student's eligibility criteria.

    Matching rules (ALL of the following must hold):
    1. Student's percentage >= scholarship's min_percentage.
    2. Student's family income <= scholarship's max_family_income.
    3. (Optional) At least one meaningful word from keywords_input appears
       in the scholarship's eligibility_keywords list.
       If keywords_input is empty, rule 3 is skipped.

    Results are sorted: scholarships with more keyword matches appear first.

    Args:
        percentage:     Student's academic percentage (0–100).
        family_income:  Annual family income in rupees.
        keywords_input: Free-text description, e.g. "engineering merit girl".

    Returns:
        Filtered and sorted list of matching scholarship dicts.
    """
    scholarships = _load_scholarships()

    # Build a set of meaningful query words from the student's input.
    query_words: set[str] = set()
    if keywords_input.strip():
        for word in keywords_input.lower().split():
            cleaned = word.strip(".,!?;:")
            if cleaned and cleaned not in _STOP_WORDS:
                query_words.add(cleaned)

    results: list[tuple[int, dict]] = []

    for s in scholarships:
        min_pct: float = float(s.get("min_percentage", 0))
        max_income: float = float(s.get("max_family_income", 999_999_999))

        # Numeric eligibility checks.
        if percentage < min_pct:
            continue
        if family_income > max_income:
            continue

        # Keyword check (only if the student provided keywords).
        eligibility_kws: list[str] = [k.lower() for k in s.get("eligibility_keywords", [])]
        if query_words:
            match_count = sum(1 for w in query_words if w in eligibility_kws)
            if match_count == 0:
                continue
        else:
            match_count = 0

        results.append((match_count, s))

    # Sort: higher match_count first; then alphabetically by name for stability.
    results.sort(key=lambda x: (-x[0], x[1].get("name", "")))
    return [s for _, s in results]


def search_by_text(query: str) -> list[dict]:
    """Search scholarships by keyword text only (no numeric filters).

    This is a convenience wrapper used when the student wants a quick
    text-only search without entering their percentage or income.

    Args:
        query: Free-text search string.

    Returns:
        Filtered and sorted list of matching scholarship dicts.
    """
    return match_scholarships(
        percentage=0.0,
        family_income=999_999_999,
        keywords_input=query,
    )
