"""
app.py — Student Financial Literacy Assistant

Streamlit entry point.  All business logic lives in services/, models/,
ai/, and utils/.  This file only handles UI layout and session state.

Run with:
    streamlit run app.py
"""

import sys
import os

# Ensure the project root is on the path so relative imports work correctly
# whether the app is launched from the project root or from elsewhere.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date

import streamlit as st

from models.budget import Budget
from models.expense import ALLOWED_CATEGORIES, Expense
from services.expense_tracker import ExpenseTracker
from services.affordability import check_affordability
from services import loan_explainer
from services import scholarship_advisor
from ai.assistant import get_response, get_suggested_questions
from utils.validators import (
    validate_positive_float,
    validate_positive_int,
    validate_budget_vs_income,
    validate_category,
    validate_date_not_future,
    validate_description_length,
    validate_interest_rate,
)
from utils.persistence import save_session, load_session

# -----------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Student Financial Literacy Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------
# Session state initialisation (runs only once per browser session)
# -----------------------------------------------------------------------
if "tracker" not in st.session_state:
    tracker = ExpenseTracker()
    budget_dict, expense_list = load_session()
    if expense_list:
        tracker.from_dict_list(expense_list)
    st.session_state["tracker"] = tracker

if "budget" not in st.session_state:
    budget_dict, _ = load_session()
    if budget_dict:
        try:
            st.session_state["budget"] = Budget.from_dict(budget_dict)
        except (KeyError, ValueError):
            st.session_state["budget"] = None
    else:
        st.session_state["budget"] = None


def _save() -> None:
    """Convenience wrapper: persist current session state to JSON."""
    budget: Budget | None = st.session_state.get("budget")
    tracker: ExpenseTracker = st.session_state["tracker"]
    save_session(
        budget_dict=budget.to_dict() if budget else None,
        expense_list=tracker.to_dict_list(),
    )


# -----------------------------------------------------------------------
# Sidebar — set income & budget
# -----------------------------------------------------------------------
with st.sidebar:
    st.title("💰 Student Finance")
    st.caption("Financial Literacy Assistant")
    st.divider()

    st.subheader("⚙️ Set Your Budget")
    with st.form("budget_form", clear_on_submit=False):
        income_input = st.number_input(
            "Monthly Income / Available Money (₹)",
            min_value=0.0,
            step=500.0,
            format="%.2f",
            value=float(st.session_state["budget"].income)
            if st.session_state["budget"]
            else 0.0,
        )
        budget_input = st.number_input(
            "Monthly Spending Budget (₹)",
            min_value=0.0,
            step=500.0,
            format="%.2f",
            value=float(st.session_state["budget"].budget_limit)
            if st.session_state["budget"]
            else 0.0,
        )
        save_budget_btn = st.form_submit_button("💾 Save Budget", use_container_width=True)

    if save_budget_btn:
        try:
            validate_positive_float(income_input, "Monthly income")
            validate_positive_float(budget_input, "Monthly budget")
            validate_budget_vs_income(budget_input, income_input)
            st.session_state["budget"] = Budget(
                income=float(income_input),
                budget_limit=float(budget_input),
            )
            _save()
            st.success("Budget saved!")
        except ValueError as e:
            st.error(str(e))

    # Live summary in sidebar
    st.divider()
    budget: Budget | None = st.session_state.get("budget")
    tracker: ExpenseTracker = st.session_state["tracker"]
    total_spent = tracker.get_total_spending()

    if budget:
        remaining = budget.get_remaining_budget(total_spent)
        st.metric("📥 Income", f"₹{budget.income:,.2f}")
        st.metric("🎯 Budget Limit", f"₹{budget.budget_limit:,.2f}")
        st.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
        colour = "normal" if remaining >= 0 else "inverse"
        st.metric("💚 Remaining", f"₹{remaining:,.2f}", delta_color=colour)
        if budget.is_over_budget(total_spent):
            st.error("⚠️ You are over budget!")
    else:
        st.info("Set your income and budget above to get started.")

    st.divider()
    st.caption(
        "ℹ️ This app is for **educational purposes only** and does not provide "
        "professional financial advice."
    )

# -----------------------------------------------------------------------
# Main tabs
# -----------------------------------------------------------------------
(
    tab_dashboard,
    tab_expenses,
    tab_analysis,
    tab_afford,
    tab_loan,
    tab_scholarship,
    tab_literacy,
) = st.tabs([
    "🏠 Dashboard",
    "📋 Add Expense",
    "📊 Analysis",
    "🤔 Can I Afford This?",
    "🏦 Loan Explainer",
    "🎓 Scholarships",
    "📚 Financial Literacy",
])

# =======================================================================
# TAB 1 — Dashboard
# =======================================================================
with tab_dashboard:
    st.header("🏠 Budget Dashboard")

    budget: Budget | None = st.session_state.get("budget")
    tracker: ExpenseTracker = st.session_state["tracker"]
    total_spent = tracker.get_total_spending()

    if not budget:
        st.info("👈 Set your income and monthly budget in the sidebar to get started.")
    else:
        remaining = budget.get_remaining_budget(total_spent)
        pct_used = (total_spent / budget.budget_limit * 100) if budget.budget_limit > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📥 Monthly Income", f"₹{budget.income:,.2f}")
        col2.metric("🎯 Budget Limit", f"₹{budget.budget_limit:,.2f}")
        col3.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
        col4.metric(
            "💚 Remaining Budget",
            f"₹{remaining:,.2f}",
            delta=f"{remaining:+,.2f}",
            delta_color="normal" if remaining >= 0 else "inverse",
        )

        st.divider()

        # Budget usage progress bar
        st.subheader("Budget Usage")
        bar_pct = min(pct_used / 100, 1.0)
        st.progress(bar_pct, text=f"{pct_used:.1f}% of budget used")

        if budget.is_over_budget(total_spent):
            st.error(
                f"⚠️ You have exceeded your budget by ₹{abs(remaining):,.2f}. "
                "Consider reviewing your expenses."
            )
        elif pct_used >= 80:
            st.warning(
                f"⚠️ You have used {pct_used:.1f}% of your budget. "
                "Spend carefully for the rest of the month."
            )
        else:
            st.success("✅ Your spending is within your budget. Keep it up!")

        st.divider()

        # Quick expense summary
        expenses = tracker.get_all_expenses()
        if expenses:
            st.subheader("Recent Expenses")
            df = tracker.as_dataframe()
            st.dataframe(df.head(5), use_container_width=True)
            if len(expenses) > 5:
                st.caption(f"Showing 5 of {len(expenses)} expenses. Go to Add Expense tab to see all.")
        else:
            st.info("No expenses recorded yet. Go to the **Add Expense** tab to add one.")

# =======================================================================
# TAB 2 — Add Expense
# =======================================================================
with tab_expenses:
    st.header("📋 Expense Tracker")

    tracker: ExpenseTracker = st.session_state["tracker"]

    # Add expense form
    st.subheader("Add a New Expense")
    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            amount_input = st.number_input(
                "Amount (₹)", min_value=0.0, step=10.0, format="%.2f"
            )
            category_input = st.selectbox("Category", ALLOWED_CATEGORIES)
        with col_b:
            date_input = st.date_input("Date", value=date.today(), max_value=date.today())
            desc_input = st.text_input("Description (optional)", max_chars=100)

        add_btn = st.form_submit_button("➕ Add Expense", use_container_width=True)

    if add_btn:
        try:
            validate_positive_float(amount_input, "Expense amount")
            validate_category(category_input)
            validate_date_not_future(str(date_input))
            validate_description_length(desc_input)
            expense = Expense(
                amount=float(amount_input),
                category=category_input,
                description=desc_input,
                date=str(date_input),
            )
            tracker.add_expense(expense)
            _save()
            st.success(
                f"✅ Expense of ₹{amount_input:,.2f} added under **{category_input}**."
            )
        except ValueError as e:
            st.error(str(e))

    st.divider()

    # View all expenses
    st.subheader("All Recorded Expenses")
    expenses = tracker.get_all_expenses()
    if not expenses:
        st.info("No expenses recorded yet. Add one using the form above.")
    else:
        df = tracker.as_dataframe()
        st.dataframe(df, use_container_width=True)
        st.caption(
            f"**Total:** ₹{tracker.get_total_spending():,.2f} across {len(expenses)} expense(s)."
        )

        st.divider()
        if st.button("🗑️ Clear All Expenses", type="secondary"):
            tracker.clear()
            _save()
            st.success("All expenses cleared.")
            st.rerun()

# =======================================================================
# TAB 3 — Spending Analysis
# =======================================================================
with tab_analysis:
    st.header("📊 Spending Analyzer")

    tracker: ExpenseTracker = st.session_state["tracker"]
    budget: Budget | None = st.session_state.get("budget")
    total_spent = tracker.get_total_spending()

    if total_spent == 0:
        st.info("No expenses recorded yet. Add some expenses to see your spending analysis.")
    else:
        # Category breakdown
        breakdown = tracker.get_category_breakdown()
        percentages = tracker.get_category_percentage()
        top_cat = tracker.get_top_category()

        st.subheader("Category-wise Spending")
        col1, col2 = st.columns([1, 1])

        with col1:
            # Bar chart using only categories with spending > 0
            active_breakdown = {k: v for k, v in breakdown.items() if v > 0}
            if active_breakdown:
                import pandas as pd
                chart_df = pd.DataFrame(
                    {"Category": list(active_breakdown.keys()),
                     "Amount (₹)": list(active_breakdown.values())}
                ).set_index("Category")
                st.bar_chart(chart_df, use_container_width=True)

        with col2:
            # Table of all categories
            import pandas as pd
            table_data = []
            for cat in ALLOWED_CATEGORIES:
                amt = breakdown.get(cat, 0.0)
                pct = percentages.get(cat, 0.0)
                table_data.append({
                    "Category": cat,
                    "Amount (₹)": f"₹{amt:,.2f}",
                    "% of Total": f"{pct:.1f}%",
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Spending Summary")

        # Top category callout
        if top_cat:
            top_amt = breakdown[top_cat]
            top_pct = percentages[top_cat]
            st.info(
                f"📌 **Highest spending category:** {top_cat} — "
                f"₹{top_amt:,.2f} ({top_pct:.1f}% of total spending)"
            )

        # Simple summary sentences
        for cat in ALLOWED_CATEGORIES:
            amt = breakdown.get(cat, 0.0)
            pct = percentages.get(cat, 0.0)
            if amt > 0:
                st.write(f"• You spent **₹{amt:,.2f}** on **{cat}** ({pct:.1f}% of your spending).")

        if budget:
            remaining = budget.get_remaining_budget(total_spent)
            pct_used = (total_spent / budget.budget_limit * 100) if budget.budget_limit > 0 else 0
            st.divider()
            st.subheader("Budget vs Spending")
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Budget Limit", f"₹{budget.budget_limit:,.2f}")
            col_b.metric("Total Spent", f"₹{total_spent:,.2f}")
            col_c.metric("Remaining", f"₹{remaining:,.2f}")
            st.progress(
                min(pct_used / 100, 1.0),
                text=f"{pct_used:.1f}% of budget used"
            )

# =======================================================================
# TAB 4 — Can I Afford This?
# =======================================================================
with tab_afford:
    st.header("🤔 Can I Afford This?")
    st.write(
        "Enter the name and price of something you want to buy. "
        "The assistant will compare it to your remaining budget."
    )
    st.caption(
        "⚠️ This is a simple budget-based calculation, not professional financial advice."
    )
    st.divider()

    budget: Budget | None = st.session_state.get("budget")
    tracker: ExpenseTracker = st.session_state["tracker"]

    if not budget:
        st.warning("Please set your income and budget in the sidebar first.")
    else:
        total_spent = tracker.get_total_spending()
        remaining = budget.get_remaining_budget(total_spent)

        with st.form("afford_form"):
            item_name = st.text_input("What do you want to buy?", placeholder="e.g. New headphones")
            item_price = st.number_input(
                "Price (₹)", min_value=0.0, step=50.0, format="%.2f"
            )
            check_btn = st.form_submit_button("🔍 Check Affordability", use_container_width=True)

        if check_btn:
            try:
                validate_positive_float(item_price, "Item price")
                response = check_affordability(item_name, float(item_price), remaining)
                st.markdown(response)
            except ValueError as e:
                st.error(str(e))

        st.divider()
        col1, col2 = st.columns(2)
        col1.metric("Your Remaining Budget", f"₹{remaining:,.2f}")
        col2.metric("Total Spent This Month", f"₹{total_spent:,.2f}")

# =======================================================================
# TAB 5 — Loan Explainer
# =======================================================================
with tab_loan:
    st.header("🏦 Loan Explainer")
    st.write(
        "Learn about loan concepts and calculate an estimated monthly EMI "
        "(Equated Monthly Instalment)."
    )
    st.caption("⚠️ All calculations are **estimates** for educational purposes only.")
    st.divider()

    # Concept selector
    st.subheader("📖 Learn a Loan Concept")
    concepts = loan_explainer.get_all_concepts()
    if concepts:
        term_names = [c["term"] for c in concepts]
        selected_term = st.selectbox("Choose a concept to learn about:", term_names)
        concept = loan_explainer.get_concept(selected_term)
        if concept:
            st.markdown(f"### {concept['term']}")
            st.markdown(concept["definition"])
            st.info(f"**Example:** {concept['example']}")
    else:
        st.warning("Loan concept data is unavailable.")

    st.divider()

    # EMI calculator
    st.subheader("🧮 EMI Calculator")
    with st.form("emi_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            principal_input = st.number_input(
                "Loan Amount (₹)", min_value=0.0, step=1000.0, format="%.2f"
            )
        with col2:
            rate_input = st.number_input(
                "Annual Interest Rate (%)", min_value=0.0, max_value=100.0,
                step=0.1, format="%.2f"
            )
        with col3:
            months_input = st.number_input(
                "Loan Duration (months)", min_value=1, max_value=360, step=1, value=12
            )
        calc_btn = st.form_submit_button("📐 Calculate EMI", use_container_width=True)

    if calc_btn:
        try:
            validate_positive_float(principal_input, "Loan amount")
            validate_interest_rate(rate_input)
            validate_positive_int(months_input, "Loan duration")
            summary = loan_explainer.get_repayment_summary(
                principal=float(principal_input),
                annual_rate_pct=float(rate_input),
                months=int(months_input),
            )
            st.success("EMI calculated successfully!")
            r1, r2, r3 = st.columns(3)
            r1.metric("📅 Monthly EMI", f"₹{summary['emi']:,.2f}")
            r2.metric("💰 Total Payable", f"₹{summary['total_payable']:,.2f}")
            r3.metric("📈 Total Interest", f"₹{summary['total_interest']:,.2f}")
            st.caption(
                f"If you borrow ₹{principal_input:,.2f} at {rate_input}% annual interest "
                f"for {months_input} months, you will pay approximately ₹{summary['emi']:,.2f} "
                f"every month. In total you will repay ₹{summary['total_payable']:,.2f} "
                f"(₹{summary['total_interest']:,.2f} as interest)."
            )
            st.caption("*This is an estimate. Actual EMI may vary based on your lender's terms.*")
        except ValueError as e:
            st.error(str(e))

# =======================================================================
# TAB 6 — Scholarship Advisor
# =======================================================================
with tab_scholarship:
    st.header("🎓 Scholarship Advisor")
    st.write(
        "Enter your basic eligibility details below to find scholarships from our "
        "sample dataset that may match your profile."
    )
    st.caption(
        "⚠️ Scholarship information is based on sample data stored in this application only. "
        "Always verify details directly with the scholarship provider before applying."
    )
    st.divider()

    with st.form("scholarship_form"):
        col1, col2 = st.columns(2)
        with col1:
            pct_input = st.number_input(
                "Your Academic Percentage (%)", min_value=0.0, max_value=100.0,
                step=0.5, format="%.1f", value=75.0
            )
            income_input_s = st.number_input(
                "Annual Family Income (₹)", min_value=0.0,
                step=10000.0, format="%.0f", value=300000.0
            )
        with col2:
            keywords_input = st.text_area(
                "Describe your situation or field of study",
                placeholder="e.g. engineering merit undergraduate, or SC student postgraduate",
                height=100,
            )
        search_btn = st.form_submit_button("🔍 Find Scholarships", use_container_width=True)

    if search_btn:
        try:
            validate_positive_float(pct_input + 0.001, "Academic percentage")  # allow 0
        except ValueError:
            pass  # percentage 0 is fine here — allow any value
        results = scholarship_advisor.match_scholarships(
            percentage=float(pct_input),
            family_income=float(income_input_s),
            keywords_input=keywords_input,
        )
        st.divider()
        if results:
            st.success(f"Found **{len(results)}** matching scholarship(s).")
            for s in results:
                with st.expander(f"🏅 {s['name']} — {s.get('amount', 'N/A')}"):
                    st.markdown(f"**Description:** {s.get('description', '')}")
                    st.markdown(f"**Eligibility:** {', '.join(s.get('eligibility_keywords', []))}")
                    st.markdown(f"**Minimum Percentage Required:** {s.get('min_percentage', 0)}%")
                    max_inc = s.get('max_family_income', 999999999)
                    if max_inc < 999999999:
                        st.markdown(f"**Maximum Family Income:** ₹{max_inc:,}")
                    else:
                        st.markdown("**Maximum Family Income:** No limit")
                    st.markdown(f"**Category:** {s.get('category', 'General')}")
                    st.markdown(f"**Deadline:** {s.get('deadline', 'Not specified')}")
                    st.markdown(f"**Award:** {s.get('amount', 'Not specified')}")
        else:
            st.info(
                "No scholarships matched your criteria. Try adjusting your percentage, "
                "income, or description."
            )

    st.divider()
    st.subheader("All Available Scholarships")
    all_s = scholarship_advisor.get_all_scholarships()
    if all_s:
        import pandas as pd
        table = [
            {
                "Name": s["name"],
                "Min %": s.get("min_percentage", 0),
                "Max Income (₹)": s.get("max_family_income", "No limit"),
                "Category": s.get("category", "General"),
                "Deadline": s.get("deadline", "—"),
                "Award": s.get("amount", "—"),
            }
            for s in all_s
        ]
        st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)

# =======================================================================
# TAB 7 — Financial Literacy Assistant
# =======================================================================
with tab_literacy:
    st.header("📚 Financial Literacy Assistant")
    st.write(
        "Ask simple questions about money, budgeting, loans, saving, and more. "
        "Get beginner-friendly explanations."
    )
    st.caption(
        "⚠️ This assistant provides **educational explanations only**. "
        "It does not provide professional financial advice."
    )
    st.divider()

    with st.form("assistant_form", clear_on_submit=True):
        question = st.text_input(
            "Ask a financial question:",
            placeholder="e.g. What is an EMI?  /  How do I save money?",
        )
        ask_btn = st.form_submit_button("💬 Ask", use_container_width=True)

    if ask_btn and question.strip():
        response = get_response(question)
        st.markdown(response)

    st.divider()
    st.subheader("💡 Suggested Questions")
    suggested = get_suggested_questions()
    cols = st.columns(2)
    for i, q in enumerate(suggested):
        with cols[i % 2]:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                st.markdown(get_response(q))
