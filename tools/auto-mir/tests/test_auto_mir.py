"""Tests for auto_mir runtime orchestration helpers."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import auto_mir


def _patch_main_context(monkeypatch, *, collect_only: bool):
    """Patch parser/context setup so main() can be exercised deterministically."""

    args = SimpleNamespace(
        bug_id="12345",
        series=None,
        output_dir=None,
        collect_only=collect_only,
        lxd_image=None,
        lxd_options="",
        keep_container=None,
        pin_uat_tooling=None,
        llm_model_small=None,
        llm_model_large=None,
        request_binaries=None,
        source_pocket="auto",
        verbose=False,
    )

    parser = SimpleNamespace(parse_args=lambda: args)
    monkeypatch.setattr(auto_mir, "build_parser", lambda: parser)

    ctx = SimpleNamespace(
        bug_id="12345",
        source_package="pkg",
        keep_container=None,
        collect_only=collect_only,
        output_dir=Path("/tmp"),
        llm_model_small=None,
        llm_model_large=None,
        vm_name="",
        evidence={"adapters": {}},
        requested_binaries=[],
        catalog={},
        findings=[],
        review_draft_path=Path("/tmp/review-draft.txt"),
        report_path=Path("/tmp/report.json"),
        failure_summary=None,
        save_evidence=lambda: None,
    )
    monkeypatch.setattr(auto_mir, "RunContext", lambda _args: ctx)
    return ctx


def test_teardown_uses_failure_summary_in_noninteractive_warning(monkeypatch):
    failure_summary = (
        "Stage 4 (analysis) failed after evidence collection encountered adapter failures."
    )
    ctx = SimpleNamespace(
        vm_name="mir-test",
        keep_container=None,
        failure_summary=failure_summary,
    )
    warnings = []

    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(auto_mir.sys.stdout, "isatty", lambda: False)
    monkeypatch.setattr(
        auto_mir.log, "warning", lambda message, *args: warnings.append(message % args)
    )
    monkeypatch.setattr(auto_mir.lxd_runner, "destroy", lambda run_ctx: None)

    auto_mir.teardown_container(ctx, evidence_collection_result=1)

    assert warnings
    assert (
        "Stage 4 (analysis) failed after evidence collection encountered adapter failures."
        in warnings[0]
    )


def test_teardown_falls_back_to_adapter_failure_summary(monkeypatch):
    ctx = SimpleNamespace(vm_name="mir-test", keep_container=None, failure_summary=None)
    warnings = []

    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(auto_mir.sys.stdout, "isatty", lambda: False)
    monkeypatch.setattr(
        auto_mir.log, "warning", lambda message, *args: warnings.append(message % args)
    )
    monkeypatch.setattr(auto_mir.lxd_runner, "destroy", lambda run_ctx: None)

    auto_mir.teardown_container(ctx, evidence_collection_result=1)

    assert warnings
    assert "Evidence collection encountered adapter failures." in warnings[0]


def test_main_runs_stages_in_expected_order(monkeypatch):
    ctx = _patch_main_context(monkeypatch, collect_only=False)
    calls: list[str] = []

    monkeypatch.setattr(auto_mir, "stage_auth", lambda _ctx: calls.append("auth"))
    monkeypatch.setattr(auto_mir, "stage_intake", lambda _ctx: calls.append("intake"))
    monkeypatch.setattr(auto_mir, "stage_spawn_container", lambda _ctx: calls.append("spawn"))

    def _collect(_ctx):
        calls.append("collect")
        return 0

    monkeypatch.setattr(auto_mir, "stage_collect_evidence", _collect)
    monkeypatch.setattr(auto_mir, "stage_analyse", lambda _ctx: calls.append("analyse"))

    def _render(_ctx):
        calls.append("render")
        _ctx.review_draft_path = Path("/tmp/review-draft.txt")
        _ctx.report_path = Path("/tmp/report.json")

    monkeypatch.setattr(auto_mir, "stage_render", _render)
    monkeypatch.setattr(auto_mir, "_save_test_artifacts", lambda _ctx: calls.append("save"))
    monkeypatch.setattr(auto_mir, "_log_artifact_locations", lambda _ctx: calls.append("artifacts"))
    monkeypatch.setattr(
        auto_mir,
        "teardown_container",
        lambda _ctx, _result=0: calls.append("teardown"),
    )
    monkeypatch.setattr(auto_mir, "_print_complete_banner", lambda _ctx: calls.append("banner"))

    assert auto_mir.main() == 0
    assert calls == [
        "auth",
        "intake",
        "spawn",
        "collect",
        "analyse",
        "render",
        "artifacts",
        "teardown",
        "banner",
    ]
    assert ctx.failure_summary is None


def test_main_collect_only_skips_auth_analysis_and_render(monkeypatch):
    _patch_main_context(monkeypatch, collect_only=True)
    calls: list[str] = []

    monkeypatch.setattr(auto_mir, "stage_auth", lambda _ctx: calls.append("auth"))
    monkeypatch.setattr(auto_mir, "stage_intake", lambda _ctx: calls.append("intake"))
    monkeypatch.setattr(auto_mir, "stage_spawn_container", lambda _ctx: calls.append("spawn"))
    monkeypatch.setattr(
        auto_mir, "stage_collect_evidence", lambda _ctx: calls.append("collect") or 0
    )
    monkeypatch.setattr(auto_mir, "stage_analyse", lambda _ctx: calls.append("analyse"))
    monkeypatch.setattr(auto_mir, "stage_render", lambda _ctx: calls.append("render"))
    monkeypatch.setattr(auto_mir, "_save_test_artifacts", lambda _ctx: calls.append("save"))
    monkeypatch.setattr(auto_mir, "_log_artifact_locations", lambda _ctx: calls.append("artifacts"))
    monkeypatch.setattr(
        auto_mir,
        "teardown_container",
        lambda _ctx, _result=0: calls.append("teardown"),
    )
    monkeypatch.setattr(auto_mir, "_print_complete_banner", lambda _ctx: calls.append("banner"))

    assert auto_mir.main() == 0
    assert calls == ["intake", "spawn", "collect", "save", "artifacts", "teardown", "banner"]


def test_main_propagates_evidence_failure_summary_to_teardown(monkeypatch):
    ctx = _patch_main_context(monkeypatch, collect_only=False)
    calls: list[str] = []
    teardown_results: list[int] = []

    monkeypatch.setattr(auto_mir, "stage_auth", lambda _ctx: calls.append("auth"))
    monkeypatch.setattr(auto_mir, "stage_intake", lambda _ctx: calls.append("intake"))
    monkeypatch.setattr(auto_mir, "stage_spawn_container", lambda _ctx: calls.append("spawn"))
    monkeypatch.setattr(
        auto_mir, "stage_collect_evidence", lambda _ctx: calls.append("collect") or 1
    )
    monkeypatch.setattr(auto_mir, "stage_analyse", lambda _ctx: calls.append("analyse"))
    monkeypatch.setattr(auto_mir, "stage_render", lambda _ctx: calls.append("render"))
    monkeypatch.setattr(auto_mir, "_log_artifact_locations", lambda _ctx: calls.append("artifacts"))
    monkeypatch.setattr(
        auto_mir,
        "teardown_container",
        lambda _ctx, result=0: teardown_results.append(result),
    )
    monkeypatch.setattr(auto_mir, "_print_complete_banner", lambda _ctx: calls.append("banner"))

    assert auto_mir.main() == 0
    assert teardown_results == [1]
    assert ctx.failure_summary == "Evidence collection encountered adapter failures."


def test_resolve_requested_binaries_empty_returns_empty():
    assert auto_mir._resolve_requested_binaries([]) == []


def test_resolve_requested_binaries_single_auto_selects_without_prompt(monkeypatch):
    def _fail(*_args, **_kwargs):
        raise AssertionError("must not prompt when exactly one binary is built")

    monkeypatch.setattr(auto_mir, "_ask_requested_binaries", _fail)
    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: True)

    assert auto_mir._resolve_requested_binaries(["linuxptp"]) == ["linuxptp"]


def test_resolve_requested_binaries_multiple_noninteractive_defaults_to_all(monkeypatch):
    def _fail(*_args, **_kwargs):
        raise AssertionError("must not prompt without an interactive terminal")

    monkeypatch.setattr(auto_mir, "_ask_requested_binaries", _fail)
    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: False)

    assert auto_mir._resolve_requested_binaries(["libfoo1", "foo-tools"]) == [
        "libfoo1",
        "foo-tools",
    ]


def test_resolve_requested_binaries_multiple_interactive_prompts(monkeypatch):
    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(auto_mir, "_ask_requested_binaries", lambda binaries: ["foo-tools"])

    assert auto_mir._resolve_requested_binaries(["libfoo1", "foo-tools"]) == ["foo-tools"]
