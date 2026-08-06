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
    body_lines: list[str] = []
    for entry in ctx.catalog["metadata"]["reporter_template_blueprint"]:
        if isinstance(entry, str):
            if entry.startswith("RULE:"):
                continue
            body_lines.append(entry)
            continue
        result = by_id[entry["item"]]
        if result.state == StatementState.NOT_APPLICABLE:
            continue
        if result.state == StatementState.RESOLVED:
            body_lines.append(_with_hanging_indent(result.statement))
            if result.rationale:
                body_lines.append(f"  ({_with_hanging_indent(result.rationale)})")
        else:
            body_lines.append(_with_hanging_indent(result.statement))
            if result.rationale:
                body_lines.append(f"  (Unavailable: {_with_hanging_indent(result.rationale)})")

    readiness = _readiness_summary(list(by_id.values()), getattr(ctx, "consistency_report", None))
    lines = [
        f"MIR report for source package: {ctx.source_package}",
        f"Target series: {ctx.series}",
        "",
        *_render_readiness_summary(ctx, readiness),
        *body_lines,
    ]
    return "\n".join(lines) + "\n"


def _render_readiness_summary(ctx, readiness: dict) -> list[str]:
    """Render the readiness summary block shown at the very top of the draft.

    Placed first (with a full-width separator marking where it ends) so the
    reporter sees "am I close to done" before the section-by-section detail,
    and each listed item is labelled by its section/title, not a bare
    catalog id, so it is meaningful without cross-referencing the catalog.
    """
    labels = {
        f"{item['id']}": f"{item['section']} / {item['title']}" for item in ctx.catalog["items"]
    }

    def _labelled(item_ids: list[str]) -> list[str]:
        if not item_ids:
            return ["  none"]
        return [f"  {item_id} -- {labels.get(item_id, '')}" for item_id in item_ids]

    separator = "=" * 70
    return [
        "[Auto-MIR readiness summary]",
        f"Ready for submission: {'yes' if readiness['ready'] else 'no'}",
        "Remaining TODOs (must resolve before submission):",
        *_labelled(readiness["blockers"]),
        "Remaining TODOs (recommended, non-blocking):",
        *_labelled(readiness["warnings"]),
        "",
        "This is a draft. Verify every statement and remove remaining TODO markers before posting.",
        separator,
        "",
    ]


def _readiness_summary(results: list[StatementResult], consistency=None) -> dict:
    """Summarize which items still block or warn on submission readiness.

    When a consistency report is available (the normal case: every real run
    calls ``run_consistency_pass``), it is the single authoritative source
    for "Blocking"/"Warning" -- it already reflects each item's *final*
    resolution state (deterministic placeholder/unresolved detection plus
    any AI-detected contradictions), not just its static catalog-declared
    readiness. This is what keeps the summary from re-listing items the
    reporter already fully answered.

    Without a consistency report (only synthetic/unit-test setups that skip
    the consistency pass), this falls back to the coarser catalog-declared
    ``readiness`` sweep so those callers keep working unchanged.
    """
    unresolved = sorted(
        result.id
        for result in results
        if result.state in {StatementState.NEEDS_INPUT, StatementState.UNAVAILABLE}
    )
    if consistency is not None:
        blockers = sorted({issue.item_id for issue in consistency.errors})
        warnings = sorted({issue.item_id for issue in consistency.warnings} - set(blockers))
        ready = consistency.ready
    else:
        blockers = sorted(
            result.id for result in results if result.readiness == ReadinessEffect.BLOCKER
        )
        warnings = sorted(
            result.id for result in results if result.readiness == ReadinessEffect.WARNING
        )
        ready = not blockers and not unresolved
    return {
        "ready": ready,
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
