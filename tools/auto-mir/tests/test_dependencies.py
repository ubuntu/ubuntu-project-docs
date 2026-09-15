"""Tests for Ubuntu-first host dependency validation."""

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.dependencies import (  # noqa: E402
    RUNTIME_DEPENDENCIES,
    ensure_runtime_environment,
    find_missing_runtime_dependencies,
)

TOOL_ROOT = Path(__file__).resolve().parent.parent


def test_runtime_registry_matches_pyproject_dependencies():
    with (TOOL_ROOT / "pyproject.toml").open("rb") as handle:
        configured = tomllib.load(handle)["project"]["dependencies"]

    declared = {requirement.split(">=", 1)[0].lower() for requirement in configured}
    registered = set(RUNTIME_DEPENDENCIES)

    assert registered == declared


def test_all_runtime_dependencies_present():
    assert find_missing_runtime_dependencies(lambda _module: object()) == ()


def test_missing_runtime_dependencies_preserve_registry_order():
    present = {"yaml", "tenacity"}

    missing = find_missing_runtime_dependencies(
        lambda module: object() if module in present else None
    )

    assert [RUNTIME_DEPENDENCIES[d][1] for d in missing] == [
        "python3-launchpadlib",
        "python3-pythonjsonlogger",
    ]


def test_missing_dependencies_report_one_apt_command(capsys):
    present = {"yaml", "tenacity"}

    with pytest.raises(SystemExit, match="1"):
        ensure_runtime_environment(
            version_info=(3, 12),
            find_spec=lambda module: object() if module in present else None,
        )

    error = capsys.readouterr().err
    assert error.count("sudo apt install") == 1
    assert "sudo apt install python3-launchpadlib python3-pythonjsonlogger" in error
    assert "pip" not in error
    assert "uv" not in error


def test_unsupported_python_reports_supported_baseline(capsys):
    with pytest.raises(SystemExit, match="1"):
        ensure_runtime_environment(version_info=(3, 11), find_spec=lambda _module: object())

    error = capsys.readouterr().err
    assert "Python 3.12 or newer" in error
    assert "Ubuntu 24.04 LTS or newer" in error


def test_help_works_without_site_packages():
    result = subprocess.run(
        [sys.executable, "-S", str(TOOL_ROOT / "auto_mir.py"), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "AI-assisted Ubuntu Main Inclusion Review assistant" in result.stdout
    assert "review" in result.stdout
    assert "report" in result.stdout
    assert "ModuleNotFoundError" not in result.stderr
