"""
utils/persistence.py

Handles loading and saving the student's session data (budget + expenses)
to a local JSON file called session_data.json.

Data is stored in this format:
{
    "budget": {"income": 30000.0, "budget_limit": 20000.0},
    "expenses": [
        {"amount": 500.0, "category": "Food", "description": "Lunch", "date": "2025-07-10"}
    ]
}
"""

import json
import os
from typing import Optional

# The JSON file is placed in the same directory as this utils module's parent.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FILE = os.path.join(_BASE_DIR, "session_data.json")


def save_session(budget_dict: Optional[dict], expense_list: list[dict]) -> None:
    """Write budget and expense data to session_data.json.

    Args:
        budget_dict:  Serialised Budget dict, or None if not set.
        expense_list: List of serialised Expense dicts.
    """
    data = {
        "budget": budget_dict,
        "expenses": expense_list,
    }
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        # Print to console so a developer can see it; the app won't crash.
        print(f"[persistence] Warning: Could not save session data — {e}")


def load_session() -> tuple[Optional[dict], list[dict]]:
    """Load budget and expense data from session_data.json.

    Returns:
        A tuple of (budget_dict, expense_list).
        budget_dict is None if the file does not exist or has no budget.
        expense_list is an empty list if there are no stored expenses.
    """
    if not os.path.exists(SESSION_FILE):
        return None, []

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        budget_dict = data.get("budget", None)
        expense_list = data.get("expenses", [])
        if not isinstance(expense_list, list):
            expense_list = []
        return budget_dict, expense_list
    except (IOError, json.JSONDecodeError) as e:
        print(f"[persistence] Warning: Could not load session data — {e}")
        return None, []
