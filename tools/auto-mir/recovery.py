"""Preflight and resume support for runs in existing output directories.

Feedback item 2: a run that crashed or was interrupted must be resumable
from its output directory - the reporter never re-inputs what they already
answered, and the tool never re-runs the expensive steps (LXD guest +
evidence collection) it already completed.

Two entry points, both called from ``auto_mir.main`` before any run state
is created:

* ``preflight_output_dir`` classifies an explicitly requested
  ``--output-dir`` (completed / aborted / legacy / foreign / empty) and
  asks the reporter whether to overwrite or continue, per the agreed
  wording.
* ``offer_recovery_scan`` scans the default output paths for the most
  recent run of this bug/package and offers to continue it when it
  aborted; otherwise it lists what was found and says no aborted runs to
  recover have been found.

``apply_resume`` then restores the persisted progress onto the fresh
run context: collected evidence (so no guest is needed at all), the
reporter's answered statement results, and the reviewer's promotion
scope.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

from utils import run_state
from utils.cli import ask_yes_no

if TYPE_CHECKING:
    from auto_mir import RunContext

# Where run output directories live by default (RunContext's default base).
DEFAULT_OUTPUT_BASE = Path("/tmp")

_STATUS_LABELS = {
    "completed": "completed run",
    "aborted": "aborted run",
    "legacy-aborted": "aborted run (pre-recovery-state tool version)",
    "mismatched": "a run for a different bug/package",
    "foreign": "no recognizable auto-mir run",
}


class RecoveryError(RuntimeError):
    """A resume could not be applied; the message tells the user what to do."""


def _interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _decline(directory: Path) -> None:
    print(f"Refusing to continue: the output directory is not empty: {directory}")
    raise SystemExit(1)


def _meta_matches(state: dict[str, Any], *, role: str, subject: str) -> bool:
    """Whether a run state belongs to the subject the user is asking about.

    Role-aware: a review run's identity is its bug id (its resolved source
    package is metadata, not a CLI argument); a report run's identity is
    the source package.
    """
    meta = state.get("meta", {})
    if role == "review":
        return meta.get("bug_id", "") == subject
    return meta.get("source_package", "") == subject


def classify_directory(directory: Path) -> dict[str, Any]:
    """Classify one output directory's contents for the preflight.

    Returns ``{"status": ..., "state": <run state or None>}`` with status one
    of ``empty``, ``completed``, ``aborted``, ``legacy-aborted`` (evidence
    and log from a tool version without run state - resumable from the
    evidence boundary only), ``mismatched`` (a run for a different
    bug/package), or ``foreign`` (unrecognized non-empty content).
    """
    if not directory.is_dir() or not any(directory.iterdir()):
        return {"status": "empty", "state": None}
    state = run_state.load_state(directory)
    if state is not None:
        if state.get("stages", {}).get("render") == "done":
            return {"status": "completed", "state": state}
        return {"status": "aborted", "state": state}
    if (directory / "evidence.json").exists() and (directory / "auto-mir.log").exists():
        return {"status": "legacy-aborted", "state": None}
    return {"status": "foreign", "state": None}


def preflight_output_dir(directory: Path, *, role: str, subject: str, alerter=None) -> Path | None:
    """Handle an explicitly requested ``--output-dir`` that already exists.

    Returns the directory to resume, or ``None`` for a full new run.
    Exits (status 1) whenever continuing is not possible or the user
    declines: the reporter must never be surprised by a silently reused or
    overwritten directory.
    """
    classification = classify_directory(directory)
    status = classification["status"]
    state = classification["state"]

    if status == "empty":
        return None

    if state is not None and not _meta_matches(state, role=role, subject=subject):
        status = "mismatched"

    if not _interactive():
        print(
            f"Cannot ask how to handle {directory} ({_STATUS_LABELS.get(status, status)}): "
            "no interactive terminal. Rerun with an empty/new --output-dir, or remove "
            "the directory contents first."
        )
        raise SystemExit(1)

    if status == "completed" or status == "mismatched":
        detail = " for a different bug/package" if status == "mismatched" else ""
        if not ask_yes_no(
            f"{directory} already contains a run{detail}, should I overwrite with a full new run?"
        ):
            _decline(directory)
        return None

    if status in {"aborted", "legacy-aborted"}:
        if not ask_yes_no(
            f"{directory} already contains a run, should I continue with the remaining steps?",
            alerter=alerter,
        ):
            _decline(directory)
        return directory

    # foreign: non-empty, but nothing resumable lives in it.
    if not ask_yes_no(
        f"{directory} is not empty and holds no recognizable auto-mir run, "
        "should I overwrite with a full new run?",
        alerter=alerter,
    ):
        _decline(directory)
    return None


def _scan_runs(base: Path, *, role: str, subject: str) -> list[tuple[Path, str, float]]:
    """Return (directory, status, recency) for every run of this subject."""
    runs: list[tuple[Path, str, float]] = []
    if not base.is_dir():
        return runs
    for directory in base.glob(f"mir-{subject}-*"):
        if not directory.is_dir():
            continue
        classification = classify_directory(directory)
        if classification["status"] == "empty":
            continue
        state = classification["state"]
        if state is not None and not _meta_matches(state, role=role, subject=subject):
            continue
        marker = directory / run_state.STATE_FILE
        if not marker.exists():
            marker = directory / "evidence.json"
        recency = marker.stat().st_mtime if marker.exists() else directory.stat().st_mtime
        runs.append((directory, classification["status"], recency))
    return runs


def offer_recovery_scan(
    *, role: str, subject: str, base: Path = DEFAULT_OUTPUT_BASE, alerter=None
) -> Path | None:
    """Scan the default output paths for the most recent run of this subject.

    Offers to continue it when it aborted; otherwise lists what was found
    and tells the user no aborted runs to recover have been found. Returns
    the directory to resume, or ``None`` (the caller starts a fresh run).
    """
    runs = _scan_runs(base, role=role, subject=subject)
    if not runs:
        print(f"No previous runs for {subject} were found under {base}.")
        return None

    runs.sort(key=lambda entry: entry[2])
    newest_dir, newest_status, _ = runs[-1]

    if newest_status in {"aborted", "legacy-aborted"}:
        if not _interactive():
            print(
                f"The most recent run for {subject} aborted: {newest_dir}\n"
                "Cannot ask whether to continue it: no interactive terminal. "
                "Rerun with '--output-dir "
                f"{newest_dir}' from an interactive terminal to resume it."
            )
            raise SystemExit(1)
        if ask_yes_no(
            f"{newest_dir} is the most recent run for {subject} "
            "(it aborted), should I recover and continue with the remaining steps?",
            alerter=alerter,
        ):
            return newest_dir
        print("No recovery performed. Exiting.")
        raise SystemExit(1)

    for directory, status, _ in runs:
        print(f"  {directory} ({_STATUS_LABELS[status]})")
    older_aborted = [entry for entry in runs[:-1] if entry[1] in {"aborted", "legacy-aborted"}]
    if older_aborted:
        print(
            "The most recent run did not abort, so no aborted runs to recover "
            "have been selected; to resume an older aborted run anyway, rerun "
            "with an explicit --output-dir pointing at it."
        )
    else:
        print("No aborted runs to recover have been found.")
    return None


def restore_statement_result(data: dict[str, Any]):
    """Rebuild one persisted ``StatementResult`` snapshot."""
    from reporter.models import Provenance, ReadinessEffect, StatementResult, StatementState

    provenance = data.get("provenance")
    return StatementResult(
        id=str(data.get("id", "")),
        section=str(data.get("section", "")),
        state=StatementState(str(data.get("state", StatementState.NEEDS_INPUT.value))),
        readiness=ReadinessEffect(str(data.get("readiness", ReadinessEffect.CLEAR.value))),
        statement=str(data.get("statement", "")),
        selected_option=data.get("selected_option"),
        provenance=Provenance(str(provenance)) if provenance else None,
        evidence_refs=[str(ref) for ref in data.get("evidence_refs", [])],
        answer_refs=[str(ref) for ref in data.get("answer_refs", [])],
        rationale=str(data.get("rationale", "")),
        human_confirmed=bool(data.get("human_confirmed", False)),
    )


def restore_prepared_suggestion(data: dict[str, Any]):
    """Rebuild one persisted ``PreparedSuggestion`` snapshot."""
    from reporter.models import PreparedSuggestion, ReadinessEffect

    option_readiness = data.get("option_readiness")
    return PreparedSuggestion(
        suggestion=str(data.get("suggestion", "")),
        rationale=str(data.get("rationale", "")),
        lock_yes_reason=data.get("lock_yes_reason"),
        option_readiness=ReadinessEffect(str(option_readiness)) if option_readiness else None,
        selected_option=str(data.get("selected_option", "")),
        evidence_refs=[str(ref) for ref in data.get("evidence_refs", [])],
        ask_human=bool(data.get("ask_human", False)),
        note_text=str(data.get("note_text", "")),
        note_detail=str(data.get("note_detail", "")),
    )


def apply_resume(ctx: RunContext, state: dict[str, Any]) -> None:
    """Restore one run's persisted progress onto a fresh run context.

    Raises :class:`RecoveryError` when the recorded progress cannot be
    replayed by this tool/catalog (the user must then start a fresh run).
    """
    ctx.run_state = state
    meta = state.get("meta", {})
    stages = state.get("stages", {})

    if stages.get("evidence") == "done":
        evidence_path = ctx.output_dir / "evidence.json"
        if evidence_path.exists():
            ctx.evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            ctx.resumed_evidence = True
        else:
            raise RecoveryError(
                f"{ctx.output_dir} claims completed evidence collection, but "
                "evidence.json is missing; start a fresh run."
            )

    if not ctx.series and meta.get("series"):
        ctx.series = meta["series"]

    review = state.get("review", {})
    ctx.requested_binaries = list(review.get("requested_binaries", []))
    if review.get("review_type"):
        ctx.review_type = review["review_type"]

    if ctx.role == "report":
        _apply_report_resume(ctx, state)


def _apply_report_resume(ctx: RunContext, state: dict[str, Any]) -> None:
    """Restore the reporter's answered statement results, in catalog order.

    A recorded answer whose catalog item no longer exists in this tool
    version cannot be replayed - that is a hard mismatch, not a partial
    resume: the run must start fresh rather than silently drop topics.
    """
    import catalog as catalog_module

    ctx.catalog = catalog_module.load_catalog_for_role(ctx.tool_root, ctx.workspace_root, "report")
    recorded = state.get("report", {}).get("results", {})
    known_ids = {item["id"] for item in ctx.catalog["items"]}
    unknown = sorted(set(recorded) - known_ids)
    if unknown:
        raise RecoveryError(
            "the run state references catalog items unknown to this tool version "
            f"({', '.join(unknown)}); the recorded answers cannot be replayed - "
            "start a fresh run"
        )
    ctx.resumed_results = [
        restore_statement_result(recorded[item["id"]])
        for item in ctx.catalog["items"]
        if item["id"] in recorded
    ]
    ctx.resumed_values = dict(state.get("report", {}).get("item_values", {}))
    ctx.resumed_prepared = {
        item_id: restore_prepared_suggestion(data)
        for item_id, data in state.get("report", {}).get("prepared", {}).items()
    }
