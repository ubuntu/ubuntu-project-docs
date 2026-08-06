"""Catalog-driven evaluation for MIR reporter statements."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

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
from reporter.text_utils import ensure_bulleted, strip_todo_prefix, substitute_source
from reporter.wizard import TerminalWizard

log = logging.getLogger("auto_mir.reporter")

Evaluator = Callable[[dict, Any], tuple[str | None, list[str], str]]
_EVALUATORS: dict[str, Evaluator] = {}


def reporter_evaluator(name: str):
    """Register one deterministic reporter evaluator by semantic name."""

    def decorator(function: Evaluator) -> Evaluator:
        if name in _EVALUATORS:
            raise ValueError(f"duplicate reporter evaluator: {name}")
        _EVALUATORS[name] = function
        return function

    return decorator


def evaluate_items(ctx, wizard: TerminalWizard) -> list[StatementResult]:
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
            _maybe_write_evidence(item, ctx, answer.value)
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
            result = StatementResult(
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
            results.append(result)
            item_values[item["id"]] = answer.value
            continue

        if mode == "ev_to_ai":
            _show_preface(item, ctx, wizard)
            result = evaluate_ai_item(item, ctx, wizard, _question_from_item(item, ctx))
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
        statement, evidence_refs, rationale = evaluator(item, ctx)
        if statement is None:
            results.append(_unavailable(item, readiness, rationale, ctx.source_package))
            item_values[item["id"]] = None
            continue
        statement = ensure_bulleted(statement)
        results.append(
            StatementResult(
                id=item["id"],
                section=item["section"],
                state=StatementState.RESOLVED,
                readiness=readiness if rationale else ReadinessEffect.CLEAR,
                statement=statement,
                provenance=Provenance.DETERMINISTIC,
                evidence_refs=evidence_refs,
                rationale=rationale,
            )
        )
        item_values[item["id"]] = statement
    return results


def _question_from_item(item: dict, ctx) -> QuestionSpec:
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
    if kind == QuestionKind.SINGLE_CHOICE:
        options = _mark_followup_options(options, item["id"], ctx)
    return QuestionSpec(
        id=item["id"],
        prompt=str(definition["prompt"]),
        kind=kind,
        required=bool(item.get("required", True)),
        options=tuple(options),
        hint=str(definition.get("hint", "")),
        default=definition.get("default")
        or _dynamic_default(definition.get("default_source"), ctx),
        rule_context=str(item.get("rule_context", "")),
        answer_guidance=str(item.get("answer_guidance", "")),
    )


def _dynamic_default(default_source: dict | None, ctx) -> str | None:
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
    options_source: dict | None, ctx, *, existing: list[QuestionOption]
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
    (``all`` or ``exclude_dev_doc_dbg``), not hardcoded to any specific item.
    """
    spell_out_filter = raw_option.get("spell_out_filter")
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
    )


def _apply_option_lock(option: QuestionOption, raw_option: dict, ctx) -> QuestionOption:
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
    )


def _mark_followup_options(
    options: list[QuestionOption], item_id: str, ctx
) -> list[QuestionOption]:
    """Flag options whose selection leads to a follow-up question.

    Purely derived from other catalog items' existing ``applicability``
    blocks (already used to gate conditional items), so a hint can be shown
    before the reporter picks an option without any new catalog authoring,
    and stays correct automatically as applicability-linked items are added,
    removed, or changed.
    """
    always, specific = _followup_trigger_values(item_id, ctx)
    if not always and not specific:
        return options
    return [
        QuestionOption(
            option.id,
            option.label,
            option.statement,
            option.exclusive,
            leads_to_followup=always or option.id in specific,
            readiness=option.readiness,
        )
        for option in options
    ]


def _followup_trigger_values(item_id: str, ctx) -> tuple[bool, set[str]]:
    """Return (always, specific_ids) describing which answers to ``item_id``
    cause another catalog item to become applicable."""
    always = False
    specific: set[str] = set()
    for other in ctx.catalog.get("items", []):
        if other.get("id") == item_id:
            continue
        found_always, found_values = _condition_triggers(other.get("applicability"), item_id)
        always = always or found_always
        specific.update(found_values)
    return always, specific


def _condition_triggers(condition: Any, item_id: str) -> tuple[bool, set[str]]:
    """Return whether/which answers to ``item_id`` satisfy one applicability condition.

    Negated conditions (``not``) are not represented as a positive hint,
    since "this triggers unless a specific answer is picked" doesn't map to
    a single triggering option.
    """
    if not isinstance(condition, dict):
        return False, set()
    if "all" in condition:
        children = [_condition_triggers(child, item_id) for child in condition["all"]]
    elif "any" in condition:
        children = [_condition_triggers(child, item_id) for child in condition["any"]]
    elif condition.get("item") == item_id:
        if condition.get("truthy") is True:
            return True, set()
        if "equals" in condition:
            return False, {str(condition["equals"])}
        if "in" in condition:
            return False, {str(value) for value in condition["in"]}
        return False, set()
    else:
        return False, set()
    always = any(found_always for found_always, _ in children)
    specific: set[str] = set()
    for _, found_values in children:
        specific.update(found_values)
    return always, specific


def _show_preface(item: dict, ctx, wizard: TerminalWizard) -> None:
    """Surface one deterministic-evidence note ahead of a human/AI question.

    Reuses the deterministic evaluator registry so preface content stays
    grounded in the same evidence-derived facts as ``deterministic`` items,
    instead of re-implementing lookups per catalog item.
    """
    name = item.get("preface_evaluator")
    if not name:
        return
    evaluator = _EVALUATORS.get(str(name))
    if evaluator is None:
        return
    statement, _evidence_refs, rationale = evaluator(item, ctx)
    if statement:
        wizard.show_note(statement, rationale)


def _human_statement(item: dict, answer: Any, source_package: str) -> str:
    template = substitute_source(str(item["template"]), source_package)
    options = item.get("question", {}).get("options", [])
    selected = answer if isinstance(answer, list) else [answer]
    option_statements = [
        substitute_source(str(option.get("statement", "")), source_package)
        for option in options
        if option.get("id") in selected and option.get("statement")
    ]
    if option_statements:
        return "\n".join(option_statements)
    answer_text = (
        ", ".join(str(value) for value in answer) if isinstance(answer, list) else str(answer)
    )
    if answer_text.strip().casefold() == "same as source":
        answer_text = source_package
    if "TBD" in template:
        return strip_todo_prefix(template.replace("TBD", answer_text, 1))
    return f"{strip_todo_prefix(template)} {answer_text}".strip()


_URL_ANSWER_PATTERN = re.compile(r"^https?://\S+$")


def _maybe_write_evidence(item: dict, ctx, answer_value: Any) -> None:
    """Backfill an evidence adapter field from a human answer, if declared.

    Lets a later catalog item's deterministic evaluator (e.g. the upstream
    project link check) benefit from a URL the reporter already typed while
    answering an earlier, differently-worded question, instead of asking
    twice or the consistency pass flagging a false contradiction between the
    two answers.
    """
    target = item.get("writes_evidence")
    if not isinstance(target, dict):
        return
    adapter_id = str(target.get("adapter", ""))
    field = str(target.get("field", ""))
    if not adapter_id or not field or not isinstance(answer_value, str):
        return
    candidate = answer_value.strip()
    if not _URL_ANSWER_PATTERN.match(candidate):
        return
    adapters = ctx.evidence.setdefault("adapters", {})
    adapter_data = adapters.setdefault(adapter_id, {})
    if not isinstance(adapter_data, dict) or adapter_data.get(field):
        return
    adapter_data[field] = candidate


def _unavailable(
    item: dict, readiness: ReadinessEffect, rationale: str, source_package: str
) -> StatementResult:
    return StatementResult(
        id=item["id"],
        section=item["section"],
        state=StatementState.UNAVAILABLE,
        readiness=readiness,
        statement=substitute_source(str(item["template"]), source_package),
        rationale=rationale,
    )


def _adapter(ctx, adapter_id: str) -> dict:
    value = ctx.evidence.get("adapters", {}).get(adapter_id, {})
    return value if isinstance(value, dict) else {}


@reporter_evaluator("source-availability")
def _source_availability(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "lp-package-api")
    if data.get("status") != "ok":
        return None, [], "Launchpad package data was unavailable"
    history = data.get("ubuntu_publish_history", [])
    components = sorted(
        {str(entry.get("component")) for entry in history if entry.get("component")}
    )
    if not history:
        return (
            f"The source package {ctx.source_package} has no published record in {ctx.series}.",
            ["lp-package-api:ubuntu_publish_history"],
            "The source must be published in Ubuntu before an MIR can proceed.",
        )
    component_text = ", ".join(components) if components else "unknown component"
    return (
        f"The source package {ctx.source_package} is published in Ubuntu ({component_text}).",
        ["lp-package-api:ubuntu_publish_history"],
        "" if "universe" in components else "The package is not confirmed in universe.",
    )


@reporter_evaluator("build-architectures")
def _build_architectures(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "lp-build-api")
    if data.get("status") != "ok":
        return None, [], "Launchpad build data was unavailable"
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
        return None, [], "No Launchpad build records were found"
    statement = "Current Launchpad builds pass on: " + (", ".join(passing) or "none") + "."
    rationale = "Non-passing build records: " + ", ".join(failing) if failing else ""
    return statement, ["lp-build-api:builds"], rationale


@reporter_evaluator("source-link")
def _source_link(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    return (
        f"Source package: https://launchpad.net/ubuntu/+source/{ctx.source_package}",
        [],
        "",
    )


@reporter_evaluator("prior-mir-history")
def _prior_mir_history(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "lp-mir-history")
    if data.get("status") != "ok":
        return None, [], "Prior MIR history was unavailable"
    bugs = data.get("prior_mir_bugs", [])
    if not bugs:
        return (
            "No prior MIR bug was found for this source or identified predecessor names.",
            ["lp-mir-history:prior_mir_bugs"],
            "",
        )
    links = [str(bug.get("web_link") or bug.get("id")) for bug in bugs[:20]]
    return (
        "Prior MIR history was found: " + ", ".join(links) + ".",
        ["lp-mir-history:prior_mir_bugs"],
        "Confirm whether the existing discussion should receive a new series task.",
    )


@reporter_evaluator("cve-history")
def _cve_history(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    ubuntu = _adapter(ctx, "ubuntu-cve-tracker")
    nvd = _adapter(ctx, "nvd-enrich")
    if ubuntu.get("status") != "ok" and nvd.get("status") != "ok":
        return None, [], "CVE evidence was unavailable"
    ids = sorted(
        {
            str(entry.get("id"))
            for entry in [*ubuntu.get("cves", []), *nvd.get("cves", [])]
            if isinstance(entry, dict) and entry.get("id")
        }
    )
    if not ids:
        return (
            "No package-associated CVEs were found in the queried trackers.",
            ["ubuntu-cve-tracker:cves", "nvd-enrich:cves"],
            "",
        )
    preview = ", ".join(ids[:20])
    suffix = f" (and {len(ids) - 20} more)" if len(ids) > 20 else ""
    return (
        f"The queried trackers found {len(ids)} associated CVE(s): {preview}{suffix}.",
        ["ubuntu-cve-tracker:cves", "nvd-enrich:cves"],
        "The reporter should verify relevance and describe handling history.",
    )


@reporter_evaluator("important-bugs")
def _important_bugs(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    ubuntu = _adapter(ctx, "lp-bug-search-api")
    debian = _adapter(ctx, "debian-bts")
    if ubuntu.get("status") != "ok" and debian.get("status") != "ok":
        return None, [], "Ubuntu and Debian bug data were unavailable"
    bugs = [*ubuntu.get("critical_bugs", []), *debian.get("rc_bugs", [])]
    if not bugs:
        return (
            "No critical Ubuntu or release-critical Debian bugs were found.",
            ["lp-bug-search-api:critical_bugs", "debian-bts:rc_bugs"],
            "",
        )
    labels = [str(bug.get("web_link") or bug.get("id") or bug.get("title")) for bug in bugs[:20]]
    return (
        f"Important open bugs found: {', '.join(labels)}.",
        ["lp-bug-search-api:critical_bugs", "debian-bts:rc_bugs"],
        "The reporter should explain their maintenance impact.",
    )


@reporter_evaluator("binary-security-surface")
def _binary_security_surface(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "binary-package-inspection")
    if data.get("status") != "ok":
        return None, [], "Built binary package inspection was unavailable"
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
    return (
        statement,
        [f"binary-package-inspection:{field}" for field in fields],
        "Explain the purpose and mitigations of each installed surface." if present else "",
    )


@reporter_evaluator("binary-integration-surface")
def _binary_integration_surface(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "binary-package-inspection")
    if data.get("status") != "ok":
        return None, [], "Built binary package inspection was unavailable"
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
    return statement, [f"binary-package-inspection:{field}" for field in fields], ""


@reporter_evaluator("build-tests")
def _build_tests(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "sbuild")
    if not data.get("build_log"):
        return None, [], "No build log was available"
    log_text = str(data["build_log"]).casefold()
    markers = [
        marker
        for marker in ("dh_auto_test", "pytest", "ctest", "make check", "meson test")
        if marker in log_text
    ]
    if markers:
        return (
            f"Build-time test execution was observed ({', '.join(markers)}).",
            ["sbuild:build_log"],
            "Verify that failures are not ignored.",
        )
    return (
        "No build-time test execution was identified in the collected build log.",
        ["sbuild:build_log"],
        "A reason or alternative test plan is required.",
    )


@reporter_evaluator("autopkgtests")
def _autopkgtests(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "autopkgtest-db")
    if data.get("status") != "ok":
        return None, [], "Autopkgtest data was unavailable"
    if not data.get("has_autopkgtest"):
        return (
            "No autopkgtest results were found for this source package.",
            ["autopkgtest-db:has_autopkgtest"],
            "A reason or alternative test plan is required.",
        )
    passing = ", ".join(sorted(data.get("passing_arches", []))) or "none"
    failing = ", ".join(sorted(data.get("failing_arches", [])))
    rationale = f"Failing architectures: {failing}" if failing else ""
    return (
        f"Autopkgtests are present and pass on: {passing}.",
        ["autopkgtest-db:passing_arches", "autopkgtest-db:failing_arches"],
        rationale,
    )


@reporter_evaluator("watch-file")
def _watch_file(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return None, [], "Packaging source data was unavailable"
    if str(data.get("debian_watch", "")).strip():
        return (
            "A debian/watch upstream-release mechanism is present.",
            ["packaging-source:debian_watch"],
            "",
        )
    return (
        "No debian/watch file was found.",
        ["packaging-source:debian_watch"],
        "Native packages or another documented update mechanism may be acceptable.",
    )


@reporter_evaluator("lintian")
def _lintian(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "lintian")
    if data.get("status") != "ok":
        return None, [], "Lintian evidence was unavailable"
    errors = data.get("lintian_errors", [])
    warnings = data.get("lintian_warnings", [])
    return (
        f"Lintian reported {len(errors)} error(s) and {len(warnings)} warning(s).",
        ["lintian:lintian_errors", "lintian:lintian_warnings"],
        "Review errors, warnings, and any overrides." if errors or warnings else "",
    )


@reporter_evaluator("source-packaging-metadata")
def _source_packaging_metadata(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return None, [], "Packaging source data was unavailable"
    maintainer = str(data.get("source_maintainer", "")).strip() or "missing"
    source_format = str(data.get("debian_source_format", "")).strip() or "unspecified"
    debconf = data.get("debconf_templates", [])
    overrides = data.get("debian_rules_overrides", [])
    statement = (
        f"Maintainer: {maintainer}; source format: {source_format}; "
        f"debconf templates: {len(debconf)}; debian/rules overrides: "
        f"{', '.join(overrides) if overrides else 'none'}."
    )
    concerning = [
        entry.get("template", "unknown")
        for entry in debconf
        if str(entry.get("priority", "")).casefold() in {"critical", "high"}
    ]
    rationale = (
        "High/critical debconf templates need review: " + ", ".join(concerning)
        if concerning
        else ""
    )
    return (
        statement,
        ["packaging-source:source_maintainer", "packaging-source:debconf_templates"],
        rationale,
    )


@reporter_evaluator("vendored-maintenance-docs")
def _vendored_maintenance_docs(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "packaging-source")
    if data.get("status") != "ok":
        return None, [], "Packaging source data was unavailable"
    vendored = data.get("shipped_vendored_dirs", [])
    if not vendored:
        return (
            "No shipped vendored directories were detected.",
            ["packaging-source:shipped_vendored_dirs"],
            "",
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
    return (
        statement,
        [
            "packaging-source:shipped_vendored_dirs",
            "packaging-source:debian_readme_source",
            "packaging-source:debian_copyright",
        ],
        "; ".join(gaps),
    )


@reporter_evaluator("dependencies")
def _dependencies(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "dep-analysis")
    if data.get("status") != "ok":
        return None, [], "Dependency analysis was unavailable"
    deps = sorted(data.get("in_scope_deps_not_in_main", data.get("deps_not_in_main", [])))
    if not deps:
        return (
            "No in-scope runtime dependencies outside main require a separate MIR.",
            ["dep-analysis:in_scope_deps_not_in_main"],
            "",
        )
    return (
        f"Runtime dependencies outside main require MIR handling: {', '.join(deps)}.",
        ["dep-analysis:in_scope_deps_not_in_main"],
        "Reference separate MIR bugs or include those sources in this request.",
    )


@reporter_evaluator("binary-packages")
def _binary_packages(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "dep-analysis")
    if data.get("status") != "ok":
        return None, [], "Dependency analysis was unavailable"
    packages = sorted(str(name) for name in data.get("binary_packages", []))
    if not packages:
        return None, [], "No binary packages were found for this source"
    return (
        f"This source builds the following binary packages: {', '.join(packages)}.",
        ["dep-analysis:binary_packages"],
        "",
    )


@reporter_evaluator("obsolete-dependencies")
def _obsolete_dependencies(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "dep-analysis")
    if data.get("status") != "ok":
        return None, [], "Dependency analysis was unavailable"
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
        return (
            "No Python 2, GTK 2, or other catalogued obsolete runtime dependency was found.",
            ["dep-analysis:runtime_deps"],
            "",
        )
    return (
        "Potential obsolete runtime dependencies: " + ", ".join(obsolete) + ".",
        ["dep-analysis:runtime_deps"],
        "Remove or replace obsolete dependencies before promotion.",
    )


@reporter_evaluator("recent-build")
def _recent_build(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "lp-build-api")
    if data.get("status") != "ok":
        return None, [], "Launchpad build evidence was unavailable"
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
        return (
            "No Launchpad build within the last three months was confirmed.",
            ["lp-build-api:builds"],
            "Provide a recent archive, test-rebuild, PPA, or local sbuild reference.",
        )
    links = [str(build.get("web_link", "")) for build in recent if build.get("web_link")]
    statement = f"Launchpad records contain {len(recent)} build(s) from the last three months."
    if links:
        statement += " Builds: " + ", ".join(links[:10]) + "."
    return statement, ["lp-build-api:builds"], ""


@reporter_evaluator("team-subscription")
def _team_subscription(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "team-mapping")
    if data.get("status") != "ok":
        return None, [], "Team subscription data was unavailable"
    teams = sorted(data.get("subscribed_teams", []))
    if teams:
        return (
            f"Package bug subscriber team(s): {', '.join(teams)}.",
            ["team-mapping:subscribed_teams"],
            "",
        )
    return (
        "No owning-team package bug subscription was found.",
        ["team-mapping:subscribed_teams"],
        "A team must subscribe before promotion.",
    )


@reporter_evaluator("upstream-link")
def _upstream_link(_item: dict, ctx) -> tuple[str | None, list[str], str]:
    data = _adapter(ctx, "upstream-tracker")
    url = str(data.get("upstream_url", "")).strip()
    if not url:
        return None, [], "No reliable upstream project URL was found"
    return f"Upstream project: {url}", ["upstream-tracker:upstream_url"], ""
