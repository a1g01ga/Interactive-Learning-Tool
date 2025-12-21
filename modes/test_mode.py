from __future__ import annotations

from datetime import datetime

from core.quiz_manager import QuizManager
from core.selector import random_unique
from core.session_helpers import (
    ensure_active_questions,
    present_and_get_result,
    print_correctness,
)
from persistence.file_handler import append_result_line


def _prompt_number_of_questions(max_count: int) -> int | None:
    """Prompt user for number of questions (1..max_count). Returns None on invalid input."""
    try:
        number_of_questions_for_test = int(
            input(f"How many questions? (1-{max_count}): ").strip()
        )
    except Exception:
        print("Invalid number.")
        return None
    if number_of_questions_for_test <= 0:
        print("Nothing to do.")
        return None
    return number_of_questions_for_test


def run_test() -> None:
    """Run a fixed-length test session over randomly sampled active questions.

    Prompts for number of questions; users can type 'exit' at answer prompts to leave.
    """
    quiz_manager = QuizManager()

    active_questions = ensure_active_questions(quiz_manager)
    if not active_questions:
        return

    print("\nEntering Test Mode. Type 'exit' to leave.\n")

    number_of_questions = _prompt_number_of_questions(len(active_questions))
    if number_of_questions is None:
        return

    selected = random_unique(active_questions, number_of_questions)
    correct_total = 0

    for i, question in enumerate(selected, start=1):
        print("-" * 80)
        print(f"Q{i}/{len(selected)}")
        exit_requested, is_correct, explanation = present_and_get_result(question)
        if exit_requested:
            return
        if is_correct:
            correct_total += 1
        print_correctness(is_correct, explanation)

    print("=" * 80)
    print(
        f"Final score: You answered {correct_total} out of {len(selected)} correctly."
    )
    date_and_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    append_result_line(f"{date_and_time} - Score: {correct_total}/{len(selected)}")
