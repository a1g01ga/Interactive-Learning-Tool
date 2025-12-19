"""Question domain model using a lightweight OOP approach.

Two concrete types are supported:
- MCQQuestion: multiple-choice with options and a correct_answer string
- FreeformQuestion: freeform with a reference_answer string

Each question carries basic statistics in-place to keep persistence simple.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Question:
    """Base class for all question types.

    Attributes:
    - id: Unique integer identifier.
    - topic: The subject of the question (e.g., "math").
    - type: A lowercased type tag (e.g., "multiple-choice", "freeform").
    - question: The prompt text shown to the user.
    - source: Where the question originated (default "LLM").
    - active: Whether this question is available for practice/test modes.
    - times_shown: Number of times the question has been shown.
    - correct_count: Number of times answered correctly.
    - incorrect_count: Number of times answered incorrectly.
    """

    id: int
    topic: str
    type: str
    question: str
    source: str = "LLM"
    active: bool = True
    times_shown: int = 0
    correct_count: int = 0
    incorrect_count: int = 0

    def as_dict(self) -> Dict[str, Any]:
        """Serialize the question to a JSON-safe dict for persistence."""
        return {
            "id": self.id,
            "topic": self.topic,
            "type": self.type,
            "question": self.question,
            "source": self.source,
            "active": self.active,
            "times_shown": self.times_shown,
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count,
        }

    @staticmethod
    def from_dict(dictionary: Dict[str, Any]) -> Question:
        """Create a Question (MCQ or Freeform) from a persisted dict.

        Returns:
        - An MCQQuestion if type == "multiple-choice",
          otherwise a FreeformQuestion.
        """
        qtype = (dictionary.get("type") or "").lower()
        base_kwargs = dict(
            id=int(dictionary.get("id", 0)),
            topic=str(dictionary.get("topic", "")),
            type=qtype,
            question=str(dictionary.get("question", "")),
            source=str(dictionary.get("source", "LLM")),
            active=bool(dictionary.get("active", True)),
            times_shown=int(dictionary.get("times_shown", 0)),
            correct_count=int(dictionary.get("correct_count", 0)),
            incorrect_count=int(dictionary.get("incorrect_count", 0)),
        )

        if qtype == "multiple-choice":
            return MCQQuestion(
                options=list(dictionary.get("options", []) or []),
                correct_answer=str(dictionary.get("correct_answer", "")),
                explanation=dictionary.get("explanation"),
                **base_kwargs,
            )

        return FreeformQuestion(
            reference_answer=str(dictionary.get("reference_answer", "")),
            **base_kwargs,
        )


@dataclass
class MCQQuestion(Question):
    """Multiple-choice question with options and a correct answer.

    Attributes:
    - options: List of candidate answers; only the first four are shown in UI.
    - correct_answer: The correct option value (case-insensitive compare).
    - explanation: Optional explanation displayed after answering.
    """

    options: List[str] = field(default_factory=list)
    correct_answer: str = ""
    explanation: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        """Extend base serialization with MCQ-specific fields."""
        data = super().as_dict()
        data.update(
            {
                "options": list(self.options),
                "correct_answer": self.correct_answer,
            }
        )
        if self.explanation is not None:
            data["explanation"] = self.explanation
        return data


@dataclass
class FreeformQuestion(Question):
    """Freeform question evaluated against a reference answer string."""

    reference_answer: str = ""

    def as_dict(self) -> Dict[str, Any]:
        """Extend base serialization with the reference answer field."""
        data = super().as_dict()
        data["reference_answer"] = self.reference_answer
        return data
