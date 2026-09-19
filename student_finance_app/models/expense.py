"""
models/expense.py

Defines the Expense dataclass and the list of allowed categories.
"""

from dataclasses import dataclass, field
from datetime import date

# The six allowed expense categories.
ALLOWED_CATEGORIES: list[str] = [
    "Food",
    "Travel",
    "Shopping",
    "Education",
    "Entertainment",
    "Other",
]


@dataclass
class Expense:
    """
    Represents a single recorded expense.

    Attributes:
        amount:      The expense amount (must be > 0).
        category:    One of the six allowed categories.
        description: Short optional label for the expense.
        date:        The date the expense was incurred (ISO string YYYY-MM-DD).
    """

    amount: float
    category: str
    description: str = ""
    date: str = field(default_factory=lambda: date.today().isoformat())

    def to_dict(self) -> dict:
        """Serialise the expense to a plain dictionary for JSON storage."""
        return {
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        """Deserialise an expense from a dictionary (loaded from JSON)."""
        return cls(
            amount=float(data["amount"]),
            category=data["category"],
            description=data.get("description", ""),
            date=data.get("date", date.today().isoformat()),
        )
