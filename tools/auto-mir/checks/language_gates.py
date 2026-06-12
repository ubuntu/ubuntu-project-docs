"""Language gate detection for auto-mir checks.

This module provides functions to detect programming language-specific packages
and determine whether language-specific checks should be activated.
"""

from __future__ import annotations

import logging

log = logging.getLogger("auto_mir.checks.language_gates")


def _is_go_package(packaging: dict) -> bool:
    """Return True when the packaging evidence indicates a Go package.

    Heuristics (any one sufficient):
    - go.sum file present in source tree
    - dh-golang or golang mentioned in debian/rules
    """
    rules = packaging.get("debian_rules", "")
    return (
        packaging.get("go_sum_present", False) or "dh-golang" in rules or "golang" in rules.lower()
    )


def _is_rust_package(packaging: dict) -> bool:
    """Return True when the packaging evidence indicates a Rust package.

    Heuristics (any one sufficient):
    - Cargo.lock file present in source tree
    - --buildsystem cargo or dh_cargo in debian/rules
    """
    rules = packaging.get("debian_rules", "")
    return (
        packaging.get("cargo_lock_present", False)
        or "--buildsystem cargo" in rules
        or "dh_cargo" in rules
    )


def _language_gate_active(gate: str, ctx) -> bool:
    """Return True when the named language gate is active for this package.

    The gate is resolved from evidence already collected by ESL-4 (Go gate)
    and ESL-8 (Rust gate).  If evidence is unavailable we conservatively
    return True (treat as potentially applicable) so the check is not silently
    skipped when we cannot confirm the absence of the language.

    Gates:
      go     — active when go.sum present or dh-golang/golang in debian/rules
      rust   — active when Cargo.lock present or dh_cargo/--buildsystem cargo in rules
      python  — active when python3 or python in runtime deps
    """
    gate = gate.lower()
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
