"""Reporter draft and structured artifact rendering."""

from __future__ import annotations

import json
from dataclasses import asdict

from reporter.models import ReadinessEffect, StatementResult, StatementState


def write_outputs(ctx, results: list[StatementResult]) -> None:
    """Write the reporter draft and role-versioned structured report."""
    by_id = {result.id: result for result in results}
    draft = _build_draft(ctx, by_id)
    _lint_draft(draft, ctx.catalog, by_id)

    ctx.reporter_draft_path = ctx.output_dir / "reporter-draft.txt"
    ctx.reporter_draft_path.write_text(ctx.secret_redactor.redact_text(draft), encoding="utf-8")

    readiness = _readiness_summary(results, getattr(ctx, "consistency_report", None))
    report = {
        "schema_version": 1,
        "role": "report",
        "source_package": ctx.source_package,
        "series": ctx.series,
        "guest_name": ctx.guest_name,
        "readiness": readiness,
        "consistency": asdict(ctx.consistency_report)
        if getattr(ctx, "consistency_report", None)
        else None,
        "statements": [asdict(result) for result in results],
        "catalog_summary": ctx.evidence.get("catalog_summary", {}),
        "collection_summary": ctx.evidence.get("collection_summary", {}),
        "llm_usage": {
            "calls_by_model": getattr(ctx, "llm_calls_by_model", {}),
            "estimated_tokens": getattr(ctx, "llm_estimated_tokens", {}),
        },
    }
    ctx.report_path = ctx.output_dir / "report.json"
    with ctx.report_path.open("w", encoding="utf-8") as handle:
        json.dump(ctx.secret_redactor.sanitize(report), handle, indent=2, default=str)


def _with_hanging_indent(text: str) -> str:
    """Indent continuation lines of multi-line text under a leading bullet.

    Human free-text answers, AI/consistency corrections, and multi-select
    catalog statements can span multiple lines. Without this, the second and
    later lines start flush-left, breaking the visual "- one bullet per
    statement" shape the draft otherwise keeps.
    """
    lines = text.split("\n")
    if len(lines) == 1:
        return text
    return "\n".join([lines[0], *(f"  {line}" if line else line for line in lines[1:])])


def _build_draft(ctx, by_id: dict[str, StatementResult]) -> str:
    lines = [
        f"MIR report for source package: {ctx.source_package}",
        f"Target series: {ctx.series}",
        "",
    ]
    for entry in ctx.catalog["metadata"]["reporter_template_blueprint"]:
        if isinstance(entry, str):
            if entry.startswith("RULE:"):
                continue
            lines.append(entry)
            continue
        result = by_id[entry["item"]]
        if result.state == StatementState.NOT_APPLICABLE:
            continue
        if result.state == StatementState.RESOLVED:
            lines.append(_with_hanging_indent(result.statement))
            if result.rationale:
                lines.append(f"  ({_with_hanging_indent(result.rationale)})")
        else:
            lines.append(_with_hanging_indent(result.statement))
            if result.rationale:
                lines.append(f"  (Unavailable: {_with_hanging_indent(result.rationale)})")

    readiness = _readiness_summary(list(by_id.values()), getattr(ctx, "consistency_report", None))
    lines.extend(
        [
            "",
            "[Auto-MIR readiness summary]",
            f"Ready for submission: {'yes' if readiness['ready'] else 'no'}",
            f"Blocking items: {', '.join(readiness['blockers']) or 'none'}",
            f"Warnings: {', '.join(readiness['warnings']) or 'none'}",
            "",
            "This is a draft. Verify every statement and remove remaining "
            "TODO markers before posting.",
        ]
    )
    return "\n".join(lines) + "\n"


def _readiness_summary(results: list[StatementResult], consistency=None) -> dict:
    """Summarize which items still block or warn on submission readiness.

    ``result.readiness`` is the single authoritative signal: deterministic
    evaluators only ever report a non-clear readiness alongside a rationale
    (enforced in ``evaluate_items``), AI-confirmed statements always carry a
    rationale (enforced by the LLM response schema), and human answers now
    carry the catalog item's own declared readiness (or a per-option
    override) once genuinely resolved. No additional "must also have a
    rationale" gate is needed on top of that.
    """
    blockers = sorted(
        result.id for result in results if result.readiness == ReadinessEffect.BLOCKER
    )
    warnings = sorted(
        result.id for result in results if result.readiness == ReadinessEffect.WARNING
    )
    unresolved = sorted(
        result.id
        for result in results
        if result.state in {StatementState.NEEDS_INPUT, StatementState.UNAVAILABLE}
    )
    consistency_blockers = (
        [issue.item_id for issue in consistency.errors] if consistency is not None else []
    )
    blockers = sorted(set(blockers) | set(consistency_blockers))
    return {
        "ready": not blockers and not unresolved and (consistency is None or consistency.ready),
        "blockers": blockers,
        "warnings": warnings,
        "unresolved": unresolved,
    }


def _lint_draft(draft: str, catalog: dict, by_id: dict[str, StatementResult]) -> None:
    """Reject structurally incomplete or falsely-ready reporter output."""
    for marker in catalog["metadata"]["section_markers"]:
        if draft.count(marker) != 1:
            raise ValueError(f"reporter draft must contain section exactly once: {marker}")
    if "RULE:" in draft:
        raise ValueError("reporter runtime draft must not contain RULE lines")
    for item in catalog["items"]:
        if item["id"] not in by_id:
            raise ValueError(f"reporter draft missing result: {item['id']}")
    for result in by_id.values():
        if result.state == StatementState.RESOLVED and result.statement.startswith("TODO"):
            raise ValueError(f"resolved reporter statement still starts with TODO: {result.id}")
