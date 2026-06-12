"""Check evaluation engine for auto-mir.

Implements deterministic, ev_to_ai, and ai mode checks against collected evidence.
This module handles the interpretation and mapping of findings to severities.
"""

from __future__ import annotations

import logging

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

        if finding["status"] != "ok" and not str(finding.get("todo") or "").startswith("TODO:"):
            finding["todo"] = f"TODO: {finding['id']} {finding['title']}"

        findings.append(finding)

    return findings


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
    """SUM-4: Team bug subscriber present on the source package."""
    subscribers = ctx.bug.get("subscribers", [])
    if "ubuntu-mir" in subscribers:
        finding["status"] = "ok"
        finding["severity"] = "ok"
        finding["confidence"] = "high"
        finding["message"] = "Package has a team bug subscriber (ubuntu-mir subscribed)."
        finding["evidence_refs"] = ["lp-bug-api:subscribers"]
    else:
        finding["status"] = "not-ok"
        finding["severity"] = "recommended"
        finding["confidence"] = "high"
        finding["message"] = "No team bug subscriber found on source package"
        finding["todo"] = (
            "TODO: The package should get a team bug subscriber before being promoted "
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
    """Evaluate checks that blend evidence with AI synthesis (not yet implemented)."""
    finding["status"] = "unknown"
    finding["confidence"] = "low"
    finding["message"] = "ev_to_ai check evaluator not yet implemented"
    finding["todo"] = f"TODO: {check.get('title', 'Check')} — manual review needed"
    return finding


# ---------------------------------------------------------------------------
# AI Check Evaluators (stubs)
# ---------------------------------------------------------------------------

def _eval_ai(check: dict, ctx, finding: dict) -> dict:
    """Evaluate checks that require AI synthesis (not yet implemented)."""
    finding["status"] = "unknown"
    finding["confidence"] = "low"
    finding["message"] = "ai check evaluator not yet implemented"
    finding["todo"] = f"TODO: {check.get('title', 'Check')} — requires AI synthesis"
    return finding


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
