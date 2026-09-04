"""Catalog-driven evaluation for MIR reporter statements."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from reporter.ai import evaluate_ai_item
from reporter.conditions import ConditionContext, evaluate_condition
from reporter.models import (
    Provenance,
    QuestionKind,
    QuestionOption,
    QuestionSpec,
    ReadinessEffect,
    StatementResult,
    StatementState,
)
from reporter.text_utils import (
    ensure_bulleted,
    maybe_write_evidence,
    resolve_option_statements,
    substitute_source,
    template_to_statement,
)
from reporter.wizard import TerminalWizard
from utils.deb_facts import built_using_entries

if TYPE_CHECKING:
    from auto_mir import RunContext

log = logging.getLogger("auto_mir.reporter")


@dataclass(frozen=True)
class Assessment:
    """One deterministic evaluator's verdict about a single catalog item.

    ``statement`` is the evidence-derived fact. ``note`` and ``action`` are
    deliberately separate, because they lead to different places in the
    report:

    * ``note`` is context the reader may want but nobody has to act on (for
      example which CVE corpora were queried). The statement stays a
      confident bullet and the note is rendered as its parenthetical.
    * ``action`` means the reporter still owes something before this MIR can
      be submitted (subscribe a team, provide a recent build reference,
      explain a failing test). The statement then moves into the section's
      "Left to clarify:" block together with the action, and the item keeps
      its catalog-declared readiness effect.

    Before this split, any non-empty rationale raised the item's readiness,
    so a purely informational note was indistinguishable from real
    outstanding work.

    ``statement is None`` means the evidence needed to judge this item was
    missing; ``unavailable_reason`` says why.
    """

    statement: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    action: str = ""
    note: str = ""
    unavailable_reason: str = ""

    def rationale(self) -> str:
        """Return action and note joined into one reader-facing sentence."""
        return " ".join(part for part in (self.action, self.note) if part)


Evaluator = Callable[[dict, "RunContext"], Assessment]
_EVALUATORS: dict[str, Evaluator] = {}


def reporter_evaluator(name: str):
    """Register one deterministic reporter evaluator by semantic name."""

    def decorator(function: Evaluator) -> Evaluator:
        if name in _EVALUATORS:
            raise ValueError(f"duplicate reporter evaluator: {name}")
        _EVALUATORS[name] = function
        return function

    return decorator


def evaluate_items(ctx: RunContext, wizard: TerminalWizard) -> list[StatementResult]:
    """Evaluate reporter items in catalog order, asking only human-owned input."""
    results: list[StatementResult] = []
    item_values: dict[str, Any] = {}
    catalog_items = ctx.catalog.get("items", [])
    total = len(catalog_items)
    for index, item in enumerate(catalog_items, start=1):
        log.info(
            "[%d/%d] Evaluating %s: %s (%s)",
            index,
            total,
            item["id"],
            item.get("title", ""),
            item.get("mode", ""),
        )
        condition_context = ConditionContext(
            items=item_values,
            evidence=ctx.evidence.get("adapters", {}),
        )
        if not evaluate_condition(item.get("applicability"), condition_context):
            results.append(
                StatementResult(
                    id=item["id"],
                    section=item["section"],
                    state=StatementState.NOT_APPLICABLE,
                    readiness=ReadinessEffect.CLEAR,
                )
            )
            item_values[item["id"]] = None
            continue
        mode = item["mode"]
        readiness = ReadinessEffect(item.get("readiness", "clear"))
        if mode == "human_only":
            _show_preface(item, ctx, wizard)
            question = _question_from_item(item, ctx)
            answer = wizard.ask(question)
            if answer is None:
                results.append(
                    StatementResult(
                        id=item["id"],
                        section=item["section"],
                        state=StatementState.NOT_APPLICABLE,
                        readiness=ReadinessEffect.CLEAR,
                    )
                )
                continue
            statement = _human_statement(item, answer.value, ctx.source_package)
            statement = _complete_statement(statement, question, wizard)
            maybe_write_evidence(item, ctx, answer.value)
            selected_option = answer.value if question.kind == QuestionKind.SINGLE_CHOICE else None
            option_readiness = None
            if selected_option is not None:
                option_readiness = next(
                    (
                        option.readiness
                        for option in question.options
                        if option.id == selected_option
                    ),
                    None,
                )
            result = _resolved_or_open(
                StatementResult(
                    id=item["id"],
                    section=item["section"],
                    state=StatementState.RESOLVED,
                    readiness=option_readiness or readiness,
                    statement=statement,
                    selected_option=selected_option,
                    provenance=Provenance.HUMAN,
                    answer_refs=[question.id],
                    human_confirmed=True,
                )
            )
            results.append(result)
            item_values[item["id"]] = answer.value
            continue

        if mode == "ev_to_ai":
            _show_preface(item, ctx, wizard)
            fallback_question = _question_from_item(item, ctx, deferrable=True)
            result = evaluate_ai_item(item, ctx, wizard, fallback_question)
            results.append(result)
            item_values[item["id"]] = result.selected_option or result.statement
            continue

        evaluator = _EVALUATORS.get(str(item.get("evaluator", "")))
        if evaluator is None:
            results.append(
                _unavailable(
                    item, readiness, "deterministic evaluator unavailable", ctx.source_package
                )
            )
            item_values[item["id"]] = None
            continue
        assessment = evaluator(item, ctx)
        if assessment.statement is None:
            results.append(
                _unavailable(item, readiness, assessment.unavailable_reason, ctx.source_package)
            )
            item_values[item["id"]] = None
            continue
        result = _deterministic_result(item, readiness, assessment)
        results.append(result)
        item_values[item["id"]] = result.statement
    return results


def _complete_statement(statement: str, question: QuestionSpec, wizard: TerminalWizard) -> str:
    """Let the reporter fill any ``TBD`` slot a chosen statement still has.

    The catalog's option statements reproduce the human template's own
    alternatives, several of which end in "... because TBD". Picking the
    alternative and completing its sentence are two distinct steps: the
    choice is a decision, the completion is prose only the reporter can
    write. Statements with nothing left to fill are returned untouched, so
    no extra editor round is imposed on the common case.
    """
    if "TBD" not in statement:
        return statement
    return wizard.complete_statement(question, statement)


def _resolved_or_open(result: StatementResult) -> StatementResult:
    """Downgrade a statement that still carries an unfilled template slot.

    A reporter may deliberately leave a ``TBD`` in place (the editor says so
    explicitly). That is a legitimate "not settled yet", so the item must
    travel to the draft's "Left to clarify:" block rather than be presented
    as a confident statement - and rather than tripping the draft linter's
    raw-TBD guard, which would abort the whole run at write time.
    """
    if "TBD" not in result.statement:
        return result
    result.state = StatementState.NEEDS_INPUT
    result.human_confirmed = False
    result.provenance = None
    return result


def _deterministic_result(
    item: dict, readiness: ReadinessEffect, assessment: Assessment
) -> StatementResult:
    """Turn one evaluator ``Assessment`` into its reporter statement result.

    An assessment carrying an ``action`` is a finding the reporter still has
    to resolve, so it becomes ``NEEDS_INPUT`` and the draft renderer lists it
    under "Left to clarify:" instead of presenting it as a settled bullet.
    Everything else is a confident statement, optionally carrying a note as
    its parenthetical, and cannot affect submission readiness.
    """
    statement = ensure_bulleted(str(assessment.statement))
    if assessment.action:
        return StatementResult(
            id=item["id"],
            section=item["section"],
            state=StatementState.NEEDS_INPUT,
            readiness=readiness,
            statement=statement,
            provenance=Provenance.DETERMINISTIC,
            evidence_refs=assessment.evidence_refs,
            rationale=assessment.rationale(),
        )
    return StatementResult(
        id=item["id"],
        section=item["section"],
        state=StatementState.RESOLVED,
        readiness=ReadinessEffect.CLEAR,
        statement=statement,
        provenance=Provenance.DETERMINISTIC,
        evidence_refs=assessment.evidence_refs,
        rationale=assessment.note,
    )


def _question_from_item(item: dict, ctx: RunContext, *, deferrable: bool = False) -> QuestionSpec:
    definition = item["question"]
    kind = QuestionKind(definition["kind"])
    source_package = ctx.source_package
    raw_options = definition.get("options", [])
    options = [
        QuestionOption(
            str(option["id"]),
            substitute_source(str(option["label"]), source_package),
            substitute_source(str(option.get("statement", "")), source_package),
            bool(option.get("exclusive", False)),
            readiness=ReadinessEffect(option["readiness"]) if "readiness" in option else None,
            todo_ref=str(option.get("todo_ref", "")),
            leads_to_followup=bool(option.get("leads_to_followup", False)),
        )
        for option in raw_options
    ]
    dynamic = _dynamic_options(definition.get("options_source"), ctx, existing=options)
    if dynamic:
        known_packages = [option.id for option in dynamic]
        options = [
            _spell_out_option(option, raw_option, known_packages)
            for option, raw_option in zip(options, raw_options, strict=True)
        ]
    options = [
        _apply_option_lock(option, raw_option, ctx)
        for option, raw_option in zip(options, raw_options, strict=True)
    ]
    return QuestionSpec(
        id=item["id"],
        prompt=str(definition["prompt"]),
        kind=kind,
        required=bool(item.get("required", True)),
        options=tuple(options),
        hint=str(definition.get("hint", "")) or _evidence_hint(item, ctx),
        default=definition.get("default")
        or _dynamic_default(definition.get("default_source"), ctx),
        rule_context=str(item.get("rule_context", "")),
        answer_guidance=str(item.get("answer_guidance", "")),
        deferrable=deferrable,
        prefill=_question_prefill(item, ctx),
    )


def _question_prefill(item: dict, ctx: RunContext) -> str:
    """Return the statement text a free-text question opens its editor on.

    Only free-text questions have one: a single_choice question offers the
    catalog's pre-written option statements instead, and completes the chosen
    one afterwards (see ``TerminalWizard.complete_statement``). A confidently
    detected value (``default_source``) fills the first TBD slot up front, so
    the reporter confirms rather than retypes what the tool already knows.
    """
    if QuestionKind(item["question"]["kind"]) not in {QuestionKind.MULTILINE, QuestionKind.TEXT}:
        return ""
    prefill = template_to_statement(str(item.get("template", "")), ctx.source_package)
    default = _dynamic_default(item["question"].get("default_source"), ctx)
    if default and "TBD" in prefill:
        prefill = prefill.replace("TBD", default, 1)
    return prefill


def _evidence_hint(item: dict, ctx: RunContext) -> str:
    """Fold an item's evidence-derived preface into its question's ``hint``.

    ``_show_preface`` already prints this ahead of the question in the
    console (as a "Note"), but that never reached the editor's commented-out
    hint area for multiline questions, leaving the reporter to answer
    evidence-gated questions (e.g. "explain every failing autopkgtest") with
    no visibility into which findings triggered them once inside the editor.
    """
    statement, rationale = _preface_text(item, ctx)
    if not statement:
        return ""
    return f"{statement} {rationale}".strip() if rationale else statement


def _dynamic_default(default_source: dict | None, ctx: RunContext) -> str | None:
    """Resolve a question's default answer from an evidence adapter field.

    Used so a confidently-detected value (e.g. an upstream project name found
    via release-monitoring.org) is offered as a one-keystroke default instead
    of asking the reporter to retype something the tool already knows.
    """
    if not default_source:
        return None
    adapter_id = str(default_source["adapter"])
    field = str(default_source["field"])
    data = _adapter(ctx, adapter_id)
    value = data.get(field) if isinstance(data, dict) else None
    text = str(value).strip() if value else ""
    return text or None


def _dynamic_options(
    options_source: dict | None, ctx: RunContext, *, existing: list[QuestionOption]
) -> list[QuestionOption]:
    """Look up the concrete evidence-derived choices an ``options_source`` names.

    These are no longer added as individually-selectable options (a catalog
    item that needs that shape uses ``single_choice`` plus a free-text
    follow-up item instead); the returned list is only used to compute the
    known package names for ``_spell_out_option``'s shortcut suffix.
    """
    if not options_source:
        return []
    adapter_id = str(options_source["adapter"])
    field = str(options_source["field"])
    data = _adapter(ctx, adapter_id)
    values = data.get(field, []) if isinstance(data, dict) else []
    existing_ids = {option.id for option in existing}
    dynamic: list[QuestionOption] = []
    for value in values:
        name = str(value)
        if name and name not in existing_ids:
            dynamic.append(QuestionOption(name, name))
            existing_ids.add(name)
    return dynamic


_DEV_DOC_DBG_SUFFIX_PATTERN = re.compile(r"-(dev|doc|dbg|dbgsym)$")


def _spell_out_option(
    option: QuestionOption, raw_option: dict, known_packages: list[str]
) -> QuestionOption:
    """Append the concrete package list a shortcut option resolves to.

    So "All binary packages built by this source" becomes "...: pkg1, pkg2,
    pkg3" instead of leaving the reporter to guess what the shortcut actually
    covers. ``spell_out_filter`` is a small catalog-declared vocabulary
    (``all``, ``exclude_dev_doc_dbg``, or ``list_only``), not hardcoded to
    any specific item.

    ``list_only`` (used by a "list them yourself" option, e.g. picking
    specific binary packages) doesn't change the recorded statement at all —
    it only adds an informational ``list_note`` line so the reporter sees
    what the source builds without the tool silently deciding the scope.
    """
    spell_out_filter = raw_option.get("spell_out_filter")
    if spell_out_filter == "list_only":
        if not known_packages:
            return option
        return QuestionOption(
            option.id,
            option.label,
            option.statement,
            option.exclusive,
            readiness=option.readiness,
            list_note=f"The packages built by this source are: {', '.join(known_packages)}",
            todo_ref=option.todo_ref,
        )
    if spell_out_filter == "all":
        selected = known_packages
    elif spell_out_filter == "exclude_dev_doc_dbg":
        selected = [name for name in known_packages if not _DEV_DOC_DBG_SUFFIX_PATTERN.search(name)]
    else:
        return option
    if not selected:
        return option
    suffix = ": " + ", ".join(selected)
    return QuestionOption(
        option.id,
        option.label + suffix,
        option.statement + suffix,
        option.exclusive,
        readiness=option.readiness,
        todo_ref=option.todo_ref,
    )


def _apply_option_lock(option: QuestionOption, raw_option: dict, ctx: RunContext) -> QuestionOption:
    """Resolve a catalog-declared ``unavailable_if`` condition against evidence.

    The option stays visible (catalog.py enforces every ``unavailable_if``
    has a matching ``unavailable_reason``) but is marked unselectable so the
    wizard can explain why instead of silently omitting it.
    """
    condition = raw_option.get("unavailable_if")
    if not condition:
        return option
    context = ConditionContext(items={}, evidence=ctx.evidence.get("adapters", {}))
    if not evaluate_condition(condition, context):
        return option
    return QuestionOption(
        option.id,
        option.label,
        option.statement,
        option.exclusive,
        readiness=option.readiness,
        locked_reason=str(raw_option.get("unavailable_reason", "")),
        list_note=option.list_note,
        todo_ref=option.todo_ref,
    )


def _show_preface(item: dict, ctx: RunContext, wizard: TerminalWizard) -> None:
    """Surface one deterministic-evidence note ahead of a human/AI question.

    Reuses the deterministic evaluator registry so preface content stays
    grounded in the same evidence-derived facts as ``deterministic`` items,
    instead of re-implementing lookups per catalog item.
    """
    statement, rationale = _preface_text(item, ctx)
    if statement:
        wizard.show_note(statement, rationale)


def _preface_text(item: dict, ctx: RunContext) -> tuple[str, str]:
    """Resolve one item's ``preface_evaluator`` into (statement, rationale).

    Shared by ``_show_preface`` (console-only "Note" block, shown ahead of
    the question) and ``_question_from_item`` (folded into the question's
    own ``hint``, so the same evidence-grounded context also reaches the
    editor's commented-out hint area, not just the console).
    """
    name = item.get("preface_evaluator")
    if not name:
        return "", ""
    evaluator = _EVALUATORS.get(str(name))
    if evaluator is None:
        return "", ""
    assessment = evaluator(item, ctx)
    # Preface context deliberately keeps BOTH parts: what the evidence says
    # and what it asks the reporter to settle. The action/note split governs
    # where a statement lands in the draft, never how much context the
    # interactive session gets.
    return assessment.statement or "", assessment.rationale()


def _human_statement(item: dict, answer: Any, source_package: str) -> str:
    """Return the reporter-authored statement for one answered human question.

    There is deliberately no splicing left here. A single_choice answer
    resolves to its option's own pre-written statement; any other answer IS
    the statement, because the reporter edited it in the editor pre-filled
    with the item's template (see ``_question_prefill``). Merging an
    interview answer into a template sentence is what produced text like
    "required in Ubuntu main for This is an entropy source alternative".
    """
    options = item.get("question", {}).get("options", [])
    option_statement = resolve_option_statements(options, answer, source_package)
    if option_statement is not None:
        return option_statement
    answer_text = (
        "\n".join(str(value) for value in answer) if isinstance(answer, list) else str(answer)
    )
    return ensure_bulleted(answer_text.strip())


def _unavailable(
    item: dict, readiness: ReadinessEffect, rationale: str, _source_package: str
) -> StatementResult:
    """Record that the evidence needed to judge this item was not available.

    No ``statement`` is set: nothing was actually established. The draft's
    "Left to clarify:" renderer reconstructs the item's original catalog
    TODO/option context from the catalog itself, so a copy of the unfilled
    template here would only be a second, divergent source of that text -
    and would look like a real statement to anything reading the structured
    report.
    """
    return StatementResult(
        id=item["id"],
        section=item["section"],
        state=StatementState.UNAVAILABLE,
        readiness=readiness,
        rationale=rationale,
    )


def _adapter(ctx: RunContext, adapter_id: str) -> dict:
    value = ctx.evidence.get("adapters", {}).get(adapter_id, {})
    return value if isinstance(value, dict) else {}


@reporter_evaluator("source-availability")
def _source_availability(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "lp-package-api")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Launchpad package data was unavailable")
    history = data.get("ubuntu_publish_history", [])
    components = sorted(
        {str(entry.get("component")) for entry in history if entry.get("component")}
    )
    if not history:
        return Assessment(
            statement=(
                f"The source package {ctx.source_package} has no published record in {ctx.series}."
            ),
            evidence_refs=["lp-package-api:ubuntu_publish_history"],
            action="The source must be published in Ubuntu before an MIR can proceed.",
        )
    component_text = ", ".join(components) if components else "unknown component"
    return Assessment(
        statement=(
            f"The source package {ctx.source_package} is published in Ubuntu ({component_text})."
        ),
        evidence_refs=["lp-package-api:ubuntu_publish_history"],
        action=(
            ""
            if "universe" in components
            else "Confirm where the package is published; it is not confirmed in universe."
        ),
    )


@reporter_evaluator("build-architectures")
def _build_architectures(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "lp-build-api")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Launchpad build data was unavailable")
    builds = data.get("builds", [])
    passing = sorted(
        {
            str(build.get("arch_tag"))
            for build in builds
            if str(build.get("build_state", "")).casefold() in {"successfully built", "full"}
            and build.get("arch_tag")
        }
    )
    failing = sorted(
        {
            str(build.get("arch_tag"))
            for build in builds
            if build.get("arch_tag")
            and str(build.get("build_state", "")).casefold() not in {"successfully built", "full"}
        }
    )
    if not builds:
        return Assessment(unavailable_reason="No Launchpad build records were found")
    return Assessment(
        statement="Current Launchpad builds pass on: " + (", ".join(passing) or "none") + ".",
        evidence_refs=["lp-build-api:builds"],
        action=(
            "Explain these non-passing build records: " + ", ".join(failing) if failing else ""
        ),
    )


@reporter_evaluator("source-link")
def _source_link(_item: dict, ctx: RunContext) -> Assessment:
    return Assessment(
        statement=f"Source package: https://launchpad.net/ubuntu/+source/{ctx.source_package}"
    )


@reporter_evaluator("prior-mir-history")
def _prior_mir_history(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "lp-mir-history")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Prior MIR history was unavailable")
    bugs = data.get("prior_mir_bugs", [])
    if not bugs:
        return Assessment(
            statement=(
                "No prior MIR bug was found for this source or identified predecessor names."
            ),
            evidence_refs=["lp-mir-history:prior_mir_bugs"],
        )
    links = [str(bug.get("web_link") or bug.get("id")) for bug in bugs[:20]]
    return Assessment(
        statement="Prior MIR history was found: " + ", ".join(links) + ".",
        evidence_refs=["lp-mir-history:prior_mir_bugs"],
        action="Confirm whether the existing discussion should receive a new series task.",
    )


# Which corpora the CVE evaluator queried. Informational only: it tells the
# reader what "no CVEs found" is based on (and what it is not - OSS-security
# mailing list chatter), but a clean result leaves the reporter nothing to do,
# so it must never raise the item's readiness on its own.
_CVE_SOURCING_NOTE = (
    "Sourcing: the Ubuntu CVE tracker plus the cross-vendor cvelistV5/NVD corpus, "
    "which also covers Debian-relevant CVE identifiers - no separate Debian or NVD "
    "check is needed. The OSS-security mailing list (pre-CVE-assignment chatter) is "
    "not covered by these adapters; flag it yourself if you are aware of such a "
    "discussion."
)


@reporter_evaluator("cve-history")
def _cve_history(_item: dict, ctx: RunContext) -> Assessment:
    ubuntu = _adapter(ctx, "ubuntu-cve-tracker")
    nvd = _adapter(ctx, "nvd-enrich")
    if ubuntu.get("status") != "ok" and nvd.get("status") != "ok":
        return Assessment(unavailable_reason="CVE evidence was unavailable")
    ids = sorted(
        {
            str(entry.get("id"))
            for entry in [*ubuntu.get("cves", []), *nvd.get("cves", [])]
            if isinstance(entry, dict) and entry.get("id")
        }
    )
    if not ids:
        return Assessment(
            statement="No package-associated CVEs were found in the queried trackers.",
            evidence_refs=["ubuntu-cve-tracker:cves", "nvd-enrich:cves"],
            note=_CVE_SOURCING_NOTE,
        )
    preview = ", ".join(ids[:20])
    suffix = f" (and {len(ids) - 20} more)" if len(ids) > 20 else ""
    return Assessment(
        statement=f"The queried trackers found {len(ids)} associated CVE(s): {preview}{suffix}.",
        evidence_refs=["ubuntu-cve-tracker:cves", "nvd-enrich:cves"],
        action="Verify their relevance and describe the handling history.",
        note=_CVE_SOURCING_NOTE,
    )


@reporter_evaluator("important-bugs")
def _important_bugs(_item: dict, ctx: RunContext) -> Assessment:
    ubuntu = _adapter(ctx, "lp-bug-search-api")
    debian = _adapter(ctx, "debian-bts")
    if ubuntu.get("status") != "ok" and debian.get("status") != "ok":
        return Assessment(unavailable_reason="Ubuntu and Debian bug data were unavailable")
    bugs = [*ubuntu.get("critical_bugs", []), *debian.get("rc_bugs", [])]
    if not bugs:
        return Assessment(
            statement="No critical Ubuntu or release-critical Debian bugs were found.",
            evidence_refs=["lp-bug-search-api:critical_bugs", "debian-bts:rc_bugs"],
        )
    labels = [str(bug.get("web_link") or bug.get("id") or bug.get("title")) for bug in bugs[:20]]
    return Assessment(
        statement=f"Important open bugs found: {', '.join(labels)}.",
        evidence_refs=["lp-bug-search-api:critical_bugs", "debian-bts:rc_bugs"],
        action="Explain their maintenance impact.",
    )


@reporter_evaluator("binary-security-surface")
def _binary_security_surface(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "binary-package-inspection")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Built binary package inspection was unavailable")
    fields = {
        "setuid/setgid": data.get("setuid_setgid_binaries", []),
        "sbin executables": data.get("sbin_executables", []),
        "systemd units": data.get("systemd_units", []),
        "cron jobs": data.get("cron_jobs", []),
    }
    present = [f"{label}: {', '.join(values)}" for label, values in fields.items() if values]
    statement = (
        "No setuid/setgid files, sbin executables, systemd units, or cron jobs were found."
        if not present
        else "Installed privileged/service surface: " + "; ".join(present) + "."
    )
    return Assessment(
        statement=statement,
        evidence_refs=[f"binary-package-inspection:{field}" for field in fields],
        action="Explain the purpose and mitigations of each installed surface." if present else "",
    )


@reporter_evaluator("binary-integration-surface")
def _binary_integration_surface(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "binary-package-inspection")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Built binary package inspection was unavailable")
    fields = {
        "AppArmor profiles": data.get("apparmor_profiles", []),
        "desktop files": data.get("desktop_files", []),
        "translations": data.get("translation_files", []),
        "plugin/extension candidates": data.get("plugin_candidates", []),
    }
    present = [f"{label}: {', '.join(values)}" for label, values in fields.items() if values]
    statement = (
        "No AppArmor profiles, desktop files, translations, or plugin candidates were found."
        if not present
        else "Installed integration surface: " + "; ".join(present) + "."
    )
    return Assessment(
        statement=statement,
        evidence_refs=[f"binary-package-inspection:{field}" for field in fields],
    )


@reporter_evaluator("build-tests")
def _build_tests(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "fetch-build")
    if not data.get("build_log"):
        return _build_tests_without_log(ctx)
    log_text = str(data["build_log"]).casefold()
    markers = [
        marker
        for marker in ("dh_auto_test", "pytest", "ctest", "make check", "meson test")
        if marker in log_text
    ]
    if markers:
        return Assessment(
            statement=f"Build-time test execution was observed ({', '.join(markers)}).",
            evidence_refs=["fetch-build:build_log"],
            action="Verify that failures are not ignored.",
        )
    return Assessment(
        statement="No build-time test execution was identified in the collected build log.",
        evidence_refs=["fetch-build:build_log"],
        action="A reason or alternative test plan is required.",
    )


def _build_tests_without_log(ctx: RunContext) -> Assessment:
    """Fall back to debian/rules when the official build log is unavailable.

    A missing build log (e.g. a carried-over architecture whose original
    build log could not be resolved either) should not silently collapse
    into an uninformative "unavailable" TODO when the packaging itself
    already reveals whether build-time tests are disabled: debian/rules is
    collected independently of the build log and its presence/absence of a
    ``dh_auto_test`` override is a confident, direct signal.
    """
    packaging = _adapter(ctx, "packaging-source")
    overrides = packaging.get("debian_rules_overrides")
    if not isinstance(overrides, list):
        return Assessment(unavailable_reason="No build log was available")
    if "dh_auto_test" in overrides:
        return Assessment(
            statement=(
                "The build log was unavailable, but debian/rules overrides the default "
                "dh_auto_test target, so the packaging - not the unmodified debhelper "
                "default - controls what (if anything) runs as a build-time test."
            ),
            evidence_refs=["packaging-source:debian_rules_overrides"],
            action="Confirm what the override actually runs and that failures are not ignored.",
        )
    return Assessment(
        statement=(
            "The build log was unavailable, but debian/rules does not override the "
            "default dh_auto_test target, so any build-time test suite upstream "
            "provides runs unmodified during the build."
        ),
        evidence_refs=["packaging-source:debian_rules_overrides"],
        action="Confirm the upstream build system actually defines a test target.",
    )


@reporter_evaluator("autopkgtests")
def _autopkgtests(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "autopkgtest-db")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Autopkgtest data was unavailable")
    if not data.get("has_autopkgtest"):
        return Assessment(
            statement="No autopkgtest results were found for this source package.",
            evidence_refs=["autopkgtest-db:has_autopkgtest"],
            action="A reason or alternative test plan is required.",
        )
    passing = ", ".join(sorted(data.get("passing_arches", []))) or "none"
    failing = ", ".join(sorted(data.get("failing_arches", [])))
    return Assessment(
        statement=f"Autopkgtests are present and pass on: {passing}.",
        evidence_refs=["autopkgtest-db:passing_arches", "autopkgtest-db:failing_arches"],
        action=f"Explain the failing architectures: {failing}." if failing else "",
    )


@reporter_evaluator("watch-file")
def _watch_file(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Packaging source data was unavailable")
    if str(data.get("debian_watch", "")).strip():
        return Assessment(
            statement="A debian/watch upstream-release mechanism is present.",
            evidence_refs=["packaging-source:debian_watch"],
        )
    return Assessment(
        statement="No debian/watch file was found.",
        evidence_refs=["packaging-source:debian_watch"],
        action=(
            "Name the update mechanism used instead; a native package or another "
            "documented mechanism may be acceptable."
        ),
    )


@reporter_evaluator("lintian")
def _lintian(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "lintian")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Lintian evidence was unavailable")
    errors = data.get("lintian_errors", [])
    warnings = data.get("lintian_warnings", [])
    return Assessment(
        statement=f"Lintian reported {len(errors)} error(s) and {len(warnings)} warning(s).",
        evidence_refs=["lintian:lintian_errors", "lintian:lintian_warnings"],
        action="Review errors, warnings, and any overrides." if errors or warnings else "",
    )


@reporter_evaluator("lintian-overrides")
def _lintian_overrides(_item: dict, ctx: RunContext) -> Assessment:
    """Judge whether every lintian override carries an explanatory comment.

    Common case (no overrides, or every override already has a preceding `#`
    comment) resolves to a plain OK statement. The rare case - one or more
    overrides with no comment - is a real problem needing the reporter's own
    explanation, surfaced by the follow-up REP-QA-PKG-009 item (gated on this
    exact evidence), mirroring the Maintainer-field 006/007 pattern.
    """
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Packaging source data was unavailable")
    entries = data.get("lintian_override_entries", [])
    uncommented = sorted(
        {str(entry.get("tag", "")) for entry in entries if not entry.get("has_comment")}
    )
    if not uncommented:
        return Assessment(
            statement="Lintian overrides are absent or already explained by a comment.",
            evidence_refs=["packaging-source:lintian_override_entries"],
        )
    return Assessment(
        statement=(
            "The following lintian override(s) lack an explanatory comment: "
            + ", ".join(uncommented)
            + "."
        ),
        evidence_refs=["packaging-source:lintian_override_entries"],
        note="See the following item for the reporter's explanation.",
    )


@reporter_evaluator("source-packaging-metadata")
def _source_packaging_metadata(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Packaging source data was unavailable")
    source_format = str(data.get("debian_source_format", "")).strip() or "unspecified"
    debconf = data.get("debconf_templates", [])
    overrides = data.get("debian_rules_overrides", [])
    statement = (
        f"Source format: {source_format}; debconf templates: {len(debconf)}; "
        f"debian/rules overrides: {', '.join(overrides) if overrides else 'none'}."
    )
    concerning = [
        entry.get("template", "unknown")
        for entry in debconf
        if str(entry.get("priority", "")).casefold() in {"critical", "high"}
    ]
    return Assessment(
        statement=statement,
        evidence_refs=[
            "packaging-source:debian_source_format",
            "packaging-source:debconf_templates",
        ],
        action=(
            "Review these high/critical debconf templates: " + ", ".join(concerning)
            if concerning
            else ""
        ),
    )


# The canonical Maintainer value `update-maintainer` (ubuntu-dev-tools) sets whenever
# a package carries an Ubuntu delta - see LP: #1951988 and the "Maintainer field"
# packaging docs. A package with no Ubuntu delta keeps its Debian-original Maintainer
# unchanged, which is equally correct.
_UBUNTU_DEVELOPERS_MAINTAINER = "Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>"


@reporter_evaluator("maintainer-field")
def _maintainer_field(_item: dict, ctx: RunContext) -> Assessment:
    """Judge debian/control's Maintainer field against the Ubuntu delta status.

    Common cases (no delta, or delta present with Maintainer already updated to
    "Ubuntu Developers ...") resolve to the same simple OK statement the human
    template's own TODO line uses. The rare case - an Ubuntu delta present but
    Maintainer never updated via `update-maintainer` - is a real problem that
    needs the reporter's own resolution plan, surfaced by the follow-up
    REP-QA-PKG-007 item (gated on this exact evidence combination).
    """
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Packaging source data was unavailable")
    delta_kind = str(data.get("delta_kind", "")).strip()
    maintainer = str(data.get("source_maintainer", "")).strip()
    if not delta_kind or delta_kind == "unknown":
        return Assessment(
            unavailable_reason=(
                "Could not determine whether Ubuntu carries a delta from the source version"
            )
        )
    if delta_kind != "ubuntu_delta" or maintainer == _UBUNTU_DEVELOPERS_MAINTAINER:
        return Assessment(
            statement="debian/control defines a correct Maintainer field",
            evidence_refs=["packaging-source:delta_kind", "packaging-source:source_maintainer"],
        )
    version = str(data.get("analyzed_version", "")).strip() or "unknown"
    statement = (
        f"debian/control's Maintainer field needs attention: Ubuntu carries a delta "
        f"(version {version}) but Maintainer is not set to Ubuntu Developers "
        f"(currently: {maintainer or 'missing'})."
    )
    return Assessment(
        statement=statement,
        evidence_refs=["packaging-source:delta_kind", "packaging-source:source_maintainer"],
        note="See the following item for the reporter's resolution plan.",
    )


@reporter_evaluator("vendored-maintenance-docs")
def _vendored_maintenance_docs(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Packaging source data was unavailable")
    vendored = data.get("shipped_vendored_dirs", [])
    if not vendored:
        return Assessment(
            statement="No shipped vendored directories were detected.",
            evidence_refs=["packaging-source:shipped_vendored_dirs"],
        )
    readme = str(data.get("debian_readme_source", "")).strip()
    copyright_text = str(data.get("debian_copyright", "")).casefold()
    documented = bool(readme) and any(
        marker in readme.casefold() for marker in ("vendor", "refresh", "update", "repack")
    )
    covered = all(path.strip("./").split("/")[-1].casefold() in copyright_text for path in vendored)
    statement = "Shipped vendored directories: " + ", ".join(vendored) + "."
    gaps: list[str] = []
    if not documented:
        gaps.append("debian/README.source does not clearly document refresh")
    if not covered:
        gaps.append("debian/copyright does not clearly cover every vendored directory")
    return Assessment(
        statement=statement,
        evidence_refs=[
            "packaging-source:shipped_vendored_dirs",
            "packaging-source:debian_readme_source",
            "packaging-source:debian_copyright",
        ],
        action="Resolve these gaps: " + "; ".join(gaps) + "." if gaps else "",
    )


@reporter_evaluator("rust-vendoring")
def _rust_vendoring(_item: dict, ctx: RunContext) -> Assessment:
    """Judge whether a Rust package's vendored dependencies are reproducibly tracked.

    Rust packages vendor their non-runtime (build-time) dependencies via the
    supported cargo packaging path; a committed Cargo.lock is what makes those
    versions reproducibly trackable and refreshable. Gated on
    ``packaging-source.is_rust_package`` so this never fires for non-Rust
    packages.
    """
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Packaging source data was unavailable")
    if not data.get("cargo_lock_present"):
        return Assessment(
            statement=(
                "This Rust package has no committed Cargo.lock, so vendored "
                "dependency versions are not reproducibly tracked."
            ),
            evidence_refs=["packaging-source:cargo_lock_present"],
            action=(
                "A Cargo.lock file is expected for reproducible dependency tracking "
                "and refresh documentation."
            ),
        )
    return Assessment(
        statement=(
            "This Rust package tracks its vendored dependencies via a committed Cargo.lock file."
        ),
        evidence_refs=["packaging-source:cargo_lock_present"],
    )


@reporter_evaluator("dependencies")
def _dependencies(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "dep-analysis")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Dependency analysis was unavailable")
    deps = sorted(data.get("in_scope_deps_not_in_main", data.get("deps_not_in_main", [])))
    if not deps:
        return Assessment(
            statement="No in-scope runtime dependencies outside main require a separate MIR.",
            evidence_refs=["dep-analysis:in_scope_deps_not_in_main"],
        )
    return Assessment(
        statement=f"Runtime dependencies outside main require MIR handling: {', '.join(deps)}.",
        evidence_refs=["dep-analysis:in_scope_deps_not_in_main"],
        action="Reference separate MIR bugs or include those sources in this request.",
    )


@reporter_evaluator("binary-packages")
def _binary_packages(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Packaging source inspection was unavailable")
    packages = sorted(str(name) for name in data.get("binary_package_names", []))
    if not packages:
        return Assessment(unavailable_reason="No binary packages were found for this source")
    return Assessment(
        statement=f"This source builds the following binary packages: {', '.join(packages)}.",
        evidence_refs=["packaging-source:binary_package_names"],
    )


@reporter_evaluator("lintian-fhs-summary")
def _lintian_fhs_summary(_item: dict, ctx: RunContext) -> Assessment:
    """Surface lintian's error/warning counts ahead of the FHS/Policy question.

    Without this, a reporter answering "does this follow FHS and Debian
    Policy" has no visibility into whether lintian actually ran, or what it
    found, until they are already inside the editor.
    """
    data = _adapter(ctx, "lintian")
    if data.get("status") != "ok":
        reason = data.get("message", "lintian did not run") if data else "lintian did not run"
        return Assessment(
            statement=(
                f"Lintian evidence is unavailable ({reason}); FHS/Policy compliance cannot be "
                "confirmed from lintian output."
            )
        )
    errors = data.get("lintian_errors", [])
    warnings = data.get("lintian_warnings", [])
    if not errors and not warnings:
        return Assessment(
            statement="Lintian reported 0 errors and 0 warnings.",
            evidence_refs=["lintian:lintian_errors", "lintian:lintian_warnings"],
        )
    return Assessment(
        statement=f"Lintian reported {len(errors)} error(s) and {len(warnings)} warning(s).",
        evidence_refs=["lintian:lintian_errors", "lintian:lintian_warnings"],
        note="; ".join(str(entry) for entry in [*errors, *warnings][:5]),
    )


@reporter_evaluator("obsolete-dependencies")
def _obsolete_dependencies(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "dep-analysis")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Dependency analysis was unavailable")
    dependency_names = {
        str(entry.get("depends", ""))
        for entry in data.get("runtime_deps", [])
        if isinstance(entry, dict)
    } | {str(name) for name in data.get("runtime_dep_packages", [])}
    obsolete = sorted(
        name
        for name in dependency_names
        if re.search(r"(?:python2|python2\.|gtk2|libgtk2|webkit1|qtwebkit|libseed)", name)
    )
    if not obsolete:
        return Assessment(
            statement=(
                "No Python 2, GTK 2, or other catalogued obsolete runtime dependency was found."
            ),
            evidence_refs=["dep-analysis:runtime_deps"],
        )
    return Assessment(
        statement="Potential obsolete runtime dependencies: " + ", ".join(obsolete) + ".",
        evidence_refs=["dep-analysis:runtime_deps"],
        action="Remove or replace obsolete dependencies before promotion.",
    )


@reporter_evaluator("recent-build")
def _recent_build(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "lp-build-api")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Launchpad build evidence was unavailable")
    threshold = datetime.now(UTC) - timedelta(days=93)
    recent: list[dict] = []
    for build in data.get("builds", []):
        value = str(build.get("date_created", "")).replace("Z", "+00:00")
        try:
            date = datetime.fromisoformat(value)
        except ValueError:
            continue
        if date.tzinfo is None:
            date = date.replace(tzinfo=UTC)
        if date >= threshold:
            recent.append(build)
    if not recent:
        return Assessment(
            statement="No Launchpad build within the last three months was confirmed.",
            evidence_refs=["lp-build-api:builds"],
            action="Provide a recent archive, test-rebuild, PPA, or local sbuild reference.",
        )
    links = [str(build.get("web_link", "")) for build in recent if build.get("web_link")]
    statement = f"Launchpad records contain {len(recent)} build(s) from the last three months."
    if links:
        statement += " Builds: " + ", ".join(links[:10]) + "."
    return Assessment(statement=statement, evidence_refs=["lp-build-api:builds"])


@reporter_evaluator("built-using-surface")
def _built_using_surface(_item: dict, ctx: RunContext) -> Assessment:
    """State which packages the built binaries declare as Built-Using.

    Facts only - the reporter (and, on the review side, the ESL checks) judge
    what the entries mean. Reuses the shared built_using_entries collector so
    reporter and reviewer always read the same shape.
    """
    deb = _adapter(ctx, "deb-metadata")
    if deb.get("status") != "ok":
        return Assessment(unavailable_reason="Built-package metadata was unavailable")
    entries = built_using_entries(deb)
    refs = ["deb-metadata:deb_packages"]
    if not entries:
        return Assessment(
            statement="Built binaries declare no Built-Using or Static-Built-Using entries.",
            evidence_refs=refs,
        )
    return Assessment(
        statement=f"Built binaries declare Built-Using/Static-Built-Using: {', '.join(entries)}.",
        evidence_refs=refs,
        note=(
            "Vendored/static build linkages carry the maintenance obligations "
            "asked about in the commitment item above."
        ),
    )


@reporter_evaluator("team-subscription")
def _team_subscription(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "team-mapping")
    if data.get("status") != "ok":
        return Assessment(unavailable_reason="Team subscription data was unavailable")
    teams = sorted(data.get("subscribed_teams", []))
    if teams:
        return Assessment(
            statement=f"Package bug subscriber team(s): {', '.join(teams)}.",
            evidence_refs=["team-mapping:subscribed_teams"],
        )
    return Assessment(
        statement="No owning-team package bug subscription was found.",
        evidence_refs=["team-mapping:subscribed_teams"],
        action="A team must subscribe before promotion.",
    )


@reporter_evaluator("upstream-link")
def _upstream_link(_item: dict, ctx: RunContext) -> Assessment:
    data = _adapter(ctx, "upstream-tracker")
    url = str(data.get("upstream_url", "")).strip()
    if not url:
        return Assessment(unavailable_reason="No reliable upstream project URL was found")
    return Assessment(
        statement=f"Upstream project: {url}", evidence_refs=["upstream-tracker:upstream_url"]
    )


@reporter_evaluator("ui-desktop-not-applicable")
def _ui_desktop_not_applicable(_item: dict, _ctx: RunContext) -> Assessment:
    """Desktop-file counterpart of REP-UI-002, gated on REP-UI-001 == not-end-user-facing.

    Always resolves to the same fixed statement with no evidence dependency
    -- the applicability gate is the only thing that decides whether this
    item is even asked, so once it is, there is nothing left to judge.
    """
    return Assessment(
        statement=(
            "Not an end-user application (server, CLI-only tool, or library) - no Desktop "
            "file is needed."
        )
    )


@reporter_evaluator("ui-translation-not-applicable")
def _ui_translation_not_applicable(_item: dict, _ctx: RunContext) -> Assessment:
    """Translation counterpart of ``_ui_desktop_not_applicable`` (REP-UI-003)."""
    return Assessment(statement="Application is not end-user facing (does not need translation).")
