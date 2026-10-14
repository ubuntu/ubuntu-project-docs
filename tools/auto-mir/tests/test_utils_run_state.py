"""Tests for incremental run-state persistence (utils/run_state.py)."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from reporter.models import (  # noqa: E402
    Provenance,
    ReadinessEffect,
    StatementResult,
    StatementState,
)
from utils import run_state  # noqa: E402
from utils.secrets import SecretRedactor  # noqa: E402


def _item(item_id, *, completes=""):
    item = {"id": item_id, "section": "Security", "title": item_id, "mode": "human_only"}
    if completes:
        item["completes"] = completes
    return item


def _result(item_id, *, state=StatementState.RESOLVED, statement="- Statement."):
    return StatementResult(
        id=item_id,
        section="Security",
        state=state,
        readiness=ReadinessEffect.CLEAR,
        statement=statement,
        provenance=Provenance.HUMAN if state == StatementState.RESOLVED else None,
    )


def _ctx(tmp_path, *, state=None):
    ctx = SimpleNamespace(
        role="report",
        bug_id="",
        source_package="libfoo",
        series="devel",
        source_pocket="auto",
        run_name="mir-libfoo-test",
        guest_name="mir-libfoo-test",
        output_dir=tmp_path,
        secret_redactor=SecretRedactor(),
        run_state=state,
    )
    return ctx


def test_init_state_records_run_metadata(tmp_path):
    ctx = _ctx(tmp_path)

    state = run_state.init_state(ctx)

    assert state["schema_version"] == run_state.STATE_SCHEMA_VERSION
    assert state["meta"]["role"] == "report"
    assert state["meta"]["source_package"] == "libfoo"
    assert state["meta"]["guest_name"] == ""
    assert state["stages"] == {}
    assert state["report"] == {"item_values": {}, "results": {}, "prepared": {}}


def test_save_and_load_state_roundtrip(tmp_path):
    ctx = _ctx(tmp_path, state=run_state.init_state(_ctx(tmp_path)))

    run_state.mark_stage_done(ctx, "intake")
    loaded = run_state.load_state(tmp_path)

    assert loaded is not None
    assert loaded["stages"] == {"intake": "done"}
    assert loaded["meta"]["guest_name"] == "mir-libfoo-test"


def test_save_state_redacts_registered_secrets(tmp_path):
    ctx = _ctx(tmp_path, state=run_state.init_state(_ctx(tmp_path)))
    ctx.secret_redactor.register("hunter2token")

    run_state.record_item_result(
        ctx,
        _item("REP-A"),
        _result("REP-A", statement="- answer mentioning hunter2token"),
        [],
        "- answer mentioning hunter2token",
    )

    saved = run_state.load_state(tmp_path)
    assert "hunter2token" not in json.dumps(saved)
    assert "[REDACTED]" in saved["report"]["results"]["REP-A"]["statement"]


def test_load_state_returns_none_for_missing_or_unreadable_state(tmp_path):
    assert run_state.load_state(tmp_path) is None

    (tmp_path / "run-state.json").write_text("not json {", encoding="utf-8")
    assert run_state.load_state(tmp_path) is None


def test_load_state_rejects_a_different_schema_version(tmp_path):
    (tmp_path / "run-state.json").write_text(
        json.dumps({"schema_version": 99, "meta": {}, "stages": {}}), encoding="utf-8"
    )

    assert run_state.load_state(tmp_path) is None


def test_record_item_result_snapshots_one_item_and_its_condition_value(tmp_path):
    ctx = _ctx(tmp_path, state=run_state.init_state(_ctx(tmp_path)))

    run_state.record_item_result(
        ctx, _item("REP-A"), _result("REP-A"), [_result("REP-A")], "chosen-option"
    )

    saved = run_state.load_state(tmp_path)
    assert saved["report"]["results"]["REP-A"]["id"] == "REP-A"
    assert saved["report"]["results"]["REP-A"]["statement"] == "- Statement."
    assert saved["report"]["item_values"]["REP-A"] == "chosen-option"


def test_record_item_result_rerecords_the_parent_of_a_merged_followup(tmp_path):
    ctx = _ctx(tmp_path, state=run_state.init_state(_ctx(tmp_path)))
    parent = _result("REP-PARENT", statement="- Parent TBD sentence.")
    followup = _result("REP-CHILD", statement="- Parent completed by the child.")
    followup.state = StatementState.MERGED

    run_state.record_item_result(
        ctx, _item("REP-CHILD", completes="REP-PARENT"), followup, [parent, followup], "answer"
    )

    saved = run_state.load_state(tmp_path)
    # The parent's freshly-mutated statement must be the persisted one.
    assert saved["report"]["results"]["REP-PARENT"]["statement"] == "- Parent TBD sentence."
    assert saved["report"]["results"]["REP-CHILD"]["state"] == str(StatementState.MERGED)


def test_record_all_results_replaces_every_snapshot(tmp_path):
    ctx = _ctx(tmp_path, state=run_state.init_state(_ctx(tmp_path)))
    results = [_result("REP-A"), _result("REP-B")]

    run_state.record_all_results(ctx, results)

    saved = run_state.load_state(tmp_path)
    assert set(saved["report"]["results"]) == {"REP-A", "REP-B"}


def test_record_review_scope_persists_promotion_scope(tmp_path):
    ctx = _ctx(tmp_path, state=run_state.init_state(_ctx(tmp_path)))
    ctx.role = "review"
    ctx.requested_binaries = ["libfoo-bin"]
    ctx.review_type = "rereview"

    run_state.record_review_scope(ctx)

    saved = run_state.load_state(tmp_path)
    assert saved["review"]["requested_binaries"] == ["libfoo-bin"]
    assert saved["review"]["review_type"] == "rereview"


def test_helpers_are_noops_without_a_state(tmp_path):
    ctx = _ctx(tmp_path)  # run_state intentionally None
    ctx.run_state = None

    run_state.save_state(ctx)
    run_state.mark_stage_done(ctx, "intake")
    run_state.record_item_result(ctx, _item("REP-A"), _result("REP-A"), [], "value")
    run_state.record_all_results(ctx, [])
    run_state.record_review_scope(ctx)

    assert not (tmp_path / "run-state.json").exists()


def test_state_file_is_atomic_and_has_no_tmp_leftover(tmp_path):
    ctx = _ctx(tmp_path, state=run_state.init_state(_ctx(tmp_path)))

    run_state.save_state(ctx)

    assert (tmp_path / "run-state.json").exists()
    assert not (tmp_path / "run-state.json.tmp").exists()
