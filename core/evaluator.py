"""Evaluation logic for MCQ and Freeform questions.

For freeform, we rely on the LLM client to make a correctness judgment
("Correct" / "Incorrect") and optional rationale.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from llm.llm_client import judge_freeform
from .question import FreeformQuestion, MCQQuestion


def evaluate_mcq(mcq_question: MCQQuestion, user_choice: str) -> Tuple[bool, str]:
    """Return (is_correct, explanation) for an MCQ question."""
    is_correct = (
            user_choice.strip().lower() == mcq_question.correct_answer.strip().lower()
    )
    explanation = mcq_question.explanation or ""
    return is_correct, explanation


def evaluate_freeform(
        freeform_question: FreeformQuestion, user_answer: str
) -> Tuple[bool, str]:
    """Use LLM client to judge user's freeform answer.

    The llm_client must define judge_freeform(question, reference_answer, user_answer)
    and return a dict with {"judgment": "Correct|Incorrect", "explanation": "..."}
    or {"error": {...}} in case of a failure.

    Additionally, if the user's answer is empty or only whitespace, we do not call
    the LLM and immediately return an incorrect judgment with a fixed explanation.
    """
    # Short-circuit empty/whitespace-only answers
    if not (user_answer or "").strip():
        return False, "The question was not answered"

    result: Dict[str, Any] = judge_freeform(
        freeform_question.question,
        freeform_question.reference_answer,
        user_answer,
    )

    if isinstance(result, dict) and "error" in result:
        return False, f"LLM error: {result['error'].get('message', 'Unknown')}"

    judgment = (result.get("judgment") or "").strip().lower()
    explanation = result.get("explanation") or ""
    return (judgment == "correct"), explanation
