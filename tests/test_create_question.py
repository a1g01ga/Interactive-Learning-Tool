"""Tests for transforming LLM question dicts into domain objects.

Covers MCQQuestion and FreeformQuestion shapes produced by create_question_object.
"""

from core.question import MCQQuestion, FreeformQuestion
from modes.generate_questions_mode import create_question_object


def test_create_mcq_question():
    """Create an MCQQuestion from a dict and verify all fields are mapped."""
    input_data = {
        "type": "multiple-choice",
        "topic": "pytest",
        "question": "What command do you use to run a test using Pytest?",
        "options": ["pytest", "run_test", "python test", "test_py"],
        "correct_answer": "pytest",
        "explanation": "The 'pytest' command is used to run tests with Pytest.",
    }

    result = create_question_object(input_data)

    assert isinstance(result, MCQQuestion)
    assert result.id == 0
    assert result.topic == "pytest"
    assert result.type == "multiple-choice"
    assert result.question == "What command do you use to run a test using Pytest?"
    assert result.options == ["pytest", "run_test", "python test", "test_py"]
    assert result.correct_answer == "pytest"
    assert (
            result.explanation == "The 'pytest' command is used to run tests with Pytest."
    )


def test_create_freeform_question():
    """Create a FreeformQuestion from a dict and verify field mapping."""
    input_data = {
        "type": "freeform",
        "topic": "pytest",
        "question": "Explain how pytest can discover and run test functions in a Python project.",
        "reference_answer": "pytest automatically discovers test functions by searching for files and functions prefixed with 'test_' in the current directory and its subdirectories. It then runs these functions as test cases.",
    }

    result = create_question_object(input_data)

    assert isinstance(result, FreeformQuestion)
    assert result.id == 0
    assert result.topic == "pytest"
    assert result.type == "freeform"
    assert (
            result.question
            == "Explain how pytest can discover and run test functions in a Python project."
    )
    assert (
            result.reference_answer
            == "pytest automatically discovers test functions by searching for files and functions prefixed with 'test_' in the current directory and its subdirectories. It then runs these functions as test cases."
    )
