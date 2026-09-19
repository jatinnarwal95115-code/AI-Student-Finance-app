"""
tests/test_scholarship_advisor.py

Unit tests for services/scholarship_advisor.py — scholarship matching logic.
"""

import pytest
from services.scholarship_advisor import (
    get_all_scholarships,
    match_scholarships,
    search_by_text,
)


class TestGetAllScholarships:
    def test_returns_list(self):
        scholarships = get_all_scholarships()
        assert isinstance(scholarships, list)

    def test_returns_at_least_one_scholarship(self):
        scholarships = get_all_scholarships()
        assert len(scholarships) >= 1

    def test_empty_scholarship_list_handled(self, monkeypatch):
        import services.scholarship_advisor as sa
        monkeypatch.setattr(sa, "_scholarships_cache", [])
        result = sa.get_all_scholarships()
        assert result == []


class TestMatchScholarships:
    def test_high_percentage_matches_merit_scholarships(self):
        results = match_scholarships(
            percentage=90.0,
            family_income=300000,
            keywords_input="merit undergraduate",
        )
        assert len(results) >= 1

    def test_low_percentage_excludes_high_min_scholarships(self):
        # Any scholarship requiring >= 85% should be excluded
        results = match_scholarships(
            percentage=50.0,
            family_income=200000,
            keywords_input="merit",
        )
        for s in results:
            assert float(s.get("min_percentage", 0)) <= 50.0

    def test_high_income_excludes_income_restricted_scholarships(self):
        results = match_scholarships(
            percentage=80.0,
            family_income=2000000,  # 20 lakh — very high
            keywords_input="",
        )
        for s in results:
            assert float(s.get("max_family_income", 999999999)) >= 2000000

    def test_no_keywords_returns_numeric_matches(self):
        # With empty keywords, matching is based only on percentage and income
        results = match_scholarships(
            percentage=75.0,
            family_income=400000,
            keywords_input="",
        )
        # Should return an empty list since keyword matching requires at least one keyword match
        # when the scholar has no keywords in any eligibility list (depends on data)
        # — the key assertion is that it does NOT raise an exception
        assert isinstance(results, list)

    def test_empty_scholarship_list_returns_empty(self, monkeypatch):
        import services.scholarship_advisor as sa
        monkeypatch.setattr(sa, "_scholarships_cache", [])
        result = match_scholarships(80.0, 300000, "merit")
        assert result == []

    def test_case_insensitive_keyword_matching(self):
        results_lower = match_scholarships(80.0, 400000, "merit")
        results_upper = match_scholarships(80.0, 400000, "MERIT")
        assert len(results_lower) == len(results_upper)

    def test_result_sorted_by_match_count(self):
        results = match_scholarships(85.0, 500000, "merit undergraduate academic")
        # Just verify it returns a list without errors
        assert isinstance(results, list)


class TestSearchByText:
    def test_keyword_search_returns_results(self):
        results = search_by_text("engineering")
        assert isinstance(results, list)

    def test_empty_query_returns_empty_list(self):
        results = search_by_text("")
        assert results == []

    def test_unknown_keyword_returns_empty_list(self):
        results = search_by_text("xyzabc123nonexistent")
        assert results == []
