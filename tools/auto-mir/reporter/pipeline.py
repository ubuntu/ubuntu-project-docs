"""Source-package-based MIR reporter pipeline stages."""

from __future__ import annotations

import logging

from reporter.consistency import run_consistency_pass
from reporter.evaluator import evaluate_items
from reporter.render import write_outputs
from reporter.wizard import TerminalWizard

log = logging.getLogger("auto_mir.reporter")


def intake(ctx, wizard: TerminalWizard) -> None:
    """Validate basic reporter input and resolve the target series."""
    source = ctx.source_package.strip()
    if not source or source != source.casefold():
        raise ValueError("source package must be a non-empty lowercase name")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789+.-")
    if source[0] not in allowed or any(character not in allowed for character in source):
        raise ValueError(f"invalid Ubuntu source package name: {source}")

    if not ctx.series:
        ctx.series = "devel"
        log.info("No --series supplied for reporter mode; using development release (devel)")
    log.info("Reporter intake: source=%s series=%s", ctx.source_package, ctx.series)


def analyse(ctx, wizard: TerminalWizard) -> None:
    """Evaluate all report-catalog items and retain their typed results."""
    ctx.statement_results = evaluate_items(ctx, wizard)
    ctx.consistency_report = run_consistency_pass(ctx, wizard)
    ctx.evidence["analysis_summary"] = {
        "total_items": len(ctx.statement_results),
        "resolved_items": sum(result.state == "resolved" for result in ctx.statement_results),
        "unavailable_items": sum(result.state == "unavailable" for result in ctx.statement_results),
        "consistency_ready": ctx.consistency_report.ready,
    }


def render(ctx) -> None:
    """Write draft and structured reporter artifacts."""
    write_outputs(ctx, ctx.statement_results)
