"""Selection strategies for choosing questions.

- Weighted selection for practice (favor questions with lower correctness)
- Random unique selection for test sessions
"""

from __future__ import annotations

import random
from typing import Sequence

from .question import Question


def weighted_choice(questions: Sequence[Question]) -> Question:
    """Pick one question with probability weighted by difficulty (inverse accuracy).

    Weight formula (simple and robust):
    weight = 1 + incorrect_count - correct_count * 0.25
    and a small epsilon to avoid zero weight.
    """
    if not questions:
        raise ValueError("No questions to choose from")

    weights: list[float] = []
    for question in questions:
        incorrect = max(0, question.incorrect_count)
        correct = max(0, question.correct_count)
        weighting_mechanism = 1.0 + incorrect - 0.25 * correct
        if weighting_mechanism < 0.1:
            weighting_mechanism = 0.1
        weights.append(weighting_mechanism)

    return random.choices(list(questions), weights=weights, k=1)[0]


def random_unique(
        questions: Sequence[Question], number_of_questions: int
) -> list[Question]:
    """Return number_of_questions distinct questions sampled uniformly at random (no repetition)."""
    if number_of_questions <= 0:
        return []
    number_of_questions = min(number_of_questions, len(questions))
    return random.sample(list(questions), number_of_questions)
