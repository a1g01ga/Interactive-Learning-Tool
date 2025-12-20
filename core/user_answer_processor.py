from __future__ import annotations

from core.evaluator import evaluate_mcq, evaluate_freeform
from core.question import MCQQuestion, FreeformQuestion


def get_user_answer(prompt: str = "Your answer: ") -> str:
    """Prompt the user and return their trimmed input.

    Parameters:
    - prompt: The prompt shown to the user.

    Returns:
    The user's input with leading/trailing whitespace removed.
    """
    answer = input(prompt).strip()
    return answer


def handle_exit(answer: str) -> bool:
    """Return True and print a message if the user chose to exit.

    Parameters:
    - answer: The user's raw input.

    Returns:
    True if the input equals 'exit' (case-insensitive); otherwise False.
    """
    if answer.lower() == "exit":
        print("Exiting this Mode.")
        return True
    return False


def process_mcq(question: MCQQuestion) -> tuple[bool | None, str | None]:
    """Process an MCQ question, possibly handling early exit.

    Parameters:
    - question: The MCQQuestion being presented.

    Returns:
    - (is_correct, explanation) on normal flow.
    - (None, None) if the user typed 'exit' to leave the mode.
    """
    answer = get_user_answer(
        "Your answer (type the full option text or letter A-D): "
    ).lower()
    if handle_exit(answer):
        return None, None

    if answer in {"a", "b", "c", "d"}:
        index = ord(answer.lower()) - ord("a")
        answer_text = (
            question.options[index] if 0 <= index < len(question.options) else answer
        )
    else:
        answer_text = answer

    return evaluate_mcq(question, answer_text)


def process_freeform(question: FreeformQuestion) -> tuple[bool | None, str | None]:
    """Process a freeform question, possibly handling early exit.

    Parameters:
    - question: The FreeformQuestion being presented.

    Returns:
    - (is_correct, explanation) on normal flow.
    - (None, None) if the user typed 'exit' to leave the mode.
    """
    answer = get_user_answer()
    if handle_exit(answer):
        return None, None

    return evaluate_freeform(question, answer)
