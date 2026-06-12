"""Check evaluation engine for auto-mir.

Package structure:
- checks (this module): public API, evaluate_checks()
- checks.deterministic: deterministic evaluators (_check_* functions, _eval_deterministic)
- checks.llm_eval: LLM-based evaluators (_eval_ev_to_ai, _eval_ai, _eval_human_only)
- checks.language_gates: language detection helpers (_is_go_package, _is_rust_package, _language_gate_active)
"""

from __future__ import annotations

import logging

from models import Finding
from checks.language_gates import _is_go_package, _is_rust_package, _language_gate_active

log = logging.getLogger("auto_mir.checks")


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
