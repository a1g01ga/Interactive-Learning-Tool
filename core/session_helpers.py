from __future__ import annotations

from typing import Tuple

from core.question import MCQQuestion, FreeformQuestion, Question
from core.questions_presenter import display_question
from core.quiz_manager import QuizManager
from core.user_answer_processor import process_freeform, process_mcq


def ensure_active_questions(quiz_manager: QuizManager) -> list[Question] | None:
    """Return the list of active questions or None after printing a notice.

    Prints a user-friendly message when there are no active questions.
    """
    active = quiz_manager.list_active()
    if not active:
        print("No active questions. Use Manage mode or Generator to add some.")
        return None
    return active


def present_and_get_result(question: Question) -> Tuple[bool, bool, str | None]:
    """Display a question and obtain the evaluation result from the user.

    Returns a tuple (exit_requested, is_correct, explanation).
    When the user types 'exit' at the prompt, returns (True, False, None).
    """
    display_question(question)

    if isinstance(question, MCQQuestion):
        result = process_mcq(question)
    else:
        assert isinstance(question, FreeformQuestion)
        result = process_freeform(question)

    if result == (None, None):
        return True, False, None

    is_correct, explanation = result
    return False, bool(is_correct), explanation


def print_correctness(is_correct: bool, explanation: str | None) -> None:
    """Print standardized correctness feedback and optional explanation."""
    print("Correct!" if is_correct else "Incorrect.")
    if explanation:
        print("Note:", explanation)
