"""
tests/test_assistant.py

Unit tests for ai/assistant.py — keyword-based financial literacy assistant.
"""

import pytest
from ai.assistant import get_response, get_suggested_questions


_DISCLAIMER_SNIPPET = "educational purposes only"


class TestGetResponse:
    def test_budget_keyword_returns_budgeting_response(self):
        response = get_response("What is a budget?")
        assert "budget" in response.lower()
        assert _DISCLAIMER_SNIPPET in response.lower()

    def test_emi_keyword_returns_emi_response(self):
        response = get_response("What is an EMI?")
        assert "emi" in response.lower()
        assert _DISCLAIMER_SNIPPET in response.lower()

    def test_saving_keyword_returns_savings_response(self):
        response = get_response("How do I save money?")
        assert "saving" in response.lower() or "save" in response.lower()

    def test_loan_keyword_returns_loan_response(self):
        response = get_response("How do loans work?")
        assert "loan" in response.lower()

    def test_scholarship_keyword_returns_scholarship_response(self):
        response = get_response("Tell me about scholarships")
        assert "scholarship" in response.lower()

    def test_needs_wants_keyword_returns_response(self):
        response = get_response("What is the difference between needs and wants?")
        assert "needs" in response.lower() or "wants" in response.lower()

    def test_interest_keyword_returns_response(self):
        response = get_response("What is interest?")
        assert "interest" in response.lower()

    def test_unknown_question_returns_fallback(self):
        response = get_response("What is the capital of France?")
        assert "don't have" in response.lower() or "try asking" in response.lower()

    def test_empty_question_returns_prompt(self):
        response = get_response("")
        assert "please type" in response.lower()

    def test_whitespace_only_returns_prompt(self):
        response = get_response("   ")
        assert "please type" in response.lower()

    def test_disclaimer_always_appended_for_known_topic(self):
        known_questions = [
            "What is budgeting?",
            "How to save?",
            "What is EMI?",
            "Tell me about loans.",
        ]
        for q in known_questions:
            assert _DISCLAIMER_SNIPPET in get_response(q).lower(), (
                f"Disclaimer missing for question: {q}"
            )

    def test_disclaimer_appended_for_fallback(self):
        response = get_response("random nonsense xyz123")
        assert _DISCLAIMER_SNIPPET in response.lower()


class TestGetSuggestedQuestions:
    def test_returns_list(self):
        qs = get_suggested_questions()
        assert isinstance(qs, list)

    def test_returns_at_least_four_questions(self):
        qs = get_suggested_questions()
        assert len(qs) >= 4

    def test_all_items_are_strings(self):
        for q in get_suggested_questions():
            assert isinstance(q, str)
