"""Tests for LXD guest provisioning helpers."""

import sys
from pathlib import Path

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
