"""Tests for catalog-driven MIR reporter-template generation."""

import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import catalog  # noqa: E402
import render_reporter_template as renderer  # noqa: E402


def test_real_report_catalog_renders_strictly_and_idempotently():
    data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")

    first = renderer.render_reporter_template(data)
    second = renderer.render_reporter_template(data)

    assert first == second
    assert renderer.validate_reporter_template(data, first) == []
    assert first.endswith("\n")
    assert "[Availability]" in first
    assert "[Maintenance/Owner]" in first


def test_every_reporter_item_template_is_generated_once():
    data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    rendered = renderer.render_reporter_template(data).splitlines()

    for item in data["items"]:
        assert rendered.count(item["template"]) == 1


def test_reporter_document_uses_generated_literalinclude():
    document = (WORKSPACE_ROOT / "docs/MIR/mir-reporters-template.md").read_text(encoding="utf-8")

    assert "{literalinclude} mir-reporters-template-body.include" in document
    assert "[Availability]" not in document
