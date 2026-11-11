"""Tests for LXD guest provisioning helpers."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lxd_runner


def test_bootstrap_archive_tools_uses_latest_shallow_head(monkeypatch):
    calls: list[tuple[str, list[str], dict]] = []

    def fake_exec_in_retry(name, command, **kwargs):
        calls.append((name, command, kwargs))

    monkeypatch.setattr(lxd_runner, "exec_in_retry", fake_exec_in_retry)

    lxd_runner._bootstrap_archive_tools("guest")

    assert calls == [
        (
            "guest",
            [
                "git",
                "clone",
                "--depth=1",
                lxd_runner._ARCHIVE_TOOLS_REPO,
                lxd_runner._ARCHIVE_TOOLS_DIR,
            ],
            {"operation": "clone ubuntu-archive-tools"},
        )
    ]


# ---------------------------------------------------------------------------
# Execution timeout safety net: nothing previously bounded how long a guest
# command could run, so an unexpectedly hanging command (e.g. a tool
# attempting interactive auth on a headless guest) could block a whole run
# indefinitely. run_command()/exec_in()/exec_in_retry() all default to a
# generous timeout; a command that exceeds it must fail clearly rather than
# hang.
# ---------------------------------------------------------------------------


def test_run_command_raises_clear_error_on_timeout(monkeypatch):
    def fake_run(*_args, timeout=None, **_kwargs):
        raise subprocess.TimeoutExpired(cmd=["sleep", "999"], timeout=timeout)

    monkeypatch.setattr(lxd_runner.subprocess, "run", fake_run)

    with pytest.raises(subprocess.TimeoutExpired):
        lxd_runner.run_command(["sleep", "999"], "host", timeout=0.01)


def test_exec_in_default_timeout_is_generous_and_forwarded(monkeypatch):
    captured = {}

    def fake_run_command(cmd, log_prefix, check, capture, timeout):
        captured["timeout"] = timeout
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(lxd_runner, "run_command", fake_run_command)

    lxd_runner.exec_in("guest", ["true"])

    assert captured["timeout"] == lxd_runner._DEFAULT_GUEST_COMMAND_TIMEOUT_SECONDS


def test_exec_in_honors_explicit_timeout_override(monkeypatch):
    captured = {}

    def fake_run_command(cmd, log_prefix, check, capture, timeout):
        captured["timeout"] = timeout
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(lxd_runner, "run_command", fake_run_command)

    lxd_runner.exec_in("guest", ["true"], timeout=5.0)

    assert captured["timeout"] == 5.0
