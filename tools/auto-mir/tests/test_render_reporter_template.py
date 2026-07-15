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
    assert "RULE: Security history" in first
    assert "RULE: Every package needs an eligible owning team" in first


def test_every_reporter_item_template_is_generated_once():
    data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    rendered = renderer.render_reporter_template(data).splitlines()

    for item in data["items"]:
        assert rendered.count(item["template"]) == 1


def test_reporter_document_uses_generated_literalinclude():
    document = (WORKSPACE_ROOT / "docs/MIR/mir-reporters-template.md").read_text(encoding="utf-8")

    assert "{literalinclude} mir-reporters-template-body.include" in document
    assert "[Availability]" not in document


def test_reporter_template_covers_every_historic_policy_family_logically():
    data = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    rendered = renderer.render_reporter_template(data)

    required_policy_terms = {
        "Ubuntu demand",
        "main versus universe",
        "existing MIR",
        "binary promotion scope",
        "Security history",
        "full release lifetime",
        "privileged binaries",
        "Deprecated algorithms",
        "reasonable configuration",
        "important, old, critical",
        "exotic hardware",
        "non-trivial build-time test suite",
        "written test plan",
        "Minimal libraries",
        "upstream release mechanism",
        "correct Maintainer field",
        "obsolete dependencies",
        "debconf questions",
        "internationalization",
        "Runtime dependencies",
        "FHS or Debian Policy",
        "full support lifetime",
        "eligible owning team",
        "Static and vendored builds",
        "Rust packages",
        "build from the last three months",
        "team affected",
        "Package descriptions",
    }
    missing = sorted(term for term in required_policy_terms if term not in rendered)
    assert not missing, f"Reporter template misses historic policy families: {missing}"
