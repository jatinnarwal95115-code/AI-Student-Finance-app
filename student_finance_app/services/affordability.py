"""
services/affordability.py

Provides the "Can I Afford This?" calculation for the Student Financial
Literacy Assistant.

This module is stateless — it only receives numbers and returns a plain-
English response string. It does not import any other service or model.
"""

_DISCLAIMER = (
    "\n\n⚠️ Note: This is a simple budget-based calculation for educational purposes only. "
    "It is not professional financial advice."
)


def check_affordability(item_name: str, price: float, remaining_budget: float) -> str:
    """Compare a purchase price against the remaining budget and return
    a plain-English explanation.

    Response tiers:
    - remaining_budget <= 0          → no budget left at all.
    - price <= remaining_budget      → purchase fits comfortably.
    - price <= remaining_budget * 1.2 → slightly over budget (within 20%).
    - price > remaining_budget * 1.2  → significantly over budget.

    Args:
        item_name:        Name or description of the planned purchase.
        price:            Cost of the item (must be > 0; validation done by caller).
        remaining_budget: How much budget is left (may be 0 or negative).

    Returns:
        A user-friendly explanation string with a disclaimer appended.
    """
    item_label = item_name.strip() if item_name.strip() else "this item"
    price_str = f"₹{price:,.2f}"
    remaining_str = f"₹{remaining_budget:,.2f}"

    if remaining_budget <= 0:
        message = (
            f"❌ You currently have no remaining budget (₹{remaining_budget:,.2f}).\n\n"
            f"You cannot afford **{item_label}** ({price_str}) right now. "
            "Consider reviewing your expenses or adjusting your budget."
        )

    elif price <= remaining_budget:
        message = (
            f"✅ Yes, you can likely afford **{item_label}**.\n\n"
            f"**Item price:** {price_str}\n"
            f"**Your remaining budget:** {remaining_str}\n\n"
            f"This purchase fits within your current budget. After buying it, "
            f"you would have **₹{remaining_budget - price:,.2f}** remaining."
        )

    elif price <= remaining_budget * 1.2:
        over_by = price - remaining_budget
        message = (
            f"⚠️ **{item_label}** is slightly over your remaining budget.\n\n"
            f"**Item price:** {price_str}\n"
            f"**Your remaining budget:** {remaining_str}\n"
            f"**Over by:** ₹{over_by:,.2f}\n\n"
            "This purchase exceeds your current budget by a small amount. "
            "You may want to wait until next month or reduce spending in another category."
        )

    else:
        over_by = price - remaining_budget
        message = (
            f"❌ **{item_label}** significantly exceeds your remaining budget.\n\n"
            f"**Item price:** {price_str}\n"
            f"**Your remaining budget:** {remaining_str}\n"
            f"**Over by:** ₹{over_by:,.2f}\n\n"
            "Buying this item would put a significant strain on your budget. "
            "Consider saving up over a few months before making this purchase."
        )

    return message + _DISCLAIMER
