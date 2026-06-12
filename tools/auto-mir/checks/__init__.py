"""Check evaluation engine for auto-mir.

Package structure:
- checks (this module): public API, language helpers, evaluate_checks()
- checks.deterministic: deterministic evaluators (_check_* functions, _eval_deterministic)
- checks.llm_eval: LLM-based evaluators (_eval_ev_to_ai, _eval_ai, _eval_human_only)
"""

from __future__ import annotations

import logging

from models import Finding

log = logging.getLogger("auto_mir.checks")


def _is_go_package(packaging: dict) -> bool:
    """Return True when the packaging evidence indicates a Go package.

    Heuristics (any one sufficient):
    - go.sum file present in source tree
    - dh-golang or golang mentioned in debian/rules
    """
    rules = packaging.get("debian_rules", "")
    return (
        packaging.get("go_sum_present", False)
        or "dh-golang" in rules
        or "golang" in rules.lower()
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


from checks.deterministic import (
    _eval_deterministic,
    _check_sum_1,
    _check_sum_2,
    _check_sum_4,
    _check_dep_1,
    _check_dep_3,
    _check_esl_1,
    _check_esl_3,
    _check_esl_4,
    _check_esl_7,
    _check_esl_8,
    _check_esl_9,
    _check_esl_10,
    _check_sec_3,
    _check_sec_4,
    _check_cb_7,
)
from checks.llm_eval import _eval_ev_to_ai, _eval_ai, _eval_human_only


def evaluate_checks(ctx) -> list[Finding]:
    """Evaluate all checks from catalog against collected evidence.

    Returns list of Finding objects with:
    - id, section, title, mode
    - status: ok|not-ok|unknown
    - severity: ok|recommended|required|nack
    - confidence: low|medium|high
    - message: reviewer-facing statement
    - todo: empty if resolved, TODO line if not
    - evidence_refs: which adapters/keys were used

    The confidence level determines how the finding is rendered in the output:
    - ``confidence == "high"`` or ``mode == "deterministic"``: a not-ok finding
      is shown under ``Problems:`` as a confirmed statement (no TODO needed).
    - ``confidence in ("low", "medium")``: a not-ok finding is shown under
      ``Left to decide:`` as a TODO for the reviewer to resolve.
    """
    if not ctx.catalog:
        return []

    checks = ctx.catalog.get("checks", [])
    findings = []

    for check in checks:
        mode = check.get("mode", "unknown")
        # Invariant: severity is always "ok" when status is "ok",
        # and always set to a non-None value by every evaluator path.
        finding = Finding(
            id=check["id"],
            section=check.get("section", "unknown"),
            title=check.get("title", ""),
            mode=mode,
            blocker_class=check.get("blocker_class", "none"),
        )

        # Apply language gate before routing to evaluator.
        # If the gate says the language is absent, mark ok/not-applicable and skip.
        gate = check.get("language_gate")
        if gate and not _language_gate_active(gate, ctx):
            finding.status = "ok"
            finding.severity = "ok"
            finding.confidence = "high"
            finding.message = (
                f"not a {gate} package, no extra constraints to consider in that regard"
            )
            finding.todo = ""
            findings.append(finding)
            continue

        # Route to appropriate evaluator
        title = str(check.get("title") or "").strip()
        if title:
            log.info("Evaluating check: %s - %s (%s)", check["id"], title, mode)
        else:
            log.info("Evaluating check: %s (%s)", check["id"], mode)
        if mode == "deterministic":
            finding = _eval_deterministic(check, ctx, finding)
        elif mode == "ev_to_ai":
            finding = _eval_ev_to_ai(check, ctx, finding)
        elif mode == "ai":
            finding = _eval_ai(check, ctx, finding)
        elif mode == "human_only":
            finding = _eval_human_only(check, ctx, finding)
        else:
            finding.status = "unknown"
            finding.message = f"Unknown mode: {mode}"

        todo_value = str(finding.todo or "")
        if finding.status != "ok" and not (
            todo_value.startswith("TODO:") or todo_value.startswith("TODO-")
        ):
            finding.todo = f"TODO: - {finding.title}"

        findings.append(finding)

    # Post-process: for unknown/low-confidence findings, record which adapter failures
    # caused the fallback so the renderer can emit visible warnings in the draft.
    adapters_store = ctx.evidence.get("adapters", {})
    failed_adapters = {
        adapter_id
        for adapter_id, data in adapters_store.items()
        if isinstance(data, dict) and data.get("status") in ("error", "pending")
    }
    if failed_adapters:
        check_by_id = {c["id"]: c for c in checks}
        for finding in findings:
            if finding.status == "unknown" or (
                finding.status != "ok" and finding.confidence == "low"
            ):
                check_def = check_by_id.get(finding.id, {})
                relevant = set(check_def.get("adapters_required", [])) | set(
                    check_def.get("adapters_optional", [])
                )
                caused_by = sorted(relevant & failed_adapters)
                if caused_by:
                    finding.adapter_error_cause = caused_by

    return findings
