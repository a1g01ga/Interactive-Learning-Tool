from __future__ import annotations

from typing import Any, Dict, List

from config import DEFAULT_NUM_MCQ, DEFAULT_NUM_FREEFORM
from core.question import MCQQuestion, FreeformQuestion, Question
from core.questions_presenter import display_question
from core.quiz_manager import QuizManager
from core.user_answer_processor import handle_exit, get_user_answer
from llm.llm_client import generate_questions


def prompt_topic() -> str | None:
    """Ask the user for a topic; return None if empty or 'exit' was typed."""
    topic = get_user_answer("Enter a topic to generate questions about: ")
    if handle_exit(topic):
        return None
    if not topic:
        print("No topic provided. Returning to menu.")
        return None
    return topic


def _parse_count_input(
        user_input_number: str | None, default_value: int, question_type: str
) -> int | None:
    """Convert user input to a non-negative int; use default on empty/invalid.

    Returns None if the user typed 'exit'.
    """
    if handle_exit(user_input_number):
        return None
    if user_input_number is None or not user_input_number.strip():
        print(f"No input for {question_type}. Using default: {default_value}.")
        return default_value
    user_input_stripped = user_input_number.strip()
    try:
        value = int(user_input_stripped)
    except ValueError:
        print(f"Invalid number for {question_type}. Using default: {default_value}.")
        return default_value
    if value < 0:
        print(f"Negative number for {question_type} not allowed. Using 0.")
        return 0
    return value


def prompt_number_of_questions(question_type: str, default_value: int) -> int | None:
    """Prompt the user to specify the number of questions of a given type.

    Args:
        question_type (str): A string describing the type of question (e.g., "multiple-choice").
        default_value (int): The default number of questions to use if the user provides no input.

    Returns:
        int | None: The number of questions specified by the user, or None if input is invalid or cancelled."""
    prompt = (
        f"How many {question_type} questions do you want? (default: {default_value}): "
    )
    answer = get_user_answer(prompt)
    return _parse_count_input(answer, default_value, question_type)


def get_values_from_number_input() -> tuple[int, int] | None:
    """Prompt the user for the number of multiple-choice and freeform-text questions.

    Returns:
        tuple[int, int] | None: A tuple containing the number of multiple-choice and freeform-text questions,
        or None if the user input is invalid or cancelled at any point."""
    num_mcq = prompt_number_of_questions("multiple-choice", DEFAULT_NUM_MCQ)
    if num_mcq is None:
        return None
    num_freeform = prompt_number_of_questions("freeform-text", DEFAULT_NUM_FREEFORM)
    if num_freeform is None:
        return None
    return num_mcq, num_freeform


def request_questions(topic: str, num_mcq: int, num_freeform: int) -> Dict[str, Any]:
    """Call the LLM client to request generation for a topic with given numbers of questions."""
    return generate_questions(topic, num_mcq=num_mcq, num_freeform=num_freeform)


def show_llm_error(result: Dict[str, Any]) -> bool:
    """Print model error details if present; return True if an error was shown."""
    if isinstance(result, dict) and "error" in result:
        print(
            f"{result['error'].get('type', 'Error')}: {result['error'].get('message', 'An error occurred.')}"
        )
        raw = result.get("raw")
        if raw:
            print("\nRaw model output:\n")
            print(raw)
        return True
    return False


def extract_questions_list(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Safely extract the 'questions' list from the LLM response dict."""
    if not isinstance(result, dict):
        return []
    questions = result.get("questions") or []
    return questions if isinstance(questions, list) else []


def create_question_object(question: Dict[str, Any]) -> Question:
    """Convert a question dict (from LLM) into a Question instance."""
    qtype = (question.get("type") or "").lower()
    if qtype == "multiple-choice":
        return MCQQuestion(
            id=0,
            topic=question.get("topic", "").lower(),
            type=qtype,
            question=question.get("question", ""),
            options=list(question.get("options", []) or []),
            correct_answer=question.get("correct_answer", ""),
            explanation=question.get("explanation"),
        )
    else:
        return FreeformQuestion(
            id=0,
            topic=question.get("topic", "").lower(),
            type=qtype,
            question=question.get("question", ""),
            reference_answer=question.get("reference_answer", ""),
        )


def preview_question(
        question_object: Question, question_as_dictionary: Dict[str, Any]
) -> None:
    """Show a preview of the question along with any answer/explanation metadata."""
    display_question(question_object)
    qtype = (question_as_dictionary.get("type") or "").lower()
    if qtype == "multiple-choice":
        if question_as_dictionary.get("correct_answer"):
            print(f"Correct answer: {question_as_dictionary.get('correct_answer')}")
        if question_as_dictionary.get("explanation"):
            print(f"Explanation: {question_as_dictionary.get('explanation')}")
    else:
        if question_as_dictionary.get("reference_answer"):
            print(f"Reference answer: {question_as_dictionary.get('reference_answer')}")
    print("-" * 80)


def _edit_question_text(question: Question) -> tuple[bool, bool]:
    """Edit the question text.

    Returns (changed, aborted).
    """
    changed = False
    new_qtext = get_user_answer("Edit question text (leave blank to keep): ")
    if handle_exit(new_qtext):
        return False, True
    if new_qtext and new_qtext != question.question:
        question.question = new_qtext
        changed = True
    return changed, False


def _edit_mcq_fields(question: MCQQuestion) -> tuple[bool, bool]:
    """Edit MCQ-specific fields: options and correct answer.

    Returns (changed, aborted).
    """
    changed = False
    opts_input = get_user_answer(
        "Edit options (separate by ';', leave blank to keep): "
    )
    if handle_exit(opts_input):
        return False, True
    if opts_input:
        new_opts = [option.strip() for option in opts_input.split(";")]
        new_opts = [option for option in new_opts if option]
        if new_opts and new_opts != question.options:
            question.options = new_opts
            changed = True

    correct_answer_input = get_user_answer(
        "Edit correct answer (leave blank to keep): "
    )
    if handle_exit(correct_answer_input):
        return False, True
    if correct_answer_input:
        if correct_answer_input != question.correct_answer:
            question.correct_answer = correct_answer_input
            changed = True
        if question.correct_answer and question.correct_answer not in question.options:
            question.options.append(question.correct_answer)
            print("Note: Correct answer was not in options; it has been added.")
    return changed, False


def _edit_freeform_fields(question: FreeformQuestion) -> tuple[bool, bool]:
    """Edit freeform-specific field: reference answer.

    Returns (changed, aborted).
    """
    ref_input = get_user_answer("Edit reference answer (leave blank to keep): ")
    if handle_exit(ref_input):
        return False, True
    if ref_input and ref_input != question.reference_answer:
        question.reference_answer = ref_input
        return True, False
    return False, False


def _edit_question_in_place(question: Question) -> bool:
    """Allow the user to modify the question/answer fields before saving.

    Returns True if any field was changed, else False.
    """
    changed_overall = False

    changed, aborted = _edit_question_text(question)
    if aborted:
        return False
    changed_overall |= changed

    if isinstance(question, MCQQuestion):
        changed, aborted = _edit_mcq_fields(question)
        if aborted:
            return False
        changed_overall |= changed
    elif isinstance(question, FreeformQuestion):
        changed, aborted = _edit_freeform_fields(question)
        if aborted:
            return False
        changed_overall |= changed

    return changed_overall


def review_and_collect(questions: List[Dict[str, Any]]) -> List[Question] | None:
    """Iterate through generated questions, letting the user accept, reject, or edit.

    Returns a list of accepted Question objects, or None if the user typed 'exit'.
    """
    print(
        "\nReview generated questions one by one. Accept to save, edit to modify, reject to skip.\n"
    )
    accepted: List[Question] = []
    for question in questions:
        question_object = create_question_object(question)
        while True:
            preview_question(question_object, question_object.as_dict())
            answer = (
                get_user_answer("[A]ccept / [E]dit / [R]eject? (default: A): ")
                .strip()
                .lower()
            )
            if handle_exit(answer):
                return None
            choice = answer or "a"
            if choice == "a":
                accepted.append(question_object)
                print("Accepted.\n")
                break
            elif choice == "e":
                was_changed = _edit_question_in_place(question_object)
                if was_changed:
                    question_object.source = "manual"
                print("Updated preview:")
            elif choice == "r":
                print("Rejected.\n")
                break
            else:
                print("Please choose A, E, R, or type 'exit'.")
    return accepted


def save_questions(accepted: List[Question]) -> None:
    """Persist accepted questions to storage and report how many were saved."""
    if not accepted:
        print("No questions were accepted.")
        return
    quiz_manager = QuizManager()
    quiz_manager.add_questions(accepted)
    print(f"Saved {len(accepted)} question(s).")


def run_generate_questions() -> None:
    """End-to-end flow for generating, reviewing, and saving new questions."""
    print("\nEntering Generate Questions Mode. Type 'exit' to leave.\n")
    topic = prompt_topic()
    if topic is None:
        return
    counts = get_values_from_number_input()
    if counts is None:
        return
    num_mcq, num_freeform = counts
    print(f"\nGenerating questions for topic: '{topic}' ...\n")
    result: Dict[str, Any] = request_questions(topic, num_mcq, num_freeform)
    if show_llm_error(result):
        return
    questions_from_model = extract_questions_list(result)
    if not questions_from_model:
        print("No questions returned by the model.")
        return
    accepted = review_and_collect(questions_from_model)
    if accepted is None:
        return
    save_questions(accepted)
