"""Unit tests for the review draft renderer in render/__init__.py."""

import sys
from pathlib import Path
from unittest.mock import Mock

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Finding
from render import (
    _lint_review_draft,
    _todo_lines_for_finding,
    _build_binary_package_header,
    _build_review_draft,
    _SECTION_ORDER,
)

# ---------------------------------------------------------------------------
# Catalog section cross-check
# ---------------------------------------------------------------------------

_CATALOG_PATH = Path(__file__).resolve().parent.parent / "catalog.yaml"


def test_section_order_covers_all_catalog_sections():
    """Every section name used in catalog.yaml checks must appear in _SECTION_ORDER.

    This prevents silent drift: adding a new section to the catalog without
    updating _SECTION_ORDER would cause those checks to be appended under a
    separate ad-hoc heading in the review draft rather than in the intended order.
    """
    with _CATALOG_PATH.open(encoding="utf-8") as fh:
        catalog = yaml.safe_load(fh)

    catalog_sections = {
        check["section"]
        for check in catalog.get("checks", [])
        if check.get("section")
    }

    missing = catalog_sections - set(_SECTION_ORDER)
    assert not missing, (
        f"These catalog sections are not in render._SECTION_ORDER and would be "
        f"silently appended as 'Other': {sorted(missing)}\n"
        f"Add them to _SECTION_ORDER in render/__init__.py in the correct position."
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok_finding(fid="TST-1", msg="everything is fine", section="Dependencies"):
    return Finding(
        id=fid,
        section=section,
        title="Test check",
        mode="deterministic",
        status="ok",
        severity="ok",
        confidence="high",
        message=msg,
        todo="",
        evidence_refs=[],
    )


def _unresolved_finding(fid="TST-2", title="Manual check needed", section="Dependencies"):
    return Finding(
        id=fid,
        section=section,
        title=title,
        mode="ai",
        status="unknown",
        severity="recommended",
        confidence="low",
        message="Need human judgment",
        todo=f"TODO: - {title}",
        evidence_refs=[],
    )


def _high_conf_failure(fid="TST-3", msg="webkit dependency found", section="Security"):
    return Finding(
        id=fid,
        section=section,
        title="webkit check",
        mode="deterministic",
        status="not-ok",
        severity="required",
        confidence="high",
        message=msg,
        todo="",
        evidence_refs=[],
    )


# ---------------------------------------------------------------------------
# _todo_lines_for_finding
# ---------------------------------------------------------------------------


def test_todo_lines_already_prefixed():
    finding = _unresolved_finding()
    finding.todo = "TODO: - check the thing"
    lines = _todo_lines_for_finding(finding)
    assert lines == ["TODO: - check the thing"]


def test_todo_lines_option_variants():
    finding = _unresolved_finding()
    finding.todo = "TODO-A: MIR team ACK\nTODO-B: MIR team NACK"
    lines = _todo_lines_for_finding(finding)
    assert lines == ["TODO-A: MIR team ACK", "TODO-B: MIR team NACK"]


def test_todo_lines_no_double_prefix():
    finding = _unresolved_finding()
    finding.todo = "TODO: TODO-A: some option"
    lines = _todo_lines_for_finding(finding)
    # Should strip the outer TODO: prefix
    assert lines == ["TODO-A: some option"]


def test_todo_lines_bare_text_gets_prefixed():
    finding = _unresolved_finding()
    finding.todo = "check the upstream tracker"
    lines = _todo_lines_for_finding(finding)
    assert lines[0].startswith("TODO:")


# ---------------------------------------------------------------------------
# _lint_review_draft — structural correctness
# ---------------------------------------------------------------------------


def _make_clean_draft():
    return "\n".join(
        [
            "Review for Source Package: mypkg",
            "Launchpad bug: https://bugs.launchpad.net/bugs/12345",
            "Target series: noble",
            "",
            "[Dependencies]",
            "OK:",
            "- everything is fine",
            "Left to decide: None",
            "",
            "[Security]",
            "Problems:",
            "- webkit dependency found",
            "Left to decide: None",
            "",
        ]
    )


def test_lint_passes_clean_draft():
    # Should not raise
    _lint_review_draft(_make_clean_draft(), [])


def test_lint_rejects_rule_line():
    draft = "RULE: This must not appear in output\n"
    try:
        _lint_review_draft(draft, [])
        assert False, "Should have raised"
    except ValueError as exc:
        assert "RULE" in str(exc)


def test_lint_rejects_todo_in_problems_block():
    draft = "\n".join(
        [
            "[Security]",
            "Problems:",
            "TODO: - this should not be here",
        ]
    )
    try:
        _lint_review_draft(draft, [])
        assert False, "Should have raised"
    except ValueError as exc:
        assert "Problems block" in str(exc)


def test_lint_rejects_non_todo_in_undecided_block():
    draft = "\n".join(
        [
            "[Security]",
            "Left to decide:",
            "- this line has no TODO prefix",
        ]
    )
    try:
        _lint_review_draft(draft, [])
        assert False, "Should have raised"
    except ValueError as exc:
        assert "Left to decide" in str(exc)


def test_lint_accepts_note_in_undecided_block():
    draft = "\n".join(
        [
            "[Security]",
            "Left to decide:",
            "NOTE: - adapter failed, left for manual follow-up",
            "TODO: - check the thing",
        ]
    )
    _lint_review_draft(draft, [])  # must not raise


def test_lint_rejects_ok_finding_with_todo_message():
    findings = [_ok_finding(msg="TODO: should not happen")]
    try:
        _lint_review_draft("", findings)
        assert False, "Should have raised"
    except ValueError as exc:
        assert "must not render as TODO" in str(exc)


def test_lint_rejects_unresolved_finding_without_todo():
    finding = _unresolved_finding()
    finding.todo = "plain text without prefix"
    try:
        _lint_review_draft("", [finding])
        assert False, "Should have raised"
    except ValueError as exc:
        assert "must include TODO" in str(exc)


# ---------------------------------------------------------------------------
# _build_binary_package_header
# ---------------------------------------------------------------------------


class _Ctx:
    def __init__(self, *, all_binaries=None, promotion_candidates=None):
        dep_status = "ok" if all_binaries is not None else "error"
        self.evidence = {
            "adapters": {
                "dep-analysis": {
                    "status": dep_status,
                    "binary_packages": all_binaries or [],
                },
                "component-mismatches": {
                    "status": "ok",
                    "promotion_candidates": promotion_candidates or [],
                },
            }
        }


def test_binary_header_empty_when_no_data():
    ctx = _Ctx(all_binaries=[], promotion_candidates=[])
    assert _build_binary_package_header(ctx) == []


def test_binary_header_lists_all_binaries():
    ctx = _Ctx(all_binaries=["libfoo1", "libfoo-dev"])
    lines = _build_binary_package_header(ctx)
    assert any("libfoo1" in l and "libfoo-dev" in l for l in lines)


def test_binary_header_shows_component_split():
    ctx = _Ctx(
        all_binaries=["libfoo1", "libfoo-dev", "libfoo-doc"],
        promotion_candidates=["libfoo1"],
    )
    lines = _build_binary_package_header(ctx)
    split_line = next((l for l in lines if "Component split" in l), None)
    assert split_line is not None
    assert "libfoo1" in split_line
    assert "libfoo-dev" in split_line or "libfoo-doc" in split_line


def test_binary_header_no_split_when_all_need_promotion():
    ctx = _Ctx(
        all_binaries=["libfoo1", "libfoo-dev"],
        promotion_candidates=["libfoo1", "libfoo-dev"],
    )
    lines = _build_binary_package_header(ctx)
    assert not any("Component split" in l for l in lines)


# ---------------------------------------------------------------------------
# Snapshot tests for complete review draft
# ---------------------------------------------------------------------------


def test_build_review_draft_complete_structure():
    """Test that a complete review draft has the expected structure."""
    # Create a mock context with findings
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.bug_id = "1234567"
    ctx.series = "noble"
    ctx.evidence = {
        "adapters": {
            "dep-analysis": {
                "status": "ok",
                "binary_packages": ["testpkg", "testpkg-dev"],
            },
            "component-mismatches": {
                "status": "ok",
                "promotion_candidates": ["testpkg"],
            },
        }
    }
    
    # Create sample findings
    ctx.findings = [
        Finding(
            id="SUM-1",
            section="Summary",
            title="Source package identified",
            mode="deterministic",
            status="ok",
            severity="ok",
            confidence="high",
            message="Source package: testpkg",
            todo="",
            evidence_refs=["lp-bug-api:source_package"],
        ),
        Finding(
            id="DEP-1",
            section="Dependencies",
            title="Runtime dependencies in main",
            mode="deterministic",
            status="not-ok",
            severity="required",
            confidence="high",
            message="Runtime dependency 'libbar' not in main",
            todo="TODO: - Promote libbar to main or remove dependency",
            evidence_refs=["dep-analysis:runtime_deps"],
        ),
        Finding(
            id="SEC-1",
            section="Security",
            title="CVE analysis",
            mode="deterministic",
            status="unknown",
            severity="ok",
            confidence="low",
            message="Could not evaluate: adapter failed",
            todo="TODO: - Manually check CVE database",
            adapter_error_cause=["ubuntu-cve-tracker"],
        ),
    ]
    
    draft = _build_review_draft(ctx)
    
    # Verify structure
    assert "[Summary]" in draft
    assert "[Dependencies]" in draft
    assert "[Security]" in draft
    assert "Source package: testpkg" in draft
    assert "Runtime dependency 'libbar' not in main" in draft
    assert "TODO: - Manually check CVE database" in draft


def test_build_review_draft_section_order():
    """Test that sections appear in canonical order."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.bug_id = "1234567"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}
    
    # Create findings for all sections (in reverse order)
    ctx.findings = [
        Finding(
            id=f"TEST-{i}",
            section=section,
            title=f"Test {section}",
            mode="deterministic",
            status="ok",
            severity="ok",
            confidence="high",
            message=f"Test message for {section}",
            todo="",
            evidence_refs=[],
        )
        for i, section in enumerate(reversed(_SECTION_ORDER))
    ]
    
    draft = _build_review_draft(ctx)
    
    # Verify sections appear in canonical order
    positions = {section: draft.find(f"[{section}]") for section in _SECTION_ORDER}
    
    # Check that each section appears after the previous one
    for i in range(len(_SECTION_ORDER) - 1):
        current = _SECTION_ORDER[i]
        next_section = _SECTION_ORDER[i + 1]
        if positions[current] != -1 and positions[next_section] != -1:
            assert positions[current] < positions[next_section], \
                f"Section {current} should appear before {next_section}"


def test_build_review_draft_empty_findings():
    """Test that an empty findings list produces a valid draft."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.bug_id = "1234567"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}
    ctx.findings = []
    
    draft = _build_review_draft(ctx)
    
    # Should still have preamble
    assert "Source Package: testpkg" in draft
    assert "1234567" in draft
    assert "noble" in draft
