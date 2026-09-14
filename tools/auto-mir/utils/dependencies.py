"""Ubuntu host dependency discovery for auto-mir.

This module intentionally uses only the Python standard library so the CLI can
display ``--help`` before checking runtime dependencies.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import Callable, Sequence

# This tool is designed to run against Ubuntu system/apt-installed packages,
# not a project-local virtualenv/pip install (auto-mir orchestrates lxc/apt-get
# and expects to run directly on a host's system Python). Each key is also
# declared in ../pyproject.toml's ``[project] dependencies`` - that copy exists
# only for packaging/dev tooling (pip metadata, IDE dependency resolution) and
# is never what actually gets installed at runtime; this is the list that
# matters, and ``ensure_runtime_environment()`` below is what tells the user
# which ``apt install`` command to run.
# ``tests/test_dependencies.py::test_runtime_registry_matches_pyproject_dependencies``
# asserts the two lists name exactly the same distributions, so they can never
# silently drift apart.
# distribution -> (import module, apt package, purpose)
RUNTIME_DEPENDENCIES: dict[str, tuple[str, str, str]] = {
    "launchpadlib": ("launchpadlib", "python3-launchpadlib", "Launchpad API access"),
    "pyyaml": ("yaml", "python3-yaml", "check catalog parsing"),
    "python-json-logger": (
        "pythonjsonlogger",
        "python3-pythonjsonlogger",
        "structured run logs",
    ),
    "tenacity": ("tenacity", "python3-tenacity", "network and LXD retry handling"),
}


def ubuntu_package_for(distribution: str) -> str:
    """Return the Ubuntu package for a declared runtime distribution."""
    return RUNTIME_DEPENDENCIES[distribution][1]


def find_missing_runtime_dependencies(
    find_spec: Callable[[str], object | None] | None = None,
) -> tuple[str, ...]:
    """Return distributions whose module is unavailable to this interpreter.

    ``find_spec`` checks only top-level import availability. It deliberately
    does not execute third-party code, so an internal or transitive import bug
    is not mislabeled as a missing Ubuntu package.
    """
    resolver = find_spec or importlib.util.find_spec
    return tuple(
        distribution
        for distribution, (module, _package, _purpose) in RUNTIME_DEPENDENCIES.items()
        if resolver(module) is None
    )


def ensure_runtime_environment(
    *,
    version_info: Sequence[int] | None = None,
    find_spec: Callable[[str], object | None] | None = None,
) -> None:
    """Exit with Ubuntu-specific guidance when the host cannot run auto-mir."""
    version = version_info or sys.version_info
    if tuple(version[:2]) < (3, 12):
        print(
            "auto-mir requires Python 3.12 or newer and supports Ubuntu 24.04 LTS or newer.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    missing = find_missing_runtime_dependencies(find_spec)
    if not missing:
        return

    print("auto-mir is missing required Ubuntu packages:", file=sys.stderr)
    for distribution in missing:
        _module, package, purpose = RUNTIME_DEPENDENCIES[distribution]
        print(f"  - {package} ({purpose})", file=sys.stderr)
    packages = " ".join(RUNTIME_DEPENDENCIES[distribution][1] for distribution in missing)
    print("Install them with:", file=sys.stderr)
    print(f"  sudo apt install {packages}", file=sys.stderr)
    print(
        "If they are already installed, use Ubuntu's system Python rather than "
        "an isolated environment that hides system packages.",
        file=sys.stderr,
    )
    raise SystemExit(1)
