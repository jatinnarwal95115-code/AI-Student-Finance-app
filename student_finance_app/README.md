# Student Financial Literacy Assistant

A beginner-friendly Python + Streamlit application that helps college students understand and manage personal finances.

## Features

1. **Budget Overview** — Set income and monthly budget; track remaining budget
2. **Expense Tracker** — Add expenses by category, description and date
3. **Spending Analyzer** — Category-wise breakdown and spending summaries
4. **Can I Afford This?** — Simple budget-based purchase check
5. **Loan Explainer** — EMI calculator and plain-English loan concept explanations
6. **Scholarship Advisor** — Match scholarships based on eligibility criteria
7. **Financial Literacy** — Educational Q&A assistant for basic financial concepts

## Installation

```bash
cd student_finance_app
pip install -r requirements.txt
```

## Running the Application

```bash
cd student_finance_app
streamlit run app.py
```

## Running Tests

```bash
cd student_finance_app
pytest tests/ -v
```

## Project Structure

```
student_finance_app/
├── app.py                      # Streamlit UI entry point
├── models/
│   ├── expense.py              # Expense dataclass
│   └── budget.py               # Budget dataclass
├── services/
│   ├── expense_tracker.py      # Expense management and calculations
│   ├── affordability.py        # "Can I Afford This?" logic
│   ├── loan_explainer.py       # EMI formula and loan concept lookup
│   └── scholarship_advisor.py  # Scholarship matching logic
├── ai/
│   └── assistant.py            # Keyword-based financial literacy Q&A
├── data/
│   ├── scholarships.json       # Sample scholarship records
│   └── loan_concepts.json      # Loan term definitions
├── utils/
│   ├── validators.py           # Input validation functions
│   └── persistence.py          # JSON load/save for session data
├── tests/                      # pytest unit tests
├── session_data.json           # Auto-created; stores budget and expenses
└── requirements.txt
```

## Disclaimer

This application is intended for financial-literacy education only.
- Budget calculations are based on information entered by the user.
- Loan EMI calculations are estimates.
- Scholarship matching is based only on the sample data stored in this application.
- This application is **not** a substitute for professional financial advice.
