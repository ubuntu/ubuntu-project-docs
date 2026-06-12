"""LLM-based check evaluators for auto-mir.

Contains ev_to_ai, ai, and human_only evaluators, plus all LLM helper
functions for prompt rendering, evidence assembly, and response mapping.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from models import Finding
from checks.registry import evaluator

log = logging.getLogger("auto_mir.checks.llm_eval")


@evaluator("ev_to_ai")
def _eval_ev_to_ai(check: dict, ctx, finding: Finding) -> Finding:
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
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = f"LLM unavailable: {exc}"
        finding.todo = _default_todo_for_check(
            check, fallback_suffix="manual review needed (LLM unavailable)"
        )
        return finding

    return _apply_llm_response(response, check, finding)


@evaluator("ai")
def _eval_ai(check: dict, ctx, finding: Finding) -> Finding:
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
        finding.status = "unknown"
        finding.confidence = "low"
        finding.message = f"LLM unavailable: {exc}"
        finding.todo = _default_todo_for_check(check, fallback_suffix="requires AI synthesis")
        return finding

    return _apply_llm_response(response, check, finding)


@evaluator("human_only")
def _eval_human_only(check: dict, ctx, finding: Finding) -> Finding:
    """Evaluate checks that require human judgment only."""
    finding.status = "unknown"
    finding.confidence = "low"
    finding.message = "Human review required"
    finding.todo = f"TODO: - {check.get('title', 'Check')} — reviewer judgment needed"
    return finding


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
    relevant = list(check.get("adapters_required", [])) + list(check.get("adapters_optional", []))
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
        "debian_rules",  # rules file
        "debian_watch",
        "debian_copyright",
        "debian_tests_control",
        "raw_output",  # component-mismatches raw output
        "build_log",
    }

    result = {}
    for k, v in data.items():
        if k in SUMMARY_FIELDS and isinstance(v, str):
            # For known large fields, just count lines/errors
            if k == "lintian_output":
                lines = v.splitlines()
                errors = sum(1 for ln in lines if ln.startswith("E: "))
                warnings = sum(1 for ln in lines if ln.startswith("W: "))
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
            "TODO references this check resolves:\n" + "\n".join(f"  {t}" for t in todo_refs)
        )

    # Pull RULE lines from the reviewer template for this section
    workspace_root = getattr(ctx, "workspace_root", None)
    if workspace_root:
        template_path = Path(workspace_root) / "docs" / "MIR" / "mir-reviewers-template.md"
        if template_path.exists():
            section_text = _extract_template_section(template_path, section)
            rule_lines = [
                line for line in section_text.splitlines() if line.strip().startswith("RULE:")
            ]
            if rule_lines:
                parts.append(
                    f"Reviewer policy rules for [{section}]:\n" + "\n".join(rule_lines[:30])
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


def _apply_llm_response(response: dict, check: dict, finding: Finding) -> Finding:
    """Map a validated LLM JSON response back onto a finding dict.

    Accepts partial responses — only overrides fields that are present and
    non-empty in the response.  Always marks the finding as requiring human
    confirmation regardless of what the model returns.
    """
    if not isinstance(response, dict):
        log.warning("LLM response for %s is not a dict: %r", check["id"], response)
        finding.status = "unknown"
        finding.todo = _default_todo_for_check(check, fallback_suffix="LLM response invalid")
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

    finding.status = status
    finding.severity = severity
    finding.confidence = confidence

    message = (response.get("message") or "").strip()
    if message:
        finding.message = message

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
            prefix_inner = "" if todo.startswith("- ") else "- "
            todo = f"TODO: {prefix_inner}{todo}"
        if not todo:
            todo = _default_todo_for_check(check, fallback_suffix="review needed")
        if rationale:
            finding.message = f"{message}\n  Rationale: {rationale}" if message else rationale
        finding.todo = todo
    else:
        if rationale:
            finding.message = f"{message}\n  ({rationale})" if message else rationale
        finding.todo = ""

    risk_flags = response.get("risk_flags", [])
    if isinstance(risk_flags, list) and risk_flags:
        finding.risk_flags = risk_flags

    ev_refs = response.get("evidence_refs", [])
    if isinstance(ev_refs, list) and ev_refs:
        finding.evidence_refs = ev_refs

    # Always require human confirmation for AI-derived findings
    finding.human_confirmation_required = True

    return finding


def _default_todo_for_check(check: dict, fallback_suffix: str) -> str:
    """Return a default TODO string for a check.

    Prefer catalog todo_refs so mutually-exclusive options (TODO-A/B/C) are kept
    visible for human review when the tool cannot decide.
    """
    todo_refs = [str(x).strip() for x in check.get("todo_refs", []) if str(x).strip()]
    if todo_refs:
        return "\n".join(todo_refs)
    return f"TODO: - {check.get('title', check.get('id', 'Check'))} — {fallback_suffix}"


def _summarise_findings_so_far(ctx) -> list[dict]:
    """Return a compact summary of findings already evaluated in this run."""
    results = []
    for f in getattr(ctx, "findings", []):
        results.append(
            {
                "id": f.id,
                "section": f.section,
                "status": f.status,
                "severity": f.severity,
                "message": (f.message or "")[:200],
            }
        )
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
