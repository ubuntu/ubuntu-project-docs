"""Characterization tests for Finding invariants and helper APIs."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Finding


def _finding(
    status="ok", severity="ok", confidence="high", message="Package identified", todo="", **extra
):
    """Direct-construction replacement for the removed Finding.ok/not_ok/unknown
    factory classmethods: tests exercise the dataclass, not convenience wrappers."""
    fields = dict(
        id="SUM-1",
        section="Summary",
        title="Source package identified",
        mode="deterministic",
        blocker_class="none",
        status=status,
        severity=severity,
        confidence=confidence,
        message=message,
        todo=todo,
    )
    fields.update(extra)
    return Finding(**fields)


def _base_check() -> dict:
    return {
        "id": "SUM-1",
        "section": "Summary",
        "title": "Source package identified",
        "mode": "deterministic",
        "blocker_class": "none",
    }


def test_finding_rejects_ok_status_with_non_ok_severity():
    with pytest.raises(ValueError, match="status='ok' requires severity='ok'"):
        Finding(
            id="SUM-1",
            section="Summary",
            title="Source package identified",
            mode="deterministic",
            status="ok",
            severity="required",
        )


def test_finding_rejects_invalid_status_enum():
    with pytest.raises(ValueError, match="invalid status"):
        Finding(
            id="SUM-1",
            section="Summary",
            title="Source package identified",
            mode="deterministic",
            status="broken",
        )


def test_fail_helper_prefixes_todo_and_updates_state():
    finding = _finding()

    finding.fail(
        message="Missing requirement",
        todo="Confirm missing requirement with reviewer",
        severity="required",
        confidence="high",
    )

    assert finding.status == "not-ok"
    assert finding.severity == "required"
    assert finding.todo.startswith("TODO:")


def test_unknown_factory_sets_low_confidence_and_adapter_error_cause():
    finding = _finding(
        status="unknown",
        confidence="low",
        message="Could not evaluate due to adapter error",
        todo="TODO: Verify manually",
        adapter_error_cause=["lp-bug-api"],
    )

    assert finding.status == "unknown"
    assert finding.severity == "ok"
    assert finding.confidence == "low"
    assert finding.adapter_error_cause == ["lp-bug-api"]


def test_mark_unknown_without_todo_clears_todo_and_keeps_unknown_state():
    finding = _finding()

    finding.mark_unknown("Evidence could not be collected")

    assert finding.status == "unknown"
    assert finding.severity == "ok"
    assert finding.confidence == "low"
    assert finding.todo == ""


def test_mark_unknown_prefixes_todo_and_allows_severity_override():
    finding = _finding()

    finding.mark_unknown(
        message="Adapter failed",
        todo="Verify manually",
        severity="recommended",
    )

    assert finding.status == "unknown"
    assert finding.severity == "recommended"
    assert finding.todo.startswith("TODO:")


def test_ensure_todo_sets_fallback_for_unresolved_without_todo_prefix():
    finding = _finding()
    finding.fail(
        message="Needs review",
        todo="not prefixed",
        severity="recommended",
        confidence="low",
    )
    finding.todo = "not prefixed"

    finding.ensure_todo("Source package identified")

    assert finding.todo == "TODO: - Source package identified"


def test_ensure_todo_is_noop_for_ok_findings():
    finding = _finding()

    finding.ensure_todo("Source package identified")

    assert finding.todo == ""


def test_fail_preserves_todo_ref_variant_without_double_prefix():
    finding = _finding()

    finding.fail(
        message="Needs follow-up",
        todo="TODO-B: Reviewer selects option B",
        severity="recommended",
    )

    assert finding.todo == "TODO-B: Reviewer selects option B"


def test_apply_ai_metadata_sets_non_empty_payload_fields_and_confirmation():
    finding = _finding()

    finding.apply_ai_metadata(
        risk_flags=["security-review-needed"],
        evidence_refs=["lp-bug-api:description"],
        human_confirmation_required=True,
    )

    assert finding.risk_flags == ["security-review-needed"]
    assert finding.evidence_refs == ["lp-bug-api:description"]
    assert finding.human_confirmation_required is True


def test_apply_ai_metadata_keeps_existing_values_for_empty_payload_fields():
    finding = _finding()
    finding.risk_flags = ["preexisting-flag"]
    finding.evidence_refs = ["preexisting:ref"]

    finding.apply_ai_metadata(
        risk_flags=[],
        evidence_refs=[],
        human_confirmation_required=False,
    )

    assert finding.risk_flags == ["preexisting-flag"]
    assert finding.evidence_refs == ["preexisting:ref"]
    assert finding.human_confirmation_required is False
