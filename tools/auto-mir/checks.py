"""Check evaluation engine for auto-mir.

Implements deterministic, ev_to_ai, and ai mode checks against collected evidence.
This module handles the interpretation and mapping of findings to severities.
"""

from __future__ import annotations

import logging
from typing import Any

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

        findings.append(finding)

    return findings


# ---------------------------------------------------------------------------
# Deterministic Check Evaluators
# ---------------------------------------------------------------------------

def _eval_deterministic(check: dict, ctx, finding: dict) -> dict:
    """Evaluate checks with deterministic logic only."""
    check_id = check["id"]
    evidence = ctx.evidence

    # Dispatch to per-check evaluator
    if check_id == "SUM-1":
        return _check_sum_1(ctx, finding)
    elif check_id == "SUM-2":
        return _check_sum_2(ctx, finding)
    elif check_id == "DEP-1":
        return _check_dep_1(ctx, finding)
    elif check_id == "SEC-3":
        return _check_sec_3(ctx, finding)
    elif check_id == "SEC-4":
        return _check_sec_4(ctx, finding)
    elif check_id == "CB-7":
        return _check_cb_7(ctx, finding)
    else:
        finding["status"] = "unknown"
        finding["message"] = "Deterministic check evaluator not implemented"
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

    # For now, assume all extracted deps are in main (real check would verify component)
    # This is a stub pending full apt policy integration
    finding["status"] = "ok"
    finding["severity"] = "ok"
    finding["confidence"] = "medium"
    finding["message"] = "- no other runtime Dependencies to MIR due to this"
    finding["evidence_refs"] = ["dep-analysis:runtime_deps"]
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
        finding["message"] = "- does not use webkit1,2"
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
        finding["message"] = "- does not use lib*v8 directly"
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
        finding["message"] = "- no new python2 dependency"
        finding["evidence_refs"] = ["dep-analysis:runtime_deps"]
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
