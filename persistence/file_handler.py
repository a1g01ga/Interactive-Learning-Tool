"""File I/O helpers for questions (JSON) and results (TXT).

This module centralizes reading/writing of persisted data. It stays intentionally
simple and tolerant to schema differences so older files continue to work.
"""

from __future__ import annotations

import json
import os
from typing import Any

from config import DATA_DIR, QUESTIONS_PATH, RESULTS_PATH


def ensure_data_dir() -> None:
    """
    Ensure that the data directory exists.

    Creates the directory specified by the DATA_DIR constant if it does not
    already exist. If the directory already exists, no action is taken.

    Returns:
        None
    """
    os.makedirs(DATA_DIR, exist_ok=True)


def load_questions(path: str = QUESTIONS_PATH) -> list[dict[str, Any]]:
    """Load a list of question dicts from JSON.

    Supports two shapes for backward compatibility:
    - a plain list of question objects
    - a dict with a "questions" key
    """
    ensure_data_dir()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception:
        return []

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("questions"), list):
        return data["questions"]
    return []


def save_questions(questions: list[dict[str, Any]], path: str = QUESTIONS_PATH) -> None:
    """Persist the entire questions list to JSON with indentation."""
    ensure_data_dir()
    with open(path, "w", encoding="utf-8") as file:
        json.dump(questions, file, ensure_ascii=False, indent=2)


def append_result_line(line: str, path: str = RESULTS_PATH) -> None:
    """Append a single line to results.txt, creating the file if missing."""
    ensure_data_dir()
    with open(path, "a", encoding="utf-8") as file:
        file.write(line.rstrip("\n") + "\n")


def get_next_id(questions: list[dict[str, Any]]) -> int:
    """Compute the next unique integer ID based on max existing id."""
    max_id = 0
    for question in questions:
        try:
            qid = int(question.get("id", 0))
            if qid > max_id:
                max_id = qid
        except Exception:
            continue
    return max_id + 1
