"""Language gate detection for auto-mir checks.

This module provides functions to detect programming language-specific packages
and determine whether language-specific checks should be activated.
"""

from __future__ import annotations

import logging
from typing import Callable

log = logging.getLogger("auto_mir.checks.language_gates")


_THIRD_PARTY_DIR_MARKERS = (
    "/vendor/",
    "/vendored/",
    "/third_party/",
    "/3rdparty/",
    "/node_modules/",
    "/.git/",
)


def _iter_non_third_party_paths(packaging: dict):
    """Yield normalized source-tree file paths, excluding common third-party trees."""
    for entry in packaging.get("file_listing", []):
        raw_path = str(entry.get("path", "") or "")
        if not raw_path:
            continue
        normalized = raw_path.lower().replace("\\", "/")
        if normalized.startswith("./"):
            normalized = normalized[1:]
        marked = normalized if normalized.startswith("/") else f"/{normalized}"
        if any(marker in marked for marker in _THIRD_PARTY_DIR_MARKERS):
            continue
        yield normalized


def _has_go_tree_hints(packaging: dict) -> bool:
    """Return True when source-tree file names indicate Go sources."""
    for path in _iter_non_third_party_paths(packaging):
        if path.endswith(".go"):
            return True
        if path.endswith("/go.mod") or path.endswith("/go.work"):
            return True
    return False


def _has_rust_tree_hints(packaging: dict) -> bool:
    """Return True when source-tree file names indicate Rust sources."""
    for path in _iter_non_third_party_paths(packaging):
        if path.endswith(".rs"):
            return True
        if path.endswith("/cargo.toml"):
            return True
    return False


def _is_go_package(packaging: dict) -> bool:
    """Return True when the packaging evidence indicates a Go package.

    Heuristics (any one sufficient):
    - go.sum file present in source tree
    - dh-golang or golang mentioned in debian/rules
    - source tree contains .go, go.mod, or go.work (excluding common vendor trees)
    """
    rules = packaging.get("debian_rules", "")
    return (
        packaging.get("go_sum_present", False)
        or "dh-golang" in rules
        or "golang" in rules.lower()
        or _has_go_tree_hints(packaging)
    )


def _is_rust_package(packaging: dict) -> bool:
    """Return True when the packaging evidence indicates a Rust package.

    Heuristics (any one sufficient):
    - Cargo.lock file present in source tree
    - --buildsystem cargo or dh_cargo in debian/rules
    - source tree contains .rs or Cargo.toml (excluding common vendor trees)
    """
    rules = packaging.get("debian_rules", "")
    return (
        packaging.get("cargo_lock_present", False)
        or "--buildsystem cargo" in rules
        or "dh_cargo" in rules
        or _has_rust_tree_hints(packaging)
    )


def _is_python_package(packaging: dict) -> bool:
    """Return True when the packaging evidence indicates a Python package.

    Detection requires a genuine Python *packaging* signal rather than the mere
    presence of a ``.py`` file, because C/C++ (and other) source trees routinely
    ship helper or test scripts written in Python. A single stray ``.py`` must
    not classify such a package as Python (this previously mis-gated e.g. a C++
    library that ships a helper script).

    Heuristics (any one sufficient):
    - a Python build system in debian/rules (dh_python(3)/dh-python/pybuild, or
      distutils/setuptools/flit);
    - a python3 / dh-python / pybuild build dependency, or an X[S]-Python*
      field, in debian/control;
    - a Python packaging metadata file (setup.py, setup.cfg, pyproject.toml) in
      the source tree (excluding vendored/third-party trees).
    """
    rules = packaging.get("debian_rules", "")
    rules_lower = rules.lower()
    if any(sig in rules for sig in ("dh_python", "dh_python3")):
        return True
    if any(
        sig in rules_lower for sig in ("dh-python", "pybuild", "distutils", "setuptools", "flit")
    ):
        return True

    # debian/control: python3 build-deps or X[S]-Python* fields.
    debian_control = packaging.get("debian_control", "")
    for raw_line in debian_control.splitlines():
        low = raw_line.lower()
        if low.startswith(("build-depends", "build-depends-indep")) and (
            "python3" in low or "dh-python" in low or "pybuild" in low
        ):
            return True
        if low.startswith(("x-python3-version", "xs-python-version", "x-python-version")):
            return True

    # Python packaging metadata files anywhere in the (non-third-party) tree.
    for path in _iter_non_third_party_paths(packaging):
        base = path.rsplit("/", 1)[-1]
        if base in ("setup.py", "setup.cfg", "pyproject.toml"):
            return True

    return False


# Maps a single-language gate name to the one detector function used both
# here and directly by any check that needs the fact outside the gating path
# (e.g. CB-8 calls ``_is_python_package`` itself). Keeping exactly one
# detector per language avoids two independently-evolving implementations of
# "is this package written in X" ever silently drifting apart.
_GATE_DETECTORS: dict[str, Callable[[dict], bool]] = {
    "go": _is_go_package,
    "rust": _is_rust_package,
    "python": _is_python_package,
}


def _language_gate_active(gate: str, ctx) -> bool:
    """Return True when the named language gate is active for this package.

    The gate is resolved from evidence already collected by ESL-4 (Go gate)
    and ESL-8 (Rust gate).  If evidence is unavailable we conservatively
    return True (treat as potentially applicable) so the check is not silently
    skipped when we cannot confirm the absence of the language.

    Gates:
            go     — active when go.sum, dh-golang/golang hints, or Go
                   source/tree hints are present (``_is_go_package``)
            rust   — active when Cargo.lock, dh_cargo/buildsystem hints, or
                   Rust source/tree hints are present (``_is_rust_package``)
      python  — active per the same packaging-metadata heuristics CB-8 uses
                   directly (``_is_python_package``)
      go|rust — active when either go or rust is present (combined gate)

    Supports pipe-separated combined gates; returns True if any of the listed
    gates would be active. Every single-language gate dispatches to the one
    detector function also used directly by checks that need the fact outside
    the gating path (e.g. CB-8 calls ``_is_python_package`` itself), so there
    is exactly one detection heuristic per language, never a second, looser
    one duplicated here.
    """
    gate = gate.lower()

    # Support combined gates like "go|rust"
    if "|" in gate:
        gates = [g.strip() for g in gate.split("|")]
        return any(_language_gate_active(g, ctx) for g in gates)

    packaging = ctx.evidence.get("adapters", {}).get("packaging-source", {})

    if packaging.get("status") != "ok":
        # Cannot confirm absence; assume gate may be active.
        return True

    detector = _GATE_DETECTORS.get(gate)
    if detector is None:
        log.warning("Unknown language gate '%s'; treating as active", gate)
        return True
    return detector(packaging)

    # Unknown gate — assume active (fail-safe).
    log.warning("Unknown language_gate '%s'; treating as active", gate)
    return True
