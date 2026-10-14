"""Reporter draft and structured artifact rendering."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict

from catalog import classify_blueprint_entry
from reporter.models import ReadinessEffect, StatementResult, StatementState
from reporter.text_utils import substitute_source

log = logging.getLogger("auto_mir.reporter")

# Heading of the per-section block collecting everything the run could not
# resolve confidently. Rendered by ``_build_draft``; an unresolved "TBD" is
# legitimate only inside this block, which is enforced at result creation
# (see ``reporter.text_utils.statement_left_open``), so it exists exactly
# once.
_CLARIFY_HEADING = "Left to clarify:"


class DraftLintFailed(RuntimeError):
    """Raised after a draft that failed lint was written, so the run fails loudly.

    The artifacts are always written first (see ``write_outputs``): the
    reporter's session must never be destroyed by a write-time lint
    rejection - the run exits non-zero and the structured report records
    the violations for recovery.
    """

    def __init__(self, violations: list[str]) -> None:
        self.violations = list(violations)
        summary = "; ".join(violations)
        super().__init__(
            "reporter draft failed lint validation; the draft and report were written "
            f"but need correction before submission: {summary}"
        )


# States that contribute no line of their own to the draft: an item ruled out
# by its applicability condition, and one whose text was folded into another
# item's statement (catalog ``completes``).
_SILENT_STATES = {StatementState.NOT_APPLICABLE, StatementState.MERGED}


def write_outputs(ctx, results: list[StatementResult]) -> None:
    """Write the reporter draft and role-versioned structured report.

    A lint failure is deliberately not a crash: both artifacts are written
    (the session's answers are never destroyed by a write-time
    rejection), readiness is forced to not-ready, the violations are
    recorded in the structured report, and ``DraftLintFailed`` is raised
    afterwards so the run still exits non-zero with a clear message.
    """
    by_id = {result.id: result for result in results}
    draft = _build_draft(ctx, by_id)
    violations = _lint_draft(draft, ctx.catalog, by_id)

    ctx.reporter_draft_path = ctx.output_dir / "reporter-draft.txt"
    ctx.reporter_draft_path.write_text(ctx.secret_redactor.redact_text(draft), encoding="utf-8")

    readiness = _readiness_summary(results, getattr(ctx, "consistency_report", None))
    if violations:
        readiness = {**readiness, "ready": False, "lint_violations": violations}
        for violation in violations:
            log.error("Draft lint violation: %s", violation)
    for line in readiness_console_lines(ctx, readiness):
        log.info(line)
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
    if violations:
        raise DraftLintFailed(violations)


def _with_hanging_indent(text: str) -> str:
    """Indent continuation lines of multi-line text under a leading bullet.

    Human free-text answers, AI/consistency corrections, and multi-select
    catalog statements can span multiple lines. Without this, the second and
    later lines start flush-left, breaking the visual "- one bullet per
    statement" shape the draft otherwise keeps.

    Runs of consecutive blank continuation lines are collapsed to one
    first: the draft's layout contract says blank lines never double, the
    renderer guarantees that structurally for the separators it inserts
    itself, and a pasted answer carrying a doubled blank line must not be
    able to break the same invariant.
    """
    lines = text.split("\n")
    if len(lines) == 1:
        return text
    continuation: list[str] = []
    for line in lines[1:]:
        if not line.strip() and continuation and not continuation[-1].strip():
            continue
        continuation.append(line)
    return "\n".join([lines[0], *(f"  {line}" if line else line for line in continuation)])


def _build_draft(ctx, by_id: dict[str, StatementResult]) -> str:
    """Render the blueprint into confident bullets plus, per section, one
    grouped "Left to clarify:" block for anything the tool could not resolve
    with confidence (an ``ev_to_ai`` item that fell back to a deferred human
    answer, or a ``deterministic`` item whose required evidence was
    unavailable) - never mixed inline with the assertive resolved statements,
    and never a bare, still-unresolved "TBD" template masquerading as a real
    statement (see ``_clarify_entry_lines``).

    Layout is derived structurally, not copied from the blueprint: the
    blueprint decides section membership and statement ORDER, this function
    decides spacing. Blueprint ``''`` separators are deliberately ignored,
    because they mark gaps between template prose the runtime draft does not
    emit at all (``RULE``/``TODO`` lines, not-applicable items, items moved
    into the clarify block) - reproducing them verbatim is what produced runs
    of stray blank lines, and appending a section's unreferenced results
    after such a separator is what swallowed the blank line before the next
    ``[Section]`` header.
    """
    items_by_id = {item["id"]: item for item in ctx.catalog["items"]}
    blueprint = ctx.catalog["metadata"]["reporter_template_blueprint"]
    referenced = {entry["item"] for entry in blueprint if isinstance(entry, dict)}
    extras: dict[str, list[StatementResult]] = {}
    for item in ctx.catalog["items"]:
        if item["id"] in referenced:
            continue
        result = by_id[item["id"]]
        if result.state in _SILENT_STATES:
            continue
        extras.setdefault(result.section, []).append(result)

    sections = _sections_from_blueprint(blueprint, by_id)
    body_lines: list[str] = []
    for header, results in sections:
        results = [*results, *extras.pop(header[1:-1], [])]
        resolved = [
            result
            for result in results
            if result.state not in {StatementState.NEEDS_INPUT, StatementState.UNAVAILABLE}
        ]
        unresolved = [
            result
            for result in results
            if result.state in {StatementState.NEEDS_INPUT, StatementState.UNAVAILABLE}
        ]
        if body_lines:
            body_lines.append("")
        body_lines.append(header)
        for result in resolved:
            body_lines.extend(_statement_lines(result))
        if unresolved:
            body_lines.append("")
            body_lines.append(_CLARIFY_HEADING)
            for result in unresolved:
                body_lines.extend(_clarify_entry_lines(items_by_id[result.id], result, ctx))

    lines = [
        f"MIR report for source package: {ctx.source_package}",
        f"Target series: {ctx.series}",
        "",
        *body_lines,
    ]
    return "\n".join(lines) + "\n"


def _sections_from_blueprint(
    blueprint: list, by_id: dict[str, StatementResult]
) -> list[tuple[str, list[StatementResult]]]:
    """Group blueprint-referenced results under their ``[Section]`` header.

    Only ``section`` and ``item`` entries carry runtime meaning; ``rule`` and
    ``todo`` prose stays in the human template (the generated docs include),
    and ``blank`` separators are spacing this renderer derives itself.
    """
    sections: list[tuple[str, list[StatementResult]]] = []
    for entry in blueprint:
        kind = classify_blueprint_entry(entry)
        if kind == "section":
            sections.append((str(entry).strip(), []))
            continue
        if kind != "item" or not sections:
            continue
        result = by_id[entry["item"]]
        if result.state in _SILENT_STATES:
            continue
        sections[-1][1].append(result)
    return sections


def _statement_lines(result: StatementResult) -> list[str]:
    """Render one resolved statement plus its optional parenthetical note."""
    lines = [_with_hanging_indent(result.statement)]
    if result.rationale:
        lines.append(f"  ({_with_hanging_indent(result.rationale)})")
    return lines


def _clarify_entry_lines(item: dict, result: StatementResult, ctx) -> list[str]:
    """Render one unresolved item under "Left to clarify:", preserving as much
    of its original catalog RULE/TODO context as possible instead of a bare
    "TBD" placeholder or a silently-dropped topic.

    An entry that already carries text - a deterministic finding the
    reporter still has to act on (see ``reporter.evaluator.Assessment``), or
    a statement the reporter left a ``TBD`` in - is shown as that text plus
    its parenthetical, so nothing the run established or the reporter wrote
    is thrown away.

    Otherwise the item was never resolved at all, and the closest available
    original context is used. For an options-based item (see
    ``reporter.ai``'s ``ev_to_ai`` + options support), every option's own
    ``todo_ref`` line is listed as a TODO-lettered alternative, exactly
    mirroring the original human template structure (e.g. "TODO-A: ..." /
    "TODO-C: ..."). For a plain free-text item, the catalog's own
    ``template`` TODO line is shown instead, even though it still literally
    contains "TBD" (that is expected and fine inside a "Left to clarify:"
    block, unlike inside a resolved statement, which ``_lint_draft`` still
    forbids).
    """
    if result.statement:
        lines = [_with_hanging_indent(result.statement)]
        if result.rationale:
            lines.append(f"  ({_with_hanging_indent(result.rationale)})")
        return lines

    intro = str(item.get("question", {}).get("prompt") or item.get("title") or item["id"])
    lines = [f"- {intro}"]
    options = item.get("question", {}).get("options", [])
    todo_refs = [
        substitute_source(str(option.get("todo_ref", "")).strip(), ctx.source_package)
        for option in options
        if str(option.get("todo_ref", "")).strip()
    ]
    if todo_refs:
        lines.extend(f"  {todo_ref}" for todo_ref in todo_refs)
    else:
        template_line = substitute_source(str(item.get("template", "")), ctx.source_package).strip()
        if template_line:
            lines.append(f"  {template_line}")
    if result.rationale:
        lines.append(f"  (Reason: {_with_hanging_indent(result.rationale)})")
    return lines


def _labelled_items(ctx, item_ids: list[str]) -> list[str]:
    """Render catalog item ids as ``id -- section / title`` lines.

    Falls back to "  none" for an empty list so the console block always has
    a visible line under each heading.
    """
    if not item_ids:
        return ["  none"]
    labels = {
        f"{item['id']}": f"{item['section']} / {item['title']}" for item in ctx.catalog["items"]
    }
    return [f"  {item_id} -- {labels.get(item_id, '')}" for item_id in item_ids]


def readiness_console_lines(ctx, readiness: dict) -> list[str]:
    """Render the console/log-only readiness summary for report mode.

    This intentionally never becomes part of ``reporter-draft.txt``: a
    submitter who copy-pastes the whole draft to Launchpad should not risk
    accidentally posting a stale "Ready for submission" line. It also
    intentionally omits the "recommended, non-blocking" TODOs -- those are,
    in practice, almost always already resolved by the time the reporter
    finishes the interactive session, and any genuinely unresolved one is
    still easy to spot in the draft itself (it stays a bare "TODO: -"
    line), so repeating a large, frequently-stale list here does more harm
    (noise, false sense of remaining work) than good.
    """
    return [
        "[Auto-MIR readiness summary]",
        f"Ready for submission: {'yes' if readiness['ready'] else 'no'}",
        "Remaining TODOs (must resolve before submission):",
        *_labelled_items(ctx, readiness["blockers"]),
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


def _lint_draft(draft: str, catalog: dict, by_id: dict[str, StatementResult]) -> list[str]:
    """Return every violation of the draft's structural contract.

    The lint only judges what the renderer itself controls: each known
    ``[Section]`` header appears exactly once (by whole-line equality, so
    content merely *mentioning* a marker cannot trip it), every catalog
    item has a result, no resolved statement still starts with an
    unfilled template marker, and the blank-line layout holds.

    Everything else in the draft is *content* - human answers, AI
    suggestions, and their rationales - and is deliberately not judged by
    line shape. Content cannot be told from template scaffolding by its
    text (a reporter may legitimately write a line that looks like
    ``[Section]``, ``RULE:``, or a raw ``TBD``), and shape-checking it is
    what aborted a fully answered session at write time (feedback item
    4). Content is guarded where it is created instead:
    ``reporter.text_utils.statement_left_open`` routes any statement or
    rationale still carrying ``TBD`` to ``Left to clarify:``, and
    ``consistency.validate_results`` flags whatever slips through.
    """
    violations: list[str] = []
    lines = draft.splitlines()
    for marker in catalog["metadata"]["section_markers"]:
        count = sum(1 for line in lines if line.strip() == marker)
        if count != 1:
            violations.append(
                f"reporter draft must contain section exactly once: {marker} (found {count})"
            )
    for item in catalog["items"]:
        if item["id"] not in by_id:
            violations.append(f"reporter draft missing result: {item['id']}")
    for result in by_id.values():
        if result.state == StatementState.RESOLVED and result.statement.startswith("TODO"):
            violations.append(f"resolved reporter statement still starts with TODO: {result.id}")
    violations.extend(_lint_draft_layout(draft, catalog["metadata"]["section_markers"]))
    return violations


def _lint_draft_layout(draft: str, section_markers: list[str]) -> list[str]:
    """Enforce the renderer-controlled visual contract line by line.

    A line counts as a section header only when its whole (stripped) text
    equals a known section marker - not when it merely has the ``[...]``
    shape, which free-text answers can legitimately produce. The
    blank-line rules apply to every line because the renderer guarantees
    them by construction: ``_build_draft`` inserts exactly the structural
    separators, and ``_with_hanging_indent`` collapses blank runs inside
    statement content.
    """
    violations: list[str] = []
    lines = draft.splitlines()
    markers = set(section_markers)
    for index, line in enumerate(lines):
        if line.strip() in markers:
            if index and lines[index - 1].strip():
                violations.append(f"reporter draft needs a blank line before section: {line!r}")
        elif not line.strip():
            if index and not lines[index - 1].strip():
                violations.append(f"reporter draft has consecutive blank lines at line {index + 1}")
    if lines and not lines[-1].strip():
        violations.append("reporter draft must not end with a blank line")
    return violations
