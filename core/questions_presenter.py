from __future__ import annotations

from typing import Iterable

from tabulate import tabulate

from core.question import MCQQuestion, Question
from core.statistics import correct_percentage


def display_question(question: Question) -> None:
    """Pretty-print a question to the console.

    - For multiple-choice questions, prints up to the first 4 options labeled A-D.
    - For other types, prints only the prompt text.

    Parameters:
    - question: The Question instance to display.
    """
    print(f"[{question.type}] Topic: {question.topic}")
    print(question.question)
    if isinstance(question, MCQQuestion):
        for index, option in enumerate(question.options[:4]):
            print(f"  {chr(65 + index)}. {option}")


def as_rows(questions: Iterable[Question]) -> list[str]:
    """Return a grid-formatted table (split into lines) summarizing questions.

    Columns: ID, Active, Source, Topic, Type, Times Shown, Correct%, Question
    """
    headers = [
        "ID",
        "Active",
        "Source",
        "Topic",
        "Type",
        "Shown",
        "Correct%",
        "Question Text",
    ]
    rows_data = []
    for question in questions:
        rows_data.append(
            [
                str(question.id),
                "Yes" if question.active else "No",
                str(question.source or ""),
                str(question.topic or ""),
                str(question.type or ""),
                str(question.times_shown or ""),
                f"{correct_percentage(question):.1f}%",
                str(question.question or ""),
            ]
        )
    table = tabulate(rows_data, headers=headers, tablefmt="grid")
    return table.splitlines()
