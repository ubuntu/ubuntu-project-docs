"""Language gate detection for auto-mir checks.

This module provides functions to detect programming language-specific packages
and determine whether language-specific checks should be activated.
"""

from __future__ import annotations

import logging

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


def _language_gate_active(gate: str, ctx) -> bool:
    """Return True when the named language gate is active for this package.

    The gate is resolved from evidence already collected by ESL-4 (Go gate)
    and ESL-8 (Rust gate).  If evidence is unavailable we conservatively
    return True (treat as potentially applicable) so the check is not silently
    skipped when we cannot confirm the absence of the language.

    Gates:
            go     — active when go.sum, dh-golang/golang hints, or Go
                   source/tree hints are present
            rust   — active when Cargo.lock, dh_cargo/buildsystem hints, or
                   Rust source/tree hints are present
      python  — active when python3 or python in runtime deps
      go|rust — active when either go or rust is present (combined gate)

    Supports pipe-separated combined gates; returns True if any of the listed
    gates would be active.
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

    if gate == "go":
        return _is_go_package(packaging)

    if gate == "rust":
        return _is_rust_package(packaging)

    if gate == "python":
        dep_analysis = ctx.evidence.get("adapters", {}).get("dep-analysis", {})
        all_deps = " ".join(dep_analysis.get("runtime_dep_packages", []))
        return "python3" in all_deps.lower() or "python" in all_deps.lower()

    # Unknown gate — assume active (fail-safe).
    log.warning("Unknown language_gate '%s'; treating as active", gate)
    return True
