from __future__ import annotations

from core.question import Question
from core.questions_presenter import as_rows
from core.quiz_manager import QuizManager
from core.user_answer_processor import handle_exit, get_user_answer


def show_manage_menu() -> str:
    """Print the Manage menu and return the user's raw choice string."""
    print("\nManage Questions:")
    print("1. List questions")
    print("2. Enable a question")
    print("3. Disable a question")
    print("4. Back to main menu")
    return get_user_answer("Choose an option: ")


def list_questions(quiz_manager: QuizManager) -> None:
    """Print all questions in a formatted table."""
    items = quiz_manager.list_all()
    for line in as_rows(items):
        print(line)


def toggle_question(quiz_manager: QuizManager, enable: bool) -> None:
    """Enable or disable a question by asking the user for its ID and confirmation.

    Parameters:
    - quiz_manager: The QuizManager instance managing questions.
    - enable: If True, set active; if False, set inactive.
    """
    try:
        question_id = int(input("Enter question ID: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    question = quiz_manager.find_by_id(question_id)
    if not question:
        print("Question not found.")
        return

    if question.active == enable:
        print(
            "Question is already enabled."
            if enable
            else "Question is already disabled."
        )
        return

    show_question_details(question)

    confirm = input(f"Confirm to set Active={enable}? [y/N] ").strip().lower() or "n"
    if confirm == "y":
        updated = quiz_manager.toggle_active(question.id, enable)
        print("Updated." if updated else "Failed to update.")
    else:
        print("Cancelled.")


def show_question_details(question: Question) -> None:
    """Print a readable, detailed view of a single question."""
    print("\nQuestion details:")
    print(
        f"ID: {question.id}\nActive: {question.active}\nTopic: {question.topic}\nType: {question.type}\nQuestion: {question.question}"
    )

    if question.type == "multiple-choice":
        options = getattr(question, "options", [])
        for i, opt in enumerate(options[:4]):
            print(f"  {chr(65 + i)}. {opt}")
        correct = getattr(question, "correct_answer", "")
        if correct:
            print(f"Correct answer: {correct}")
    else:
        reference = getattr(question, "reference_answer", "")
        if reference:
            print(f"Reference answer: {reference}")


def run_manage_questions() -> None:
    """Entry point for Manage Questions Mode with 'exit' support."""
    print("\nEntering Manage Questions Mode. Type 'exit' to leave.\n")
    quiz_manager = QuizManager()
    while True:
        choice = show_manage_menu()
        if handle_exit(choice):
            return
        if choice == "1":
            list_questions(quiz_manager)
        elif choice in {"2", "3"}:
            toggle_question(quiz_manager, enable=(choice == "2"))
        elif choice == "4":
            return
        else:
            print("Invalid option.")
