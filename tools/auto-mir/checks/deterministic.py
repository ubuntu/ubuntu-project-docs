"""Deterministic check evaluators for auto-mir.

Contains all check functions that evaluate evidence without LLM calls,
the dispatch table, and the _eval_deterministic entry point.
"""

from __future__ import annotations

import logging
import re

from checks.language_gates import _is_go_package, _is_rust_package
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
        finding.message = render_check_message(check, "ok_message", source_package=ctx.source_package)
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
        finding.message = render_check_message(check, "not_ok_message", deps=", ".join(in_scope_deps))
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
            check, "not_ok_message", vendored_dirs=", ".join(vendored_dirs)
        )
        finding.todo = render_check_message(
            check, "not_ok_todo", vendored_dirs=", ".join(vendored_dirs)
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
        finding.message = render_check_message(
            check, "not_ok_message", entries=entries_joined
        )
        finding.todo = render_check_message(
            check, "not_ok_todo", entries=entries_joined
        )
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
            e for e in all_built_using
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
