"""Tests for auto_mir runtime orchestration helpers."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import auto_mir
from utils.secrets import SecretRedactor


def test_pin_uat_tooling_option_is_removed():
    parser = auto_mir.build_parser()

    assert "--pin-uat-tooling" not in parser.format_help()
    with pytest.raises(SystemExit, match="2"):
        parser.parse_args(["12345", "--pin-uat-tooling", "deadbeef"])


def test_cli_normalizes_legacy_numeric_bug_to_review():
    args = auto_mir.build_parser().parse_args(["12345"])

    assert args.role == "review"
    assert args.bug_id == "12345"
    assert args.legacy_invocation is True


def test_cli_accepts_explicit_review_command():
    args = auto_mir.build_parser().parse_args(["review", "12345"])

    assert args.role == "review"
    assert args.bug_id == "12345"
    assert args.legacy_invocation is False


def test_cli_accepts_report_source_and_no_llm():
    args = auto_mir.build_parser().parse_args(["report", "libfoo", "--no-llm"])

    assert args.role == "report"
    assert args.source_package == "libfoo"
    assert args.no_llm is True


def test_cli_series_help_explains_role_specific_defaults():
    parser = auto_mir.build_parser()
    subcommands = parser._subparsers._group_actions[0].choices
    help_text = subcommands["report"].format_help()

    assert "Reviewer mode detects it from" in help_text
    assert "Launchpad bug tasks" in help_text
    assert "reporter mode defaults" in help_text
    assert "release ('devel')" in help_text


def test_cli_does_not_treat_bare_source_as_legacy_review():
    with pytest.raises(SystemExit, match="2"):
        auto_mir.build_parser().parse_args(["libfoo"])


def test_main_report_requires_tty_before_preflight(monkeypatch):
    calls: list[str] = []
    args = SimpleNamespace(role="report")
    parser = SimpleNamespace(
        parse_args=lambda: args,
        error=lambda message: (_ for _ in ()).throw(SystemExit(message)),
    )
    monkeypatch.setattr(auto_mir, "build_parser", lambda: parser)
    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(auto_mir.sys.stdout, "isatty", lambda: False)
    monkeypatch.setattr(auto_mir, "ensure_runtime_environment", lambda: calls.append("preflight"))

    with pytest.raises(SystemExit, match="requires an interactive terminal"):
        auto_mir.main()

    assert calls == []


def test_main_report_runs_connected_reporter_pipeline(monkeypatch, tmp_path):
    from reporter import pipeline as reporter_pipeline

    calls: list[str] = []
    args = SimpleNamespace(role="report", verbose=False, legacy_invocation=False)
    parser = SimpleNamespace(parse_args=lambda: args)
    ctx = SimpleNamespace(
        role="report",
        bug_id="",
        source_package="libfoo",
        series="devel",
        keep_guest=None,
        collect_only=False,
        output_dir=tmp_path,
        llm_model_small=None,
        llm_model_large=None,
        guest_name="",
        evidence={"adapters": {}},
        requested_binaries=[],
        catalog={},
        findings=[],
        statement_results=[],
        review_draft_path=None,
        reporter_draft_path=None,
        report_path=None,
        failure_summary=None,
        secret_redactor=SecretRedactor(),
        save_evidence=lambda: calls.append("save"),
    )
    monkeypatch.setattr(auto_mir, "build_parser", lambda: parser)
    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(auto_mir.sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(auto_mir, "ensure_runtime_environment", lambda: calls.append("preflight"))
    monkeypatch.setattr(auto_mir, "RunContext", lambda _args: ctx)
    monkeypatch.setattr(auto_mir, "stage_optional_auth", lambda _ctx: calls.append("auth"))
    monkeypatch.setattr(reporter_pipeline, "intake", lambda _ctx, _wizard: calls.append("intake"))
    monkeypatch.setattr(auto_mir, "stage_spawn_guest", lambda _ctx: calls.append("spawn"))
    monkeypatch.setattr(
        auto_mir, "stage_collect_evidence", lambda _ctx: calls.append("collect") or 0
    )
    monkeypatch.setattr(reporter_pipeline, "analyse", lambda _ctx, _wizard: calls.append("analyse"))
    monkeypatch.setattr(reporter_pipeline, "render", lambda _ctx: calls.append("render"))
    monkeypatch.setattr(
        auto_mir,
        "_finish_run",
        lambda _ctx, _evidence_result, exit_code: calls.append("finish") or exit_code,
    )

    assert auto_mir.main() == 0
    assert calls == [
        "preflight",
        "auth",
        "intake",
        "spawn",
        "collect",
        "save",
        "analyse",
        "render",
        "finish",
    ]


def _patch_main_context(monkeypatch, *, collect_only: bool):
    """Patch parser/context setup so main() can be exercised deterministically."""

    args = SimpleNamespace(
        role="review",
        legacy_invocation=False,
        bug_id="12345",
        series=None,
        output_dir=None,
        collect_only=collect_only,
        lxd_image=None,
        lxd_options="",
        keep_guest=None,
        llm_model_small=None,
        llm_model_large=None,
        request_binaries=None,
        source_pocket="auto",
        verbose=False,
    )

    parser = SimpleNamespace(parse_args=lambda: args)
    monkeypatch.setattr(auto_mir, "build_parser", lambda: parser)

    ctx = SimpleNamespace(
        role="review",
        bug_id="12345",
        source_package="pkg",
        keep_guest=None,
        collect_only=collect_only,
        output_dir=Path("/tmp"),
        llm_model_small=None,
        llm_model_large=None,
        guest_name="",
        evidence={"adapters": {}},
        requested_binaries=[],
        catalog={},
        findings=[],
        review_draft_path=Path("/tmp/review-draft.txt"),
        report_path=Path("/tmp/report.json"),
        failure_summary=None,
        secret_redactor=SecretRedactor(),
        save_evidence=lambda: None,
    )
    monkeypatch.setattr(auto_mir, "RunContext", lambda _args: ctx)
    return ctx


def test_main_checks_dependencies_after_parsing_before_context(monkeypatch):
    calls: list[str] = []
    parser = SimpleNamespace(parse_args=lambda: calls.append("parse") or SimpleNamespace())

    monkeypatch.setattr(auto_mir, "build_parser", lambda: parser)

    def _stop_after_preflight():
        calls.append("preflight")
        raise SystemExit(1)

    monkeypatch.setattr(auto_mir, "ensure_runtime_environment", _stop_after_preflight)
    monkeypatch.setattr(
        auto_mir,
        "RunContext",
        lambda _args: calls.append("context") or SimpleNamespace(),
    )

    with pytest.raises(SystemExit, match="1"):
        auto_mir.main()

    assert calls == ["parse", "preflight"]


def test_teardown_uses_failure_summary_in_noninteractive_warning(monkeypatch):
    failure_summary = (
        "Stage 4 (analysis) failed after evidence collection encountered adapter failures."
    )
    ctx = SimpleNamespace(
        guest_name="mir-test",
        keep_guest=None,
        failure_summary=failure_summary,
    )
    warnings = []

    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(auto_mir.sys.stdout, "isatty", lambda: False)
    monkeypatch.setattr(
        auto_mir.log, "warning", lambda message, *args: warnings.append(message % args)
    )
    monkeypatch.setattr(auto_mir, "_destroy_guest", lambda run_ctx: None)

    auto_mir.teardown_guest(ctx, evidence_collection_result=1)

    assert warnings
    assert (
        "Stage 4 (analysis) failed after evidence collection encountered adapter failures."
        in warnings[0]
    )


def test_teardown_falls_back_to_adapter_failure_summary(monkeypatch):
    ctx = SimpleNamespace(guest_name="mir-test", keep_guest=None, failure_summary=None)
    warnings = []

    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: False)
    monkeypatch.setattr(auto_mir.sys.stdout, "isatty", lambda: False)
    monkeypatch.setattr(
        auto_mir.log, "warning", lambda message, *args: warnings.append(message % args)
    )
    monkeypatch.setattr(auto_mir, "_destroy_guest", lambda run_ctx: None)

    auto_mir.teardown_guest(ctx, evidence_collection_result=1)

    assert warnings
    assert "Evidence collection encountered adapter failures." in warnings[0]


def test_teardown_skips_prompt_when_only_host_adapters_failed(monkeypatch):
    """Host-only adapter failures never touch the guest, so no prompt/keep."""
    ctx = SimpleNamespace(
        guest_name="mir-test",
        keep_guest=None,
        failure_summary="Evidence collection encountered adapter failures.",
        evidence={"collection_summary": {"guest_adapter_failed": False}},
    )
    infos = []
    destroyed = []

    monkeypatch.setattr(auto_mir.log, "info", lambda message, *args: infos.append(message % args))
    monkeypatch.setattr(auto_mir, "_destroy_guest", lambda run_ctx: destroyed.append(run_ctx))

    def _unexpected_input(_prompt=""):
        raise AssertionError("must not prompt when only host adapters failed")

    monkeypatch.setattr("builtins.input", _unexpected_input)

    auto_mir.teardown_guest(ctx, evidence_collection_result=1)

    assert destroyed == [ctx]
    assert infos
    assert "host-side adapter" in infos[0]


def test_teardown_still_prompts_when_guest_adapter_failed(monkeypatch):
    """A genuine guest-side adapter failure still offers to preserve the guest."""
    ctx = SimpleNamespace(
        guest_name="mir-test",
        keep_guest=None,
        failure_summary="Evidence collection encountered adapter failures.",
        evidence={"collection_summary": {"guest_adapter_failed": True}},
    )
    destroyed = []

    monkeypatch.setattr(auto_mir.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(auto_mir.sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(auto_mir, "_destroy_guest", lambda run_ctx: destroyed.append(run_ctx))
    inputs = iter(["n"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))

    auto_mir.teardown_guest(ctx, evidence_collection_result=1)

    assert destroyed == [ctx]


def test_stage_collect_evidence_marks_guest_adapter_failed(monkeypatch):
    """A failed guest-module adapter should be flagged in collection_summary."""

    def _fake_collector(_ctx):
        return {}

    _fake_collector.__module__ = "evidence.guest_adapters"

    def _fake_collect_from_catalog(run_ctx):
        run_ctx.evidence["adapters"] = {
            "packaging-source": {"status": "error", "message": "boom"},
            "upstream-tracker": {"status": "ok"},
        }
        return 1

    import evidence
    import evidence.registry

    monkeypatch.setattr(evidence, "collect_from_catalog", _fake_collect_from_catalog)
    monkeypatch.setattr(
        evidence.registry, "ADAPTER_REGISTRY", {"packaging-source": (_fake_collector, [])}
    )

    ctx = SimpleNamespace(source_package="foo", catalog={"items": []}, evidence={})

    result = auto_mir.stage_collect_evidence(ctx)

    assert result == 1
    assert ctx.evidence["collection_summary"]["guest_adapter_failed"] is True


def test_stage_collect_evidence_host_only_failure_not_marked_guest(monkeypatch):
    """A failed host-module adapter should not be flagged as a guest failure."""

    def _fake_collector(_ctx):
        return {}

    _fake_collector.__module__ = "evidence.host_adapters"

    def _fake_collect_from_catalog(run_ctx):
        run_ctx.evidence["adapters"] = {
            "upstream-tracker": {"status": "error", "message": "no match"},
        }
        return 1

    import evidence
    import evidence.registry

    monkeypatch.setattr(evidence, "collect_from_catalog", _fake_collect_from_catalog)
    monkeypatch.setattr(
        evidence.registry, "ADAPTER_REGISTRY", {"upstream-tracker": (_fake_collector, [])}
    )

    ctx = SimpleNamespace(source_package="foo", catalog={"items": []}, evidence={})

    result = auto_mir.stage_collect_evidence(ctx)

    assert result == 1
    assert ctx.evidence["collection_summary"]["guest_adapter_failed"] is False


def test_main_runs_stages_in_expected_order(monkeypatch):
    ctx = _patch_main_context(monkeypatch, collect_only=False)
    calls: list[str] = []

    monkeypatch.setattr(auto_mir, "stage_auth", lambda _ctx: calls.append("auth"))
    monkeypatch.setattr(auto_mir, "stage_intake", lambda _ctx: calls.append("intake"))
    monkeypatch.setattr(auto_mir, "stage_spawn_guest", lambda _ctx: calls.append("spawn"))

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
        "teardown_guest",
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
    monkeypatch.setattr(auto_mir, "stage_spawn_guest", lambda _ctx: calls.append("spawn"))
    monkeypatch.setattr(
        auto_mir, "stage_collect_evidence", lambda _ctx: calls.append("collect") or 0
    )
    monkeypatch.setattr(auto_mir, "stage_analyse", lambda _ctx: calls.append("analyse"))
    monkeypatch.setattr(auto_mir, "stage_render", lambda _ctx: calls.append("render"))
    monkeypatch.setattr(auto_mir, "_save_test_artifacts", lambda _ctx: calls.append("save"))
    monkeypatch.setattr(auto_mir, "_log_artifact_locations", lambda _ctx: calls.append("artifacts"))
    monkeypatch.setattr(
        auto_mir,
        "teardown_guest",
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
    monkeypatch.setattr(auto_mir, "stage_spawn_guest", lambda _ctx: calls.append("spawn"))
    monkeypatch.setattr(
        auto_mir, "stage_collect_evidence", lambda _ctx: calls.append("collect") or 1
    )
    monkeypatch.setattr(auto_mir, "stage_analyse", lambda _ctx: calls.append("analyse"))
    monkeypatch.setattr(auto_mir, "stage_render", lambda _ctx: calls.append("render"))
    monkeypatch.setattr(auto_mir, "_log_artifact_locations", lambda _ctx: calls.append("artifacts"))
    monkeypatch.setattr(
        auto_mir,
        "teardown_guest",
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
