"""
services/expense_tracker.py

Manages the student's list of expenses and provides all spending calculations.
This class is completely independent of Streamlit — it is pure business logic.
"""

from models.expense import Expense, ALLOWED_CATEGORIES

try:
    import pandas as pd
    _PANDAS_AVAILABLE = True
except ImportError:
    _PANDAS_AVAILABLE = False


class ExpenseTracker:
    """
    Owns and manages the in-memory list of Expense objects.

    Responsibilities:
    - Add expenses.
    - Return the full list of expenses.
    - Calculate totals and category breakdowns.
    - Provide serialisation helpers for persistence.
    """

    def __init__(self) -> None:
        self._expenses: list[Expense] = []

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_expense(self, expense: Expense) -> None:
        """Append a validated Expense to the internal list.

        Args:
            expense: An already-validated Expense object.
        """
        self._expenses.append(expense)

    def clear(self) -> None:
        """Remove all recorded expenses."""
        self._expenses.clear()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_all_expenses(self) -> list[Expense]:
        """Return a copy of the full expense list."""
        return list(self._expenses)

    def get_total_spending(self) -> float:
        """Return the sum of all expense amounts.

        Returns:
            0.0 if no expenses have been recorded.
        """
        return sum(e.amount for e in self._expenses)

    def get_category_breakdown(self) -> dict[str, float]:
        """Return a dict mapping each category to its total spending.

        Categories with zero spending are included with a value of 0.0
        so the UI always has a complete picture.

        Returns:
            e.g. {"Food": 800.0, "Travel": 0.0, ...}
        """
        totals: dict[str, float] = {cat: 0.0 for cat in ALLOWED_CATEGORIES}
        for expense in self._expenses:
            if expense.category in totals:
                totals[expense.category] += expense.amount
        return totals

    def get_top_category(self) -> str | None:
        """Return the category with the highest total spending.

        Returns:
            The category name, or None if there are no expenses.
        """
        if not self._expenses:
            return None
        breakdown = self.get_category_breakdown()
        # Only consider categories that have been spent in.
        active = {k: v for k, v in breakdown.items() if v > 0}
        if not active:
            return None
        return max(active, key=lambda k: active[k])

    def get_category_percentage(self) -> dict[str, float]:
        """Return each category's spending as a percentage of total spending.

        Returns:
            e.g. {"Food": 45.0, "Travel": 20.0, ...} or all zeros if no expenses.
        """
        total = self.get_total_spending()
        if total == 0:
            return {cat: 0.0 for cat in ALLOWED_CATEGORIES}
        breakdown = self.get_category_breakdown()
        return {cat: round((amt / total) * 100, 1) for cat, amt in breakdown.items()}

    # ------------------------------------------------------------------
    # Serialisation / Deserialisation
    # ------------------------------------------------------------------

    def to_dict_list(self) -> list[dict]:
        """Convert all expenses to a list of dicts for JSON serialisation."""
        return [e.to_dict() for e in self._expenses]

    def from_dict_list(self, data: list[dict]) -> None:
        """Populate the expense list from a list of dicts (loaded from JSON).

        Replaces any existing expenses.

        Args:
            data: List of expense dicts as loaded from JSON.
        """
        self._expenses = [Expense.from_dict(d) for d in data]

    # ------------------------------------------------------------------
    # Pandas DataFrame helper
    # ------------------------------------------------------------------

    def as_dataframe(self):
        """Return expenses as a Pandas DataFrame for Streamlit display.

        Returns:
            A DataFrame with columns: Date, Category, Description, Amount (₹).
            Returns an empty DataFrame with those columns if no expenses.
        """
        if not _PANDAS_AVAILABLE:
            raise ImportError("pandas is required for as_dataframe(). Run: pip install pandas")

        columns = ["Date", "Category", "Description", "Amount (₹)"]
        if not self._expenses:
            return pd.DataFrame(columns=columns)

        rows = [
            {
                "Date": e.date,
                "Category": e.category,
                "Description": e.description,
                "Amount (₹)": e.amount,
            }
            for e in self._expenses
        ]
        df = pd.DataFrame(rows, columns=columns)
        return df.sort_values("Date", ascending=False).reset_index(drop=True)
