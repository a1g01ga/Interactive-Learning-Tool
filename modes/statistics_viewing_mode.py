from __future__ import annotations

from core.questions_presenter import as_rows
from core.quiz_manager import QuizManager
from core.user_answer_processor import handle_exit, get_user_answer


def run_statistics_viewing() -> None:
    """Display questions summary table and wait until the user types 'exit'."""
    print("\nEntering Statistics Viewing Mode. Type 'exit' to leave.\n")

    qm = QuizManager()
    rows = as_rows(qm.list_all())
    print()
    for r in rows:
        print(r)

    while True:
        answer = get_user_answer("Type 'exit' to return to the main menu: ")
        if handle_exit(answer):
            return
        print("Please type 'exit' to leave statistics mode.")
