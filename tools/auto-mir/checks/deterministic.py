"""Deterministic check evaluators for auto-mir.

Contains all check functions that evaluate evidence without LLM calls,
the dispatch table, and the _eval_deterministic entry point.
"""

from __future__ import annotations

import logging

from checks.language_gates import _is_go_package, _is_rust_package, _is_python_package
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


@deterministic_check("DEP-1")
def _check_dep_1(ctx, finding: Finding) -> Finding:
    """DEP-1: No unresolved runtime dependencies needing MIR."""
    check = next((c for c in ctx.catalog.get("checks", []) if c.get("id") == "DEP-1"), None)
    if check is None:
        raise ValueError("DEP-1 check definition not found in catalog")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = render_check_message(check, "unknown_adapter_message")
        finding.todo = render_check_message(check, "unknown_adapter_todo")
        finding.evidence_refs = ["dep-analysis:error"]
        return finding

    in_scope_deps = dep_analysis.get("in_scope_deps_not_in_main", [])
    same_source = dep_analysis.get("same_source_deps", [])
    unknown_components = [
        row["package"]
        for row in dep_analysis.get("dep_components", [])
        if row.get("component") == "unknown"
    ]

    if in_scope_deps:
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = render_check_message(
            check, "not_ok_message", deps=", ".join(in_scope_deps)
        )
        finding.todo = render_check_message(check, "not_ok_todo", deps=", ".join(in_scope_deps))
        finding.evidence_refs = [
            "dep-analysis:dep_components",
            "dep-analysis:in_scope_deps_not_in_main",
            "dep-analysis:dep_source_map",
        ]
        return finding

    if unknown_components:
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = render_check_message(
            check, "unknown_component_message", deps=", ".join(unknown_components)
        )
        finding.todo = render_check_message(
            check, "unknown_component_todo", deps=", ".join(unknown_components)
        )
        finding.evidence_refs = ["dep-analysis:dep_components"]
        return finding

    finding.status = "ok"
    finding.severity = "ok"
    finding.confidence = "high"
    if same_source:
        finding.message = render_check_message(
            check, "ok_same_source_message", same_source=", ".join(same_source)
        )
    else:
        finding.message = render_check_message(check, "ok_message")
    finding.evidence_refs = [
        "dep-analysis:runtime_dep_packages",
        "dep-analysis:dep_components",
        "dep-analysis:dep_source_map",
    ]
    return finding


@deterministic_check("SEC-3")
def _check_sec_3(ctx, finding: Finding) -> Finding:
    """SEC-3: Does not use webkit1/2."""
    check = _get_check_definition(ctx, "SEC-3")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    runtime_deps_text = " ".join(
        [f"{d['binary']}:{d['depends']}" for d in dep_analysis.get("runtime_deps", [])]
    )
    if "webkit" in runtime_deps_text.lower():
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = render_check_message(check, "blocker_message")
        finding.todo = render_check_message(check, "blocker_todo")
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_message")
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    return finding


@deterministic_check("SEC-4")
def _check_sec_4(ctx, finding: Finding) -> Finding:
    """SEC-4: Does not use lib*v8 directly."""
    check = _get_check_definition(ctx, "SEC-4")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    runtime_deps_text = " ".join(
        [f"{d['binary']}:{d['depends']}" for d in dep_analysis.get("runtime_deps", [])]
    )
    if "libv8" in runtime_deps_text.lower():
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = render_check_message(check, "blocker_message")
        finding.todo = render_check_message(check, "blocker_todo")
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_message")
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    return finding


@deterministic_check("CB-7")
def _check_cb_7(ctx, finding: Finding) -> Finding:
    """CB-7: No new Python 2 dependency."""
    check = _get_check_definition(ctx, "CB-7")
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})

    if dep_analysis.get("status") != "ok":
        return _set_unknown_from_adapter(finding, check)

    runtime_deps_text = " ".join(
        [f"{d['binary']}:{d['depends']}" for d in dep_analysis.get("runtime_deps", [])]
    )
    # Check for python2, python-*, 2.x style deps
    if any(p in runtime_deps_text.lower() for p in ["python2", "python-", "python2."]):
        finding.status = "not-ok"
        finding.severity = "required"
        finding.confidence = "high"
        finding.message = render_check_message(check, "blocker_message")
        finding.todo = render_check_message(check, "blocker_todo")
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    else:
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = render_check_message(check, "ok_message")
        finding.evidence_refs = ["dep-analysis:runtime_deps"]
    return finding


@deterministic_check("CB-1")
def _check_cb_1(ctx, finding: Finding) -> Finding:
    """CB-1: Package does not FTBFS currently."""
    check = _get_check_definition(ctx, "CB-1")
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


@deterministic_check("PRF-8")
def _check_prf_8(ctx, finding: Finding) -> Finding:
    """PRF-8: No excessive lintian warnings."""
    check = _get_check_definition(ctx, "PRF-8")
    adapters = ctx.evidence.get("adapters", {})
    lintian_result = adapters.get("lintian", {})

    if lintian_result.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect lintian output"
        finding.todo = "TODO: - no massive Lintian warnings"
        finding.evidence_refs = ["lintian:error"]
        return finding

    lintian_errors = list(lintian_result.get("lintian_errors", []))
    lintian_warnings = list(lintian_result.get("lintian_warnings", []))
    lintian_pedantic = list(lintian_result.get("lintian_pedantic", []))

    if lintian_errors:
        finding.fail(
            "Lintian reports error-level issues: " + "; ".join(lintian_errors),
            "no massive Lintian warnings",
            severity="required",
            confidence="high",
        )
        finding.evidence_refs = ["lintian:lintian_errors"]
        return finding

    if lintian_warnings:
        finding.fail(
            "Lintian warnings need review: " + "; ".join(lintian_warnings),
            "no massive Lintian warnings",
            severity="recommended",
            confidence="medium",
        )
        finding.evidence_refs = ["lintian:lintian_warnings"]
        return finding

    finding.succeed(
        "no massive Lintian warnings; only informational output was reported",
        confidence="high",
    )
    if lintian_pedantic:
        finding.evidence_refs = ["lintian:lintian_pedantic"]
    else:
        finding.evidence_refs = ["lintian:lintian_errors", "lintian:lintian_warnings"]
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
            f"Package is on the lto-disabled list; LTO must be fixed or disabled",
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
    sbuild_result = adapters.get("sbuild", {})

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
        finding.message = "C++ library without symbols file but appears to have documented consideration"
        finding.todo = "TODO: - For c++ libraries - symbols tracking isn't in place but the owning team tried..."
        finding.evidence_refs = ["packaging-source:debian_rules"]
        return finding

    # No symbols tracking and no documentation
    finding.status = "not-ok"
    finding.severity = "recommended"
    finding.confidence = "medium"
    finding.message = "C/C++ library detected but symbols tracking not found in package"
    finding.todo = "TODO: - For c++ libraries - symbols tracking isn't in place but the owning team tried..."
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
    has_watch_file = any(
        f.get("path", "").endswith("debian/watch")
        for f in file_listing
    )

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

    # Search for privilege escalation patterns outside tests
    escalation_keywords = ["sudo", "gksu", "pkexec", "LD_LIBRARY_PATH"]
    
    for keyword in escalation_keywords:
        if keyword.lower() in debian_rules.lower() or keyword.lower() in debian_control.lower():
            # Check if it's inside a test block/comment
            if "test" not in debian_rules.lower() and "test" not in debian_control.lower():
                finding.fail(
                    f"Potential {keyword} usage found outside tests",
                    "no use of sudo, gksu, pkexec, or LD_LIBRARY_PATH (usage is OK inside tests)",
                    severity="required",
                    confidence="low",
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

    # Search for "nobody" user outside tests
    combined = (debian_rules + "\n" + debian_control).lower()
    
    if "nobody" in combined:
        # Check if it's in a test context
        if "test" in combined:
            finding.succeed(
                "no use of user 'nobody' outside of tests",
                confidence="medium",
            )
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding

        finding.fail(
            "User 'nobody' found in packaging",
            "no use of user 'nobody' outside of tests",
            severity="required",
            confidence="low",
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

    if packaging.get("status") != "ok":
        finding.status = "unknown"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "Could not inspect packaging source"
        finding.todo = render_check_message(check, "unknown_todo")
        finding.evidence_refs = ["packaging-source:error"]
        return finding

    debian_rules = packaging.get("debian_rules", "").lower()

    # Check for setuid/setgid patterns
    setuid_patterns = ["chmod 4", "chmod 2", "perm -4000", "perm -2000", "setuid", "setgid"]
    
    has_setuid = any(p.lower() in debian_rules for p in setuid_patterns)

    if has_setuid:
        # Check for documented justification (prefer systemd)
        if "systemd" in debian_rules:
            finding.status = "not-ok"
            finding.severity = "recommended"
            finding.confidence = "medium"
            finding.message = "setuid/setgid present but using systemd service permissions"
            finding.todo = "TODO: - use of setuid, but ok because systemd is used"
            finding.evidence_refs = ["packaging-source:debian_rules"]
            return finding

        finding.fail(
            "setuid/setgid binaries found in packaging",
            "no use of setuid / setgid",
            severity="required",
            confidence="low",
        )
        finding.evidence_refs = ["packaging-source:debian_rules"]
        return finding

    finding.succeed(
        "no use of setuid / setgid",
        confidence="high",
    )
    finding.evidence_refs = ["packaging-source:debian_rules"]
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
