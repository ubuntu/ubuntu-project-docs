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

    readiness = _readiness_summary(results)
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


def _build_draft(ctx, by_id: dict[str, StatementResult]) -> str:
    lines = [
        f"MIR report for source package: {ctx.source_package}",
        f"Target series: {ctx.series}",
        "",
    ]
    for entry in ctx.catalog["metadata"]["reporter_template_blueprint"]:
        if isinstance(entry, str):
            lines.append(entry)
            continue
        result = by_id[entry["item"]]
        if result.state == StatementState.NOT_APPLICABLE:
            continue
        if result.state == StatementState.RESOLVED:
            lines.append(result.statement)
            if result.rationale:
                lines.append(f"  ({result.rationale})")
        else:
            lines.append(result.statement)
            if result.rationale:
                lines.append(f"  (Unavailable: {result.rationale})")

    readiness = _readiness_summary(list(by_id.values()))
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


def _readiness_summary(results: list[StatementResult]) -> dict:
    blockers = sorted(
        result.id
        for result in results
        if result.readiness == ReadinessEffect.BLOCKER
        and (result.state != StatementState.RESOLVED or result.rationale)
    )
    warnings = sorted(
        result.id
        for result in results
        if result.readiness == ReadinessEffect.WARNING
        and (result.state != StatementState.RESOLVED or result.rationale)
    )
    unresolved = sorted(
        result.id
        for result in results
        if result.state in {StatementState.NEEDS_INPUT, StatementState.UNAVAILABLE}
    )
    return {
        "ready": not blockers and not unresolved,
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
