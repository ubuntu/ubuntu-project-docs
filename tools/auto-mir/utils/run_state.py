"""Incremental run-state persistence for crash and interrupt recovery.

The output directory already carries the full JSON log and ``evidence.json``,
but a reporter's *answers* only ever reached ``report.json`` at the very end
of a run - so any crash or interrupt before rendering destroyed the whole
interactive session. This module persists a small ``run-state.json``
incrementally: stage markers as each pipeline stage completes, and one
statement result (plus the condition value it produced) at a time while the
reporter answers questions. Writes are atomic (``tmp`` + ``os.replace``),
so a crash mid-write can only ever lose the in-flight item.

All helpers are no-ops when the context carries no state (unit-test
contexts, and any caller that does not opt into persistence).
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from auto_mir import RunContext

from utils.secrets import ensure_secret_redactor

log = logging.getLogger("auto_mir.run_state")

STATE_SCHEMA_VERSION = 1
STATE_FILE = "run-state.json"

# Pipeline stage markers, in execution order. A stage's value is "done"
# once it has fully completed; a state file whose "render" stage is done
# describes a completed run, anything else an aborted one.
STAGES = ("intake", "guest", "evidence", "analysis", "render")


def state_path(output_dir: Path) -> Path:
    """Return the run-state file path inside one output directory."""
    return Path(output_dir) / STATE_FILE


def init_state(ctx: RunContext) -> dict[str, Any]:
    """Build the initial run state for one run, from its resolved context.

    Attribute reads are getattr-tolerant so partially-populated test
    contexts (see ``tests/test_auto_mir.py``) can run ``main()`` unchanged.
    """
    started = datetime.now(UTC).isoformat()
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "meta": {
            "role": getattr(ctx, "role", ""),
            "bug_id": str(getattr(ctx, "bug_id", "") or ""),
            "source_package": str(getattr(ctx, "source_package", "") or ""),
            "series": getattr(ctx, "series", None),
            "source_pocket": getattr(ctx, "source_pocket", "auto"),
            "run_name": getattr(ctx, "run_name", ""),
            "guest_name": "",
            "started_utc": started,
            "updated_utc": started,
        },
        "stages": {},
        "review": {"requested_binaries": [], "review_type": "fresh"},
        "report": {"item_values": {}, "results": {}, "prepared": {}},
    }


def save_state(ctx: RunContext) -> None:
    """Atomically persist the run state, sanitized like every artifact."""
    state = getattr(ctx, "run_state", None)
    if state is None:
        return
    state["meta"]["updated_utc"] = datetime.now(UTC).isoformat()
    if getattr(ctx, "guest_name", ""):
        state["meta"]["guest_name"] = ctx.guest_name
    redactor = ensure_secret_redactor(ctx)
    sanitized = redactor.sanitize(state)
    path = state_path(ctx.output_dir)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(sanitized, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, path)


def mark_stage_done(ctx: RunContext, stage: str) -> None:
    """Record that one pipeline stage fully completed, and persist."""
    state = getattr(ctx, "run_state", None)
    if state is None:
        return
    state["stages"][stage] = "done"
    save_state(ctx)


def record_review_scope(ctx: RunContext) -> None:
    """Persist the reviewer role's promotion scope and review type."""
    state = getattr(ctx, "run_state", None)
    if state is None:
        return
    state["review"]["requested_binaries"] = list(getattr(ctx, "requested_binaries", []))
    state["review"]["review_type"] = getattr(ctx, "review_type", "fresh")
    save_state(ctx)


def record_item_result(
    ctx: RunContext, item: dict[str, Any], result: Any, results: list, value: Any
) -> None:
    """Persist one evaluated statement result plus its condition value.

    Called after each catalog item completes, so an interrupt costs at most
    the in-flight question. When the item is a ``completes`` follow-up that
    was merged into its parent, the parent's freshly-mutated result is
    re-recorded too.
    """
    state = getattr(ctx, "run_state", None)
    if state is None:
        return
    report = state["report"]
    report["results"][result.id] = _snapshot(result)
    report["item_values"][str(item["id"])] = value
    parent_id = str(item.get("completes", ""))
    if parent_id and result.id != parent_id:
        parent = next((entry for entry in results if entry.id == parent_id), None)
        if parent is not None:
            report["results"][parent_id] = _snapshot(parent)
    save_state(ctx)


def record_prepared(ctx: RunContext, item_id: str, suggestion: Any) -> None:
    """Persist one prepared AI suggestion, so a resumed run skips its LLM call."""
    state = getattr(ctx, "run_state", None)
    if state is None:
        return
    state["report"]["prepared"][item_id] = _snapshot(suggestion)
    save_state(ctx)


def record_all_results(ctx: RunContext, results: list) -> None:
    """Re-record every statement result (used after the consistency pass,
    whose corrections replace statements after the per-item recording)."""
    state = getattr(ctx, "run_state", None)
    if state is None:
        return
    state["report"]["results"] = {result.id: _snapshot(result) for result in results}
    save_state(ctx)


def load_state(output_dir: Path) -> dict[str, Any] | None:
    """Return the persisted run state, or ``None`` when absent/unreadable.

    ``None`` also covers a schema-version mismatch: a state file written by
    a different generation of this tool is not recoverable by this one.
    """
    path = state_path(output_dir)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(raw, dict) or raw.get("schema_version") != STATE_SCHEMA_VERSION:
        return None
    if not isinstance(raw.get("meta"), dict) or not isinstance(raw.get("stages"), dict):
        return None
    return raw


def _snapshot(result: Any) -> dict[str, Any]:
    """Return a JSON-ready snapshot of one ``StatementResult``."""
    return asdict(result)
