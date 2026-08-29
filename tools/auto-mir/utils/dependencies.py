"""Ubuntu host dependency discovery for auto-mir.

This module intentionally uses only the Python standard library so the CLI can
display ``--help`` before checking runtime dependencies.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class RuntimeDependency:
    """Map project metadata and Python imports to an Ubuntu binary package."""

    distribution: str
    module: str
    ubuntu_package: str
    purpose: str


# This tool is designed to run against Ubuntu system/apt-installed packages,
# not a project-local virtualenv/pip install (auto-mir orchestrates lxc/apt-get
# and expects to run directly on a host's system Python). Each ``distribution``
# below is also declared in ../pyproject.toml's ``[project] dependencies`` -
# that copy exists only for packaging/dev tooling (pip metadata, IDE dependency
# resolution) and is never what actually gets installed at runtime; this is
# the list that matters, and ``ensure_runtime_environment()`` below is what
# tells the user which ``apt install`` command to run.
# ``tests/test_dependencies.py::test_runtime_registry_matches_pyproject_dependencies``
# asserts the two lists name exactly the same distributions, so they can never
# silently drift apart.
RUNTIME_DEPENDENCIES = (
    RuntimeDependency(
        distribution="launchpadlib",
        module="launchpadlib",
        ubuntu_package="python3-launchpadlib",
        purpose="Launchpad API access",
    ),
    RuntimeDependency(
        distribution="pyyaml",
        module="yaml",
        ubuntu_package="python3-yaml",
        purpose="check catalog parsing",
    ),
    RuntimeDependency(
        distribution="python-json-logger",
        module="pythonjsonlogger",
        ubuntu_package="python3-pythonjsonlogger",
        purpose="structured run logs",
    ),
    RuntimeDependency(
        distribution="tenacity",
        module="tenacity",
        ubuntu_package="python3-tenacity",
        purpose="network and LXD retry handling",
    ),
)


def ubuntu_package_for(distribution: str) -> str:
    """Return the Ubuntu package for a declared runtime distribution."""
    for dependency in RUNTIME_DEPENDENCIES:
        if dependency.distribution == distribution:
            return dependency.ubuntu_package
    raise KeyError(distribution)


def find_missing_runtime_dependencies(
    find_spec: Callable[[str], object | None] | None = None,
) -> tuple[RuntimeDependency, ...]:
    """Return direct runtime dependencies unavailable to this interpreter.

    ``find_spec`` checks only top-level import availability. It deliberately
    does not execute third-party code, so an internal or transitive import bug
    is not mislabeled as a missing Ubuntu package.
    """
    resolver = find_spec or importlib.util.find_spec
    return tuple(
        dependency for dependency in RUNTIME_DEPENDENCIES if resolver(dependency.module) is None
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
    for dependency in missing:
        print(
            f"  - {dependency.ubuntu_package} ({dependency.purpose})",
            file=sys.stderr,
        )
    packages = " ".join(dependency.ubuntu_package for dependency in missing)
    print("Install them with:", file=sys.stderr)
    print(f"  sudo apt install {packages}", file=sys.stderr)
    print(
        "If they are already installed, use Ubuntu's system Python rather than "
        "an isolated environment that hides system packages.",
        file=sys.stderr,
    )
    raise SystemExit(1)
