"""Tests for auto_mir runtime orchestration helpers."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import auto_mir


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
