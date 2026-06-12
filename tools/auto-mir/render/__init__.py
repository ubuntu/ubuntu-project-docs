"""Renderer for auto-mir structured outputs.

The review draft mirrors the structure of docs/MIR/mir-reviewers-template.md:
each template section becomes a labelled block with an OK: sub-block for
resolved checks and a Problems: sub-block for outstanding TODO items.
This keeps the draft directly usable as a starting point for the human
reviewer to paste into the Launchpad bug.
"""
from __future__ import annotations

import json
from collections import defaultdict


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
    report = {
        "bug_id": ctx.bug_id,
        "source_package": ctx.source_package,
        "series": ctx.series,
        "container_name": ctx.container_name,
        "policy_hashes": ctx.policy_hashes,
        "catalog_summary": ctx.evidence.get("catalog_summary", {}),
        "analysis_summary": ctx.evidence.get("analysis_summary", {}),
        "findings": ctx.findings,
    }

    ctx.report_path = ctx.output_dir / "report.json"
    with ctx.report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)

    draft = _build_review_draft(ctx)
    _lint_review_draft(draft, ctx.findings)

    ctx.review_draft_path = ctx.output_dir / "review-draft.txt"
    ctx.review_draft_path.write_text(draft, encoding="utf-8")


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
        lines += _render_section(section, findings_in_section)
        lines.append("")  # blank line between sections

    return "\n".join(lines)


def _render_section(section: str, findings: list[dict]) -> list[str]:
    """Render a single [Section] block."""
    lines: list[str] = [f"[{section}]"]

    ok_findings = [f for f in findings if f["status"] == "ok"]
    problem_findings = [f for f in findings if f["status"] != "ok"]

    # OK sub-block
    if ok_findings:
        lines.append("OK:")
        for finding in ok_findings:
            msg = (finding.get("message") or "").strip()
            if msg:
                lines.append(f"- {msg}")

    # Problems sub-block
    if problem_findings:
        lines.append("Problems:")
        for finding in problem_findings:
            todo = (finding.get("todo") or "").strip()
            if not todo.startswith("TODO:"):
                todo = f"TODO: {finding['id']} {finding['title']}"
            lines.append(f"- {todo}")
    else:
        lines.append("Problems: None")

    return lines


# ---------------------------------------------------------------------------
# Linter
# ---------------------------------------------------------------------------

def _lint_review_draft(draft: str, findings: list[dict]) -> None:
    """Validate the rendered draft for structural correctness.

    Rules enforced:
    - No RULE: lines (template directives must never reach the output)
    - Lines inside a Problems: block must start with "- TODO:" or be blank
    - Resolved (ok) findings must not produce a TODO message
    - Unresolved findings must carry a TODO string
    """
    in_problems_block = False
    for line in draft.splitlines():
        # No raw RULE lines allowed
        if line.startswith("RULE:") or line.startswith("RULE "):
            raise ValueError("Review draft still contains RULE lines")

        # Track section / sub-section transitions
        if line.startswith("[") and line.endswith("]"):
            in_problems_block = False
            continue
        if line == "Problems:":
            in_problems_block = True
            continue
        if line.startswith("Problems: ") or line in ("OK:", ""):
            in_problems_block = False
            continue

        # Every content line inside a Problems: block must be a TODO entry
        if in_problems_block and line:
            if not line.startswith("- TODO:"):
                raise ValueError(
                    f"Problems block line must start with '- TODO:': {line!r}"
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
        if status != "ok" and not todo.startswith("TODO:"):
            raise ValueError(
                f"Unresolved finding {finding.get('id')} must include TODO"
            )