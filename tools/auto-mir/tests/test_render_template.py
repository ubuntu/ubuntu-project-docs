"""Tests for catalog-driven human template generation (both roles)."""

import sys
from pathlib import Path

import pytest

TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import catalog  # noqa: E402
import render_template as renderer  # noqa: E402


def _review_catalog(blueprint: list, checks: list[dict] | None = None) -> dict:
    return {
        "metadata": {"review_template_blueprint": blueprint},
        "checks": checks or [],
    }


def test_render_expands_check_refs_and_preserves_order_and_whitespace():
    data = _review_catalog(
        ["", "first  ", {"check": "SUM-1", "todo_ref": 0}, {"literal": "last"}],
        [{"id": "SUM-1", "todo_refs": ["TODO: selected"]}],
    )

    assert renderer.render_template(data, "review") == "\nfirst  \nTODO: selected\nlast\n"


@pytest.mark.parametrize(
    ("entry", "message"),
    [
        ({"check": "SUM-9", "todo_ref": 0}, "unknown check id"),
        ({"check": "SUM-1"}, "Invalid check-ref blueprint item"),
        ({"check": "SUM-1", "todo_ref": 5}, "out of range"),
        ({"check": "SUM-1", "todo_ref": 1}, "non-TODO entry"),
        ({"item": "REP-NOPE"}, "unknown item"),
        ({"bogus": 1}, "Invalid blueprint item"),
        (42, "Invalid blueprint item type"),
    ],
)
def test_render_rejects_invalid_blueprint_entries(entry, message):
    if isinstance(entry, dict) and "item" in entry:
        data = {
            "metadata": {"reporter_template_blueprint": [entry]},
            "items": [],
        }
        with pytest.raises(RuntimeError, match=message):
            renderer.render_template(data, "report")
    else:
        data = _review_catalog(
            [entry],
            [{"id": "SUM-1", "todo_refs": ["TODO: fine", "plain text"]}]
            if message == "non-TODO entry"
            else [{"id": "SUM-1", "todo_refs": ["TODO: fine"]}],
        )
        with pytest.raises(RuntimeError, match=message):
            renderer.render_template(data, "review")


def test_real_catalogs_render_idempotently():
    for role in ("review", "report"):
        data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, role)
        first = renderer.render_template(data, role)
        second = renderer.render_template(data, role)
        assert first == second
        assert first.endswith("\n")
        assert "[" in first  # section markers present


def test_reporter_strict_validation_checks_section_markers():
    data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    rendered = renderer.render_template(data, "report")
    assert renderer.validate_reporter_template(data, rendered) == []


def test_reporter_document_uses_generated_literalinclude():
    document = (WORKSPACE_ROOT / "docs/MIR/mir-reporters-template.md").read_text(encoding="utf-8")

    assert "{literalinclude} mir-reporters-template-body.include" in document
    assert "[Availability]" not in document
