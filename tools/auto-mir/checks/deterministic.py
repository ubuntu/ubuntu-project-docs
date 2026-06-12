"""Deterministic check evaluators for auto-mir.

Contains all check functions that evaluate evidence without LLM calls,
the dispatch table, and the _eval_deterministic entry point.
"""

from __future__ import annotations

import logging
import re

log = logging.getLogger("auto_mir.checks.deterministic")

from checks.language_gates import _is_go_package, _is_rust_package
from models import Finding
from checks.registry import deterministic_check, evaluator, DETERMINISTIC_CHECKS

@deterministic_check("SUM-1")
def _check_sum_1(ctx, finding: Finding) -> Finding:
    """SUM-1: Source package identified."""
    if ctx.source_package:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = f"Review for Source Package: {ctx.source_package}"
        finding.evidence_refs = ["lp-bug-api:source_package"]
    else:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = "Source package could not be determined"
        finding.todo = "TODO: Clarify which source package this review is for"
    return finding


@deterministic_check("SUM-2")
def _check_sum_2(ctx, finding: Finding) -> Finding:
    """SUM-2: Reporter MIR content present."""
    if ctx.reporter_mir_content:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "Reporter MIR content found and used as context."
        finding.evidence_refs = ["lp-bug-api:reporter_content"]
    else:
        finding.status = "not-ok"
        finding.severity = "nack"
        finding.confidence = "high"
        finding.message = "Reporter MIR template content not found (hard stop)"
        finding.todo = "TODO: - Reporter must post their completed MIR template"
    return finding


@deterministic_check("DEP-1")
def _check_dep_1(ctx, finding: Finding) -> Finding:
    """DEP-1: No unresolved runtime dependencies needing MIR."""
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not analyse runtime dependencies"
        finding.todo = "TODO: - Verify no runtime dependencies in universe need MIR"
        finding.evidence_refs = ["dep-analysis:error"]
        return finding

    deps_not_in_main = dep_analysis.get("deps_not_in_main", [])
    unknown_components = [
        row["package"]
        for row in dep_analysis.get("dep_components", [])
        if row.get("component") == "unknown"
    ]

    if deps_not_in_main:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = "Runtime dependencies outside main detected: " + ", ".join(
            deps_not_in_main
        )
        finding.todo = (
            "TODO: - File MIR/extra-exclude for runtime dependencies outside main: "
            + ", ".join(deps_not_in_main)
        )
        finding.evidence_refs = [
            "dep-analysis:dep_components",
            "dep-analysis:deps_not_in_main",
        ]
        return finding

    if unknown_components:
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = (
            "Could not determine component for some runtime dependencies: "
            + ", ".join(unknown_components)
        )
        finding.todo = "TODO: - Verify Ubuntu component for runtime dependencies: " + ", ".join(
            unknown_components
        )
        finding.evidence_refs = ["dep-analysis:dep_components"]
        return finding

    finding.status = "ok"
    finding.severity = "ok"
    finding.confidence = "high"
    finding.message = "no other runtime Dependencies to MIR due to this"
    finding.evidence_refs = [
        "dep-analysis:runtime_dep_packages",
        "dep-analysis:dep_components",
    ]
    return finding


@deterministic_check("SEC-3")
def _check_sec_3(ctx, finding: Finding) -> Finding:
    """SEC-3: Does not use webkit1/2."""
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not analyse webkit dependencies"
        return finding

    runtime_deps_text = " ".join(
        [f"{d['binary']}:{d['depends']}" for d in dep_analysis.get("runtime_deps", [])]
    )
    if "webkit" in runtime_deps_text.lower():
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = "webkit1/2 dependency found — hard blocker"
        finding.todo = "TODO: - webkit1/2 dependency must be removed before main inclusion"
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "does not use webkit1,2"
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    return finding


@deterministic_check("SEC-4")
def _check_sec_4(ctx, finding: Finding) -> Finding:
    """SEC-4: Does not use lib*v8 directly."""
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not analyse v8 dependencies"
        return finding

    runtime_deps_text = " ".join(
        [f"{d['binary']}:{d['depends']}" for d in dep_analysis.get("runtime_deps", [])]
    )
    if "libv8" in runtime_deps_text.lower():
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = "lib*v8 dependency found — hard blocker"
        finding.todo = "TODO: - direct lib*v8 dependency must be removed before main inclusion"
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "does not use lib*v8 directly"
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    return finding


@deterministic_check("CB-7")
def _check_cb_7(ctx, finding: Finding) -> Finding:
    """CB-7: No new Python 2 dependency."""
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not analyse Python2 dependencies"
        return finding

    runtime_deps_text = " ".join(
        [f"{d['binary']}:{d['depends']}" for d in dep_analysis.get("runtime_deps", [])]
    )
    # Check for python2, python-*, 2.x style deps
    if any(p in runtime_deps_text.lower() for p in ["python2", "python-", "python2."]):
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = "Python2 dependency found — hard blocker"
        finding.todo = "TODO: - python2 dependency must be removed or ported before main inclusion"
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "no new python2 dependency"
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    return finding


@deterministic_check("SUM-4")
def _check_sum_4(ctx, finding: Finding) -> Finding:
    """SUM-4: Package has a team subscriber in package-team-mapping."""
    adapters = ctx.evidence.get("adapters", {})
    team_mapping_adapter = adapters.get("team-mapping", {})
    
    if team_mapping_adapter.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not check team subscription (team-mapping adapter failed)"
        finding.todo = "TODO: - Manually verify package has a team subscriber"
        finding.evidence_refs = ["team-mapping:error"]
        return finding
    
    subscribed_teams = team_mapping_adapter.get("subscribed_teams", [])
    
    if subscribed_teams:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = f"Package has team subscriber(s): {', '.join(subscribed_teams)}"
        finding.evidence_refs = ["team-mapping:subscribed_teams"]
    else:
        finding.status = "not-ok"
        finding.severity = "recommended"
        finding.confidence = "high"
        finding.message = "Package does not have a team subscriber"
        finding.todo = (
            "TODO: - The package should get a team bug subscriber on this bug before being promoted"
        )
        finding.evidence_refs = ["team-mapping:subscribed_teams"]
    
    return finding


@deterministic_check("DEP-3")
def _check_dep_3(ctx, finding: Finding) -> Finding:
    """DEP-3: No -dev/-debug/-doc packages needing exclusion."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not analyse binary packages"
        finding.todo = "TODO: - Check whether -dev/-debug/-doc packages need exclusion"
        return finding

    binary_packages = dep_analysis.get("binary_packages", [])
    special = [
        p
        for p in binary_packages
        if any(p.endswith(s) for s in ("-dev", "-dbg", "-debug", "-doc", "-docs"))
    ]

    if not special:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "no -dev/-debug/-doc packages that need exclusion"
        finding.evidence_refs = ["packaging-source:debian_control"]
    else:
        # Check whether any of those special packages have deps outside main
        deps_not_in_main = (
            dep_analysis.get("deps_not_in_main", []) if dep_analysis.get("status") == "ok" else []
        )
        if deps_not_in_main:
            finding.status = "not-ok"
            finding.severity = "recommended"
            finding.confidence = "medium"
            finding.message = (
                f"Special packages {special} may pull universe deps; verify extra-excludes needed"
            )
            finding.todo = (
                f"TODO: - Verify whether {', '.join(special)} should be added to extra-exclude list "
                "(they may pull universe deps into component-mismatches)"
            )
        else:
            finding.status = "ok"
            finding.severity = "ok"
            finding.confidence = "medium"
            finding.message = (
                f"Special packages present ({', '.join(special)}) "
                "but their deps appear to be in main"
            )
        finding.evidence_refs = [
            "packaging-source:debian_control",
            "dep-analysis:dep_components",
        ]
    return finding


@deterministic_check("ESL-1")
def _check_esl_1(ctx, finding: Finding) -> Finding:
    """ESL-1: No embedded source present."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not collect packaging source"
        finding.todo = (
            "TODO: - Check for embedded source (packaging-source collection failed)"
        )
        return finding

    vendored_dirs = packaging.get("vendored_dirs", [])
    # Also check debian/control for Built-Using (indicates possible embedded source)
    debian_control = packaging.get("debian_control", "")
    has_built_using = "Built-Using" in debian_control or "Static-Built-Using" in debian_control

    if vendored_dirs:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = f"Vendored directories found: {', '.join(vendored_dirs)}"
        finding.todo = (
            "TODO: - Embedded source found — either remove and use archive packages, "
            "or get security team sign-off. Vendored dirs: " + ", ".join(vendored_dirs)
        )
        finding.evidence_refs = ["packaging-source:vendored_dirs"]
    elif has_built_using:
        # Built-Using alone is not a blocker; ESL-3 handles unexpected entries.
        # Here we note it's clean w.r.t. embedded source.
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "medium"
        finding.message = (
            "no embedded source present (Built-Using present; see ESL-3 for review)"
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "no embedded source present"
        finding.evidence_refs = ["packaging-source:vendored_dirs"]
    return finding


@deterministic_check("ESL-3")
def _check_esl_3(ctx, finding: Finding) -> Finding:
    """ESL-3: No unexpected Built-Using entries."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not collect debian/control"
        finding.todo = "TODO: - Check for unexpected Built-Using entries"
        return finding

    debian_control = packaging.get("debian_control", "")

    built_using_entries = re.findall(
        r"(?:Built-Using|Static-Built-Using)\s*:\s*([^\n]+(?:\n\s[^\n]+)*)",
        debian_control,
        flags=re.IGNORECASE,
    )

    if not built_using_entries:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "does not have unexpected Built-Using entries"
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # Check for toolchain-only pattern (acceptable) vs. other entries
    all_entries_text = " ".join(built_using_entries).lower()
    # Toolchain-only Built-Using (golang, rust, cgo) are expected.
    # Anything else (especially ${misc:Built-Using} with explicit pkg list) needs attention.
    if (
        "golang" in all_entries_text
        or "rust" in all_entries_text
        or "${misc:built-using}" in all_entries_text
    ):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "medium"
        finding.message = (
            "Built-Using entries present but appear to be standard toolchain entries: "
            + "; ".join(built_using_entries)
        )
    else:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "medium"
        finding.message = (
            "Unexpected Built-Using entries that may indicate untracked embedded source: "
            + "; ".join(built_using_entries)
        )
        finding.todo = (
            "TODO: - Review Built-Using entries — possible untracked embedded source: "
            + "; ".join(built_using_entries)
        )
    finding.evidence_refs = ["packaging-source:debian_control"]
    return finding


@deterministic_check("ESL-4")
def _check_esl_4(ctx, finding: Finding) -> Finding:
    """ESL-4: Go language detection gate."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not determine language (packaging-source failed)"
        finding.todo = "TODO: - Determine if this is a Go package"
        return finding

    if _is_go_package(packaging):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "Go Package — Debian Go packaging guidelines apply (see ESL-5/6/7)"
        # ESL-4 itself is just the gate; it's ok to confirm it's Go.
        # The actual compliance checks are ESL-5, ESL-6, ESL-7.
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "not a go package, no extra constraints to consider in that regard"
    finding.evidence_refs = [
        "packaging-source:go_sum_present",
        "packaging-source:debian_rules",
    ]
    return finding


@deterministic_check("ESL-7")
def _check_esl_7(ctx, finding: Finding) -> Finding:
    """ESL-7: Go build type (shared vs static)."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not determine Go build type (packaging-source failed)"
        finding.todo = "TODO: - Determine Go build type (shared vs static)"
        return finding

    if not _is_go_package(packaging):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "not a go package, no extra constraints to consider in that regard"
        finding.evidence_refs = []
        return finding

    # Detect build mode
    debian_rules = packaging.get("debian_rules", "")
    if "-buildmode=shared" in debian_rules or "linkshared" in debian_rules:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "golang: shared builds"
    elif "DH_GOLANG_BUILDPKG" in debian_rules or "dh_golang" in debian_rules:
        # dh-golang without explicit shared mode defaults to static in modern versions.
        # This needs human confirmation.
        finding.status = "not-ok"
        finding.severity = "recommended"
        finding.confidence = "medium"
        finding.message = "Go package uses dh-golang; build mode not confirmed as shared"
        finding.todo = (
            "TODO: - Confirm Go build mode — if static, team must confirm commitment to "
            "additional maintenance responsibilities implied by static builds"
        )
    else:
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Go package but build mode could not be determined from debian/rules"
        finding.todo = "TODO: - Determine Go build type (shared vs static)"
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


@deterministic_check("ESL-8")
def _check_esl_8(ctx, finding: Finding) -> Finding:
    """ESL-8: Rust language detection gate."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not determine language (packaging-source failed)"
        finding.todo = "TODO: - Determine if this is a Rust package"
        return finding

    if _is_rust_package(packaging):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "Rust Package — Rust-specific constraints apply (see ESL-9/10)"
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "not a rust package, no extra constraints to consider in that regard"
    finding.evidence_refs = [
        "packaging-source:cargo_lock_present",
        "packaging-source:debian_rules",
    ]
    return finding


@deterministic_check("ESL-9")
def _check_esl_9(ctx, finding: Finding) -> Finding:
    """ESL-9: Rust package uses dh_cargo."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not check debian/rules (packaging-source failed)"
        finding.todo = "TODO: - Verify Rust package uses dh_cargo"
        return finding

    if not _is_rust_package(packaging):
        # Not a Rust package; gate doesn't apply.
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "not a rust package, dh_cargo gate not applicable"
        finding.evidence_refs = []
        return finding

    debian_rules = packaging.get("debian_rules", "")
    uses_dh_cargo = "--buildsystem cargo" in debian_rules or "dh_cargo" in debian_rules
    if uses_dh_cargo:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "rust package using dh_cargo (dh ... --buildsystem cargo)"
    else:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = (
            "Rust package detected but dh_cargo / --buildsystem cargo not found in debian/rules"
        )
        finding.todo = "TODO: - Rust packages must use dh_cargo (dh ... --buildsystem cargo)"
    finding.evidence_refs = [
        "packaging-source:debian_rules",
        "packaging-source:cargo_lock_present",
    ]
    return finding


@deterministic_check("ESL-10")
def _check_esl_10(ctx, finding: Finding) -> Finding:
    """ESL-10: Rust: vendored deps, no unexpected Built-Using, Cargo.lock present."""
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = "Could not collect packaging source"
        finding.todo = "TODO: - Verify Rust vendored deps / Cargo.lock / Built-Using"
        return finding

    if not _is_rust_package(packaging):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "not a rust package, ESL-10 constraints not applicable"
        finding.evidence_refs = []
        return finding

    problems = []
    if not packaging.get("cargo_lock_present", False):
        problems.append("Cargo.lock not found")

    # Check for unexpected Built-Using (Rust packages should have none or only toolchain)
    debian_control = packaging.get("debian_control", "")

    built_using_entries = re.findall(
        r"(?:Built-Using|Static-Built-Using)\s*:\s*([^\n]+(?:\n\s[^\n]+)*)",
        debian_control,
        flags=re.IGNORECASE,
    )
    unexpected_bu = [
        e for e in built_using_entries if "rust" not in e.lower() and "cargo" not in e.lower()
    ]
    if unexpected_bu:
        problems.append("Unexpected Built-Using entries: " + "; ".join(unexpected_bu))

    if problems:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = "Rust package has issues: " + "; ".join(problems)
        finding.todo = "TODO: - Fix Rust package issues: " + "; ".join(problems)
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = (
            "Rust package that has all dependencies vendored. "
            "It does neither have *Built-Using (after build). "
            "Nor does the build log indicate built-in sources missed as Built-Using."
        )
    finding.evidence_refs = [
        "packaging-source:cargo_lock_present",
        "packaging-source:debian_control",
    ]
    return finding


# ---------------------------------------------------------------------------
# Deterministic dispatch table
# Must be defined after all _check_* functions it references.
# ---------------------------------------------------------------------------

@evaluator("deterministic")
def _eval_deterministic(check: dict, ctx, finding: Finding) -> Finding:
    """Evaluate checks with deterministic logic only."""
    check_id = check["id"]
    evaluator_func = DETERMINISTIC_CHECKS.get(check_id)
    if evaluator_func:
        return evaluator_func(ctx, finding)
    else:
        finding.fail("Deterministic check evaluator not implemented", finding.title, status="unknown")
        return finding
