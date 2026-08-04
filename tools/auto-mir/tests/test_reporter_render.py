"""Focused unit tests for reporter/render.py draft formatting helpers."""

import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from reporter.render import _with_hanging_indent  # noqa: E402


def test_with_hanging_indent_leaves_single_line_text_unchanged():
    assert _with_hanging_indent("- One-line statement.") == "- One-line statement."


def test_with_hanging_indent_indents_continuation_lines():
    text = "- First line of a multi-select answer.\n- Second option also selected."

    result = _with_hanging_indent(text)

    lines = result.split("\n")
    assert lines[0] == "- First line of a multi-select answer."
    assert lines[1] == "  - Second option also selected."


def test_with_hanging_indent_skips_blank_continuation_lines():
    text = "- First line.\n\n- Third line after a blank one."

    result = _with_hanging_indent(text)

    lines = result.split("\n")
    assert lines[1] == ""
    assert lines[2] == "  - Third line after a blank one."
