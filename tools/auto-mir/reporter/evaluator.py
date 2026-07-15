"""Catalog-driven evaluation for MIR reporter statements."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from reporter.models import (
    Provenance,
    QuestionKind,
    QuestionOption,
    QuestionSpec,
    ReadinessEffect,
    StatementResult,
    StatementState,
)
from reporter.wizard import TerminalWizard

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
    for item in ctx.catalog.get("items", []):
        mode = item["mode"]
        readiness = ReadinessEffect(item.get("readiness", "clear"))
        if mode == "human_only":
            question = _question_from_item(item)
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
            statement = _human_statement(item, str(answer.value), ctx.source_package)
            results.append(
                StatementResult(
                    id=item["id"],
                    section=item["section"],
                    state=StatementState.RESOLVED,
                    readiness=ReadinessEffect.CLEAR,
                    statement=statement,
                    provenance=Provenance.HUMAN,
                    answer_refs=[question.id],
                    human_confirmed=True,
                )
            )
            continue

        evaluator = _EVALUATORS.get(str(item.get("evaluator", "")))
        if evaluator is None:
            results.append(_unavailable(item, readiness, "deterministic evaluator unavailable"))
            continue
        statement, evidence_refs, rationale = evaluator(item, ctx)
        if statement is None:
            results.append(_unavailable(item, readiness, rationale))
            continue
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
    return results


def _question_from_item(item: dict) -> QuestionSpec:
    definition = item["question"]
    kind = QuestionKind(definition["kind"])
    options = tuple(
        QuestionOption(str(option["id"]), str(option["label"]))
        for option in definition.get("options", [])
    )
    return QuestionSpec(
        id=item["id"],
        prompt=str(definition["prompt"]),
        kind=kind,
        required=bool(item.get("required", True)),
        options=options,
        hint=str(definition.get("hint", "")),
        default=definition.get("default"),
    )


def _human_statement(item: dict, answer: str, source_package: str) -> str:
    template = str(item["template"]).replace("TBDSRC", source_package)
    if "TBD" in template:
        return template.replace("TBD", answer, 1).removeprefix("TODO: ")
    return f"{template.removeprefix('TODO: ')} {answer}".strip()


def _unavailable(item: dict, readiness: ReadinessEffect, rationale: str) -> StatementResult:
    return StatementResult(
        id=item["id"],
        section=item["section"],
        state=StatementState.UNAVAILABLE,
        readiness=readiness,
        statement=str(item["template"]),
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
