from __future__ import annotations

from core.quiz_manager import QuizManager
from core.selector import weighted_choice
from core.session_helpers import (
    ensure_active_questions,
    present_and_get_result,
    print_correctness,
)


def run_practice() -> None:
    """Interactive practice loop that picks weighted questions until exit.

    Users can type 'exit' at any answer prompt to return to the main menu.
    """
    quiz_manager = QuizManager()

    if not ensure_active_questions(quiz_manager):
        return

    print("\nEntering Practice Mode. Type 'exit' to leave.\n")

    while True:
        active_questions = quiz_manager.list_active()
        if not active_questions:
            print("No active questions left.")
            return

        question = weighted_choice(active_questions)
        print("-" * 80)
        exit_requested, is_correct, explanation = present_and_get_result(question)
        if exit_requested:
            return

        quiz_manager.record_result(question, is_correct)
        print_correctness(is_correct, explanation)
