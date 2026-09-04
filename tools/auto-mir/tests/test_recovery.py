"""Tests for output-directory preflight, --recovery scanning, and resume."""

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import recovery  # noqa: E402
from reporter.models import StatementState  # noqa: E402
from utils import run_state  # noqa: E402


def _write_state(directory: Path, *, source_package="libfoo", bug_id="", render_done=False):
    state = {
        "schema_version": run_state.STATE_SCHEMA_VERSION,
        "meta": {
            "role": "report",
            "bug_id": bug_id,
            "source_package": source_package,
            "series": "devel",
            "source_pocket": "auto",
            "run_name": directory.name,
            "guest_name": "",
            "started_utc": "2026-09-04T00:00:00+00:00",
            "updated_utc": "2026-09-04T00:00:00+00:00",
        },
        "stages": {"evidence": "done"},
        "review": {"requested_binaries": [], "review_type": "fresh"},
        "report": {"item_values": {}, "results": {}, "prepared": {}},
    }
    if render_done:
        state["stages"]["render"] = "done"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / run_state.STATE_FILE).write_text(json.dumps(state), encoding="utf-8")
    (directory / "evidence.json").write_text(
        json.dumps({"adapters": {"lp-package-api": {"status": "ok"}}}), encoding="utf-8"
    )
    return state


def _always_interactive(monkeypatch):
    monkeypatch.setattr(recovery, "_interactive", lambda: True)


class _Answers:
    """ask_yes_no stub answering a scripted sequence."""

    def __init__(self, answers):
        self.answers = iter(answers)
        self.prompts = []

    def __call__(self, prompt, *, default=None, **_kwargs):
        self.prompts.append(prompt)
        return next(self.answers)


def test_classify_directory_statuses(tmp_path):
    missing = tmp_path / "missing"
    empty = tmp_path / "empty"
    empty.mkdir()

    assert recovery.classify_directory(missing)["status"] == "empty"
    assert recovery.classify_directory(empty)["status"] == "empty"

    completed = tmp_path / "mir-libfoo-completed"
    _write_state(completed, render_done=True)
    assert recovery.classify_directory(completed)["status"] == "completed"

    aborted = tmp_path / "mir-libfoo-aborted"
    _write_state(aborted)
    assert recovery.classify_directory(aborted)["status"] == "aborted"

    legacy = tmp_path / "mir-libfoo-legacy"
    legacy.mkdir()
    (legacy / "evidence.json").write_text("{}", encoding="utf-8")
    (legacy / "auto-mir.log").write_text("{}", encoding="utf-8")
    assert recovery.classify_directory(legacy)["status"] == "legacy-aborted"

    foreign = tmp_path / "unrelated"
    foreign.mkdir()
    (foreign / "something.txt").write_text("x", encoding="utf-8")
    assert recovery.classify_directory(foreign)["status"] == "foreign"


def test_preflight_empty_or_missing_directory_starts_a_fresh_run(tmp_path):
    assert (
        recovery.preflight_output_dir(tmp_path / "missing", role="report", subject="libfoo") is None
    )

    empty = tmp_path / "empty"
    empty.mkdir()
    assert recovery.preflight_output_dir(empty, role="report", subject="libfoo") is None


def test_preflight_completed_run_offers_overwrite(tmp_path, monkeypatch):
    _always_interactive(monkeypatch)
    completed = tmp_path / "mir-libfoo-done"
    _write_state(completed, render_done=True)
    answers = _Answers([False])
    monkeypatch.setattr(recovery, "ask_yes_no", answers)

    with pytest.raises(SystemExit):
        recovery.preflight_output_dir(completed, role="report", subject="libfoo")
    assert "overwrite with a full new run" in answers.prompts[0]

    answers = _Answers([True])
    monkeypatch.setattr(recovery, "ask_yes_no", answers)
    assert recovery.preflight_output_dir(completed, role="report", subject="libfoo") is None


def test_preflight_aborted_run_offers_continue(tmp_path, monkeypatch):
    _always_interactive(monkeypatch)
    aborted = tmp_path / "mir-libfoo-aborted"
    _write_state(aborted)
    answers = _Answers([True])
    monkeypatch.setattr(recovery, "ask_yes_no", answers)

    resumed = recovery.preflight_output_dir(aborted, role="report", subject="libfoo")

    assert resumed == aborted
    assert "continue with the remaining steps" in answers.prompts[0]

    # Declining exits early stating the output directory is not empty.
    answers = _Answers([False])
    monkeypatch.setattr(recovery, "ask_yes_no", answers)
    with pytest.raises(SystemExit):
        recovery.preflight_output_dir(aborted, role="report", subject="libfoo")


def test_preflight_mismatched_subject_offers_overwrite(tmp_path, monkeypatch):
    _always_interactive(monkeypatch)
    other = tmp_path / "mir-otherpkg-run"
    _write_state(other, source_package="otherpkg")
    answers = _Answers([False])
    monkeypatch.setattr(recovery, "ask_yes_no", answers)

    with pytest.raises(SystemExit):
        recovery.preflight_output_dir(other, role="report", subject="libfoo")
    assert "different bug/package" in answers.prompts[0]


def test_preflight_noninteractive_refuses_instead_of_prompting(tmp_path, monkeypatch):
    monkeypatch.setattr(recovery, "_interactive", lambda: False)
    aborted = tmp_path / "mir-libfoo-aborted"
    _write_state(aborted)

    with pytest.raises(SystemExit):
        recovery.preflight_output_dir(aborted, role="report", subject="libfoo")


def test_recovery_scan_offers_the_most_recent_aborted_run(tmp_path, monkeypatch):
    _always_interactive(monkeypatch)
    old = tmp_path / "mir-libfoo-a"
    new = tmp_path / "mir-libfoo-b"
    _write_state(old)
    _write_state(new)
    # Make the "b" run the most recent one.
    state_file = new / run_state.STATE_FILE
    state_file.write_text(state_file.read_text(encoding="utf-8"), encoding="utf-8")
    os.utime(state_file, (2_000_000_000, 2_000_000_000))
    answers = _Answers([True])
    monkeypatch.setattr(recovery, "ask_yes_no", answers)

    resumed = recovery.offer_recovery_scan(role="report", subject="libfoo", base=tmp_path)

    assert resumed == new


def test_recovery_scan_lists_runs_when_nothing_aborted(tmp_path, capsys):
    done = tmp_path / "mir-libfoo-done"
    _write_state(done, render_done=True)

    resumed = recovery.offer_recovery_scan(role="report", subject="libfoo", base=tmp_path)

    assert resumed is None
    out = capsys.readouterr().out
    assert str(done) in out
    assert "No aborted runs to recover have been found." in out


def test_recovery_scan_without_any_runs_says_so(tmp_path, capsys):
    resumed = recovery.offer_recovery_scan(role="report", subject="libfoo", base=tmp_path)

    assert resumed is None
    assert "No previous runs" in capsys.readouterr().out


def test_restore_statement_result_roundtrips_a_snapshot():
    data = {
        "id": "REP-X",
        "section": "Security",
        "state": "resolved",
        "readiness": "warning",
        "statement": "- A statement.",
        "selected_option": "opt-a",
        "provenance": "human",
        "evidence_refs": ["lp-package-api:history"],
        "answer_refs": ["REP-X"],
        "rationale": "Because.",
        "human_confirmed": True,
    }

    result = recovery.restore_statement_result(data)

    assert result.id == "REP-X"
    assert result.state == StatementState.RESOLVED
    assert result.statement == "- A statement."
    assert result.provenance is not None
    assert result.human_confirmed is True


def _resume_ctx(tmp_path, role="report"):
    return SimpleNamespace(
        role=role,
        output_dir=tmp_path,
        series=None,
        evidence={},
        requested_binaries=[],
        review_type="fresh",
        resumed_evidence=False,
        resumed_results=[],
        resumed_values=[],
        tool_root=TOOL_ROOT,
        workspace_root=WORKSPACE_ROOT,
    )


def test_apply_resume_restores_evidence_scope_and_report_results(tmp_path):
    import catalog as catalog_module

    directory = tmp_path
    state = _write_state(directory)
    state["report"]["results"] = {
        "REP-AVAIL-001": {
            "id": "REP-AVAIL-001",
            "section": "Availability",
            "state": "resolved",
            "readiness": "clear",
            "statement": "- The source package libfoo is published in Ubuntu (universe).",
            "provenance": "deterministic",
            "human_confirmed": False,
        }
    }
    state["report"]["item_values"] = {"REP-AVAIL-001": "- The source package libfoo is published."}
    (directory / run_state.STATE_FILE).write_text(json.dumps(state), encoding="utf-8")

    ctx = _resume_ctx(directory)
    recovery.apply_resume(ctx, json.loads((directory / run_state.STATE_FILE).read_text()))

    assert ctx.resumed_evidence is True
    assert ctx.evidence["adapters"]["lp-package-api"]["status"] == "ok"
    assert ctx.series == "devel"
    assert [result.id for result in ctx.resumed_results] == ["REP-AVAIL-001"]
    assert ctx.resumed_values["REP-AVAIL-001"].startswith("- The source package")
    # The catalog is loaded so evaluation (and restore ordering) works.
    assert ctx.catalog == catalog_module.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")


def test_apply_resume_restores_the_reviewer_scope(tmp_path):
    directory = tmp_path
    state = _write_state(directory)
    state["meta"]["role"] = "review"
    state["meta"]["bug_id"] = "12345"
    state["review"] = {"requested_binaries": ["libfoo-bin"], "review_type": "rereview"}
    (directory / run_state.STATE_FILE).write_text(json.dumps(state), encoding="utf-8")

    ctx = _resume_ctx(directory, role="review")
    recovery.apply_resume(ctx, json.loads((directory / run_state.STATE_FILE).read_text()))

    assert ctx.requested_binaries == ["libfoo-bin"]
    assert ctx.review_type == "rereview"


def test_apply_resume_rejects_answers_unknown_to_the_current_catalog(tmp_path):
    directory = tmp_path
    state = _write_state(directory)
    state["report"]["results"] = {
        "REP-GONE": {
            "id": "REP-GONE",
            "section": "Availability",
            "state": "resolved",
            "readiness": "clear",
            "statement": "- Whatever.",
            "provenance": "deterministic",
        }
    }
    (directory / run_state.STATE_FILE).write_text(json.dumps(state), encoding="utf-8")

    ctx = _resume_ctx(directory)
    with pytest.raises(recovery.RecoveryError) as excinfo:
        recovery.apply_resume(ctx, json.loads((directory / run_state.STATE_FILE).read_text()))

    assert "REP-GONE" in str(excinfo.value)


def test_apply_resume_rejects_missing_evidence_file(tmp_path):
    directory = tmp_path
    _write_state(directory)
    (directory / "evidence.json").unlink()

    ctx = _resume_ctx(directory)
    with pytest.raises(recovery.RecoveryError):
        recovery.apply_resume(ctx, json.loads((directory / run_state.STATE_FILE).read_text()))
