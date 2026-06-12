"""Renderer for auto-mir structured outputs.

The review draft mirrors the structure of docs/MIR/mir-reviewers-template.md.
Most sections are rendered with an OK: sub-block and a Left to decide:
sub-block. The [Summary] section is handled specially and keeps explicit
"Required TODOs:" and "Recommended TODOs:" blocks for final human judgment.
"""
from __future__ import annotations

import json
from collections import defaultdict


def _estimate_llm_tokens(ctx) -> dict:
    """Estimate token usage for LLM calls made during this run."""
    calls_by_model = getattr(ctx, 'llm_calls_by_model', {})
    tokens_by_model = getattr(ctx, 'llm_estimated_tokens', {})

    if not calls_by_model:
        return {"total_calls": 0, "by_model": {}}

    total_calls = sum(calls_by_model.values())
    total_tokens = sum(tokens_by_model.values())
    by_model = {}

    for model in sorted(calls_by_model.keys()):
        calls = calls_by_model.get(model, 0)
        tokens = tokens_by_model.get(model, 0)
        by_model[model] = {"calls": calls, "estimated_tokens": tokens}

    return {
        "total_calls": total_calls,
        "total_estimated_tokens": total_tokens,
        "by_model": by_model,
    }



# Canonical section order mirrors the reviewer template exactly.
# Any check whose section name is not listed here is appended at the end
# under an "Other" heading so nothing is silently dropped.
_SECTION_ORDER = [
    "Summary",
    "Rationale, Duplication and Ownership",
    "Dependencies",
    "Embedded sources and static linking",
    "Security",
    "Common blockers",
    "Packaging red flags",
    "Upstream red flags",
]


def write_outputs(ctx) -> None:
    """Write structured report (JSON) and reviewer draft (text) for a run."""
    # Prepare LLM token usage estimates
    llm_usage = _estimate_llm_tokens(ctx)

    report = {
        "bug_id": ctx.bug_id,
        "source_package": ctx.source_package,
        "series": ctx.series,
        "container_name": ctx.container_name,
        "policy_hashes": ctx.policy_hashes,
        "catalog_summary": ctx.evidence.get("catalog_summary", {}),
        "analysis_summary": ctx.evidence.get("analysis_summary", {}),
        "findings": ctx.findings,
        "llm_usage": llm_usage,
    }

    ctx.report_path = ctx.output_dir / "report.json"
    with ctx.report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)

    draft = _build_review_draft(ctx)
    _lint_review_draft(draft, ctx.findings)

    ctx.review_draft_path = ctx.output_dir / "review-draft.txt"
    ctx.review_draft_path.write_text(draft, encoding="utf-8")

    # Print LLM usage report to console instead of including in review-draft
    llm_report = _render_llm_usage_report(ctx)
    if llm_report:
        print("\n" + "\n".join(llm_report))


# ---------------------------------------------------------------------------
# Draft builder
# ---------------------------------------------------------------------------

def _build_review_draft(ctx) -> str:
    """Build the reviewer draft with one [Section] block per template section.

    Within each section:
      OK:        one line per resolved check (ok status)
      Problems:  one TODO line per unresolved check; "Problems: None" when clean
    """
    lines: list[str] = []

    # Preamble header (matches the RULE at top of template)
    lines += [
        f"Review for Source Package: {ctx.source_package}",
        f"Launchpad bug: https://bugs.launchpad.net/bugs/{ctx.bug_id}",
        f"Target series: {ctx.series or 'TBD'}",
        "",
    ]

    # Group findings by section, preserving per-section order from catalog
    by_section: dict[str, list[dict]] = defaultdict(list)
    for finding in ctx.findings:
        section = finding.get("section") or "Other"
        by_section[section].append(finding)

    # Emit sections in canonical template order, then any remainder
    known = list(_SECTION_ORDER)
    remainder = [s for s in by_section if s not in known]
    for section in known + remainder:
        if section not in by_section:
            continue
        findings_in_section = by_section[section]
        if section == "Summary":
            lines += _render_summary_section(findings_in_section, ctx.findings)
        else:
            lines += _render_section(section, findings_in_section)
        lines.append("")  # blank line between sections

    return "\n".join(lines)


def _render_section(section: str, findings: list[dict]) -> list[str]:
    """Render a standard [Section] block."""
    lines: list[str] = [f"[{section}]"]

    ok_findings = [f for f in findings if f["status"] == "ok"]
    undecided_findings = [f for f in findings if f["status"] != "ok"]

    # OK sub-block
    if ok_findings:
        lines.append("OK:")
        for finding in ok_findings:
            msg = (finding.get("message") or "").strip()
            if msg:
                lines.append(f"- {msg}")

    # Left to decide sub-block
    if undecided_findings:
        lines.append("Left to decide:")
        for finding in undecided_findings:
            for todo_line in _todo_lines_for_finding(finding):
                lines.append(f"- {todo_line}")
    else:
        lines.append("Left to decide: None")

    return lines


def _render_summary_section(summary_findings: list[dict], all_findings: list[dict]) -> list[str]:
    """Render [Summary] with special MIR template semantics.

    - Keep resolved summary checks under OK:
    - Do not emit a "Problems:" block here.
    - Keep unresolved summary TODO options visible for reviewer choice.
    - Always include Required TODOs: and Recommended TODOs: blocks.
    - SUM-4 is a gate check and is intentionally not rendered in the draft.
    """
    lines: list[str] = ["[Summary]"]

    visible_summary = [f for f in summary_findings if f.get("id") != "SUM-4"]
    ok_findings = [f for f in visible_summary if f.get("status") == "ok"]
    unresolved = [f for f in visible_summary if f.get("status") != "ok"]

    if ok_findings:
        lines.append("OK:")
        for finding in ok_findings:
            msg = (finding.get("message") or "").strip()
            if msg:
                lines.append(f"- {msg}")

    if unresolved:
        lines.append("Left to decide:")
        for finding in unresolved:
            for todo_line in _todo_lines_for_finding(finding):
                lines.append(f"- {todo_line}")
    else:
        lines.append("Left to decide: None")

    lines.append("Required TODOs:")
    lines.append("- TODO: - TBD (Please add them numbered for later reference)")
    required = _collect_todos_by_severity(all_findings, "required")
    if required:
        for todo in required:
            lines.append(f"- {todo}")

    lines.append("Recommended TODOs:")
    lines.append("- TODO: - TBD (Please add them numbered for later reference)")
    recommended = _collect_todos_by_severity(all_findings, "recommended")
    if recommended:
        for todo in recommended:
            lines.append(f"- {todo}")

    return lines


def _collect_todos_by_severity(findings: list[dict], severity: str) -> list[str]:
    seen: set[str] = set()
    todos: list[str] = []
    for finding in findings:
        if finding.get("id") == "SUM-4":
            # SUM-4 is a gate only and should not render in the final draft.
            continue
        if finding.get("status") == "ok":
            continue
        if finding.get("severity") != severity:
            continue
        for todo_line in _todo_lines_for_finding(finding):
            if todo_line not in seen:
                seen.add(todo_line)
                todos.append(todo_line)
    return todos


def _todo_lines_for_finding(finding: dict) -> list[str]:
    """Return normalized TODO lines for a finding, preserving option variants."""
    todo_text = (finding.get("todo") or "").strip()
    if not todo_text:
        todo_text = f"TODO: {finding.get('id')} {finding.get('title', '')}".strip()

    lines = [line.strip() for line in todo_text.splitlines() if line.strip()]
    normalized: list[str] = []
    for line in lines:
        # Avoid double-prefix outputs like "TODO: TODO-A: ..."
        if line.startswith("TODO: TODO-"):
            line = line[len("TODO: "):]
        if not (line.startswith("TODO:") or line.startswith("TODO-")):
            line = f"TODO: {line}"
        normalized.append(line)
    return normalized


# ---------------------------------------------------------------------------
# Linter
# ---------------------------------------------------------------------------

def _lint_review_draft(draft: str, findings: list[dict]) -> None:
    """Validate the rendered draft for structural correctness.

    Rules enforced:
    - No RULE: lines (template directives must never reach the output)
    - Lines inside a Left to decide: block must start with "- TODO:" or "- TODO-"
    - Resolved (ok) findings must not produce a TODO message
    - Unresolved findings must carry a TODO string
    """
    in_undecided_block = False
    for line in draft.splitlines():
        # No raw RULE lines allowed
        if line.startswith("RULE:") or line.startswith("RULE "):
            raise ValueError("Review draft still contains RULE lines")

        # Track section / sub-section transitions
        if line.startswith("[") and line.endswith("]"):
            in_undecided_block = False
            continue
        if line == "Left to decide:":
            in_undecided_block = True
            continue
        if line.startswith("Left to decide: ") or line in ("OK:", "Required TODOs:", "Recommended TODOs:", ""):
            in_undecided_block = False
            continue

        # Every content line inside undecided block must be a TODO entry
        if in_undecided_block and line:
            if not (line.startswith("- TODO:") or line.startswith("- TODO-")):
                raise ValueError(
                    f"Left to decide block line must start with '- TODO:' or '- TODO-': {line!r}"
                )

    # Per-finding invariants
    for finding in findings:
        status = finding.get("status")
        message = (finding.get("message") or "").strip()
        todo = (finding.get("todo") or "").strip()

        if status == "ok" and message.startswith("TODO:"):
            raise ValueError(
                f"Resolved finding {finding.get('id')} must not render as TODO"
            )
        if status != "ok" and not (todo.startswith("TODO:") or todo.startswith("TODO-")):
            raise ValueError(
                f"Unresolved finding {finding.get('id')} must include TODO"
            )


# ---------------------------------------------------------------------------
# LLM Usage Report
# ---------------------------------------------------------------------------

def _render_llm_usage_report(ctx) -> list[str]:
    """Render a usage report showing LLM model calls and token consumption."""
    lines: list[str] = [
        "",
        "[LLM Usage Report]",
    ]

    # Get usage data (may be empty if no LLM calls were made)
    calls_by_model = getattr(ctx, 'llm_calls_by_model', {})
    tokens_by_model = getattr(ctx, 'llm_estimated_tokens', {})

    if not calls_by_model:
        lines.append("No LLM calls made (deterministic-only evaluation).")
        return lines

    total_calls = sum(calls_by_model.values())
    total_tokens = sum(tokens_by_model.values())
    lines.append(f"Total LLM calls: {total_calls}")
    lines.append(f"Total estimated tokens: {total_tokens}")
    lines.append("")

    # Model-by-model breakdown
    for model in sorted(calls_by_model.keys()):
        calls = calls_by_model.get(model, 0)
        tokens = tokens_by_model.get(model, 0)
        lines.append(f"  {model}: {calls} calls, {tokens} tokens")

    return lines

