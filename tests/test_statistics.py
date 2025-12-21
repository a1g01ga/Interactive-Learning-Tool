"""Tests for statistics helpers.

Focuses on correct_percentage edge cases and typical scenarios.
"""

import pytest

from core.question import Question
from core.statistics import correct_percentage


def _make_question(correct: int, incorrect: int) -> Question:
    """Helper to instantiate a minimal Question with provided stats."""
    return Question(
        id=94,
        topic="pytest",
        type="freeform-text",
        question="Explain how pytest can discover and run test functions in a Python project.",
        correct_count=correct,
        incorrect_count=incorrect,
    )


def test_correct_percentage_never_shown_returns_zero():
    """When no answers recorded, percentage should be 0.0 (avoid division by zero)."""
    question = _make_question(0, 0)
    assert correct_percentage(question) == 0.0


def test_correct_percentage_only_correct_is_100():
    """All answers correct -> 100%."""
    question = _make_question(5, 0)
    assert correct_percentage(question) == 100.0


def test_correct_percentage_only_incorrect_is_0():
    """All answers incorrect -> 0%."""
    question = _make_question(0, 7)
    assert correct_percentage(question) == 0.0


def test_correct_percentage_mixed_simple():
    """3 correct, 1 incorrect -> 75%."""
    question = _make_question(3, 1)
    assert correct_percentage(question) == 75.0


def test_correct_percentage_fractional_approx():
    """Fractional case (2/3) ~= 66.6667% using pytest.approx for tolerance."""
    question = _make_question(2, 1)
    assert correct_percentage(question) == pytest.approx(66.6666667, rel=1e-6)
