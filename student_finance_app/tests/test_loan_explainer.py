"""
tests/test_loan_explainer.py

Unit tests for services/loan_explainer.py — EMI calculation and concept lookup.
"""

import pytest
from services.loan_explainer import calculate_emi, get_repayment_summary, get_concept, get_all_concepts


class TestCalculateEmi:
    def test_standard_emi_calculation(self):
        # Known reference: P=100000, r=12% annual, n=12 months → EMI ≈ 8884.88
        emi = calculate_emi(principal=100000.0, annual_rate_pct=12.0, months=12)
        assert abs(emi - 8884.88) < 1.0  # allow ₹1 tolerance for rounding

    def test_zero_interest_rate(self):
        # P=60000, 0% interest, 12 months → EMI = 5000
        emi = calculate_emi(principal=60000.0, annual_rate_pct=0.0, months=12)
        assert emi == 5000.0

    def test_single_month_loan(self):
        # 1-month loan → EMI = full principal + 1 month interest
        emi = calculate_emi(principal=10000.0, annual_rate_pct=12.0, months=1)
        expected = 10000.0 * (0.01) * (1.01) / (1.01 - 1)
        assert abs(emi - expected) < 0.01

    def test_emi_is_positive(self):
        emi = calculate_emi(principal=50000.0, annual_rate_pct=10.0, months=24)
        assert emi > 0

    def test_invalid_principal_zero_raises(self):
        with pytest.raises(ValueError, match="greater than zero"):
            calculate_emi(principal=0.0, annual_rate_pct=10.0, months=12)

    def test_invalid_principal_negative_raises(self):
        with pytest.raises(ValueError, match="greater than zero"):
            calculate_emi(principal=-5000.0, annual_rate_pct=10.0, months=12)

    def test_invalid_months_zero_raises(self):
        with pytest.raises(ValueError, match="at least 1 month"):
            calculate_emi(principal=50000.0, annual_rate_pct=10.0, months=0)

    def test_invalid_months_negative_raises(self):
        with pytest.raises(ValueError, match="at least 1 month"):
            calculate_emi(principal=50000.0, annual_rate_pct=10.0, months=-6)

    def test_longer_tenure_means_smaller_emi(self):
        emi_12 = calculate_emi(100000.0, 12.0, 12)
        emi_24 = calculate_emi(100000.0, 12.0, 24)
        assert emi_24 < emi_12


class TestGetRepaymentSummary:
    def test_summary_keys_present(self):
        summary = get_repayment_summary(100000.0, 12.0, 12)
        assert "emi" in summary
        assert "total_payable" in summary
        assert "total_interest" in summary

    def test_total_payable_equals_emi_times_months(self):
        summary = get_repayment_summary(100000.0, 12.0, 12)
        assert abs(summary["total_payable"] - summary["emi"] * 12) < 0.02

    def test_total_interest_positive_with_nonzero_rate(self):
        summary = get_repayment_summary(100000.0, 12.0, 12)
        assert summary["total_interest"] > 0

    def test_total_interest_zero_with_zero_rate(self):
        summary = get_repayment_summary(60000.0, 0.0, 12)
        assert summary["total_interest"] == 0.0

    def test_total_payable_greater_than_principal(self):
        summary = get_repayment_summary(100000.0, 10.0, 24)
        assert summary["total_payable"] > 100000.0


class TestGetConcept:
    def test_known_term_returns_dict(self):
        concept = get_concept("EMI")
        assert concept is not None
        assert "term" in concept
        assert "definition" in concept
        assert "example" in concept

    def test_case_insensitive_lookup(self):
        assert get_concept("emi") is not None
        assert get_concept("EMI") is not None
        assert get_concept("Emi") is not None

    def test_unknown_term_returns_none(self):
        assert get_concept("Cryptocurrency") is None

    def test_all_concepts_returned(self):
        concepts = get_all_concepts()
        assert isinstance(concepts, list)
        assert len(concepts) >= 5  # we have at least 6 in data/loan_concepts.json
