"""Statistics helpers and CLI rendering."""

from __future__ import annotations

from .question import Question


def correct_percentage(question: Question) -> float:
    """Compute the percentage of correct answers for a question.

    Returns 0.0 if the question has never been shown.
    """
    total = question.correct_count + question.incorrect_count
    if total <= 0:
        return 0.0
    return (question.correct_count / total) * 100.0
