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
    assert "RULE: The security history and the current state of security issues" in first
    assert "RULE: The package must have an acceptable level of maintenance corresponding" in first


def test_reporter_template_never_leaks_rule_clause_tags():
    """RULE[<slug>] is a machine-readable coverage annotation only - it must
    never appear in the rendered, reporter-facing template text."""
    data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    rendered = renderer.render_reporter_template(data)

    assert "RULE[" not in rendered
    assert "RULE: - Non-obvious or non-properly commented lintian overrides" in rendered


def test_every_reporter_item_template_is_generated_once():
    """Every item the blueprint references must have its template (including
    restored multi-line historical trees) rendered exactly once. The
    blueprint is authoritative; runtime-only items may be absent."""
    data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    rendered = renderer.render_reporter_template(data)

    refs = [
        entry["item"]
        for entry in data["metadata"]["reporter_template_blueprint"]
        if isinstance(entry, dict)
    ]
    by_id = {item["id"]: item for item in data["items"]}
    assert refs
    for item_id in refs:
        assert rendered.count(by_id[item_id]["template"]) == 1, item_id


def test_reporter_document_uses_generated_literalinclude():
    document = (WORKSPACE_ROOT / "docs/MIR/mir-reporters-template.md").read_text(encoding="utf-8")

    assert "{literalinclude} mir-reporters-template-body.include" in document
    assert "[Availability]" not in document
