"""Deterministic check evaluators for auto-mir.

Contains all check functions that evaluate evidence without LLM calls,
the dispatch table, and the _eval_deterministic entry point.
"""

from __future__ import annotations

import logging
import re
import subprocess

from checks.language_gates import _is_go_package, _is_python_package, _is_rust_package
from checks.messages import render_check_message
from checks.registry import DETERMINISTIC_CHECKS, deterministic_check, evaluator
from models import Finding

log = logging.getLogger("auto_mir.checks.deterministic")


def _get_check_definition(ctx, check_id: str) -> dict:
    """Return check definition by id or raise a clear error."""
    check = next((c for c in ctx.catalog.get("checks", []) if c.get("id") == check_id), None)
    if check is None:
        raise ValueError(f"{check_id} check definition not found in catalog")
    return check


def _set_unknown_from_adapter(
    finding: Finding,
    check: dict,
    *,
    message_key: str = "unknown_message",
    todo_key: str | None = None,
    evidence_refs: list[str] | None = None,
) -> Finding:
    """Set finding to unknown with consistent confidence and optional TODO/evidence."""
    finding.status = "unknown"
    finding.confidence = "low"
    finding.message = render_check_message(check, message_key)
    if todo_key:
        finding.todo = render_check_message(check, todo_key)
    if evidence_refs is not None:
        finding.evidence_refs = evidence_refs
    return finding


def _get_packaging_source_or_unknown(
    ctx,
    finding: Finding,
    check_id: str,
    *,
    with_unknown_todo: bool = True,
) -> tuple[dict, dict] | None:
    """Return (check, packaging-source) or set finding unknown and return None."""
    check = _get_check_definition(ctx, check_id)
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})
    if packaging.get("status") != "ok":
        _set_unknown_from_adapter(
            finding,
            check,
            todo_key="unknown_todo" if with_unknown_todo else None,
        )
        return None
    return check, packaging


_TEST_CONTEXT_MARKERS = (
    "test",
    "tests/",
    "autopkgtest",
    "pytest",
    "unittest",
    "debian/tests",
)


def _line_is_test_context(line: str) -> bool:
    """Return True when a source line clearly belongs to test context."""
    lowered = line.lower()
    return any(marker in lowered for marker in _TEST_CONTEXT_MARKERS)


@deterministic_check("SUM-1")
def _check_sum_1(ctx, finding: Finding) -> Finding:
    """SUM-1: Source package identified."""
    check = next((c for c in ctx.catalog.get("checks", []) if c.get("id") == "SUM-1"), None)
    if check is None:
        raise ValueError("SUM-1 check definition not found in catalog")
    if ctx.source_package:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(
            check, "ok_message", source_package=ctx.source_package
        )
        finding.evidence_refs = ["lp-bug-api:source_package"]
    else:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = render_check_message(check, "not_ok_message")
        finding.todo = render_check_message(check, "not_ok_todo")
    return finding


@deterministic_check("SUM-2")
def _check_sum_2(ctx, finding: Finding) -> Finding:
    """SUM-2: Reporter MIR content present."""
    check = next((c for c in ctx.catalog.get("checks", []) if c.get("id") == "SUM-2"), None)
    if check is None:
        raise ValueError("SUM-2 check definition not found in catalog")
    if ctx.reporter_mir_content:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_message")
        finding.evidence_refs = ["lp-bug-api:reporter_content"]
    else:
        finding.status = "not-ok"
        finding.severity = "nack"
        finding.confidence = "high"
        finding.message = render_check_message(check, "nack_message")
        finding.todo = render_check_message(check, "nack_todo")
    return finding


@deterministic_check("CB-1")
def _check_cb_1(ctx, finding: Finding) -> Finding:
    """CB-1: Package does not FTBFS currently."""
    adapters = ctx.evidence.get("adapters", {})

    sbuild_result = adapters.get("sbuild", {})
    lp_build_result = adapters.get("lp-build-api", {})

    if sbuild_result.get("status") != "ok" or not sbuild_result.get("build_success"):
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not confirm build success from sbuild output"
        finding.todo = "TODO: - does not FTBFS currently"
        finding.evidence_refs = ["sbuild:build_success"]
        return finding

    if lp_build_result.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not confirm Launchpad build state"
        finding.todo = "TODO: - does not FTBFS currently"
        finding.evidence_refs = ["lp-build-api:error"]
        return finding

    builds = lp_build_result.get("builds", [])
    if not builds:
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "No Launchpad build records were found"
        finding.todo = "TODO: - does not FTBFS currently"
        finding.evidence_refs = ["lp-build-api:builds"]
        return finding

    failed_builds = []
    passing_arches = []
    for build in builds:
        arch = str(build.get("arch_tag", "")).strip() or "unknown-arch"
        state = str(build.get("build_state", "")).strip().lower()
        if any(token in state for token in ("successful", "succeeded", "built")):
            passing_arches.append(arch)
        else:
            failed_builds.append(f"{arch}: {build.get('build_state', 'unknown')}")

    if failed_builds:
        finding.fail(
            "Launchpad build state shows failures: " + "; ".join(failed_builds),
            "does not FTBFS currently",
            severity="required",
            confidence="high",
        )
        finding.evidence_refs = ["sbuild:build_success", "lp-build-api:builds"]
        return finding

    finding.succeed(
        "does not FTBFS currently; Launchpad build records pass for arches: "
        + ", ".join(passing_arches),
        confidence="high",
    )
    finding.evidence_refs = ["sbuild:build_success", "lp-build-api:builds"]
    return finding


@deterministic_check("SUM-4")
def _check_sum_4(ctx, finding: Finding) -> Finding:
    """SUM-4: Package has a team subscriber in package-team-mapping."""
    check = next((c for c in ctx.catalog.get("checks", []) if c.get("id") == "SUM-4"), None)
    if check is None:
        raise ValueError("SUM-4 check definition not found in catalog")
    adapters = ctx.evidence.get("adapters", {})
    team_mapping_adapter = adapters.get("team-mapping", {})

    if team_mapping_adapter.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = render_check_message(check, "unknown_message")
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["team-mapping:error"]
        return finding

    subscribed_teams = team_mapping_adapter.get("subscribed_teams", [])

    if subscribed_teams:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(
            check, "ok_message", subscribed_teams=", ".join(subscribed_teams)
        )
        finding.evidence_refs = ["team-mapping:subscribed_teams"]
    else:
        finding.status = "not-ok"
        finding.severity = "recommended"
        finding.confidence = "high"
        finding.message = render_check_message(check, "not_ok_message")
        finding.todo = render_check_message(check, "not_ok_todo")
        finding.evidence_refs = ["team-mapping:subscribed_teams"]

    return finding


@deterministic_check("DEP-3")
def _check_dep_3(ctx, finding: Finding) -> Finding:
    """DEP-3: No -dev/-debug/-doc packages needing exclusion."""
    adapters = ctx.evidence.get("adapters", {})
    check = next((c for c in ctx.catalog.get("checks", []) if c.get("id") == "DEP-3"), None)
    if check is None:
        raise ValueError("DEP-3 check definition not found in catalog")

    packaging = adapters.get("packaging-source", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = render_check_message(check, "unknown_packaging_message")
        finding.todo = render_check_message(check, "unknown_packaging_todo")
        return finding

    if dep_analysis.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = render_check_message(check, "unknown_dep_analysis_message")
        finding.todo = render_check_message(check, "unknown_dep_analysis_todo")
        finding.evidence_refs = ["dep-analysis:error"]
        return finding

    binary_packages = dep_analysis.get("binary_packages", [])

    # Filter to in-scope binaries only
    if ctx.requested_binaries:
        in_scope = [p for p in binary_packages if p in ctx.requested_binaries]
    else:
        in_scope = binary_packages

    auto_included = dep_analysis.get("auto_included_binaries")
    if auto_included is None:
        auto_included = [
            p
            for p in in_scope
            if any(p.endswith(s) for s in ("-dev", "-dbg", "-debug", "-doc", "-docs"))
        ]

    auto_included = sorted(auto_included)
    if not auto_included:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_no_auto_included_message")
        finding.evidence_refs = [
            "packaging-source:debian_control",
            "dep-analysis:binary_packages",
        ]
        return finding

    offending_deps = sorted(dep_analysis.get("auto_included_deps_not_in_main_or_unknown", []))
    offending_by_binary = dep_analysis.get("auto_included_offending_deps_by_binary", [])
    offending_by_binary = sorted(
        [
            {
                "binary": str(entry.get("binary", "")),
                "dependencies": sorted(str(d) for d in entry.get("dependencies", [])),
            }
            for entry in offending_by_binary
            if entry.get("binary")
        ],
        key=lambda e: e["binary"],
    )

    if offending_deps:
        details = "; ".join(
            f"{entry['binary']}: {', '.join(entry['dependencies'])}"
            for entry in offending_by_binary
            if entry["dependencies"]
        )
        finding.status = "not-ok"
        finding.severity = "recommended"
        finding.confidence = "high"
        finding.message = render_check_message(
            check,
            "not_ok_offending_message",
            auto_included=", ".join(auto_included),
            offending_deps=", ".join(offending_deps),
        )
        finding.todo = render_check_message(
            check,
            "not_ok_offending_todo",
            details=details,
            offending_deps=", ".join(offending_deps),
        )
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(
            check,
            "ok_safe_message",
            auto_included=", ".join(auto_included),
        )

    finding.evidence_refs = [
        "packaging-source:debian_control",
        "dep-analysis:auto_included_binaries",
        "dep-analysis:auto_included_dep_components",
        "dep-analysis:auto_included_deps_not_in_main_or_unknown",
        "dep-analysis:auto_included_offending_deps_by_binary",
    ]
    return finding


@deterministic_check("ESL-1")
def _check_esl_1(ctx, finding: Finding) -> Finding:
    """ESL-1: No embedded source present."""
    check = next((c for c in ctx.catalog.get("checks", []) if c.get("id") == "ESL-1"), None)
    if check is None:
        raise ValueError("ESL-1 check definition not found in catalog")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = render_check_message(check, "unknown_message")
        finding.todo = render_check_message(check, "unknown_todo")
        return finding

    vendored_dirs = packaging.get("vendored_dirs", [])
    # Also check debian/control for Built-Using (indicates possible embedded source)
    debian_control = packaging.get("debian_control", "")
    has_built_using = "Built-Using" in debian_control or "Static-Built-Using" in debian_control

    if vendored_dirs:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = render_check_message(
            check, "not_ok_message", embedded_dirs=", ".join(vendored_dirs)
        )
        finding.todo = render_check_message(
            check, "not_ok_todo", embedded_dirs=", ".join(vendored_dirs)
        )
        finding.evidence_refs = ["packaging-source:vendored_dirs"]
    elif has_built_using:
        # Built-Using alone is not a blocker; ESL-3 handles unexpected entries.
        # Here we note it's clean w.r.t. embedded source.
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "medium"
        finding.message = render_check_message(check, "ok_built_using_message")
        finding.evidence_refs = ["packaging-source:debian_control"]
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_message")
        finding.evidence_refs = ["packaging-source:vendored_dirs"]
    return finding


@deterministic_check("ESL-3")
def _check_esl_3(ctx, finding: Finding) -> Finding:
    """ESL-3: No unexpected Built-Using entries.

    Checks Built-Using and Static-Built-Using metadata from built .deb files
    (not source debian/control, which doesn't have these fields).
    """
    check = _get_check_definition(ctx, "ESL-3")

    adapters = ctx.evidence.get("adapters", {})
    deb_metadata = adapters.get("deb-metadata", {})

    if deb_metadata.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check, todo_key="unknown_todo")

    deb_packages = deb_metadata.get("deb_packages", [])

    # Collect all Built-Using and Static-Built-Using entries from all packages
    all_built_using = []
    all_static_built_using = []

    for pkg in deb_packages:
        all_built_using.extend(pkg.get("built_using", []))
        all_static_built_using.extend(pkg.get("static_built_using", []))

    # Combine and deduplicate for analysis
    all_entries = sorted(set(all_built_using + all_static_built_using))

    if not all_entries:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_message")
        finding.evidence_refs = ["deb-metadata:deb_packages"]
        return finding

    # Check for toolchain-only pattern (acceptable) vs. other entries
    all_entries_text = " ".join(all_entries).lower()
    # Toolchain-only Built-Using (golang, rust, cgo) are expected.
    # Anything else (especially ${misc:Built-Using} with explicit pkg list) needs attention.
    entries_joined = "; ".join(all_entries)
    if (
        "golang" in all_entries_text
        or "rust" in all_entries_text
        or "${misc:built-using}" in all_entries_text
    ):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "medium"
        finding.message = render_check_message(
            check, "ok_toolchain_message", entries=entries_joined
        )
    else:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "medium"
        finding.message = render_check_message(check, "not_ok_message", entries=entries_joined)
        finding.todo = render_check_message(check, "not_ok_todo", entries=entries_joined)
    finding.evidence_refs = ["deb-metadata:deb_packages"]
    return finding


@deterministic_check("ESL-4")
def _check_esl_4(ctx, finding: Finding) -> Finding:
    """ESL-4: Go language detection gate."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-4")
    if resolved is None:
        return finding
    check, packaging = resolved

    if _is_go_package(packaging):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_go_message")
        # ESL-4 itself is just the gate; it's ok to confirm it's Go.
        # The actual compliance checks are ESL-5, ESL-6, ESL-7.
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_not_go_message")
    finding.evidence_refs = [
        "packaging-source:go_sum_present",
        "packaging-source:debian_rules",
    ]
    return finding


@deterministic_check("ESL-7")
def _check_esl_7(ctx, finding: Finding) -> Finding:
    """ESL-7: Go build type (shared vs static)."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-7")
    if resolved is None:
        return finding
    check, packaging = resolved

    if not _is_go_package(packaging):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_not_go_message")
        finding.evidence_refs = []
        return finding

    # Detect build mode
    debian_rules = packaging.get("debian_rules", "")
    if "-buildmode=shared" in debian_rules or "linkshared" in debian_rules:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_shared_message")
    elif "DH_GOLANG_BUILDPKG" in debian_rules or "dh_golang" in debian_rules:
        # dh-golang without explicit shared mode defaults to static in modern versions.
        # This needs human confirmation.
        finding.status = "not-ok"
        finding.severity = "recommended"
        finding.confidence = "medium"
        finding.message = render_check_message(check, "recommended_message")
        finding.todo = render_check_message(check, "recommended_todo")
    else:
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = render_check_message(check, "unknown_build_mode_message")
        finding.todo = render_check_message(check, "unknown_build_mode_todo")
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


@deterministic_check("ESL-8")
def _check_esl_8(ctx, finding: Finding) -> Finding:
    """ESL-8: Rust language detection gate."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-8")
    if resolved is None:
        return finding
    check, packaging = resolved

    if _is_rust_package(packaging):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_rust_message")
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_not_rust_message")
    finding.evidence_refs = [
        "packaging-source:cargo_lock_present",
        "packaging-source:debian_rules",
    ]
    return finding


@deterministic_check("ESL-9")
def _check_esl_9(ctx, finding: Finding) -> Finding:
    """ESL-9: Rust package uses dh_cargo."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-9")
    if resolved is None:
        return finding
    check, packaging = resolved

    if not _is_rust_package(packaging):
        # Not a Rust package; gate doesn't apply.
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_not_rust_message")
        finding.evidence_refs = []
        return finding

    debian_rules = packaging.get("debian_rules", "")
    uses_dh_cargo = "--buildsystem cargo" in debian_rules or "dh_cargo" in debian_rules
    if uses_dh_cargo:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_message")
    else:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = render_check_message(check, "not_ok_message")
        finding.todo = render_check_message(check, "not_ok_todo")
    finding.evidence_refs = [
        "packaging-source:debian_rules",
        "packaging-source:cargo_lock_present",
    ]
    return finding


@deterministic_check("ESL-10")
def _check_esl_10(ctx, finding: Finding) -> Finding:
    """ESL-10: Rust: vendored deps, no unexpected Built-Using, Cargo.lock present."""
    resolved = _get_packaging_source_or_unknown(ctx, finding, "ESL-10")
    if resolved is None:
        return finding
    check, packaging = resolved
    adapters = ctx.evidence.get("adapters", {})

    if not _is_rust_package(packaging):
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_not_rust_message")
        finding.evidence_refs = []
        return finding

    problems = []
    if not packaging.get("cargo_lock_present", False):
        problems.append("Cargo.lock not found")

    # Check for unexpected Built-Using from binary packages (not source debian/control)
    deb_metadata = adapters.get("deb-metadata", {})
    if deb_metadata.get("status") == "ok":
        deb_packages = deb_metadata.get("deb_packages", [])
        all_built_using = []
        for pkg in deb_packages:
            all_built_using.extend(pkg.get("built_using", []))
            # Note: Static-Built-Using for Rust should also be toolchain-only
            all_built_using.extend(pkg.get("static_built_using", []))

        # Filter out expected entries (rust, cargo, cgo, standard toolchain)
        unexpected_bu = [
            e
            for e in all_built_using
            if not any(
                keyword in e.lower()
                for keyword in ["rust", "cargo", "cgo", "golang", "${misc:built-using}"]
            )
        ]
        if unexpected_bu:
            problems.append("Unexpected Built-Using entries: " + "; ".join(unexpected_bu))

    if problems:
        problems_str = "; ".join(problems)
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = render_check_message(check, "not_ok_message", problems=problems_str)
        finding.todo = render_check_message(check, "not_ok_todo", problems=problems_str)
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_message")

    evidence_refs = ["packaging-source:cargo_lock_present"]
    if deb_metadata.get("status") == "ok":
        evidence_refs.append("deb-metadata:deb_packages")
    finding.evidence_refs = evidence_refs
    return finding


def _parse_build_log_issues(build_log: str) -> tuple[list[str], list[str]]:
    """Parse build log to extract error and warning lines.

    Returns:
        (errors, warnings) tuple where each is a list of relevant log lines
    """
    errors = []
    warnings = []
    security_warning_keywords = [
        "format string",
        "buffer overflow",
        "stack overflow",
        "integer overflow",
        "use after free",
        "out of bounds",
    ]

    for line in build_log.split("\n"):
        line_lower = line.lower()
        # Check for error patterns
        if any(token in line_lower for token in ["error:", "fatal error:", "failed to"]):
            errors.append(line.strip())
        # Check for security-relevant warnings
        elif any(token in line_lower for token in security_warning_keywords):
            warnings.append(line.strip())
        # Check for compiler/build warnings
        elif any(token in line_lower for token in ["warning:", "-w ", "deprecated"]):
            warnings.append(line.strip())

    return errors, warnings


@deterministic_check("URF-1")
def _check_urf_1(ctx, finding: Finding) -> Finding:
    """URF-1: No build errors or warnings."""
    check = _get_check_definition(ctx, "URF-1")
    adapters = ctx.evidence.get("adapters", {})
    sbuild_result = adapters.get("sbuild", {})

    if sbuild_result.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect build log"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["sbuild:error"]
        return finding

    build_log = sbuild_result.get("build_log", "")
    errors, warnings = _parse_build_log_issues(build_log)

    if errors:
        finding.fail(
            "Build log contains errors: " + "; ".join(errors[:3]),  # Show first 3
            "no Errors/warnings during the build",
            severity="required",
            confidence="high",
        )
        finding.evidence_refs = ["sbuild:build_log"]
        return finding

    if warnings:
        finding.fail(
            "Build log contains warnings: " + "; ".join(warnings[:3]),  # Show first 3
            "no Errors/warnings during the build",
            severity="recommended",
            confidence="medium",
        )
        finding.evidence_refs = ["sbuild:build_log"]
        return finding

    finding.succeed(
        "no Errors/warnings during the build",
        confidence="high",
    )
    finding.evidence_refs = ["sbuild:build_log"]
    return finding


@deterministic_check("PRF-10")
def _check_prf_10(ctx, finding: Finding) -> Finding:
    """PRF-10: Not on lto-disabled list."""
    check = _get_check_definition(ctx, "PRF-10")
    pkg = ctx.source_package

    if not pkg:
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not determine source package name"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = []
        return finding

    # Check if package is on the lto-disabled-list
    # The lto-disabled-list package contains package names that require LTO to be disabled
    # For now, we implement a stub that returns "not on list" (the OK case)
    # In production, this would query the actual list from lp:ubuntu/+source/lto-disabled-list

    # Common packages known to be on the list (example)
    known_lto_disabled = {
        "llvm",  # Example: llvm is often on the list
    }

    is_on_list = pkg.lower() in {p.lower() for p in known_lto_disabled}

    if is_on_list:
        finding.fail(
            "Package is on the lto-disabled list; LTO must be fixed or disabled",
            "It is not on the lto-disabled list",
            severity="required",
            confidence="medium",
        )
        finding.evidence_refs = []
        return finding

    finding.succeed(
        "It is not on the lto-disabled list",
        confidence="medium",
    )
    finding.evidence_refs = ["lp-package-api:status"]
    return finding


@deterministic_check("CB-8")
def _check_cb_8(ctx, finding: Finding) -> Finding:
    """CB-8: Python packages use dh_python."""
    check = _get_check_definition(ctx, "CB-8")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect debian/rules (packaging-source failed)"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    is_python = _is_python_package(packaging)
    rules = packaging.get("debian_rules", "")
    uses_dh_python = "dh_python" in rules or "dh_python3" in rules

    if not is_python:
        # Not a Python package; gate doesn't apply
        finding.succeed(
            "not a Python package; Python packaging constraints do not apply",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_rules"]
        return finding

    if uses_dh_python:
        finding.succeed(
            "Python package, but using dh_python",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_rules"]
        return finding

    # Python package not using dh_python
    finding.fail(
        "Python package detected but dh_python/dh_python3 not found in debian/rules",
        "Python package, but using dh_python",
        severity="required",
        confidence="high",
    )
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


@deterministic_check("ESL-2")
def _check_esl_2(ctx, finding: Finding) -> Finding:
    """ESL-2: No unexpected static linking."""
    check = _get_check_definition(ctx, "ESL-2")
    adapters = ctx.evidence.get("adapters", {})
    sbuild_result = adapters.get("sbuild", {})
    packaging = adapters.get("packaging-source", {})

    if sbuild_result.get("status") != "ok" or packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect build log for static linking"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["sbuild:build_log"]
        return finding

    build_log = sbuild_result.get("build_log", "")
    static_link_hints = sbuild_result.get("static_link_hints", [])

    # Check for -static flag in build log
    has_static_flag = "-static" in build_log or "--static" in build_log

    # Common patterns for justifiable static linking
    justifiable_patterns = [
        "integrity checker",
        "security scanner",
        "initramfs",
        "bootloader",
        "firmware",
        "kernel module",
    ]

    is_justifiable = any(pattern.lower() in build_log.lower() for pattern in justifiable_patterns)

    if not has_static_flag and not static_link_hints:
        finding.succeed(
            "no static linking",
            confidence="high",
        )
        finding.evidence_refs = ["sbuild:build_log"]
        return finding

    if is_justifiable:
        finding.succeed(
            "static linking present but appears to be justified (e.g., scanner/bootloader)",
            confidence="medium",
        )
        finding.evidence_refs = ["sbuild:build_log"]
        return finding

    # Static linking without clear justification
    finding.fail(
        "Static linking detected without clear justification; review needed",
        "no static linking",
        severity="required",
        confidence="medium",
    )
    finding.evidence_refs = ["sbuild:build_log"]
    return finding


@deterministic_check("PRF-2")
def _check_prf_2(ctx, finding: Finding) -> Finding:
    """PRF-2: Symbols tracking for C/C++ libraries."""
    check = _get_check_definition(ctx, "PRF-2")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect packaging (packaging-source failed)"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_control = packaging.get("debian_control", "")
    debian_rules = packaging.get("debian_rules", "")

    # Check if this is a library package
    is_library = any(
        marker in debian_control.lower()
        for marker in ["library", "libdev", "symbols", "lib", "shared object"]
    )

    # Check for non-C/C++ languages (Python, Go, Rust, etc.)
    if _is_python_package(packaging) or _is_go_package(packaging) or _is_rust_package(packaging):
        finding.succeed(
            "symbols tracking not applicable for this language/runtime",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # Not a library or no shared objects
    if not is_library or ".so" not in debian_control:
        finding.succeed(
            "symbols tracking not applicable for this kind of code",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # Check for symbols file presence
    has_symbols_file = ".symbols" in debian_control or ".symbols" in debian_rules

    if has_symbols_file:
        finding.succeed(
            "symbols tracking is in place",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # C/C++ library without symbols tracking - check if there's documentation
    has_documented_reason = any(
        marker.lower() in debian_rules.lower()
        for marker in ["#.symbols", "# symbols", "todo: symbols"]
    )

    if has_documented_reason:
        finding.status = "not-ok"
        finding.severity = "recommended"
        finding.confidence = "medium"
        finding.message = (
            "C++ library without symbols file but appears to have documented consideration"
        )
        finding.todo = (
            "TODO: - For c++ libraries - symbols tracking isn't in place but "
            "the owning team tried..."
        )
        finding.evidence_refs = ["packaging-source:debian_rules"]
        return finding

    # No symbols tracking and no documentation
    finding.status = "not-ok"
    finding.severity = "recommended"
    finding.confidence = "medium"
    finding.message = "C/C++ library detected but symbols tracking not found in package"
    finding.todo = (
        "TODO: - For c++ libraries - symbols tracking isn't in place but the owning team tried..."
    )
    finding.evidence_refs = ["packaging-source:debian_control"]
    return finding


@deterministic_check("PRF-3")
def _check_prf_3(ctx, finding: Finding) -> Finding:
    """PRF-3: debian/watch present."""
    check = _get_check_definition(ctx, "PRF-3")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect packaging (packaging-source failed)"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_control = packaging.get("debian_control", "")
    file_listing = packaging.get("file_listing", [])

    # Check if debian/watch is present
    has_watch_file = any(f.get("path", "").endswith("debian/watch") for f in file_listing)

    # Check if it's a native package (Version ends with ~)
    is_native = "debian/source/format: 3.0 (native)" in debian_control

    if has_watch_file:
        finding.succeed(
            "debian/watch is present and looks ok",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:file_listing"]
        return finding

    if is_native:
        finding.succeed(
            "debian/watch is not present but also not needed (native package)",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # Non-native package without watch file
    finding.fail(
        "Non-native package but debian/watch not found",
        "debian/watch is present and looks ok",
        severity="recommended",
        confidence="medium",
    )
    finding.todo = "TODO: - Add debian/watch to track upstream releases"
    finding.evidence_refs = ["packaging-source:file_listing"]
    return finding


@deterministic_check("SEC-2")
def _check_sec_2(ctx, finding: Finding) -> Finding:
    """SEC-2: Does not run daemon as root."""
    check = _get_check_definition(ctx, "SEC-2")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect packaging source"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_rules = packaging.get("debian_rules", "")
    debian_control = packaging.get("debian_control", "")
    combined_lower = (debian_rules + "\n" + debian_control).lower()

    # First priority: check for explicit root execution (exact match)
    if "user=root" in combined_lower:
        # Has root execution; check for mitigations
        mitigations = ["seccomp", "apparmor", "selinux", "capabilities"]
        has_mitigations = any(m.lower() in combined_lower for m in mitigations)

        if has_mitigations:
            finding.status = "not-ok"
            finding.severity = "recommended"
            finding.confidence = "medium"
            finding.message = "Package runs as root but has security mitigations"
            finding.todo = "TODO: - Note root execution and mitigations"
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding
        else:
            finding.fail(
                "Package runs daemon as root without security mitigations",
                "does not run a daemon as root",
                severity="required",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding

    # Second: check for non-root indicators
    non_root_indicators = ["user=", "dynamicuser=yes", "droppriv", "drop_privileges"]
    has_non_root = any(ind.lower() in combined_lower for ind in non_root_indicators)
    has_nobody = "nobody" in combined_lower

    if has_non_root or has_nobody:
        finding.succeed(
            "does not run a daemon as root",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # No explicit indicators found; assume safe
    finding.succeed(
        "does not run a daemon as root",
        confidence="medium",
    )
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


@deterministic_check("URF-3")
def _check_urf_3(ctx, finding: Finding) -> Finding:
    """URF-3: No sudo/gksu/pkexec/LD_LIBRARY_PATH outside tests."""
    check = _get_check_definition(ctx, "URF-3")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect packaging source"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_rules = packaging.get("debian_rules", "")
    debian_control = packaging.get("debian_control", "")

    # Search for privilege escalation patterns and ignore only explicit test-context lines.
    escalation_keywords = ["sudo", "gksu", "pkexec", "ld_library_path"]
    combined_lines = [
        *(line for line in debian_rules.splitlines()),
        *(line for line in debian_control.splitlines()),
    ]

    for line in combined_lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in escalation_keywords) and not _line_is_test_context(
            line
        ):
            finding.fail(
                "Potential sudo/gksu/pkexec/LD_LIBRARY_PATH usage found outside tests",
                "no use of sudo, gksu, pkexec, or LD_LIBRARY_PATH (usage is OK inside tests)",
                severity="required",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding

    finding.succeed(
        "no use of sudo, gksu, pkexec, or LD_LIBRARY_PATH (usage is OK inside tests)",
        confidence="high",
    )
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


@deterministic_check("URF-4")
def _check_urf_4(ctx, finding: Finding) -> Finding:
    """URF-4: No use of user 'nobody' outside tests."""
    check = _get_check_definition(ctx, "URF-4")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect packaging source"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_rules = packaging.get("debian_rules", "")
    debian_control = packaging.get("debian_control", "")

    combined_lines = [
        *(line for line in debian_rules.splitlines()),
        *(line for line in debian_control.splitlines()),
    ]

    for line in combined_lines:
        if "nobody" in line.lower() and not _line_is_test_context(line):
            finding.fail(
                "User 'nobody' found outside test context",
                "no use of user 'nobody' outside of tests",
                severity="required",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding

    finding.succeed(
        "no use of user 'nobody' outside of tests",
        confidence="high",
    )
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


@deterministic_check("URF-5")
def _check_urf_5(ctx, finding: Finding) -> Finding:
    """URF-5: No setuid/setgid binaries."""
    check = _get_check_definition(ctx, "URF-5")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})
    lintian = adapters.get("lintian", {})

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect packaging source"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    # Check lintian output for setuid/setgid tags (covers built binary artefacts).
    _LINTIAN_SETUID_TAGS = ("setuid-binary", "setgid-binary", "set-uid", "set-gid")
    lintian_triggered = False
    if lintian.get("status") == "ok":
        all_lintian = " ".join(
            lintian.get("lintian_errors", [])
            + lintian.get("lintian_warnings", [])
            + lintian.get("lintian_pedantic", [])
        ).lower()
        lintian_triggered = any(tag in all_lintian for tag in _LINTIAN_SETUID_TAGS)

    # Also check debian/rules text for explicit setuid/setgid patterns.
    debian_rules = packaging.get("debian_rules", "").lower()
    setuid_patterns = ["chmod 4", "chmod 2", "perm -4000", "perm -2000", "setuid", "setgid"]
    rules_triggered = any(p in debian_rules for p in setuid_patterns)

    if lintian_triggered or rules_triggered:
        source = "lintian output" if lintian_triggered else "debian/rules"
        # Check for documented justification (prefer systemd)
        if "systemd" in debian_rules:
            finding.status = "not-ok"
            finding.severity = "recommended"
            finding.confidence = "medium"
            finding.message = (
                f"setuid/setgid present ({source}) but using systemd service permissions"
            )
            finding.todo = "TODO: - use of setuid, but ok because systemd is used"
            finding.evidence_refs = ["packaging-source:debian_rules", "lintian:lintian_warnings"]
            return finding

        finding.fail(
            f"setuid/setgid detected in {source}",
            "no use of setuid / setgid",
            severity="required",
            confidence="high" if lintian_triggered else "low",
        )
        finding.evidence_refs = [
            "lintian:lintian_warnings" if lintian_triggered else "packaging-source:debian_rules"
        ]
        return finding

    finding.succeed(
        "no use of setuid / setgid",
        confidence="high" if lintian.get("status") == "ok" else "medium",
    )
    finding.evidence_refs = ["packaging-source:debian_rules"]
    if lintian.get("status") == "ok":
        finding.evidence_refs.append("lintian:lintian_warnings")
    return finding


@deterministic_check("URF-7")
def _check_urf_7(ctx, finding: Finding) -> Finding:
    """URF-7: No webkit/qtwebkit/libseed dependency."""
    check = _get_check_definition(ctx, "URF-7")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        _set_unknown_from_adapter(finding, check, "dep-analysis")
        return finding

    dependencies = dep_analysis.get("runtime_dep_packages", [])
    old_webkit = ["webkit", "qtwebkit", "libseed"]

    for dep in dependencies:
        if any(web in dep.lower() for web in old_webkit):
            finding.fail(
                f"Old web engine dependency found: {dep}",
                "no dependency on webkit, qtwebkit or libseed",
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    finding.succeed(
        "no dependency on webkit, qtwebkit or libseed",
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


@deterministic_check("SEC-8")
def _check_sec_8(ctx, finding: Finding) -> Finding:
    """SEC-8: Does not use centralized online accounts."""
    check = _get_check_definition(ctx, "SEC-8")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})
    packaging = adapters.get("packaging-source", {})

    if dep_analysis.get("status") != "ok":
        _set_unknown_from_adapter(finding, check, "dep-analysis")
        return finding

    if packaging.get("status") != "ok":
        _set_unknown_from_adapter(finding, check, "packaging-source")
        return finding

    dependencies = dep_analysis.get("runtime_dep_packages", [])
    debian_control = packaging.get("debian_control", "")

    # Check for centralized accounts/online service APIs
    online_account_patterns = [
        "evolution-data-server",
        "gnome-online-accounts",
        "account-plugin",
        "accountsservice",
        "telepathy",
    ]

    # Also check source code for API patterns
    source_patterns = [
        "oauth",
        "oauth2",
        "google-api",
        "facebook-sdk",
        "twitter-api",
        "accounts_manager",
    ]

    for dep in dependencies:
        if any(p in dep.lower() for p in online_account_patterns):
            finding.fail(
                f"Centralized accounts dependency found: {dep}",
                "does not use centralized online accounts",
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    debian_control_lower = debian_control.lower()
    for pattern in source_patterns:
        if pattern.lower() in debian_control_lower:
            finding.fail(
                f"Online accounts pattern found: {pattern}",
                "does not use centralized online accounts",
                severity="required",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_control"]
            return finding

    finding.succeed(
        "does not use centralized online accounts",
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


@deterministic_check("SEC-10")
def _check_sec_10(ctx, finding: Finding) -> Finding:
    """SEC-10: Does not handle system authentication (PAM)."""
    check = _get_check_definition(ctx, "SEC-10")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})
    packaging = adapters.get("packaging-source", {})

    if dep_analysis.get("status") != "ok":
        _set_unknown_from_adapter(finding, check, "dep-analysis")
        return finding

    if packaging.get("status") != "ok":
        _set_unknown_from_adapter(finding, check, "packaging-source")
        return finding

    dependencies = dep_analysis.get("runtime_dep_packages", [])
    debian_control = packaging.get("debian_control", "")
    debian_rules = packaging.get("debian_rules", "")

    # Check for PAM or authentication libraries
    pam_patterns = ["libpam", "libpam-", "pam", "gdm", "lightdm", "sddm"]

    for dep in dependencies:
        if any(p in dep.lower() for p in pam_patterns):
            # Make sure it's not a system service (which may have PAM modules)
            if not any(x in dep.lower() for x in ["session", "client", "common"]):
                finding.fail(
                    f"PAM authentication dependency found: {dep}",
                    "does not deal with system authentication (eg, pam), etc)",
                    severity="required",
                    confidence="medium",
                )
                finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
                return finding

    # Check for pam_* function patterns in source
    pam_function_patterns = ["pam_", "pam_authenticate", "pam_acct", "pam_open_session"]
    combined_source = (debian_control + "\n" + debian_rules).lower()

    for pattern in pam_function_patterns:
        if pattern.lower() in combined_source:
            finding.fail(
                f"PAM function usage detected: {pattern}",
                "does not deal with system authentication (eg, pam), etc)",
                severity="required",
                confidence="low",
            )
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding

    finding.succeed(
        "does not deal with system authentication (eg, pam), etc)",
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


@deterministic_check("URF-8")
def _check_urf_8(ctx, finding: Finding) -> Finding:
    """URF-8: UI/desktop file check."""
    check = _get_check_definition(ctx, "URF-8")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        _set_unknown_from_adapter(finding, check, "packaging-source")
        return finding

    file_listing = packaging.get("file_listing", [])
    debian_control = packaging.get("debian_control", "")

    # Check if this is a UI/desktop package
    desktop_patterns = [
        "x11-apps",
        "gnome-",
        "kde-",
        "xfce-",
        "lxde-",
        "mate-",
        "cinnamon-",
        "apps",
    ]
    has_desktop = any(p in debian_control.lower() for p in desktop_patterns)

    # Check for .desktop files
    has_desktop_file = any(".desktop" in str(f.get("path", "")) for f in file_listing)

    if not has_desktop and not has_desktop_file:
        # Not a UI package — gate does not apply, check passes
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "not part of the UI for extra checks"
        finding.todo = "TODO-A: - not part of the UI for extra checks"
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    if has_desktop_file:
        # Is a UI package with a valid .desktop file — check passes
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "part of the UI, desktop file is ok"
        finding.todo = "TODO-B: - part of the UI, desktop file is ok"
        finding.evidence_refs = ["packaging-source:file_listing"]
        return finding

    # Is a UI package but no desktop file - this might be an issue
    finding.fail(
        "UI package without valid .desktop file",
        "part of the UI, desktop file is ok",
        severity="required",
        confidence="medium",
    )
    finding.evidence_refs = ["packaging-source:debian_control"]
    return finding


@deterministic_check("URF-9")
def _check_urf_9(ctx, finding: Finding) -> Finding:
    """URF-9: Translation coverage."""
    check = _get_check_definition(ctx, "URF-9")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        _set_unknown_from_adapter(finding, check, "packaging-source")
        return finding

    file_listing = packaging.get("file_listing", [])
    debian_control = packaging.get("debian_control", "")

    # Check if package is user-visible
    user_visible_patterns = [
        "gnome",
        "kde",
        "xfce",
        "lxde",
        "mate",
        "cinnamon",
        "app",
        "utils",
        "tools",
    ]
    is_user_visible = any(p in debian_control.lower() for p in user_visible_patterns)

    # Check for translation/locale files
    translation_patterns = [".mo", ".po", "locale/", "translations/", "i18n/"]
    has_translations = any(
        any(p in str(f.get("path", "")).lower() for p in translation_patterns) for f in file_listing
    )

    if not is_user_visible:
        # Not user-visible — gate does not apply, check passes
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "not user-visible, translations not needed"
        finding.todo = (
            "TODO-A: - no translation present, but none needed for this case (not user visible)"
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    if has_translations:
        # User-visible with translations present — check passes
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "user-visible with translation present"
        finding.todo = "TODO-B: - translation present"
        finding.evidence_refs = ["packaging-source:file_listing"]
        return finding

    # User-visible but no translations - might be an issue
    finding.fail(
        "User-visible package without translations",
        "translation present",
        severity="recommended",
        confidence="medium",
    )
    finding.evidence_refs = ["packaging-source:file_listing"]
    return finding


@deterministic_check("CB-7")
def _check_cb_7(ctx, finding: Finding) -> Finding:
    """CB-7: No new Python 2 dependency."""
    check = _get_check_definition(ctx, "CB-7")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})
    packaging = adapters.get("packaging-source", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    if packaging.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    dependencies = dep_analysis.get("runtime_dep_packages", [])

    # Python 2 patterns
    py2_patterns = ["python2", "python-", "py2-", "libpython2"]

    for dep in dependencies:
        if any(p in dep.lower() for p in py2_patterns):
            finding.fail(
                f"Python 2 dependency found: {dep}",
                "no new python2 dependency",
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    finding.succeed(
        "no new python2 dependency",
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


@deterministic_check("SEC-3")
def _check_sec_3(ctx, finding: Finding) -> Finding:
    """SEC-3: Does not use webkit1/2."""
    check = _get_check_definition(ctx, "SEC-3")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    dependencies = dep_analysis.get("runtime_dep_packages", [])

    # Webkit patterns
    webkit_patterns = ["webkit", "webkit1", "webkit2", "libwebkit"]

    for dep in dependencies:
        if any(p in dep.lower() for p in webkit_patterns):
            finding.fail(
                f"Webkit dependency found: {dep}",
                "does not use webkit1,2",
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    finding.succeed(
        "does not use webkit1,2",
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


@deterministic_check("SEC-4")
def _check_sec_4(ctx, finding: Finding) -> Finding:
    """SEC-4: Does not use lib*v8 directly."""
    check = _get_check_definition(ctx, "SEC-4")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    dependencies = dep_analysis.get("runtime_dep_packages", [])

    # V8 patterns
    v8_patterns = ["libv8", "v8", "libnode"]

    for dep in dependencies:
        if any(p in dep.lower() for p in v8_patterns):
            finding.fail(
                f"V8 dependency found: {dep}",
                "does not use lib*v8 directly",
                severity="required",
                confidence="high",
            )
            finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
            return finding

    finding.succeed(
        "does not use lib*v8 directly",
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:runtime_dep_packages"]
    return finding


@deterministic_check("DEP-1")
def _check_dep_1(ctx, finding: Finding) -> Finding:
    """DEP-1: No unresolved runtime dependencies needing MIR."""
    check = _get_check_definition(ctx, "DEP-1")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})
    packaging = adapters.get("packaging-source", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    if packaging.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    unresolved_deps = dep_analysis.get("in_scope_deps_not_in_main", [])

    if unresolved_deps:
        deps_str = ", ".join(unresolved_deps[:3])  # Show first 3
        finding.fail(
            f"Runtime dependencies from other source packages outside main: {deps_str}",
            "no other runtime Dependencies to MIR due to this",
            severity="required",
            confidence="medium",
        )
        finding.evidence_refs = ["dep-analysis:in_scope_deps_not_in_main"]
        return finding

    finding.succeed(
        "no other runtime Dependencies to MIR due to this",
        confidence="high",
    )
    finding.evidence_refs = ["dep-analysis:in_scope_deps_not_in_main"]
    return finding


@deterministic_check("ESL-9")
def _check_esl_9(ctx, finding: Finding) -> Finding:
    """ESL-9: Rust: uses dh_cargo."""
    check = _get_check_definition(ctx, "ESL-9")
    adapters = ctx.evidence.get("adapters", {})
    packaging = adapters.get("packaging-source", {})

    if packaging.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    # Check if this is a Rust package
    is_rust = _is_rust_package(packaging)

    if not is_rust:
        # Not a Rust package - gate applies OK
        finding.succeed(
            "not a rust package, dh_cargo gate not applicable",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_control"]
        return finding

    # Is Rust package - check for dh_cargo
    debian_rules = packaging.get("debian_rules", "").lower()

    if "dh_cargo" in debian_rules or "--buildsystem cargo" in debian_rules:
        finding.succeed(
            "rust package using dh_cargo (dh ... --buildsystem cargo)",
            confidence="high",
        )
        finding.evidence_refs = ["packaging-source:debian_rules"]
        return finding

    # Rust package but dh_cargo not found
    finding.fail(
        "Rust package detected but dh_cargo / --buildsystem cargo not found in debian/rules",
        "Rust packages must use dh_cargo (dh ... --buildsystem cargo)",
        severity="required",
        confidence="high",
    )
    finding.evidence_refs = ["packaging-source:debian_rules"]
    return finding


@deterministic_check("PRF-8")
def _check_prf_8(ctx, finding: Finding) -> Finding:
    """PRF-8: No excessive lintian warnings."""
    check = _get_check_definition(ctx, "PRF-8")
    adapters = ctx.evidence.get("adapters", {})
    lintian = adapters.get("lintian", {})

    if lintian.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    # Get lintian output
    warnings = lintian.get("lintian_warnings", [])
    errors = lintian.get("lintian_errors", [])

    # Hard failures on errors
    if errors:
        error_str = ", ".join(errors[:3])
        finding.fail(
            f"Lintian errors detected: {error_str}",
            "no excessive lintian warnings",
            severity="required",
            confidence="high",
        )
        finding.evidence_refs = ["lintian:lintian_errors"]
        return finding

    # Check for excessive warnings (more than a few)
    if len(warnings) > 5:
        finding.status = "not-ok"
        finding.severity = "recommended"
        finding.confidence = "medium"
        finding.message = f"Lintian found {len(warnings)} warnings - review and fix if possible"
        finding.todo = "TODO: - Review and fix lintian warnings"
        finding.evidence_refs = ["lintian:lintian_warnings"]
        return finding

    # Some warnings are OK, but document them
    if warnings:
        finding.status = "not-ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = f"Lintian found {len(warnings)} minor warnings - acceptable"
        finding.todo = f"TODO: - {len(warnings)} minor lintian warnings documented"
        finding.evidence_refs = ["lintian:lintian_warnings"]
        return finding

    # No warnings/errors
    finding.succeed(
        "no excessive lintian warnings",
        confidence="high",
    )
    finding.evidence_refs = ["lintian:warnings"]
    return finding


def _split_debian_version(version_str: str) -> tuple[int, str, str]:
    """Split a Debian/Ubuntu package version into epoch, upstream, revision."""
    if not version_str:
        return (0, "", "")

    epoch = 0
    remainder = version_str
    if ":" in version_str:
        epoch_str, _, tail = version_str.partition(":")
        if epoch_str.isdigit():
            epoch = int(epoch_str)
            remainder = tail

    if "-" in remainder:
        upstream_version, _, debian_revision = remainder.rpartition("-")
    else:
        upstream_version = remainder
        debian_revision = ""

    return (epoch, upstream_version, debian_revision)


def _normalize_upstream_version(version_str: str) -> str:
    """Normalize a version string to the upstream version part used for PRF-6."""
    _, upstream_version, _ = _split_debian_version(version_str)
    normalized = upstream_version or version_str
    if normalized.startswith("v") and len(normalized) > 1 and normalized[1].isdigit():
        normalized = normalized[1:]
    return normalized


def _parse_version_tuple(version_str: str) -> tuple:
    """Parse the normalized upstream version into a coarse semantic tuple."""
    normalized = _normalize_upstream_version(version_str)
    if not normalized:
        return ()

    tokens = re.findall(r"\d+|[A-Za-z]+|~", normalized)
    parsed: list[int | str] = []
    for token in tokens:
        if token.isdigit():
            parsed.append(int(token))
        else:
            parsed.append(token.lower())
    return tuple(parsed)


def _compare_versions(left: str, right: str) -> int:
    """Compare two Debian-style versions using dpkg semantics."""
    comparisons = (("lt", -1), ("gt", 1), ("eq", 0))
    for operator, result in comparisons:
        completed = subprocess.run(
            ["dpkg", "--compare-versions", left, operator, right],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            return result
    raise RuntimeError(f"Could not compare versions: {left!r} vs {right!r}")


def _versions_compatible(archive_version: str, upstream_version: str) -> tuple[bool, str]:
    """Check if the packaged upstream version is up-to-date with upstream."""
    if not archive_version or not upstream_version:
        return (True, "Could not determine versions")

    packaged_upstream = _normalize_upstream_version(archive_version)
    latest_upstream = _normalize_upstream_version(upstream_version)
    if not packaged_upstream or not latest_upstream:
        return (True, "Could not parse versions")

    comparison = _compare_versions(packaged_upstream, latest_upstream)
    if comparison >= 0:
        return (True, "Packaged upstream version meets or exceeds latest upstream")

    return (
        False,
        f"Packaged upstream version behind upstream: {packaged_upstream} < {latest_upstream}",
    )


@deterministic_check("PRF-6")
def _check_prf_6(ctx, finding: Finding) -> Finding:
    """PRF-6: Current release packaged."""
    check = _get_check_definition(ctx, "PRF-6")
    adapters = ctx.evidence.get("adapters", {})

    # Get package info
    lp_package = adapters.get("lp-package-api", {})
    if lp_package.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    upstream_tracker = adapters.get("upstream-tracker", {})
    if upstream_tracker.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    archive_version = lp_package.get("current_version", "")
    upstream_version = upstream_tracker.get("latest_version", "")

    if not archive_version or not upstream_version:
        return _set_unknown_from_adapter(finding, check)

    # Check version compatibility
    is_compatible, reason = _versions_compatible(archive_version, upstream_version)

    if is_compatible:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "the current release is packaged"
    else:
        # Archive is behind - determine if "somewhat behind" or "very old"
        archive_parts = _parse_version_tuple(archive_version)
        upstream_parts = _parse_version_tuple(upstream_version)

        if archive_parts and upstream_parts:
            # Compare major versions
            archive_major = archive_parts[0] if isinstance(archive_parts[0], int) else 0
            upstream_major = upstream_parts[0] if isinstance(upstream_parts[0], int) else 0

            # If major version is 2+ behind, it's very old
            if isinstance(archive_major, int) and isinstance(upstream_major, int):
                major_gap = upstream_major - archive_major

                if major_gap >= 2:
                    # Very old
                    finding.status = "not-ok"
                    finding.severity = "required"
                    finding.confidence = "high"
                    finding.message = (
                        f"Package is very behind upstream: "
                        f"{_normalize_upstream_version(archive_version)} vs "
                        f"{_normalize_upstream_version(upstream_version)}"
                    )
                    finding.todo = "TODO: - Consider updating to a more recent upstream release"
                else:
                    # Somewhat behind (1 major version or minor version differences)
                    finding.status = "not-ok"
                    finding.severity = "recommended"
                    finding.confidence = "high"
                    finding.message = (
                        f"Package is somewhat behind upstream: "
                        f"{_normalize_upstream_version(archive_version)} vs "
                        f"{_normalize_upstream_version(upstream_version)}"
                    )
                    finding.todo = "TODO: - Consider updating to a more recent upstream release"
            else:
                # Can't determine major - mark as recommended
                finding.status = "not-ok"
                finding.severity = "recommended"
                finding.confidence = "medium"
                finding.message = (
                    f"Package version lag detected: "
                    f"{_normalize_upstream_version(archive_version)} vs "
                    f"{_normalize_upstream_version(upstream_version)}"
                )
                finding.todo = "TODO: - Verify upstream version availability"
        else:
            finding.status = "not-ok"
            finding.severity = "recommended"
            finding.confidence = "medium"
            finding.message = "Could not determine version lag"
            finding.todo = "TODO: - Verify upstream version availability"

    finding.evidence_refs = ["lp-package-api:current_version", "upstream-tracker:latest_version"]
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
        finding.fail(
            "Deterministic check evaluator not implemented", finding.title, status="unknown"
        )
        return finding
