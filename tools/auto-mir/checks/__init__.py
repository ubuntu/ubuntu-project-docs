"""Check evaluation engine for auto-mir.

Package structure:
- checks (this module): public API, evaluate_checks()
- checks.deterministic: deterministic evaluators (_check_* functions, _eval_deterministic)
- checks.llm_eval: LLM-based evaluators (_eval_ev_to_ai, _eval_ai, _eval_human_only)
- checks.language_gates: language detection helpers (_language_gate_active)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auto_mir import RunContext

import importlib
import logging

import review_type
from checks.language_gates import _language_gate_active
from checks.registry import EVALUATORS
from models import Finding

log = logging.getLogger("auto_mir.checks")


def _ensure_evaluators_registered() -> None:
    """Import evaluator modules for their registration side effects."""
    importlib.import_module("checks.deterministic")
    importlib.import_module("checks.llm_eval")


# Severities considered "blocking" that a re-review / reorg fast-path softens
# down to a plain recommendation.
_BLOCKING_SEVERITIES = {"required", "nack"}


def _apply_review_type_softening(findings: list[Finding], decision) -> None:
    """Soften blocking findings in place for re-review / reorg fast-paths.

    For voluntary re-reviews and renamed/reorganised sources, MIR policy treats
    everything as non-blocking and recommendation-only. We therefore downgrade
    every non-Summary finding whose severity is 'required' or 'nack' to
    'recommended' so it lands in the Summary's *Recommended* TODO block rather
    than the *Required* one, and so the SUM-5 verdict synthesis (which runs next
    and reads these findings) naturally leans towards ACK.

    Summary-section findings (the ACK/NACK verdict and security-review decision)
    are left untouched: they are the reviewer's judgement surface, not blocking
    action items. The human can always promote a softened line back to Required.
    """
    if decision.review_type == review_type.FRESH:
        return
    softened = 0
    for finding in findings:
        if finding.section == "Summary":
            continue
        if finding.severity in _BLOCKING_SEVERITIES:
            finding.severity = "recommended"
            softened += 1
    log.info(
        "review type '%s': softened %d blocking finding(s) to recommended",
        decision.review_type,
        softened,
    )


def evaluate_checks(ctx: "RunContext") -> list[Finding]:
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

    _ensure_evaluators_registered()

    # Detect (or honour a forced) review type up front so the softening pass and
    # the SUM-5/SUM-6 synthesis both see a consistent decision. Store it on the
    # context and in the evidence so the renderer and report.json can surface it.
    decision = review_type.detect_review_type(ctx)
    ctx.review_type = decision.review_type
    if isinstance(getattr(ctx, "evidence", None), dict):
        ctx.evidence["review_type"] = decision.to_evidence()
    log.info("review type resolved to '%s' (forced=%s)", decision.review_type, decision.forced)

    checks = ctx.catalog.get("checks", [])

    # Two-pass evaluation: synthesis checks (e.g. SUM-5 overall verdict, SUM-6
    # security-review-needed) summarise the other checks, so they must run AFTER
    # all non-synthesis checks. We evaluate non-synthesis checks first, expose
    # their findings via ctx.findings, then evaluate the deferred synthesis
    # checks. The returned list is reassembled in catalog order so rendering and
    # Summary-section placement are unaffected.
    findings_by_id: dict[str, Finding] = {}

    # Pass 1: non-synthesis checks, in catalog order.
    # ctx.findings is populated incrementally so a later check can consult an
    # earlier one's result within this pass (e.g. CB-5 gates on CB-4's verdict).
    pass1_findings: list[Finding] = []
    ctx.findings = pass1_findings
    for check in checks:
        if check.get("synthesis"):
            continue
        finding = _evaluate_single_check(check, ctx)
        findings_by_id[check["id"]] = finding
        pass1_findings.append(finding)

    # Make pass-1 findings available to synthesis evaluators (SUM-5/SUM-6 read
    # ctx.findings); it is overwritten with the full ordered list by the caller.
    #
    # Re-review / reorg fast-paths soften blocking findings to recommendations
    # BEFORE the synthesis runs, so the SUM-5 verdict naturally leans towards ACK
    # (it sees no remaining required findings) and the softened severities flow
    # into the consolidated Recommended TODO block.
    _apply_review_type_softening(pass1_findings, decision)
    ctx.findings = list(pass1_findings)

    # Pass 2: deferred synthesis checks, after everything else.
    for check in checks:
        if not check.get("synthesis"):
            continue
        finding = _evaluate_single_check(check, ctx)
        findings_by_id[check["id"]] = finding

    # Reassemble in catalog order so render/Summary placement is unchanged.
    findings = [findings_by_id[check["id"]] for check in checks]

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


def _evaluate_single_check(check: dict, ctx: "RunContext") -> Finding:
    """Evaluate one catalog check and return its Finding.

    Handles the language gate, evaluator routing, and TODO normalisation shared
    by both evaluation passes in evaluate_checks().
    """
    mode = check.get("mode", "unknown")
    # Invariant: severity is always "ok" when status is "ok",
    # and always set to a non-None value by every evaluator path.
    finding = Finding(
        id=check["id"],
        section=check.get("section", "unknown"),
        title=check.get("title", ""),
        mode=mode,
        blocker_class=check.get("blocker_class", "none"),
        aggregate_todo=bool(check.get("aggregate_todo", False)),
    )

    # Apply language gate before routing to evaluator.
    # If the gate says the language is absent, mark ok/not-applicable and skip.
    gate = check.get("language_gate")
    if gate and not _language_gate_active(gate, ctx):
        # Combined gates (e.g. "go|rust") would emit a redundant umbrella line
        # on top of the per-language statements produced by the single-language
        # gate checks (e.g. ESL-4 for go, ESL-8 for rust). Suppress the umbrella
        # message so only the specific per-language lines render.
        if "|" in gate:
            finding.succeed("", confidence="high")
        else:
            finding.succeed(
                f"not a {gate} package, no extra constraints to consider in that regard",
                confidence="high",
            )
        return finding

    # Route to appropriate evaluator
    title = str(check.get("title") or "").strip()
    if title:
        log.info("Evaluating check: %s - %s (%s)", check["id"], title, mode)
    else:
        log.info("Evaluating check: %s (%s)", check["id"], mode)
    evaluator = EVALUATORS.get(mode)
    if evaluator:
        finding = evaluator(check, ctx, finding)
    else:
        finding.fail(f"Unknown mode: {mode}", finding.title, status="unknown")

    finding.ensure_todo(finding.title)

    return finding
