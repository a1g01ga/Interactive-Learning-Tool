"""Tests for persistence.file_handler helpers.

This module validates get_next_id, ensuring it skips non-integer ids and
computes the next sequential integer greater than the current maximum.
"""

from typing import Any

import pytest

from persistence.file_handler import get_next_id


@pytest.mark.parametrize(
    "questions, expected",
    [
        ([], 1),
        ([{"id": 1}], 2),
        ([{"id": 1}, {"id": 3}, {"id": 2}], 4),
        ([{"text": "Question 1"}, {"id": 2}], 3),
        ([{"id": "5"}, {"id": None}, {"id": "not a number"}], 6),
        ([{"id": "3"}, {"text": "no id"}, {"id": 10}, {"id": "oops"}], 11),
        ([{"id": -1}, {"id": 0}, {"id": 2}], 3),
    ],
)
def test_get_next_id(questions: list[dict[str, Any]], expected: int):
    """Return the next id as max(valid ids) + 1 for various malformed inputs."""
    assert get_next_id(questions) == expected
