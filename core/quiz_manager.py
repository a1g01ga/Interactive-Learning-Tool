"""QuizManager: orchestrates loading, saving, and updating questions."""

from __future__ import annotations

from typing import Optional

from persistence.file_handler import load_questions, save_questions, get_next_id
from .question import Question


class QuizManager:
    """In-memory questions store with simple persistence hooks."""

    def __init__(self) -> None:
        """Initialize the manager by loading questions from disk."""
        self._questions: list[Question] = [
            Question.from_dict(d) for d in load_questions()
        ]
        for question in self._questions:
            if getattr(question, "active", None) is None:
                question.active = True

    def list_all(self) -> list[Question]:
        """Return a shallow copy of all questions (active and inactive)."""
        return list(self._questions)

    def list_active(self) -> list[Question]:
        """Return only questions currently marked as active."""
        return [q for q in self._questions if q.active]

    def find_by_id(self, qid: int) -> Optional[Question]:
        """Find a question by its numeric ID, or return None if missing."""
        for question in self._questions:
            if question.id == qid:
                return question
        return None

    def toggle_active(self, qid: int, active: bool) -> bool:
        """Set the active flag for a question; return True if updated, else False."""
        question = self.find_by_id(qid)
        if not question:
            return False
        question.active = active
        self._persist()
        return True

    def add_questions(self, new_questions: list[Question]) -> None:
        """Append new questions, auto-assigning non-colliding incremental IDs."""
        # Assign IDs that don't collide with existing max
        next_id = get_next_id([question.as_dict() for question in self._questions])
        for question in new_questions:
            question.id = next_id
            next_id += 1
            self._questions.append(question)
        self._persist()

    def record_result(self, question: Question, is_correct: bool) -> None:
        """Update the question's statistics and persist the change."""
        question.times_shown += 1
        if is_correct:
            question.correct_count += 1
        else:
            question.incorrect_count += 1
        self._persist()

    def _persist(self) -> None:
        """Write current in-memory questions to disk as JSON."""
        save_questions([question.as_dict() for question in self._questions])
