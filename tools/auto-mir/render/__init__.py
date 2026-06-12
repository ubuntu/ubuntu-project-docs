"""Renderer for auto-mir structured outputs.

The review draft mirrors the structure of docs/MIR/mir-reviewers-template.md.
Most sections are rendered with a three-tier structure:

  OK:              Resolved checks (status == "ok").
  Problems:        High-confidence or deterministic failures (status != "ok"
                   and confidence == "high" or mode == "deterministic").
                   The reviewer should treat these as confirmed findings.
  Left to decide:  Unresolvable items and low/medium-confidence results that
                   need human judgment.  Always rendered as ``TODO: - <text>``
                   lines (without a leading ``- `` prefix added by the renderer).

The [Summary] section is handled specially and keeps explicit
"Required TODOs:" and "Recommended TODOs:" blocks for final human judgment.
Each collected TODO is emitted as-is (``TODO: - <text>``) so the reviewer
can resolve it by removing the ``TODO: `` prefix.

Linting rules enforced before writing the draft:
- Lines in a Left to decide: block must start with ``TODO:`` or ``TODO-``.
- Lines in a Problems: block must not start with ``TODO:``.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict

from models import Finding


def _estimate_llm_tokens(ctx) -> dict:
    """Estimate token usage for LLM calls made during this run."""
    calls_by_model = getattr(ctx, "llm_calls_by_model", {})
    tokens_by_model = getattr(ctx, "llm_estimated_tokens", {})

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
        "vm_name": ctx.vm_name,
        "catalog_summary": ctx.evidence.get("catalog_summary", {}),
        "analysis_summary": ctx.evidence.get("analysis_summary", {}),
        "findings": [asdict(f) for f in ctx.findings],
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

    # Print adapter failure warning to console so degraded checks are obvious
    failure_warning = _render_adapter_failure_warning(ctx)
    if failure_warning:
        print("\n" + "\n".join(failure_warning))


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
    ]

    # Binary package overview — helps the reviewer see scope at a glance.
    # Data comes from dep-analysis (all binaries) and component-mismatches
    # (which are already in main vs. need promotion).  Both are best-effort;
    # the SUM-3 check in [Summary] handles the formal scope decision.
    binary_lines = _build_binary_package_header(ctx)
    if binary_lines:
        lines += binary_lines

    lines.append("")

    # Group findings by section, preserving per-section order from catalog
    by_section: dict[str, list[Finding]] = defaultdict(list)
    for finding in ctx.findings:
        section = finding.section or "Other"
        by_section[section].append(finding)

    # Emit sections in canonical template order, then any remainder
    known = list(_SECTION_ORDER)
    remainder = [s for s in by_section if s not in known]
    for section in known + remainder:
        if section not in by_section:
            continue
        findings_in_section = by_section[section]
        if section == "Summary":
            lines += _render_summary_section(findings_in_section, ctx.findings, ctx)
        else:
            lines += _render_section(section, findings_in_section)
        lines.append("")  # blank line between sections

    return "\n".join(lines)


def _build_binary_package_header(ctx) -> list[str]:
    """Build binary package overview lines for the draft preamble.

    Returns an empty list when no binary package data is available so
    the header degrades gracefully to 'Source Package / bug / series' only.

    When data is available, emits:
      Binary packages: <list>
      Component split: <binaries already in main> | <binaries needing promotion>
    The component split line is only emitted when both sets are non-empty.
    """
    adapters = ctx.evidence.get("adapters", {})
    dep_analysis = adapters.get("dep-analysis", {})
    cm = adapters.get("component-mismatches", {})

    all_binaries: list[str] = dep_analysis.get("binary_packages", [])
    promotion_candidates: list[str] = cm.get("promotion_candidates", [])

    if not all_binaries and not promotion_candidates:
        return []

    lines: list[str] = []

    if all_binaries:
        lines.append(f"Binary packages: {', '.join(sorted(all_binaries))}")
    elif promotion_candidates:
        # Fallback: only component-mismatches data available
        lines.append(
            f"Binary packages (promotion candidates only): {', '.join(sorted(promotion_candidates))}"
        )
        return lines

    # Component split: binaries NOT in the promotion list are presumably already in main
    if promotion_candidates:
        already_in_main = sorted(set(all_binaries) - set(promotion_candidates))
        needing_promotion = sorted(set(promotion_candidates) & set(all_binaries))
        if already_in_main and needing_promotion:
            lines.append(
                f"Component split: already in main: {', '.join(already_in_main)}"
                f" | needs promotion: {', '.join(needing_promotion)}"
            )

    return lines


def _build_out_of_scope_dep_hint(ctx) -> list[str]:
    """Add informational hint about out-of-scope dependencies.

    These are universe dependencies belonging to binary packages NOT requested
    for promotion. They do not need a MIR and are shown as informational only.
    """
    dep_analysis = ctx.evidence.get("adapters", {}).get("dep-analysis", {})
    out_of_scope = dep_analysis.get("out_of_scope_deps_not_in_main", [])
    if out_of_scope:
        return [
            "Note: The following universe dependencies belong to binary packages "
            "NOT requested for promotion and do not need a MIR: " + ", ".join(sorted(out_of_scope))
        ]
    return []


def _is_high_confidence_failure(finding: Finding) -> bool:
    """Return True when a not-ok finding is deterministic or AI high-confidence.

    Such findings are shown under Problems: rather than Left to decide: so the
    reviewer can see confirmed issues separately from items needing judgment.
    """
    if finding.status == "unknown":
        return False
    return finding.confidence == "high" or finding.mode == "deterministic"


def _render_section(section: str, findings: list[Finding]) -> list[str]:
    """Render a standard [Section] block with the three-tier structure.

    OK:              resolved checks
    Problems:        high-confidence / deterministic failures
    Left to decide:  low/medium-confidence or unresolvable items (as TODO lines)
    """
    lines: list[str] = [f"[{section}]"]

    ok_findings = [f for f in findings if f.status == "ok"]
    not_ok = [f for f in findings if f.status != "ok"]
    problems = [f for f in not_ok if _is_high_confidence_failure(f)]
    undecided = [f for f in not_ok if not _is_high_confidence_failure(f)]

    # OK sub-block — de-duplicate identical messages (e.g. "not a go package" repeated per check)
    if ok_findings:
        lines.append("OK:")
        seen_msgs: set[str] = set()
        for finding in ok_findings:
            msg = (finding.message or "").strip()
            if msg and msg not in seen_msgs:
                lines.append(f"- {msg}")
                seen_msgs.add(msg)

    # Problems sub-block — confirmed findings, shown as statements not TODOs
    if problems:
        lines.append("Problems:")
        for finding in problems:
            msg = (finding.message or "").strip()
            if msg:
                lines.append(f"- {msg}")

    # Left to decide sub-block
    if undecided:
        lines.append("Left to decide:")
        for finding in undecided:
            causes = finding.adapter_error_cause
            if causes:
                lines.append(
                    f"NOTE: - left for manual follow-up; adapter(s) failed: {', '.join(causes)}"
                )
            for todo_line in _todo_lines_for_finding(finding):
                lines.append(todo_line)
    elif not problems:
        lines.append("Left to decide: None")

    return lines


def _render_summary_section(
    summary_findings: list[Finding], all_findings: list[Finding], ctx
) -> list[str]:
    """Render [Summary] with special MIR template semantics.

    - Keep resolved summary checks under OK:
    - Do not emit a "Problems:" block here.
    - Keep unresolved summary TODO options visible for reviewer choice.
    - Always include Required TODOs: and Recommended TODOs: blocks.
    - SUM-4 is a gate check and is intentionally not rendered in the draft.
    - Include out-of-scope dependency hints as informational notes.
    """
    lines: list[str] = ["[Summary]"]

    visible_summary = [f for f in summary_findings if f.id != "SUM-4"]
    ok_findings = [f for f in visible_summary if f.status == "ok"]
    unresolved = [f for f in visible_summary if f.status != "ok"]

    if ok_findings:
        lines.append("OK:")
        for finding in ok_findings:
            msg = (finding.message or "").strip()
            if msg:
                lines.append(f"- {msg}")

    # Add out-of-scope dependency hints
    out_of_scope_hints = _build_out_of_scope_dep_hint(ctx)
    if out_of_scope_hints:
        for hint in out_of_scope_hints:
            lines.append(f"- {hint}")

    if unresolved:
        lines.append("Left to decide:")
        for finding in unresolved:
            causes = finding.adapter_error_cause
            if causes:
                lines.append(
                    f"NOTE: - left for manual follow-up; adapter(s) failed: {', '.join(causes)}"
                )
            for todo_line in _todo_lines_for_finding(finding):
                lines.append(todo_line)
    else:
        lines.append("Left to decide: None")

    lines.append("Required TODOs:")
    lines.append("- TODO: - TBD (Please add them numbered for later reference)")
    required = _collect_todos_by_severity(all_findings, "required")
    if required:
        for todo in required:
            lines.append(todo)

    lines.append("Recommended TODOs:")
    lines.append("- TODO: - TBD (Please add them numbered for later reference)")
    recommended = _collect_todos_by_severity(all_findings, "recommended")
    if recommended:
        for todo in recommended:
            lines.append(todo)

    return lines


def _collect_todos_by_severity(findings: list[Finding], severity: str) -> list[str]:
    seen: set[str] = set()
    todos: list[str] = []
    for finding in findings:
        if finding.id == "SUM-4":
            # SUM-4 is a gate only and should not render in the final draft.
            continue
        if finding.status == "ok":
            continue
        if finding.severity != severity:
            continue
        for todo_line in _todo_lines_for_finding(finding):
            if todo_line not in seen:
                seen.add(todo_line)
                todos.append(todo_line)
    return todos


def _todo_lines_for_finding(finding: Finding) -> list[str]:
    """Return normalized TODO lines for a finding, preserving option variants."""
    todo_text = (finding.todo or "").strip()
    if not todo_text:
        todo_text = f"TODO: - {finding.id} {finding.title}".strip()

    lines = [line.strip() for line in todo_text.splitlines() if line.strip()]
    normalized: list[str] = []
    for line in lines:
        # Avoid double-prefix outputs like "TODO: TODO-A: ..."
        if line.startswith("TODO: TODO-"):
            line = line[len("TODO: ") :]
        if not (line.startswith("TODO:") or line.startswith("TODO-")):
            prefix_inner = "" if line.startswith("- ") else "- "
            line = f"TODO: {prefix_inner}{line}"
        normalized.append(line)
    return normalized


# ---------------------------------------------------------------------------
# Linter
# ---------------------------------------------------------------------------


def _lint_review_draft(draft: str, findings: list[Finding]) -> None:
    """Validate the rendered draft for structural correctness.

    Rules enforced:
    - No RULE: lines (template directives must never reach the output)
    - Lines inside a Left to decide: block must start with "- TODO:" or "- TODO-"
    - Lines inside a Problems: block must not start with "- TODO:" (confirmed findings)
    - Resolved (ok) findings must not produce a TODO message
    - Unresolved low/medium-confidence findings must carry a TODO string
    """
    in_undecided_block = False
    in_problems_block = False
    for line in draft.splitlines():
        # No raw RULE lines allowed
        if line.startswith("RULE:") or line.startswith("RULE "):
            raise ValueError("Review draft still contains RULE lines")

        # Track section / sub-section transitions
        if line.startswith("[") and line.endswith("]"):
            in_undecided_block = False
            in_problems_block = False
            continue
        if line == "Left to decide:":
            in_undecided_block = True
            in_problems_block = False
            continue
        if line == "Problems:":
            in_problems_block = True
            in_undecided_block = False
            continue
        if line.startswith("Left to decide: ") or line in (
            "OK:",
            "Required TODOs:",
            "Recommended TODOs:",
            "",
        ):
            in_undecided_block = False
            in_problems_block = False
            continue

        # Every content line inside undecided block must be a TODO, NOTE, or list entry
        if in_undecided_block and line:
            if not (
                line.startswith("TODO:") or line.startswith("TODO-") or line.startswith("NOTE:")
            ):
                raise ValueError(
                    f"Left to decide block line must start with 'TODO:', 'TODO-', or 'NOTE:': {line!r}"
                )

        # Problems block lines are confirmed finding statements, not TODOs
        if in_problems_block and line:
            if line.startswith("TODO:") or line.startswith("TODO-"):
                raise ValueError(f"Problems block line must not be a TODO line: {line!r}")

    # Per-finding invariants
    for finding in findings:
        status = finding.status
        message = (finding.message or "").strip()
        todo = (finding.todo or "").strip()

        if status == "ok" and message.startswith("TODO:"):
            raise ValueError(f"Resolved finding {finding.id} must not render as TODO")
        # High-confidence failures render under Problems: and need a message, not a TODO
        if status != "ok" and not _is_high_confidence_failure(finding):
            if not (todo.startswith("TODO:") or todo.startswith("TODO-")):
                raise ValueError(f"Unresolved finding {finding.id} must include TODO")


# ---------------------------------------------------------------------------
# LLM Usage Report
# ---------------------------------------------------------------------------


def _render_adapter_failure_warning(ctx) -> list[str]:
    """Render a console warning summarizing adapter failures and the checks they affected."""
    failed_findings = [f for f in ctx.findings if f.adapter_error_cause]
    if not failed_findings:
        return []

    lines = [
        "WARNING: adapter failure(s) caused the following checks to be left as TODO:",
    ]
    for finding in failed_findings:
        causes = ", ".join(finding.adapter_error_cause)
        title = finding.title
        lines.append(f"  - {finding.id} {title} (adapter(s) failed: {causes})")
    lines.append("  Review the TODO lines marked with NOTE: in the draft and follow up manually.")
    return lines


def _render_llm_usage_report(ctx) -> list[str]:
    """Render a usage report showing LLM model calls and token consumption."""
    lines: list[str] = [
        "",
        "[LLM Usage Report]",
    ]

    # Get usage data (may be empty if no LLM calls were made)
    calls_by_model = getattr(ctx, "llm_calls_by_model", {})
    tokens_by_model = getattr(ctx, "llm_estimated_tokens", {})

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
