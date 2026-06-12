"""Check evaluation engine for auto-mir.

Implements deterministic, ev_to_ai, and ai mode checks against collected evidence.
This module handles the interpretation and mapping of findings to severities.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

log = logging.getLogger("auto_mir.checks")


def evaluate_checks(ctx) -> list[dict]:
    """Evaluate all checks from catalog against collected evidence.

    Returns list of findings dicts with:
    - id, section, title, mode
    - status: ok|not-ok|unknown
    - severity: ok|recommended|required|nack
    - confidence: low|medium|high
    - message: reviewer-facing statement
    - todo: empty if resolved, TODO line if not
    - evidence_refs: which adapters/keys were used
    """
    if not ctx.catalog:
        return []

    checks = ctx.catalog.get("checks", [])
    findings = []

    for check in checks:
        mode = check.get("mode", "unknown")
        finding = {
            "id": check["id"],
            "section": check.get("section", "unknown"),
            "title": check.get("title", ""),
            "mode": mode,
            "status": "not-evaluated",
            "severity": None,
            "confidence": "low",
            "message": "Check not evaluated",
            "todo": "",
            "evidence_refs": [],
            "blocker_class": check.get("blocker_class", "none"),
        }

        # Apply language gate before routing to evaluator.
        # If the gate says the language is absent, mark ok/not-applicable and skip.
        gate = check.get("language_gate")
        if gate and not _language_gate_active(gate, ctx):
            finding["status"] = "ok"
            finding["severity"] = "ok"
            finding["confidence"] = "high"
            finding["message"] = (
                f"not a {gate} package, no extra constraints to consider in that regard"
            )
            finding["todo"] = ""
            findings.append(finding)
            continue

        # Route to appropriate evaluator
        if mode == "deterministic":
            finding = _eval_deterministic(check, ctx, finding)
        elif mode == "ev_to_ai":
            finding = _eval_ev_to_ai(check, ctx, finding)
        elif mode == "ai":
            finding = _eval_ai(check, ctx, finding)
        elif mode == "human_only":
            finding = _eval_human_only(check, ctx, finding)
        else:
            finding["status"] = "unknown"
            finding["message"] = f"Unknown mode: {mode}"

        todo_value = str(finding.get("todo") or "")
        if finding["status"] != "ok" and not (
            todo_value.startswith("TODO:") or todo_value.startswith("TODO-")
        ):
            finding["todo"] = f"TODO: {finding['id']} {finding['title']}"

        findings.append(finding)

    return findings


# ---------------------------------------------------------------------------
# Language-gate helpers
# ---------------------------------------------------------------------------

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

    rules = packaging.get("debian_rules", "")
    control = packaging.get("debian_control", "")

    if gate == "go":
        go_sum = packaging.get("go_sum_present", False)
        is_go = (
            go_sum
            or "dh-golang" in rules
            or "golang" in rules.lower()
        )
        return is_go

    if gate == "rust":
        cargo_lock = packaging.get("cargo_lock_present", False)
        is_rust = (
            cargo_lock
            or "--buildsystem cargo" in rules
            or "dh_cargo" in rules
        )
        return is_rust

    if gate == "python":
        dep_analysis = ctx.evidence.get("adapters", {}).get("dep-analysis", {})
        all_deps = " ".join(dep_analysis.get("runtime_dep_packages", []))
        return "python3" in all_deps.lower() or "python" in all_deps.lower()

    # Unknown gate — assume active (fail-safe).
    log.warning("Unknown language_gate '%s'; treating as active", gate)
    return True


# ---------------------------------------------------------------------------
# Deterministic Check Evaluators
# ---------------------------------------------------------------------------

def _eval_deterministic(check: dict, ctx, finding: dict) -> dict:
    """Evaluate checks with deterministic logic only."""
    check_id = check["id"]

    # Dispatch to per-check evaluator
    _dispatch = {
        "SUM-1":  _check_sum_1,
        "SUM-2":  _check_sum_2,
        "SUM-4":  _check_sum_4,
        "DEP-1":  _check_dep_1,
        "DEP-3":  _check_dep_3,
        "ESL-1":  _check_esl_1,
        "ESL-3":  _check_esl_3,
        "ESL-4":  _check_esl_4,
        "ESL-7":  _check_esl_7,
        "ESL-8":  _check_esl_8,
        "ESL-9":  _check_esl_9,
        "ESL-10": _check_esl_10,
        "SEC-3":  _check_sec_3,
        "SEC-4":  _check_sec_4,
        "CB-7":   _check_cb_7,
    }
    evaluator = _dispatch.get(check_id)
    if evaluator:
        return evaluator(ctx, finding)
    else:
        finding["status"] = "unknown"
        finding["message"] = "Deterministic check evaluator not implemented"
        finding["todo"] = f"TODO: {finding['id']} {finding['title']}"
        return finding


def _check_sum_1(ctx, finding: dict) -> dict:
    """SUM-1: Source package identified."""
    if ctx.source_package:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = f"Review for Source Package: {ctx.source_package}"
        finding["evidence_refs"] = ["lp-bug-api:source_package"]
    else:
        finding["status"] = "not-ok"
        finding["severity"] = "required"
        finding["confidence"] = "high"
        finding["message"] = "Source package could not be determined"
        finding["todo"] = "TODO: Clarify which source package this review is for"
    return finding


def _check_sum_2(ctx, finding: dict) -> dict:
    """SUM-2: Reporter MIR content present."""
    if ctx.reporter_mir_content:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "Reporter MIR content found and used as context."
        finding["evidence_refs"] = ["lp-bug-api:reporter_content"]
    else:
        finding["status"] = "not-ok"
        finding["severity"] = "nack"
        finding["confidence"] = "high"
        finding["message"] = "Reporter MIR template content not found (hard stop)"
        finding["todo"] = "TODO: Reporter must post their completed MIR template"
    return finding


def _check_dep_1(ctx, finding: dict) -> dict:
    """DEP-1: No unresolved runtime dependencies needing MIR."""
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not analyse runtime dependencies"
        finding["todo"] = "TODO: Verify no runtime dependencies in universe need MIR"
        finding["evidence_refs"] = ["dep-analysis:error"]
        return finding

    deps_not_in_main = dep_analysis.get("deps_not_in_main", [])
    unknown_components = [
        row["package"]
        for row in dep_analysis.get("dep_components", [])
        if row.get("component") == "unknown"
    ]

    if deps_not_in_main:
        finding["status"] = "not-ok"
        finding["severity"] = "required"
        finding["confidence"] = "high"
        finding["message"] = (
            "Runtime dependencies outside main detected: "
            + ", ".join(deps_not_in_main)
        )
        finding["todo"] = (
            "TODO: File MIR/extra-exclude for runtime dependencies outside main: "
            + ", ".join(deps_not_in_main)
        )
        finding["evidence_refs"] = [
            "dep-analysis:dep_components",
            "dep-analysis:deps_not_in_main",
        ]
        return finding

    if unknown_components:
        finding["status"] = "unknown"
        finding["severity"] = "recommended"
        finding["confidence"] = "low"
        finding["message"] = (
            "Could not determine component for some runtime dependencies: "
            + ", ".join(unknown_components)
        )
        finding["todo"] = (
            "TODO: Verify Ubuntu component for runtime dependencies: "
            + ", ".join(unknown_components)
        )
        finding["evidence_refs"] = ["dep-analysis:dep_components"]
        return finding

    finding["status"] = "ok"
    finding["severity"] = "ok"
    finding["confidence"] = "high"
    finding["message"] = "no other runtime Dependencies to MIR due to this"
    finding["evidence_refs"] = [
        "dep-analysis:runtime_dep_packages",
        "dep-analysis:dep_components",
    ]
    return finding


def _check_sec_3(ctx, finding: dict) -> dict:
    """SEC-3: Does not use webkit1/2."""
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not analyse webkit dependencies"
        return finding

    runtime_deps_text = " ".join(
        [f"{d['binary']}:{d['depends']}" for d in dep_analysis.get("runtime_deps", [])]
    )
    if "webkit" in runtime_deps_text.lower():
        finding["status"] = "not-ok"
        finding["severity"] = "required"
        finding["confidence"] = "high"
        finding["message"] = "webkit1/2 dependency found — hard blocker"
        finding["todo"] = "TODO: webkit1/2 dependency must be removed before main inclusion"
        finding["evidence_refs"] = ["dep-analysis:runtime_deps"]
    else:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "does not use webkit1,2"
        finding["evidence_refs"] = ["dep-analysis:runtime_deps"]
    return finding


def _check_sec_4(ctx, finding: dict) -> dict:
    """SEC-4: Does not use lib*v8 directly."""
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not analyse v8 dependencies"
        return finding

    runtime_deps_text = " ".join(
        [f"{d['binary']}:{d['depends']}" for d in dep_analysis.get("runtime_deps", [])]
    )
    if "libv8" in runtime_deps_text.lower():
        finding["status"] = "not-ok"
        finding["severity"] = "required"
        finding["confidence"] = "high"
        finding["message"] = "lib*v8 dependency found — hard blocker"
        finding["todo"] = "TODO: direct lib*v8 dependency must be removed before main inclusion"
        finding["evidence_refs"] = ["dep-analysis:runtime_deps"]
    else:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "does not use lib*v8 directly"
        finding["evidence_refs"] = ["dep-analysis:runtime_deps"]
    return finding


def _check_cb_7(ctx, finding: dict) -> dict:
    """CB-7: No new Python 2 dependency."""
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not analyse Python2 dependencies"
        return finding

    runtime_deps_text = " ".join(
        [f"{d['binary']}:{d['depends']}" for d in dep_analysis.get("runtime_deps", [])]
    )
    # Check for python2, python-*, 2.x style deps
    if any(p in runtime_deps_text.lower() for p in ["python2", "python-", "python2."]):
        finding["status"] = "not-ok"
        finding["severity"] = "required"
        finding["confidence"] = "high"
        finding["message"] = "Python2 dependency found — hard blocker"
        finding["todo"] = "TODO: python2 dependency must be removed or ported before main inclusion"
        finding["evidence_refs"] = ["dep-analysis:runtime_deps"]
    else:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "no new python2 dependency"
        finding["evidence_refs"] = ["dep-analysis:runtime_deps"]
    return finding


def _check_sum_4(ctx, finding: dict) -> dict:
    """SUM-4: ubuntu-mir team is subscribed to the bug."""
    subscribers = ctx.bug.get("subscribers", [])
    if "ubuntu-mir" in subscribers:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "ubuntu-mir is subscribed to this bug."
        finding["evidence_refs"] = ["lp-bug-api:subscribers"]
    else:
        finding["status"] = "not-ok"
        finding["severity"] = "recommended"
        finding["confidence"] = "high"
        finding["message"] = "ubuntu-mir is not subscribed to this bug"
        finding["todo"] = (
            "TODO: The package should get a team bug subscriber on this bug before being promoted "
            "(will block AA promotion)"
        )
        finding["evidence_refs"] = ["lp-bug-api:subscribers"]
    return finding


def _check_dep_3(ctx, finding: dict) -> dict:
    """DEP-3: No -dev/-debug/-doc packages needing exclusion."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if packaging.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not analyse binary packages"
        finding["todo"] = "TODO: DEP-3 Check whether -dev/-debug/-doc packages need exclusion"
        return finding

    binary_packages = dep_analysis.get("binary_packages", [])
    special = [p for p in binary_packages
               if any(p.endswith(s) for s in ("-dev", "-dbg", "-debug", "-doc", "-docs"))]

    if not special:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "no -dev/-debug/-doc packages that need exclusion"
        finding["evidence_refs"] = ["packaging-source:debian_control"]
    else:
        # Check whether any of those special packages have deps outside main
        deps_not_in_main = dep_analysis.get("deps_not_in_main", []) if dep_analysis.get("status") == "ok" else []
        if deps_not_in_main:
            finding["status"] = "not-ok"
            finding["severity"] = "recommended"
            finding["confidence"] = "medium"
            finding["message"] = (
                f"Special packages {special} may pull universe deps; verify extra-excludes needed"
            )
            finding["todo"] = (
                f"TODO: Verify whether {', '.join(special)} should be added to extra-exclude list "
                "(they may pull universe deps into component-mismatches)"
            )
        else:
            finding["status"] = "ok"
            finding["severity"] = "ok"
            finding["confidence"] = "medium"
            finding["message"] = (
                f"Special packages present ({', '.join(special)}) "
                "but their deps appear to be in main"
            )
        finding["evidence_refs"] = ["packaging-source:debian_control", "dep-analysis:dep_components"]
    return finding


def _check_esl_1(ctx, finding: dict) -> dict:
    """ESL-1: No embedded source present."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not collect packaging source"
        finding["todo"] = "TODO: ESL-1 Check for embedded source (packaging-source collection failed)"
        return finding

    vendored_dirs = packaging.get("vendored_dirs", [])
    # Also check debian/control for Built-Using (indicates possible embedded source)
    debian_control = packaging.get("debian_control", "")
    has_built_using = "Built-Using" in debian_control or "Static-Built-Using" in debian_control

    if vendored_dirs:
        finding["status"] = "not-ok"
        finding["severity"] = "required"
        finding["confidence"] = "high"
        finding["message"] = f"Vendored directories found: {', '.join(vendored_dirs)}"
        finding["todo"] = (
            "TODO: Embedded source found — either remove and use archive packages, "
            "or get security team sign-off. Vendored dirs: " + ", ".join(vendored_dirs)
        )
        finding["evidence_refs"] = ["packaging-source:vendored_dirs"]
    elif has_built_using:
        # Built-Using alone is not a blocker; ESL-3 handles unexpected entries.
        # Here we note it's clean w.r.t. embedded source.
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "medium"
        finding["message"] = "no embedded source present (Built-Using present; see ESL-3 for review)"
        finding["evidence_refs"] = ["packaging-source:debian_control"]
    else:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "no embedded source present"
        finding["evidence_refs"] = ["packaging-source:vendored_dirs"]
    return finding


def _check_esl_3(ctx, finding: dict) -> dict:
    """ESL-3: No unexpected Built-Using entries."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not collect debian/control"
        finding["todo"] = "TODO: ESL-3 Check for unexpected Built-Using entries"
        return finding

    debian_control = packaging.get("debian_control", "")

    import re as _re
    built_using_entries = _re.findall(
        r"(?:Built-Using|Static-Built-Using)\s*:\s*([^\n]+(?:\n\s[^\n]+)*)",
        debian_control,
        flags=_re.IGNORECASE,
    )

    if not built_using_entries:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "does not have unexpected Built-Using entries"
        finding["evidence_refs"] = ["packaging-source:debian_control"]
        return finding

    # Check for toolchain-only pattern (acceptable) vs. other entries
    all_entries_text = " ".join(built_using_entries).lower()
    # Toolchain-only Built-Using (golang, rust, cgo) are expected.
    # Anything else (especially ${misc:Built-Using} with explicit pkg list) needs attention.
    if "golang" in all_entries_text or "rust" in all_entries_text or "${misc:built-using}" in all_entries_text:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "medium"
        finding["message"] = (
            "Built-Using entries present but appear to be standard toolchain entries: "
            + "; ".join(built_using_entries)
        )
    else:
        finding["status"] = "not-ok"
        finding["severity"] = "required"
        finding["confidence"] = "medium"
        finding["message"] = (
            "Unexpected Built-Using entries that may indicate untracked embedded source: "
            + "; ".join(built_using_entries)
        )
        finding["todo"] = (
            "TODO: Review Built-Using entries — possible untracked embedded source: "
            + "; ".join(built_using_entries)
        )
    finding["evidence_refs"] = ["packaging-source:debian_control"]
    return finding


def _check_esl_4(ctx, finding: dict) -> dict:
    """ESL-4: Go language detection gate."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not determine language (packaging-source failed)"
        finding["todo"] = "TODO: ESL-4 Determine if this is a Go package"
        return finding

    go_sum = packaging.get("go_sum_present", False)
    debian_rules = packaging.get("debian_rules", "")
    is_go = go_sum or "dh-golang" in debian_rules or "golang" in debian_rules.lower()

    if is_go:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "Go Package — Debian Go packaging guidelines apply (see ESL-5/6/7)"
        # ESL-4 itself is just the gate; it's ok to confirm it's Go.
        # The actual compliance checks are ESL-5, ESL-6, ESL-7.
    else:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "not a go package, no extra constraints to consider in that regard"
    finding["evidence_refs"] = ["packaging-source:go_sum_present", "packaging-source:debian_rules"]
    return finding


def _check_esl_7(ctx, finding: dict) -> dict:
    """ESL-7: Go build type (shared vs static)."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not determine Go build type (packaging-source failed)"
        finding["todo"] = "TODO: ESL-7 Determine Go build type (shared vs static)"
        return finding

    go_sum = packaging.get("go_sum_present", False)
    debian_rules = packaging.get("debian_rules", "")
    is_go = go_sum or "dh-golang" in debian_rules or "golang" in debian_rules.lower()

    if not is_go:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "not a go package, no extra constraints to consider in that regard"
        finding["evidence_refs"] = []
        return finding

    # Detect build mode
    if "-buildmode=shared" in debian_rules or "linkshared" in debian_rules:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "golang: shared builds"
    elif "DH_GOLANG_BUILDPKG" in debian_rules or "dh_golang" in debian_rules:
        # dh-golang without explicit shared mode defaults to static in modern versions.
        # This needs human confirmation.
        finding["status"] = "not-ok"
        finding["severity"] = "recommended"
        finding["confidence"] = "medium"
        finding["message"] = "Go package uses dh-golang; build mode not confirmed as shared"
        finding["todo"] = (
            "TODO: Confirm Go build mode — if static, team must confirm commitment to "
            "additional maintenance responsibilities implied by static builds"
        )
    else:
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Go package but build mode could not be determined from debian/rules"
        finding["todo"] = "TODO: ESL-7 Determine Go build type (shared vs static)"
    finding["evidence_refs"] = ["packaging-source:debian_rules"]
    return finding


def _check_esl_8(ctx, finding: dict) -> dict:
    """ESL-8: Rust language detection gate."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not determine language (packaging-source failed)"
        finding["todo"] = "TODO: ESL-8 Determine if this is a Rust package"
        return finding

    cargo_lock = packaging.get("cargo_lock_present", False)
    debian_rules = packaging.get("debian_rules", "")
    is_rust = cargo_lock or "--buildsystem cargo" in debian_rules or "dh_cargo" in debian_rules

    if is_rust:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = (
            "Rust Package — Rust-specific constraints apply (see ESL-9/10)"
        )
    else:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "not a rust package, no extra constraints to consider in that regard"
    finding["evidence_refs"] = [
        "packaging-source:cargo_lock_present", "packaging-source:debian_rules"
    ]
    return finding


def _check_esl_9(ctx, finding: dict) -> dict:
    """ESL-9: Rust package uses dh_cargo."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not check debian/rules (packaging-source failed)"
        finding["todo"] = "TODO: ESL-9 Verify Rust package uses dh_cargo"
        return finding

    cargo_lock = packaging.get("cargo_lock_present", False)
    debian_rules = packaging.get("debian_rules", "")
    is_rust = cargo_lock or "--buildsystem cargo" in debian_rules or "dh_cargo" in debian_rules

    if not is_rust:
        # Not a Rust package; gate doesn't apply.
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "not a rust package, dh_cargo gate not applicable"
        finding["evidence_refs"] = []
        return finding

    uses_dh_cargo = "--buildsystem cargo" in debian_rules or "dh_cargo" in debian_rules
    if uses_dh_cargo:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "rust package using dh_cargo (dh ... --buildsystem cargo)"
    else:
        finding["status"] = "not-ok"
        finding["severity"] = "required"
        finding["confidence"] = "high"
        finding["message"] = "Rust package detected but dh_cargo / --buildsystem cargo not found in debian/rules"
        finding["todo"] = "TODO: Rust packages must use dh_cargo (dh ... --buildsystem cargo)"
    finding["evidence_refs"] = ["packaging-source:debian_rules", "packaging-source:cargo_lock_present"]
    return finding


def _check_esl_10(ctx, finding: dict) -> dict:
    """ESL-10: Rust: vendored deps, no unexpected Built-Using, Cargo.lock present."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = "Could not collect packaging source"
        finding["todo"] = "TODO: ESL-10 Verify Rust vendored deps / Cargo.lock / Built-Using"
        return finding

    cargo_lock = packaging.get("cargo_lock_present", False)
    debian_rules = packaging.get("debian_rules", "")
    is_rust = cargo_lock or "--buildsystem cargo" in debian_rules or "dh_cargo" in debian_rules

    if not is_rust:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "not a rust package, ESL-10 constraints not applicable"
        finding["evidence_refs"] = []
        return finding

    problems = []
    if not cargo_lock:
        problems.append("Cargo.lock not found")

    # Check for unexpected Built-Using (Rust packages should have none or only toolchain)
    debian_control = packaging.get("debian_control", "")
    import re as _re
    built_using_entries = _re.findall(
        r"(?:Built-Using|Static-Built-Using)\s*:\s*([^\n]+(?:\n\s[^\n]+)*)",
        debian_control,
        flags=_re.IGNORECASE,
    )
    unexpected_bu = [
        e for e in built_using_entries
        if "rust" not in e.lower() and "cargo" not in e.lower()
    ]
    if unexpected_bu:
        problems.append("Unexpected Built-Using entries: " + "; ".join(unexpected_bu))

    if problems:
        finding["status"] = "not-ok"
        finding["severity"] = "required"
        finding["confidence"] = "high"
        finding["message"] = "Rust package has issues: " + "; ".join(problems)
        finding["todo"] = "TODO: Fix Rust package issues: " + "; ".join(problems)
    else:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = (
            "Rust package that has all dependencies vendored. "
            "It does neither have *Built-Using (after build). "
            "Nor does the build log indicate built-in sources missed as Built-Using."
        )
    finding["evidence_refs"] = [
        "packaging-source:cargo_lock_present",
        "packaging-source:debian_control",
    ]
    return finding


# ---------------------------------------------------------------------------
# EV_TO_AI Check Evaluators (stubs)
# ---------------------------------------------------------------------------

def _eval_ev_to_ai(check: dict, ctx, finding: dict) -> dict:
    """Evaluate a check by combining collected evidence with an LLM call.

    Assembles the evidence payload relevant to this check, renders the
    ev_to_ai.md prompt template, calls the LLM, and maps the response back
    to a finding dict.  Falls back to a manual-review TODO on any failure.
    """
    import llm

    evidence_payload = _build_evidence_payload(check, ctx)
    policy_excerpt = _build_policy_excerpt(check, ctx)
    prompt = _render_ev_to_ai_prompt(check, evidence_payload, policy_excerpt, ctx)

    try:
        response = llm.call_llm(prompt, ctx)
    except llm.LLMError as exc:
        log.warning("LLM call failed for check %s: %s", check["id"], exc)
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = f"LLM unavailable: {exc}"
        finding["todo"] = _default_todo_for_check(check, fallback_suffix="manual review needed (LLM unavailable)")
        return finding

    return _apply_llm_response(response, check, finding)


# ---------------------------------------------------------------------------
# AI Check Evaluators
# ---------------------------------------------------------------------------

def _eval_ai(check: dict, ctx, finding: dict) -> dict:
    """Evaluate checks that require pure AI synthesis over the full findings set.

    Uses the same LLM path as ev_to_ai but passes the full evidence store rather
    than check-specific adapters.  Used for checks like SUM-5 (overall verdict).
    """
    import llm

    # For pure-AI checks, pass all available context (findings so far + bug metadata).
    full_evidence = {
        "source_package": ctx.source_package,
        "bug_id": ctx.bug_id,
        "series": ctx.series,
        "bug_title": ctx.bug.get("title", ""),
        "reporter_mir_content_present": bool(ctx.reporter_mir_content),
        "findings_so_far": _summarise_findings_so_far(ctx),
    }
    policy_excerpt = _build_policy_excerpt(check, ctx)
    prompt = _render_ev_to_ai_prompt(check, full_evidence, policy_excerpt, ctx)

    try:
        response = llm.call_llm(prompt, ctx)
    except llm.LLMError as exc:
        log.warning("LLM call failed for check %s: %s", check["id"], exc)
        finding["status"] = "unknown"
        finding["confidence"] = "low"
        finding["message"] = f"LLM unavailable: {exc}"
        finding["todo"] = _default_todo_for_check(check, fallback_suffix="requires AI synthesis")
        return finding

    return _apply_llm_response(response, check, finding)


# ---------------------------------------------------------------------------
# Human-Only Check Evaluators
# ---------------------------------------------------------------------------

def _eval_human_only(check: dict, ctx, finding: dict) -> dict:
    """Evaluate checks that require human judgment only."""
    finding["status"] = "unknown"
    finding["confidence"] = "low"
    finding["message"] = "Human review required"
    finding["todo"] = f"TODO: {check.get('title', 'Check')} — reviewer judgment needed"
    return finding


# ---------------------------------------------------------------------------
# LLM helpers — prompt rendering and response mapping
# ---------------------------------------------------------------------------

def _build_evidence_payload(check: dict, ctx) -> dict:
    """Build a compact evidence dict for the adapters required by this check.

    Only includes adapter outputs listed in adapters_required/adapters_optional
    for the check, plus basic package/bug metadata.  Large raw strings are
    truncated to keep prompt size manageable.
    """
    payload: dict = {
        "source_package": ctx.source_package,
        "bug_id": ctx.bug_id,
        "series": ctx.series,
        "bug_title": ctx.bug.get("title", ""),
    }

    adapters_store = ctx.evidence.get("adapters", {})
    relevant = (
        list(check.get("adapters_required", []))
        + list(check.get("adapters_optional", []))
    )
    for adapter_id in relevant:
        data = adapters_store.get(adapter_id)
        if data is None:
            payload[adapter_id] = {"status": "not_collected"}
        else:
            payload[adapter_id] = _truncate_adapter_data(data)

    # Always include compact bug context
    payload["reporter_mir_content_snippet"] = (ctx.reporter_mir_content or "")[:2000]
    payload["bug_subscribers"] = ctx.bug.get("subscribers", [])
    payload["bug_tags"] = ctx.bug.get("tags", [])

    return payload


def _truncate_adapter_data(data: dict, max_str_len: int = 1000) -> dict:
    """Return a copy of data with large outputs trimmed for LLM token budget.

    For known large fields (lintian_output, debian_*, build_log), only include
    a brief summary or first few lines. For other large strings, truncate to 1000 chars.
    """
    SUMMARY_FIELDS = {
        "lintian_output",  # lintian full output
        "debian_control",  # control file
        "debian_rules",    # rules file
        "debian_watch",
        "debian_copyright",
        "debian_tests_control",
        "raw_output",      # component-mismatches raw output
        "build_log",
    }

    result = {}
    for k, v in data.items():
        if k in SUMMARY_FIELDS and isinstance(v, str):
            # For known large fields, just count lines/errors
            if k == "lintian_output":
                lines = v.splitlines()
                errors = sum(1 for l in lines if l.startswith("E: "))
                warnings = sum(1 for l in lines if l.startswith("W: "))
                result[k] = f"[{len(lines)} lines, {errors} errors, {warnings} warnings]"
            else:
                # Keep a 300-char preview
                result[k] = v[:300] + ("..." if len(v) > 300 else "")
        elif isinstance(v, str) and len(v) > max_str_len:
            result[k] = v[:max_str_len] + f" ... [truncated, total {len(v)} chars]"
        elif isinstance(v, dict):
            result[k] = _truncate_adapter_data(v, max_str_len)
        elif isinstance(v, list) and len(v) > 30:
            # Truncate large lists to first 15 items + summary
            result[k] = v[:15] + [{"...": f"plus {len(v) - 15} more items"}]
        else:
            result[k] = v
    return result


def _build_policy_excerpt(check: dict, ctx) -> str:
    """Extract relevant policy text for a check from the MIR reviewer template.

    Combines:
    - The check's ai_policy field (specific reviewer guidance)
    - The todo_refs list (what this check resolves)
    - RULE lines from the matching section in mir-reviewers-template.md
    """
    section = check.get("section", "")
    todo_refs = check.get("todo_refs", [])
    ai_policy = check.get("ai_policy", "")

    parts = []
    if ai_policy:
        parts.append(f"AI policy for this check:\n{ai_policy.strip()}")

    if todo_refs:
        parts.append(
            "TODO references this check resolves:\n"
            + "\n".join(f"  {t}" for t in todo_refs)
        )

    # Pull RULE lines from the reviewer template for this section
    workspace_root = getattr(ctx, "workspace_root", None)
    if workspace_root:
        template_path = (
            Path(workspace_root) / "docs" / "MIR" / "mir-reviewers-template.md"
        )
        if template_path.exists():
            section_text = _extract_template_section(template_path, section)
            rule_lines = [
                line for line in section_text.splitlines()
                if line.strip().startswith("RULE:")
            ]
            if rule_lines:
                parts.append(
                    f"Reviewer policy rules for [{section}]:\n"
                    + "\n".join(rule_lines[:30])
                )

    return "\n\n".join(parts) if parts else f"Check {check.get('id')} in section [{section}]"


def _extract_template_section(template_path: Path, section: str) -> str:
    """Return the raw text of a named section from the MIR reviewer template."""
    try:
        text = template_path.read_text(encoding="utf-8")
    except OSError:
        return ""

    header = f"[{section}]"
    lines = text.splitlines()
    in_section = False
    collected: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == header:
            in_section = True
            continue
        if in_section:
            if stripped.startswith("[") and stripped.endswith("]") and stripped != header:
                break
            collected.append(line)
    return "\n".join(collected)


def _render_ev_to_ai_prompt(
    check: dict,
    evidence_payload: dict,
    policy_excerpt: str,
    ctx,
) -> str:
    """Render the ev_to_ai.md prompt template with check-specific substitutions."""
    tool_root = getattr(ctx, "tool_root", None)
    template_path = tool_root and (Path(tool_root) / "prompts" / "ev_to_ai.md")

    if template_path and Path(template_path).exists():
        template = Path(template_path).read_text(encoding="utf-8")
    else:
        template = _FALLBACK_PROMPT_TEMPLATE

    confidence_model = (
        ctx.catalog.get("global_policies", {})
        .get("confidence_model", {})
        .get("description", "low | medium | high")
    )

    substitutions = {
        "{{check_id}}": check.get("id", ""),
        "{{check_title}}": check.get("title", ""),
        "{{section}}": check.get("section", ""),
        "{{todo_refs}}": "\n".join(check.get("todo_refs", [])),
        "{{policy_excerpt}}": policy_excerpt,
        "{{evidence_json}}": json.dumps(evidence_payload, indent=2, default=str),
        "{{confidence_model}}": confidence_model,
    }
    result = template
    for placeholder, value in substitutions.items():
        result = result.replace(placeholder, value)
    return result


def _apply_llm_response(response: dict, check: dict, finding: dict) -> dict:
    """Map a validated LLM JSON response back onto a finding dict.

    Accepts partial responses — only overrides fields that are present and
    non-empty in the response.  Always marks the finding as requiring human
    confirmation regardless of what the model returns.
    """
    if not isinstance(response, dict):
        log.warning("LLM response for %s is not a dict: %r", check["id"], response)
        finding["status"] = "unknown"
        finding["todo"] = _default_todo_for_check(check, fallback_suffix="LLM response invalid")
        return finding

    valid_statuses = {"ok", "not-ok", "unknown"}
    valid_severities = {"ok", "recommended", "required", "nack"}
    valid_confidences = {"low", "medium", "high"}

    status = response.get("status", "unknown")
    if status not in valid_statuses:
        status = "unknown"

    severity = response.get("severity", "ok")
    if severity not in valid_severities:
        severity = "ok"

    confidence = response.get("confidence", "medium")
    if confidence not in valid_confidences:
        confidence = "medium"
    # AI-derived findings are capped at medium unless a deterministic check corroborates.
    if confidence == "high":
        confidence = "medium"

    finding["status"] = status
    finding["severity"] = severity
    finding["confidence"] = confidence

    message = (response.get("message") or "").strip()
    if message:
        finding["message"] = message

    todo = (response.get("todo") or "").strip()
    rationale = (response.get("rationale") or "").strip()

    if status != "ok":
        # [Summary] option checks (e.g. SUM-5/SUM-6) must keep all variants
        # visible for human final judgment when unresolved.
        if check.get("section") == "Summary" and check.get("options"):
            todo_refs = [str(x).strip() for x in check.get("todo_refs", []) if str(x).strip()]
            if todo_refs:
                todo = "\n".join(todo_refs)

        if todo and not (todo.startswith("TODO:") or todo.startswith("TODO-")):
            todo = f"TODO: {todo}"
        if not todo:
            todo = _default_todo_for_check(check, fallback_suffix="review needed")
        if rationale:
            finding["message"] = f"{message}\n  Rationale: {rationale}" if message else rationale
        finding["todo"] = todo
    else:
        if rationale:
            finding["message"] = f"{message}\n  ({rationale})" if message else rationale
        finding["todo"] = ""

    risk_flags = response.get("risk_flags", [])
    if isinstance(risk_flags, list) and risk_flags:
        finding["risk_flags"] = risk_flags

    ev_refs = response.get("evidence_refs", [])
    if isinstance(ev_refs, list) and ev_refs:
        finding["evidence_refs"] = ev_refs

    # Always require human confirmation for AI-derived findings
    finding["human_confirmation_required"] = True

    return finding


def _default_todo_for_check(check: dict, fallback_suffix: str) -> str:
    """Return a default TODO string for a check.

    Prefer catalog todo_refs so mutually-exclusive options (TODO-A/B/C) are kept
    visible for human review when the tool cannot decide.
    """
    todo_refs = [str(x).strip() for x in check.get("todo_refs", []) if str(x).strip()]
    if todo_refs:
        return "\n".join(todo_refs)
    return f"TODO: {check.get('title', check.get('id', 'Check'))} — {fallback_suffix}"


def _summarise_findings_so_far(ctx) -> list[dict]:
    """Return a compact summary of findings already evaluated in this run."""
    results = []
    for f in getattr(ctx, "findings", []):
        results.append({
            "id": f.get("id"),
            "section": f.get("section"),
            "status": f.get("status"),
            "severity": f.get("severity"),
            "message": (f.get("message") or "")[:200],
        })
    return results


# Fallback prompt template — used when prompts/ev_to_ai.md is missing.
_FALLBACK_PROMPT_TEMPLATE = """\
You are assisting a human MIR reviewer for Ubuntu main inclusion.

Task:
- Evaluate check {{check_id}} ({{check_title}}) in section {{section}}.
- Use only the provided evidence payload.
- Apply Ubuntu MIR policy as authoritative.
- Return a tentative reviewer-facing finding.

Policy:
{{policy_excerpt}}

TODO references this check resolves:
{{todo_refs}}

Evidence:
{{evidence_json}}

Confidence model: {{confidence_model}}

Return ONLY a JSON object with these exact fields (no markdown fences):
{
  "id": "{{check_id}}",
  "status": "ok|not-ok|unknown",
  "severity": "ok|recommended|required|nack",
  "confidence": "low|medium|high",
  "message": "short reviewer-facing statement (1-2 sentences)",
  "todo": "empty string if resolved, otherwise a TODO: prefixed line",
  "rationale": "max 2 sentences grounded in evidence",
  "human_confirmation_required": true,
  "evidence_refs": ["adapter:key"],
  "risk_flags": []
}
"""

