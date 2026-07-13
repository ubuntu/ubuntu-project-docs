"""Unit tests for the review draft renderer in render/__init__.py."""

import sys
from pathlib import Path
from unittest.mock import Mock

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Finding
from render import (
    _SECTION_ORDER,
    _build_binary_package_header,
    _build_review_draft,
    _build_review_type_line,
    _lint_review_draft,
    _render_section,
    _render_summary_section,
    _todo_lines_for_finding,
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
        check["section"] for check in catalog.get("checks", []) if check.get("section")
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
# _render_section — Left to decide omission
# ---------------------------------------------------------------------------


def test_render_section_omits_empty_left_to_decide():
    """A section with no undecided items must not print a 'Left to decide' line."""
    lines = _render_section("Dependencies", [_ok_finding()])
    text = "\n".join(lines)
    assert "Left to decide" not in text
    assert "Problems: none" in text


def test_render_section_shows_left_to_decide_when_present():
    """A section with an undecided item still renders the block with the TODO."""
    lines = _render_section("Dependencies", [_ok_finding(), _unresolved_finding()])
    text = "\n".join(lines)
    assert "Left to decide:" in text
    assert "TODO: - Manual check needed" in text


def test_render_section_never_emits_left_to_decide_none():
    """The meaningless 'Left to decide: None' line is never produced anymore."""
    lines = _render_section("Security", [_high_conf_failure()])
    assert "Left to decide: None" not in "\n".join(lines)


def test_render_section_blank_line_before_left_to_decide():
    """A blank line precedes 'Left to decide:' so it reads as its own block."""
    lines = _render_section("Dependencies", [_ok_finding(), _unresolved_finding()])
    idx = lines.index("Left to decide:")
    assert idx > 0
    assert lines[idx - 1] == "", (
        "Expected a blank line immediately before the 'Left to decide:' header"
    )


def test_render_summary_blank_lines_before_headers():
    """Summary headers each get a preceding blank line for readable flow."""
    ctx = Mock()
    ctx.evidence = {}
    summary_findings = [
        _ok_finding(fid="SUM-1", msg="reporter content found", section="Summary"),
        _unresolved_finding(fid="SUM-5", title="MIR team ACK/NACK", section="Summary"),
    ]
    required = _high_conf_failure(fid="CB-2", msg="does FTBFS", section="Common blockers")
    lines = _render_summary_section(summary_findings, summary_findings + [required], ctx)
    for header in ("Left to decide:", "Required TODOs:", "Recommended TODOs:"):
        idx = lines.index(header)
        assert idx > 0
        assert lines[idx - 1] == "", f"Expected a blank line immediately before '{header}'"


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
    assert any("libfoo1" in line and "libfoo-dev" in line for line in lines)


def test_binary_header_shows_component_split():
    ctx = _Ctx(
        all_binaries=["libfoo1", "libfoo-dev", "libfoo-doc"],
        promotion_candidates=["libfoo1"],
    )
    lines = _build_binary_package_header(ctx)
    split_line = next((line for line in lines if "Component split" in line), None)
    assert split_line is not None
    assert "libfoo1" in split_line
    assert "libfoo-dev" in split_line or "libfoo-doc" in split_line


def test_binary_header_no_split_when_all_need_promotion():
    ctx = _Ctx(
        all_binaries=["libfoo1", "libfoo-dev"],
        promotion_candidates=["libfoo1", "libfoo-dev"],
    )
    lines = _build_binary_package_header(ctx)
    assert not any("Component split" in line for line in lines)


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
            assert positions[current] < positions[next_section], (
                f"Section {current} should appear before {next_section}"
            )


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


# ---------------------------------------------------------------------------
# Summary TODO routing — no duplication between inline and consolidated blocks
# ---------------------------------------------------------------------------


def _summary_ctx_with_decision_finding():
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.bug_id = "1234567"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}
    ctx.findings = [
        # A Summary decision check (e.g. SUM-5 ACK/NACK) rendering reviewer
        # options inline. It must not be duplicated into Required TODOs.
        Finding(
            id="SUM-5",
            section="Summary",
            title="Overall ACK/NACK",
            mode="ai",
            status="unknown",
            severity="required",
            confidence="low",
            message="Need verdict",
            todo="TODO-A: MIR team ACK\nTODO-B: MIR team NACK",
            aggregate_todo=False,
        ),
    ]
    return ctx


def test_summary_decision_finding_not_duplicated_in_required_todos():
    """A Summary decision check renders inline only, never re-listed below."""
    ctx = _summary_ctx_with_decision_finding()
    draft = _build_review_draft(ctx)

    # The decision options must appear exactly once (in Left to decide), not
    # again under Required TODOs.
    assert draft.count("TODO-A: MIR team ACK") == 1
    assert draft.count("TODO-B: MIR team NACK") == 1


def test_summary_aggregate_todo_finding_surfaces_in_consolidated_block():
    """A Summary finding flagged aggregate_todo IS surfaced in the TODO blocks."""
    ctx = _summary_ctx_with_decision_finding()
    ctx.findings.append(
        Finding(
            id="SUM-4",
            section="Summary",
            title="Team bug subscriber present",
            mode="deterministic",
            status="not-ok",
            severity="recommended",
            confidence="high",
            message="Package does not have a team subscriber",
            todo="TODO: - The package should get a team bug subscriber before being promoted",
            aggregate_todo=True,
        )
    )
    draft = _build_review_draft(ctx)

    # The subscriber TODO belongs in the consolidated Recommended TODOs block.
    recommended_idx = draft.index("Recommended TODOs:")
    assert "team bug subscriber" in draft[recommended_idx:]


def test_security_finding_not_in_consolidated_todos_but_in_problems():
    """A confident [Security] failure surfaces in Security Problems, not TODOs.

    Security signals are evidence for the reviewer's 'needs a security review?'
    call, not action items for the reporter, so they must never appear in the
    Summary's Required/Recommended TODO blocks.
    """
    ctx = _summary_ctx_with_decision_finding()
    ctx.findings.append(
        Finding(
            id="SEC-5",
            section="Security",
            title="Parses untrusted data formats",
            mode="ev_to_ai",
            status="not-ok",
            severity="recommended",
            confidence="high",
            message="does parse data formats from an untrusted source",
            todo="TODO: - does parse data formats from an untrusted source",
            aggregate_todo=False,
        )
    )
    draft = _build_review_draft(ctx)

    # It renders in the [Security] section Problems block ...
    security_idx = draft.index("[Security]")
    assert "does parse data formats" in draft[security_idx:]

    # ... but must not appear in the Summary's consolidated TODO blocks, which
    # sit before the [Security] section in the draft.
    required_idx = draft.index("Required TODOs:")
    summary_todo_region = draft[required_idx:security_idx]
    assert "does parse data formats" not in summary_todo_region


def test_security_hard_blocker_not_in_consolidated_todos():
    """A required-severity [Security] finding (e.g. webkit) stays out of TODOs.

    Hard blockers still render in the Security Problems block and drive the
    verdict, but they are not duplicated into the consolidated reporter TODOs.
    """
    ctx = _summary_ctx_with_decision_finding()
    ctx.findings.append(
        Finding(
            id="SEC-3",
            section="Security",
            title="Uses webkit",
            mode="deterministic",
            status="not-ok",
            severity="required",
            confidence="high",
            message="webkit1/2 dependency found",
            todo="TODO: - webkit1/2 dependency must be removed before main inclusion",
            aggregate_todo=False,
        )
    )
    draft = _build_review_draft(ctx)

    security_idx = draft.index("[Security]")
    required_idx = draft.index("Required TODOs:")
    assert "webkit" not in draft[required_idx:security_idx]
    assert "webkit1/2 dependency found" in draft[security_idx:]


# ---------------------------------------------------------------------------
# Review type — preamble line and Summary note
# ---------------------------------------------------------------------------


def test_review_type_line_omitted_for_fresh():
    ctx = Mock()
    ctx.evidence = {"review_type": {"review_type": "fresh", "rationale": "normal"}}
    ctx.review_type = "fresh"
    assert _build_review_type_line(ctx) == ""


def test_review_type_line_present_for_rereview():
    ctx = Mock()
    ctx.evidence = {
        "review_type": {
            "review_type": "rereview",
            "rationale": "all binary packages are already in main",
        }
    }
    ctx.review_type = "rereview"
    line = _build_review_type_line(ctx)
    assert line.startswith("Review type: rereview")
    assert "voluntary re-review" in line
    assert "already in main" in line


def test_summary_note_for_reorg_review():
    ctx = _summary_ctx_with_decision_finding()
    ctx.evidence["review_type"] = {
        "review_type": "reorg",
        "rationale": "renamed source",
    }
    ctx.review_type = "reorg"
    draft = _build_review_draft(ctx)

    summary_idx = draft.index("[Summary]")
    required_idx = draft.index("Required TODOs:")
    note_region = draft[summary_idx:required_idx]
    assert "renamed/reorganised source" in note_region
    assert "non-blocking recommendations" in note_region
    # Preamble also carries the review-type line.
    assert "Review type: reorg" in draft[:summary_idx]


# ---------------------------------------------------------------------------
# Problems status sentinel
# ---------------------------------------------------------------------------


def test_clean_section_states_problems_none():
    """A non-summary section with no problems must explicitly say 'Problems: none'."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.bug_id = "1234567"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}
    ctx.findings = [_ok_finding(fid="DEP-1", section="Dependencies")]

    draft = _build_review_draft(ctx)

    assert "Problems: none" in draft
    # The 'none' sentinel must be preceded by a blank line for visual separation.
    lines = draft.splitlines()
    idx = lines.index("Problems: none")
    assert lines[idx - 1] == ""


def test_section_with_problem_has_no_none_sentinel():
    """A section that has a real problem shows the Problems list, not 'none'."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.bug_id = "1234567"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}
    ctx.findings = [_high_conf_failure(fid="SEC-7", section="Security")]

    draft = _build_review_draft(ctx)

    # Security section should list the problem and not claim 'Problems: none'.
    sec_idx = draft.index("[Security]")
    security_block = draft[sec_idx:]
    next_section = security_block.find("\n[", 1)
    security_only = security_block if next_section == -1 else security_block[:next_section]
    assert "webkit dependency found" in security_only
    assert "Problems: none" not in security_only


# ---------------------------------------------------------------------------
# Consolidated TODO numbering
# ---------------------------------------------------------------------------


def test_consolidated_todos_are_numbered_continuously():
    """Required and Recommended TODO items share one continuous #N index."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.bug_id = "1234567"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}
    ctx.findings = [
        _ok_finding(fid="SUM-1", section="Summary"),
        Finding(
            id="DEP-1",
            section="Dependencies",
            title="dep one",
            mode="deterministic",
            status="not-ok",
            severity="required",
            confidence="high",
            message="dep one problem",
            todo="TODO: - fix dependency one",
        ),
        Finding(
            id="DEP-2",
            section="Dependencies",
            title="dep two",
            mode="deterministic",
            status="not-ok",
            severity="required",
            confidence="high",
            message="dep two problem",
            todo="TODO: - fix dependency two",
        ),
        Finding(
            id="PRF-3",
            section="Packaging red flags",
            title="watch",
            mode="deterministic",
            status="not-ok",
            severity="recommended",
            confidence="medium",
            message="watch problem",
            todo="TODO: - add debian/watch",
        ),
    ]

    draft = _build_review_draft(ctx)

    assert "- #1 fix dependency one" in draft
    assert "- #2 fix dependency two" in draft
    # Numbering continues into the Recommended block.
    assert "- #3 add debian/watch" in draft
    rec_idx = draft.index("Recommended TODOs:")
    assert "- #3 add debian/watch" in draft[rec_idx:]


def test_strip_todo_prefix_variants():
    from render import _strip_todo_prefix

    assert _strip_todo_prefix("TODO: - foo") == "foo"
    assert _strip_todo_prefix("TODO: foo") == "foo"
    assert _strip_todo_prefix("TODO-A: foo") == "foo"
    assert _strip_todo_prefix("plain text") == "plain text"


def test_sum4_ok_message_visible_in_summary():
    """When a team subscriber is present, SUM-4's OK statement shows in Summary."""
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.bug_id = "1234567"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}
    ctx.findings = [
        Finding(
            id="SUM-4",
            section="Summary",
            title="Team bug subscriber present",
            mode="deterministic",
            status="ok",
            severity="ok",
            confidence="high",
            message="Package has team subscriber(s): foo-team",
            todo="",
            aggregate_todo=True,
        ),
    ]

    draft = _build_review_draft(ctx)

    summary_idx = draft.index("[Summary]")
    summary_block = draft[summary_idx:]
    assert "Package has team subscriber(s): foo-team" in summary_block


# ---------------------------------------------------------------------------
# Three-path model: outcome classification, negation, rationale continuation
# ---------------------------------------------------------------------------


def _catalog_ctx(findings, checks):
    ctx = Mock()
    ctx.source_package = "testpkg"
    ctx.bug_id = "1234567"
    ctx.series = "noble"
    ctx.evidence = {"adapters": {}}
    ctx.catalog = {"checks": checks}
    ctx.findings = findings
    return ctx


def test_outcome_class_deterministic_not_ok_is_problem():
    from render import finding_outcome_class

    f = _high_conf_failure()
    assert finding_outcome_class(f) == "problem"


def test_outcome_class_ai_medium_not_ok_is_undecided():
    from render import finding_outcome_class

    f = Finding(
        id="SEC-5",
        section="Security",
        title="parse untrusted",
        mode="ev_to_ai",
        status="not-ok",
        severity="recommended",
        confidence="medium",
        message="might parse untrusted data",
        todo="TODO: - does not parse data formats from an untrusted source",
    )
    assert finding_outcome_class(f) == "undecided"


def test_outcome_class_ai_high_not_ok_is_problem():
    from render import finding_outcome_class

    f = Finding(
        id="SEC-5",
        section="Security",
        title="parse untrusted",
        mode="ev_to_ai",
        status="not-ok",
        severity="required",
        confidence="high",
        message="parses untrusted data",
        todo="TODO: - does not parse data formats from an untrusted source",
    )
    assert finding_outcome_class(f) == "problem"


def test_undecided_finding_keeps_statement_and_adds_cant_decide_rationale():
    """Feedback #2: an undecided item keeps its original TODO statement and the
    reasoning is carried as a 'Can't decide:' continuation line."""
    finding = Finding(
        id="URF-1",
        section="Upstream red flags",
        title="No build errors or warnings",
        mode="deterministic",
        status="unknown",
        severity="recommended",
        confidence="medium",
        message="Build log contains 57 toolchain warning(s)",
        todo="TODO: - no Errors/warnings during the build",
        rationale="review 57 build warning(s) and decide if acceptable: threadpool.h deprecated",
    )
    lines = _render_section("Upstream red flags", [finding])
    text = "\n".join(lines)
    assert "TODO: - no Errors/warnings during the build" in text
    assert "(Can't decide: review 57 build warning(s)" in text


def test_problem_finding_uses_negated_statement_with_rationale():
    """Feedback #4/#5: a confirmed problem is phrased with the negated statement
    and carries its evidence as a parenthetical."""
    checks = [
        {"id": "CB-1", "section": "Common blockers", "negated_statement": "does FTBFS currently"}
    ]
    finding = Finding(
        id="CB-1",
        section="Common blockers",
        title="Does not FTBFS currently",
        mode="deterministic",
        status="not-ok",
        severity="required",
        confidence="high",
        message="Launchpad build state shows failures: s390x: Dependency wait",
        todo="TODO: - does not FTBFS currently",
    )
    checks_by_id = {c["id"]: c for c in checks}
    lines = _render_section("Common blockers", [finding], checks_by_id)
    text = "\n".join(lines)
    assert "- does FTBFS currently" in text
    assert "(Launchpad build state shows failures: s390x: Dependency wait)" in text
    # The pass-oriented template line must not leak into the Problems block.
    assert "does not FTBFS currently" not in text


def test_undecided_ai_finding_not_duplicated_in_summary_todos():
    """Feedback #3: a medium-confidence AI failure lives in its section's
    'Left to decide' only and is never surfaced as a Summary TODO."""
    checks = [{"id": "SEC-5", "section": "Security"}]
    findings = [
        _ok_finding(fid="SUM-1", section="Summary"),
        Finding(
            id="SEC-5",
            section="Security",
            title="parse untrusted",
            mode="ev_to_ai",
            status="not-ok",
            severity="recommended",
            confidence="medium",
            message="might parse untrusted data",
            todo="TODO: - does not parse data formats from an untrusted source",
            rationale="the library decodes AV1 bitstreams",
        ),
    ]
    ctx = _catalog_ctx(findings, checks)
    draft = _build_review_draft(ctx)

    # Present once, in the Security section's Left to decide.
    assert draft.count("does not parse data formats from an untrusted source") == 1
    # The Summary's Recommended TODOs block (bounded by the next section header)
    # must not re-list the undecided item.
    rec_idx = draft.index("Recommended TODOs:")
    summary_todo_block = draft[rec_idx : draft.index("[", rec_idx)]
    assert "parse data formats" not in summary_todo_block


def test_problem_finding_negated_statement_surfaces_in_summary_todo():
    """A confident problem is surfaced as a Summary TODO using its negated
    statement plus rationale, continuously numbered."""
    checks = [
        {"id": "CB-1", "section": "Common blockers", "negated_statement": "does FTBFS currently"}
    ]
    findings = [
        _ok_finding(fid="SUM-1", section="Summary"),
        Finding(
            id="CB-1",
            section="Common blockers",
            title="Does not FTBFS currently",
            mode="deterministic",
            status="not-ok",
            severity="required",
            confidence="high",
            message="Launchpad build state shows failures: s390x: Dependency wait",
            todo="TODO: - does not FTBFS currently",
        ),
    ]
    ctx = _catalog_ctx(findings, checks)
    draft = _build_review_draft(ctx)

    req_idx = draft.index("Required TODOs:")
    req_block = draft[req_idx:]
    assert "- #1 does FTBFS currently" in req_block
    assert "s390x: Dependency wait" in req_block


def test_preamble_shows_analysed_version_and_pocket():
    """Feedback #7: the draft preamble states which version/pocket was analysed."""
    ctx = Mock()
    ctx.source_package = "libgav1"
    ctx.bug_id = "2158712"
    ctx.series = "devel"
    ctx.catalog = {"checks": []}
    ctx.evidence = {
        "adapters": {
            "packaging-source": {
                "status": "ok",
                "analyzed_version": "0.20.0-2ubuntu1",
                "analyzed_pocket": "proposed",
            }
        }
    }
    ctx.findings = []

    draft = _build_review_draft(ctx)
    assert "Analysed source version: 0.20.0-2ubuntu1 (proposed pocket)" in draft


def test_preamble_omits_version_line_when_unknown():
    ctx = Mock()
    ctx.source_package = "libgav1"
    ctx.bug_id = "2158712"
    ctx.series = "devel"
    ctx.catalog = {"checks": []}
    ctx.evidence = {"adapters": {}}
    ctx.findings = []

    draft = _build_review_draft(ctx)
    assert "Analysed source version" not in draft
