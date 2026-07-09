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
import re
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
        "llm_reasoning_traces": getattr(ctx, "llm_reasoning_traces", []),
    }

    ctx.report_path = ctx.output_dir / "report.json"
    with ctx.report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)

    draft = _build_review_draft(ctx)
    _lint_review_draft(draft, ctx.findings)

    ctx.review_draft_path = ctx.output_dir / "review-draft.txt"
    ctx.review_draft_path.write_text(draft, encoding="utf-8")

    # Print adapter failure warning to console so degraded checks are obvious.
    # The LLM usage report is printed later, just before the completion banner,
    # so it appears together with the final artifact list (see auto_mir.py).
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

    # Surface which upload was actually fetched, built and analysed, and from
    # which pocket, so the reviewer knows whether a staged -proposed version was
    # used rather than the release-pocket one.
    version_line = _build_analysed_version_line(ctx)
    if version_line:
        lines.append(version_line)

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
    checks_by_id = _checks_by_id(ctx)
    for section in known + remainder:
        if section not in by_section:
            continue
        findings_in_section = by_section[section]
        if section == "Summary":
            lines += _render_summary_section(findings_in_section, ctx.findings, ctx, checks_by_id)
        else:
            lines += _render_section(section, findings_in_section, checks_by_id)
        lines.append("")  # blank line between sections

    return "\n".join(lines)


def _build_analysed_version_line(ctx) -> str:
    """Return the 'Analysed source version' preamble line, or '' when unknown.

    Reads the version actually unpacked and the pocket it came from
    (packaging-source), degrading gracefully when the adapter did not run.
    """
    packaging = ctx.evidence.get("adapters", {}).get("packaging-source", {})
    if not isinstance(packaging, dict):
        return ""
    version = str(packaging.get("analyzed_version", "") or "").strip()
    pocket = str(packaging.get("analyzed_pocket", "") or "").strip()
    if not version:
        return ""
    if pocket:
        return f"Analysed source version: {version} ({pocket} pocket)"
    return f"Analysed source version: {version}"


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
            "Binary packages (promotion candidates only): "
            f"{', '.join(sorted(promotion_candidates))}"
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


def finding_outcome_class(finding: Finding) -> str:
    """Classify a finding into one of the three reviewer-facing paths.

    Returns one of:
      - "ok":        the check is satisfied (status == "ok").
      - "problem":   a confident failure — a deterministic not-ok, or an
                     AI not-ok the model reported with high confidence. These
                     are shown under Problems: and surfaced as Required/
                     Recommended TODOs in the Summary.
      - "undecided": everything else (unknown status, or an AI failure below
                     high confidence). These are shown under Left to decide:
                     only and never duplicated into the Summary TODOs.
    """
    if finding.status == "ok":
        return "ok"
    if finding.status == "not-ok" and (
        finding.mode == "deterministic" or finding.confidence == "high"
    ):
        return "problem"
    return "undecided"


def _is_high_confidence_failure(finding: Finding) -> bool:
    """Return True when a not-ok finding is a confident (Problems-worthy) failure."""
    return finding_outcome_class(finding) == "problem"


def _checks_by_id(ctx) -> dict[str, dict]:
    """Return a {check_id: check_definition} map from the run catalog.

    Used by the renderer to look up per-check statement variants (the
    affirmative template statement and its ``negated_statement``) so problem
    and undecided lines can be phrased correctly and carry their rationale.
    """
    catalog = getattr(ctx, "catalog", None)
    if not isinstance(catalog, dict):
        return {}
    return {c["id"]: c for c in catalog.get("checks", []) if isinstance(c, dict) and c.get("id")}


def _affirmative_statement(check: dict | None) -> str | None:
    """Return the single canonical affirmative statement for a check, or None.

    Applies only to single-statement checks (exactly one non-placeholder
    todo_ref, no options, not a Summary decision check). Option and Summary
    checks keep their own message/todo wording.
    """
    if not check or check.get("options") or check.get("section") == "Summary":
        return None
    todo_refs = [str(x).strip() for x in check.get("todo_refs", []) if str(x).strip()]
    if len(todo_refs) != 1:
        return None
    statement = _strip_todo_prefix(todo_refs[0])
    if not statement or "TBD" in statement or "<" in statement:
        return None
    return statement


def _negated_statement(check: dict | None) -> str | None:
    """Return the catalog-provided negated statement for a check, or None.

    Negation is stored explicitly in the catalog (``negated_statement``) rather
    than rewritten on the fly, so a problem is phrased as the reviewer expects
    (e.g. "does FTBFS currently") instead of the pass-oriented template line.
    """
    if not check:
        return None
    negated = check.get("negated_statement")
    if isinstance(negated, str) and negated.strip():
        return negated.strip()
    return None


def _with_rationale(statement: str, rationale: str, *, cant_decide: bool = False) -> str:
    """Append a rationale as an indented parenthetical continuation line.

    Keeps the statement on its own line and the reasoning/evidence on an
    indented follow-up line, matching how a human reviewer annotates the draft.
    """
    statement = statement.rstrip()
    rationale = (rationale or "").strip()
    if not rationale:
        return statement
    prefix = "Can't decide: " if cant_decide else ""
    return f"{statement}\n  ({prefix}{rationale})"


def _problem_line(finding: Finding, check: dict | None) -> str:
    """Compose a Problems: line: the negated statement plus its rationale.

    When the catalog provides a negated statement it is used (with the
    finding's rationale/evidence in parentheses). Otherwise the finding's own
    message is used verbatim, since deterministic checks phrase their message
    as the evidence statement directly.
    """
    negated = _negated_statement(check)
    if negated:
        return "- " + _with_rationale(negated, finding.rationale or finding.message)
    rationale = (
        finding.rationale if finding.rationale and finding.rationale != finding.message else ""
    )
    return "- " + _with_rationale(finding.message, rationale)


def _ok_line(finding: Finding) -> str:
    """Compose an OK: line: the affirmative statement plus its rationale."""
    return "- " + _with_rationale(finding.message, finding.rationale)


def _render_section(
    section: str, findings: list[Finding], checks_by_id: dict[str, dict] | None = None
) -> list[str]:
    """Render a standard [Section] block with the three-tier structure.

    OK:              resolved checks
    Problems:        high-confidence / deterministic failures
    Left to decide:  low/medium-confidence or unresolvable items (as TODO lines)
    """
    checks_by_id = checks_by_id or {}
    lines: list[str] = [f"[{section}]"]

    ok_findings = [f for f in findings if f.status == "ok"]
    not_ok = [f for f in findings if f.status != "ok"]
    problems = [f for f in not_ok if _is_high_confidence_failure(f)]
    undecided = [f for f in not_ok if not _is_high_confidence_failure(f)]

    # OK sub-block — de-duplicate identical statements (e.g. "not a go package"
    # repeated per check). De-dup keys on the statement (message) so findings
    # that share a statement but differ in rationale still collapse to one line.
    if ok_findings:
        lines.append("OK:")
        seen_msgs: set[str] = set()
        for finding in ok_findings:
            msg = (finding.message or "").strip()
            if msg and msg not in seen_msgs:
                lines.append(_ok_line(finding))
                seen_msgs.add(msg)

    # Left to decide sub-block — only rendered when there is something to
    # decide. An empty "Left to decide" carries no meaning (unlike
    # "Problems: none", which asserts the checks ran and found nothing), so it
    # is omitted entirely when there are no undecided items.
    if undecided:
        lines.append("Left to decide:")
        for finding in undecided:
            causes = finding.adapter_error_cause
            if causes:
                lines.append(
                    f"NOTE: - left for manual follow-up; adapter(s) failed: {', '.join(causes)}"
                )
            todo_block = "\n".join(_todo_lines_for_finding(finding))
            if finding.rationale:
                todo_block = _with_rationale(todo_block, finding.rationale, cant_decide=True)
            lines.append(todo_block)

    # Problems sub-block — always rendered last, separated by a blank line, so a
    # clean section explicitly states "Problems: none" rather than silently
    # omitting any problem status.
    lines.append("")
    if problems:
        lines.append("Problems:")
        for finding in problems:
            check = checks_by_id.get(finding.id)
            lines.append(_problem_line(finding, check))
    else:
        lines.append("Problems: none")

    return lines


def _render_summary_section(
    summary_findings: list[Finding],
    all_findings: list[Finding],
    ctx,
    checks_by_id: dict[str, dict] | None = None,
) -> list[str]:
    """Render [Summary] with special MIR template semantics.

    - Keep resolved summary checks under OK:
    - Do not emit a "Problems:" block here.
    - Keep unresolved summary decision checks visible for reviewer choice.
    - Always include Required TODOs: and Recommended TODOs: blocks.
    - Findings flagged aggregate_todo (e.g. the team-subscriber gate) render
      their OK statement here but route their TODO to the consolidated blocks
      rather than the inline "Left to decide" list.
    - Include out-of-scope dependency hints as informational notes.
    """
    checks_by_id = checks_by_id or {}
    lines: list[str] = ["[Summary]"]

    ok_findings = [f for f in summary_findings if f.status == "ok"]
    # Decision checks (ACK/NACK verdict, security review) stay inline under
    # "Left to decide". aggregate_todo findings are forwarded to the consolidated
    # Required/Recommended blocks instead, so exclude them here to avoid listing
    # them twice.
    unresolved = [f for f in summary_findings if f.status != "ok" and not f.aggregate_todo]

    if ok_findings:
        lines.append("OK:")
        for finding in ok_findings:
            msg = (finding.message or "").strip()
            if msg:
                lines.append(_ok_line(finding))

    # Add out-of-scope dependency hints
    out_of_scope_hints = _build_out_of_scope_dep_hint(ctx)
    if out_of_scope_hints:
        for hint in out_of_scope_hints:
            lines.append(f"- {hint}")

    # Only render "Left to decide" when there is something undecided; an empty
    # block carries no meaning and is omitted (see _render_section).
    if unresolved:
        lines.append("Left to decide:")
        for finding in unresolved:
            causes = finding.adapter_error_cause
            if causes:
                lines.append(
                    f"NOTE: - left for manual follow-up; adapter(s) failed: {', '.join(causes)}"
                )
            todo_block = "\n".join(_todo_lines_for_finding(finding))
            if finding.rationale:
                todo_block = _with_rationale(todo_block, finding.rationale, cant_decide=True)
            lines.append(todo_block)

    lines.append("Required TODOs:")
    required = _collect_todos_by_severity(all_findings, "required", checks_by_id)
    numbered, todo_index = _render_numbered_todos(required, start_index=1)
    lines.extend(numbered)
    lines.append("- TODO: - TBD (Please add more, numbered for later reference)")

    lines.append("Recommended TODOs:")
    recommended = _collect_todos_by_severity(all_findings, "recommended", checks_by_id)
    numbered, todo_index = _render_numbered_todos(recommended, start_index=todo_index)
    lines.extend(numbered)
    lines.append("- TODO: - TBD (Please add more, numbered for later reference)")

    return lines


_TODO_PREFIX_RE = re.compile(r"^\s*(?:TODO(?:-[A-Z])?:\s*)+(?:-\s*)?")


def _strip_todo_prefix(line: str) -> str:
    """Strip leading ``TODO:``/``TODO-X:`` and ``- `` markers, leaving the text."""
    return _TODO_PREFIX_RE.sub("", line).strip()


def _render_numbered_todos(items: list[str], start_index: int) -> tuple[list[str], int]:
    """Render consolidated TODO items as ``- #N <text>`` with a running index.

    The index continues across the Required and Recommended blocks so each item
    has a stable, unique reference number the reviewer can cite. Returns the
    rendered lines and the next free index.
    """
    out: list[str] = []
    index = start_index
    for item in items:
        text = _strip_todo_prefix(item)
        if not text:
            continue
        out.append(f"- #{index} {text}")
        index += 1
    return out, index


def _collect_todos_by_severity(
    findings: list[Finding], severity: str, checks_by_id: dict[str, dict] | None = None
) -> list[str]:
    checks_by_id = checks_by_id or {}
    seen: set[str] = set()
    todos: list[str] = []
    for finding in findings:
        # Summary-section decision checks (ACK/NACK verdict, security review,
        # promotion list) render inline in the [Summary] block. Re-listing them
        # here would duplicate them in the consolidated TODO blocks. Findings
        # explicitly flagged aggregate_todo (e.g. the team-subscriber gate) are
        # the exception: they belong in the consolidated list.
        if finding.section == "Summary" and not finding.aggregate_todo:
            continue
        if finding.status == "ok":
            continue
        # Only confident problems become Required/Recommended TODOs. Undecided
        # items (unknown status, or an AI failure below high confidence) live in
        # their section's "Left to decide" block only and must not be duplicated
        # here. aggregate_todo findings are always forwarded regardless.
        if not finding.aggregate_todo and finding_outcome_class(finding) != "problem":
            continue
        if finding.severity != severity:
            continue
        for text in _summary_todo_texts_for_finding(finding, checks_by_id):
            if text not in seen:
                seen.add(text)
                todos.append(text)
    return todos


def _summary_todo_texts_for_finding(finding: Finding, checks_by_id: dict[str, dict]) -> list[str]:
    """Return consolidated-TODO text(s) for a finding.

    A confident problem with a catalog-provided negated statement is phrased as
    that negated statement plus its rationale (so the reviewer sees, e.g.,
    "does FTBFS currently (…s390x…)" rather than the pass-oriented template
    line). Otherwise the finding's TODO lines are used verbatim.
    """
    check = checks_by_id.get(finding.id)
    negated = _negated_statement(check)
    if negated and finding_outcome_class(finding) == "problem":
        return [_with_rationale(negated, finding.rationale or finding.message)]
    return _todo_lines_for_finding(finding)


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
            # Indented continuation lines carry the rationale parenthetical for
            # the preceding TODO and are exempt from the prefix rule.
            if line[:1] in (" ", "\t"):
                continue
            if not (
                line.startswith("TODO:") or line.startswith("TODO-") or line.startswith("NOTE:")
            ):
                raise ValueError(
                    "Left to decide block line must start with "
                    f"'TODO:', 'TODO-', or 'NOTE:': {line!r}"
                )

        # Problems block lines are confirmed finding statements, not TODOs
        if in_problems_block and line:
            # Indented continuation lines carry the rationale parenthetical.
            if line[:1] in (" ", "\t"):
                continue
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
