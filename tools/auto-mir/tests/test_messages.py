"""Tests for check message template rendering helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.messages import render_check_message, render_check_message_or_default


def test_render_check_message_strict_success():
    check = {
        "id": "DEP-3",
        "messages": {
            "ok_safe_message": "Auto-included binaries ({auto_included}) are safe",
        },
    }

    rendered = render_check_message(check, "ok_safe_message", auto_included="libfoo-dev")
    assert rendered == "Auto-included binaries (libfoo-dev) are safe"


def test_render_check_message_missing_template_key_raises():
    check = {"id": "DEP-3", "messages": {}}

    try:
        render_check_message(check, "ok_safe_message", auto_included="x")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "missing required message template" in str(exc)


def test_render_check_message_missing_placeholder_raises():
    check = {
        "id": "DEP-3",
        "messages": {
            "ok_safe_message": "Auto-included binaries ({auto_included}) are safe",
        },
    }

    try:
        render_check_message(check, "ok_safe_message")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "missing placeholder value" in str(exc)


def test_render_check_message_or_default_uses_default_when_unmigrated():
    check = {"id": "SEC-1"}

    rendered = render_check_message_or_default(
        check,
        "llm_unavailable_message",
        "LLM unavailable: boom",
        error="boom",
    )
    assert rendered == "LLM unavailable: boom"
