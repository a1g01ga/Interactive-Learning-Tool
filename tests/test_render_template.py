"""Tests for llm.llm_client prompt template rendering.

This suite ensures that Jinja2 templates are rendered correctly from the
configured prompts directory and that missing templates raise a clear error.
"""

import os

import pytest

from config import PROMPTS_DIR
from llm.llm_client import _render_template


def test_render_template_success():
    """Render an ad-hoc template file and verify the substituted output."""
    template_name = "my_test_prompt.j2"
    template_path = PROMPTS_DIR
    template_content = "Hello {{ name }}!"

    os.makedirs(template_path, exist_ok=True)

    full_path = os.path.join(template_path, template_name)

    with open(full_path, "w", encoding="utf-8") as file:
        file.write(template_content)

    try:
        result = _render_template(template_name, name="Alice")
        assert result == "Hello Alice!"

    finally:
        if os.path.exists(full_path):
            os.remove(full_path)


def test_render_template_template_not_found():
    """Attempt to render a non-existing template and expect a RuntimeError."""
    missing_template_name = "non_existent_template.j2"
    missing_template_path = os.path.join(PROMPTS_DIR, missing_template_name)

    if os.path.exists(missing_template_path):
        os.remove(missing_template_path)

    with pytest.raises(RuntimeError, match="Prompt template not found"):
        _render_template(missing_template_name, name="Alice")
