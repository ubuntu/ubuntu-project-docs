"""Minimal renderer for auto-mir structured outputs."""

from __future__ import annotations

import json
from pathlib import Path


def write_outputs(ctx) -> None:
    """Write the first structured outputs for a run.

    This is intentionally minimal: it produces a machine-readable report and a
    reviewer-facing draft that only contains validated statements or explicit
    TODO lines.
    """
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
    _lint_review_draft(draft)

    ctx.review_draft_path = ctx.output_dir / "review-draft.txt"
    ctx.review_draft_path.write_text(draft, encoding="utf-8")


def _build_review_draft(ctx) -> str:
    lines = [
        f"Source package: {ctx.source_package}",
        f"Launchpad bug: {ctx.bug_id}",
        f"Target series: {ctx.series or 'TBD'}",
        "",
        "Validated summary:",
    ]

    for finding in ctx.findings:
        if finding["status"] == "ok":
            lines.append(finding["message"])

    lines.extend([
        "",
        "Outstanding work:",
    ])

    pending = [finding for finding in ctx.findings if finding["status"] != "ok"]
    for finding in pending:
        lines.append(f"TODO: {finding['id']} {finding['title']}")

    return "\n".join(lines) + "\n"


def _lint_review_draft(draft: str) -> None:
    for line in draft.splitlines():
        if line.startswith("RULE:") or line.startswith("RULE "):
            raise ValueError("Review draft still contains RULE lines")