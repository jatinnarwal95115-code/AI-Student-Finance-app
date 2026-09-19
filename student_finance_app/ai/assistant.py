"""
ai/assistant.py

A simple keyword-based financial literacy assistant.

This module has zero knowledge of the student's personal data (budget,
expenses, income). It only receives a question string and returns a
beginner-friendly educational explanation.

No external API, no machine learning. All answers are stored as a plain
Python dictionary. This makes it easy for a beginner to read and extend.
"""

from typing import Optional

_DISCLAIMER = (
    "\n\n*This explanation is for educational purposes only and is not "
    "professional financial advice.*"
)

# -----------------------------------------------------------------------
# Knowledge base
# Each entry has:
#   keywords  – list of words that trigger this topic
#   response  – the educational explanation to return
# -----------------------------------------------------------------------
_KNOWLEDGE_BASE: list[dict] = [
    {
        "keywords": ["budget", "budgeting", "spending limit", "spending plan", "monthly plan"],
        "response": (
            "**Budgeting** means deciding in advance how you will spend your money.\n\n"
            "You start by listing your monthly income (money coming in) and then plan "
            "how much you will spend on different things like food, travel, and entertainment.\n\n"
            "A simple rule to follow is the **50-30-20 rule**:\n"
            "- **50%** of your income on needs (food, rent, transport)\n"
            "- **30%** on wants (entertainment, shopping)\n"
            "- **20%** on savings\n\n"
            "Even if you cannot follow this exactly, just having a plan helps you avoid "
            "running out of money before the month ends."
        ),
    },
    {
        "keywords": ["saving", "savings", "save money", "save", "emergency fund"],
        "response": (
            "**Saving** means setting aside a part of your money regularly instead of spending it all.\n\n"
            "Why save?\n"
            "- To handle unexpected expenses (medical bills, phone repairs).\n"
            "- To reach a future goal (laptop, course, travel).\n"
            "- To build financial security over time.\n\n"
            "A good starting goal is to save at least **10%** of whatever you receive each month. "
            "Even saving ₹200–₹500 per month adds up over a year.\n\n"
            "Keep your savings separate from your spending money so you are not tempted to use it."
        ),
    },
    {
        "keywords": ["expense", "expenses", "spending", "spend", "track expenses", "where money goes"],
        "response": (
            "An **expense** is any money you spend.\n\n"
            "Tracking your expenses means writing down (or recording in an app) every time you "
            "spend money — how much, on what, and when.\n\n"
            "Why track expenses?\n"
            "- You can see where your money is actually going.\n"
            "- You can identify areas where you are overspending.\n"
            "- It helps you stick to your budget.\n\n"
            "Common expense categories for students: Food, Travel, Shopping, Education, Entertainment."
        ),
    },
    {
        "keywords": ["interest", "interest rate", "rate of interest"],
        "response": (
            "**Interest** is the extra money you pay when you borrow money, or the extra money "
            "you earn when you save or invest.\n\n"
            "**Borrowing interest:** If you take a loan of ₹1,00,000 at 10% annual interest, "
            "you pay ₹10,000 extra per year just for borrowing that money.\n\n"
            "**Saving interest:** If you keep ₹10,000 in a savings account at 4% annual interest, "
            "the bank pays you ₹400 extra after one year.\n\n"
            "The **interest rate** is usually shown as a percentage per year (annual rate). "
            "Higher interest rate on a loan = more money you pay back."
        ),
    },
    {
        "keywords": ["loan", "borrow", "borrowing", "debt", "credit"],
        "response": (
            "A **loan** is money you borrow from a bank or lender with a promise to pay it back "
            "over time, usually with interest.\n\n"
            "Key things to understand about loans:\n"
            "- **Principal** – the original amount you borrow.\n"
            "- **Interest** – extra money you pay for borrowing.\n"
            "- **EMI** – the fixed monthly payment you make to repay the loan.\n"
            "- **Tenure** – the total time to repay (e.g., 24 months = 2 years).\n\n"
            "Before taking a loan, always check:\n"
            "1. Can you afford the monthly EMI?\n"
            "2. What is the total amount you will repay?\n"
            "3. Are there any extra charges or fees?"
        ),
    },
    {
        "keywords": ["emi", "equated monthly", "monthly instalment", "installment"],
        "response": (
            "**EMI** stands for Equated Monthly Instalment.\n\n"
            "It is the fixed amount you pay to the bank every single month until your loan is "
            "fully repaid.\n\n"
            "Each EMI payment has two parts:\n"
            "- A part that reduces your **principal** (original loan amount).\n"
            "- A part that pays the **interest** for that month.\n\n"
            "In the early months, most of your EMI goes toward interest. Over time, more of "
            "it goes toward reducing the principal.\n\n"
            "**Example:** If you borrow ₹60,000 at 12% annual interest for 2 years (24 months), "
            "your EMI will be approximately ₹2,825 per month."
        ),
    },
    {
        "keywords": ["scholarship", "scholarships", "financial aid", "grant", "fellowship"],
        "response": (
            "A **scholarship** is money given to a student to help pay for education. "
            "Unlike a loan, you do **not** have to repay a scholarship.\n\n"
            "Scholarships are usually awarded based on:\n"
            "- **Merit** – your academic performance.\n"
            "- **Need** – your family's financial situation.\n"
            "- **Category** – SC, ST, OBC, minority, etc.\n"
            "- **Field of study** – engineering, science, arts, etc.\n\n"
            "Tips for finding scholarships:\n"
            "- Check the National Scholarship Portal (scholarships.gov.in).\n"
            "- Ask your college's financial aid office.\n"
            "- Look for state government scholarships in your region."
        ),
    },
    {
        "keywords": ["needs", "wants", "needs vs wants", "need vs want", "necessity", "necessary"],
        "response": (
            "Understanding the difference between **needs** and **wants** is one of the most "
            "important money skills.\n\n"
            "**Needs** are things you must have to survive and function:\n"
            "- Food, water, shelter, basic clothing, transport to college.\n\n"
            "**Wants** are things you would like to have but can live without:\n"
            "- New phone, branded clothes, eating at restaurants, streaming subscriptions.\n\n"
            "When money is tight, always cover your **needs first**. Then, if money is left, "
            "consider your wants.\n\n"
            "A simple question to ask before spending: *'Do I need this, or do I just want it?'"
        ),
    },
    {
        "keywords": ["inflation", "price rise", "prices rising", "cost of living"],
        "response": (
            "**Inflation** means prices of goods and services rise over time.\n\n"
            "For example, if your monthly grocery bill is ₹3,000 today, in 5 years it might "
            "cost ₹3,500–₹4,000 for the same items — even if you buy the same things.\n\n"
            "Inflation affects students because:\n"
            "- Your college fees may increase each year.\n"
            "- Food and transport costs go up.\n\n"
            "To protect against inflation, try to grow your savings at a rate that beats inflation "
            "(e.g., fixed deposits or government savings schemes rather than keeping cash at home)."
        ),
    },
    {
        "keywords": ["credit card", "credit cards", "card debt"],
        "response": (
            "A **credit card** lets you buy things now and pay for them later.\n\n"
            "Used wisely, a credit card can be helpful (rewards, emergency use). "
            "Used carelessly, it can lead to serious debt.\n\n"
            "Key rules for students with credit cards:\n"
            "1. **Pay the full balance every month** — not just the minimum amount.\n"
            "2. Credit card interest rates are very high (24–42% per year) if you carry a balance.\n"
            "3. Never spend more on a credit card than you can actually afford to pay back.\n"
            "4. Treat a credit card like a debit card — only spend what you already have."
        ),
    },
]

_FALLBACK_RESPONSE = (
    "I don't have a specific answer for that question yet. "
    "Try asking about one of these topics:\n\n"
    "- **Budgeting** — how to plan your spending\n"
    "- **Saving** — how to save money\n"
    "- **Expenses** — how to track what you spend\n"
    "- **Interest** — what interest means\n"
    "- **Loans** — how loans work\n"
    "- **EMI** — what EMI means\n"
    "- **Scholarships** — how to find financial aid\n"
    "- **Needs vs Wants** — how to prioritise spending"
)


def _find_best_match(question: str) -> Optional[dict]:
    """Find the knowledge-base entry with the most keyword matches.

    Args:
        question: The student's question (any free text).

    Returns:
        The best-matching knowledge-base entry dict, or None if no match.
    """
    question_lower = question.lower()
    best_entry: Optional[dict] = None
    best_count: int = 0

    for entry in _KNOWLEDGE_BASE:
        count = sum(1 for kw in entry["keywords"] if kw in question_lower)
        if count > best_count:
            best_count = count
            best_entry = entry

    return best_entry if best_count > 0 else None


def get_response(question: str) -> str:
    """Return a beginner-friendly educational response to the question.

    The function uses keyword matching to find the most relevant topic.
    If no keyword matches, a friendly fallback is returned.

    A disclaimer is appended to every response.

    Args:
        question: The student's free-text question.

    Returns:
        An educational response string with a disclaimer.
    """
    if not question or not question.strip():
        return (
            "Please type a question! For example: 'What is an EMI?' or 'How do I budget?'"
            + _DISCLAIMER
        )

    match = _find_best_match(question)
    if match:
        return match["response"] + _DISCLAIMER
    return _FALLBACK_RESPONSE + _DISCLAIMER


def get_suggested_questions() -> list[str]:
    """Return a list of starter questions to show in the UI."""
    return [
        "What is a budget?",
        "How do I save money as a student?",
        "What is an EMI?",
        "What is interest?",
        "How do loans work?",
        "What are scholarships?",
        "What is the difference between needs and wants?",
        "What is inflation?",
    ]
