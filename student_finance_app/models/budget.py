"""
models/budget.py

Defines the Budget dataclass that holds the student's income and
spending limit, plus computed helper methods.
"""

from dataclasses import dataclass


@dataclass
class Budget:
    """
    Holds the student's monthly financial baseline.

    Attributes:
        income:       Monthly income or available money (must be > 0).
        budget_limit: Maximum planned monthly spending (must be > 0).
    """

    income: float
    budget_limit: float

    # ------------------------------------------------------------------
    # Computed helpers
    # ------------------------------------------------------------------

    def get_remaining_budget(self, total_spent: float) -> float:
        """Return how much budget is left after spending.

        Args:
            total_spent: Sum of all recorded expenses.

        Returns:
            Remaining budget (may be negative if over budget).
        """
        return self.budget_limit - total_spent

    def is_over_budget(self, total_spent: float) -> bool:
        """Return True if total spending has exceeded the budget limit.

        Args:
            total_spent: Sum of all recorded expenses.
        """
        return total_spent > self.budget_limit

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise the budget to a plain dictionary for JSON storage."""
        return {
            "income": self.income,
            "budget_limit": self.budget_limit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        """Deserialise a Budget from a dictionary (loaded from JSON)."""
        return cls(
            income=float(data["income"]),
            budget_limit=float(data["budget_limit"]),
        )
