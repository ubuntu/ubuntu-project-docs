"""Characterization tests for Finding invariants and helper APIs."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import Finding


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
    finding = Finding.ok(_base_check(), "Package identified")

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
    finding = Finding.unknown(
        _base_check(),
        message="Could not evaluate due to adapter error",
        todo="TODO: Verify manually",
        adapter_error_cause=["lp-bug-api"],
    )

    assert finding.status == "unknown"
    assert finding.severity == "ok"
    assert finding.confidence == "low"
    assert finding.adapter_error_cause == ["lp-bug-api"]


def test_mark_unknown_without_todo_clears_todo_and_keeps_unknown_state():
    finding = Finding.ok(_base_check(), "Package identified")

    finding.mark_unknown("Evidence could not be collected")

    assert finding.status == "unknown"
    assert finding.severity == "ok"
    assert finding.confidence == "low"
    assert finding.todo == ""


def test_mark_unknown_prefixes_todo_and_allows_severity_override():
    finding = Finding.ok(_base_check(), "Package identified")

    finding.mark_unknown(
        message="Adapter failed",
        todo="Verify manually",
        severity="recommended",
    )

    assert finding.status == "unknown"
    assert finding.severity == "recommended"
    assert finding.todo.startswith("TODO:")
