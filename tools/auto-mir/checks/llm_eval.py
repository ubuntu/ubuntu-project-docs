"""LLM-based check evaluators for auto-mir.

Contains ev_to_ai, ai, and human_only evaluators, plus all LLM helper
functions for prompt rendering, evidence assembly, and response mapping.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from checks.messages import render_check_message
from models import Finding
from reporter.text_utils import strip_todo_and_dash_prefix
from utils import llm_evidence, llm_sanitize

if TYPE_CHECKING:
    from auto_mir import RunContext

log = logging.getLogger("auto_mir.checks.llm_eval")

_PROMPT_LARGE_THRESHOLD_CHARS = 24000
_EVIDENCE_LARGE_THRESHOLD_CHARS = 12000
_MAX_ADDITIONAL_EVIDENCE_REQUESTS = 3

# Input-sizing budgets. Synthesis checks (SUM-5 overall verdict, SUM-6
# security-review-needed) must reason over essentially all of the run, so they
# get much larger caps than per-check evaluations. Caps still exist as a cost
# guardrail, just set high; the large model's context is not the bottleneck.
_DEFAULT_FINDING_MESSAGE_CHARS = 200
_SYNTHESIS_FINDING_MESSAGE_CHARS = 1500
_DEFAULT_REPORTER_SNIPPET_CHARS = 2000
_SYNTHESIS_REPORTER_CONTENT_CHARS = 20000

# Checks that must receive specific large adapter fields verbatim (bounded only
# by a generous cap) rather than the short summary preview, because the check's
# judgement depends on the full content.
_FULL_CONTENT_FIELDS_BY_CHECK: dict[str, set[str]] = {
    "PRF-9": {"debian_rules"},
    "CB-3": {"debian_tests_control"},
}


def _eval_ev_to_ai(
    check: dict,
    ctx: RunContext,
    finding: Finding,
    *,
    evidence_payload: dict | None = None,
    model_tier: str | None = None,
    fallback_suffix: str = "manual review needed (LLM unavailable)",
    fallback_rationale: bool = True,
    refine: bool = True,
) -> Finding:
    """Evaluate a check by combining collected evidence with an LLM call.

    Assembles the evidence payload relevant to this check, renders the
    ev_to_ai.md prompt template, calls the LLM, and maps the response back
    to a finding dict.  Falls back to a manual-review TODO on any failure.
    ``ai`` checks reuse this path with their own full-findings payload, a
    fixed large tier and no refinement step.
    """
    import llm

    # (``is True`` so a test-double ctx with an auto-created attribute can
    # never trip the deliberate-mode path.)
    if getattr(ctx, "no_llm", False) is True:
        # --no-llm: no call is attempted at all; degrade to the standard
        # fallback (with the check's deterministic facts as the rationale) so
        # the draft states this was a deliberate deterministic-only run.
        _apply_llm_unavailable_fallback(
            check,
            finding,
            "disabled by --no-llm",
            fallback_suffix=fallback_suffix,
        )
        if fallback_rationale:
            finding.rationale = _fallback_rationale_for_check(check, ctx)
        return finding

    if evidence_payload is None:
        evidence_payload = _build_evidence_payload(check, ctx)
    policy_excerpt = _build_policy_excerpt(check, ctx)
    prompt = _render_ev_to_ai_prompt(check, evidence_payload, policy_excerpt, ctx)

    # Synthesis checks always use the large tier; their inputs are intentionally
    # large and they reason over the whole run. Other ev_to_ai checks select the
    # tier from prompt/evidence complexity, with the one-shot larger-budget retry
    # in call_llm() as the backstop when a reasoning model overflows.
    if model_tier is None:
        if check.get("synthesis"):
            model_tier = "large"
        else:
            model_tier = _select_ev_to_ai_model_tier(prompt, evidence_payload)

    try:
        response = llm.call_llm(prompt, ctx, model_tier=model_tier, trace_label=check["id"])
    except llm.LLMError as exc:
        log.warning("LLM call failed for check %s: %s", check["id"], exc)
        finding.llm_error_cause = str(exc)
        _apply_llm_unavailable_fallback(
            check,
            finding,
            exc,
            fallback_suffix=fallback_suffix,
        )
        if fallback_rationale:
            # Even when the model is unavailable, surface any deterministic evidence
            # already gathered (e.g. dup-search candidates for RDO-1) so the reviewer
            # is not left with a bare TODO.
            finding.rationale = _fallback_rationale_for_check(check, ctx)
        return finding

    if refine:
        response = _maybe_refine_with_additional_evidence(
            check,
            ctx,
            response,
            evidence_payload,
            policy_excerpt,
            model_tier,
        )

    return _apply_llm_response(response, check, finding)


def _eval_ai(check: dict, ctx: RunContext, finding: Finding) -> Finding:
    """Evaluate checks that require pure AI synthesis over the full findings set.

    Uses the same LLM path as ev_to_ai but passes the full evidence store rather
    than check-specific adapters.  Used for checks like SUM-5 (overall verdict).
    """
    # Pure-AI synthesis checks (e.g. SUM-5 overall verdict) must see essentially
    # all the information, so include the full reporter MIR content and larger
    # per-finding messages rather than the compact per-check budgets.
    full_evidence = {
        "source_package": ctx.source_package,
        "bug_id": ctx.bug_id,
        "series": ctx.series,
        "bug_title": _wrap_untrusted(ctx, "bug_title", ctx.bug.get("title", "")),
        "reporter_mir_content_present": bool(ctx.reporter_mir_content),
        "reporter_mir_content": _wrap_untrusted(
            ctx,
            "reporter_mir_content",
            (ctx.reporter_mir_content or "")[:_SYNTHESIS_REPORTER_CONTENT_CHARS],
        ),
        "findings_so_far": _summarise_findings_so_far(
            ctx, max_message_len=_SYNTHESIS_FINDING_MESSAGE_CHARS
        ),
    }
    return _eval_ev_to_ai(
        check,
        ctx,
        finding,
        evidence_payload=full_evidence,
        model_tier="large",
        fallback_suffix="requires AI synthesis",
        fallback_rationale=False,
        refine=False,
    )


def _eval_human_only(check: dict, ctx: RunContext, finding: Finding) -> Finding:
    """Evaluate checks that require human judgment only."""
    finding.mark_unknown(
        message=render_check_message(check, "human_only_message"),
        todo=render_check_message(check, "human_only_todo", title=check.get("title", "Check")),
    )
    return finding


def _apply_llm_unavailable_fallback(
    check: dict,
    finding: Finding,
    error: Exception | str,
    *,
    fallback_suffix: str,
) -> None:
    """Apply the standard unknown/low-confidence fallback for LLM outages.

    ``error`` carries the reason into the rendered message (an exception
    from a failed call, or a plain string for deliberate degradation such
    as --no-llm).
    """
    finding.mark_unknown(
        message=render_check_message(check, "llm_unavailable_message", error=str(error)),
        todo=_default_todo_for_check(check, fallback_suffix=fallback_suffix),
    )


def _wrap_untrusted(ctx: RunContext, label: str, text: str) -> str:
    """Wrap attacker-controllable text in a per-run untrusted-data envelope.

    Uses the run's nonce (ctx.untrusted_nonce) so injected content cannot forge
    the closing delimiter. Falls back to a fresh nonce if the context predates
    nonce assignment (e.g. in unit tests).
    """
    nonce = getattr(ctx, "untrusted_nonce", None) or llm_sanitize.make_nonce()
    return llm_sanitize.wrap_untrusted(label, text, nonce)


def _spotlight_lp_bug_api(ctx: RunContext, data: dict) -> dict:
    """Wrap the attacker-controllable fields of the lp-bug-api adapter output.

    bug_title, bug_description, and bug_comments originate from Launchpad bug
    text that anyone can post, so they are neutralised and enveloped before
    reaching the LLM. Other fields (subscribers, tags, package, series) are
    left untouched.
    """
    if not isinstance(data, dict):
        return data
    result = dict(data)
    if "bug_title" in result:
        result["bug_title"] = _wrap_untrusted(ctx, "bug_title", str(result.get("bug_title") or ""))
    if "bug_description" in result:
        result["bug_description"] = _wrap_untrusted(
            ctx, "bug_description", str(result.get("bug_description") or "")
        )
    comments = result.get("bug_comments")
    if isinstance(comments, list):
        result["bug_comments"] = [
            _wrap_untrusted(ctx, f"bug_comment[{i}]", str(comment))
            for i, comment in enumerate(comments)
        ]
    return result


def _build_evidence_payload(check: dict, ctx: RunContext) -> dict:
    """Build a compact evidence dict for the adapters required by this check.

    Only includes adapter outputs listed in adapters_required/adapters_optional
    for the check, plus basic package/bug metadata.  Large raw strings are
    truncated to keep prompt size manageable.

    For ESL-1 specifically, also extracts build hints from fetch-build to detect
    embedded source usage patterns.
    """
    payload: dict = {
        "source_package": ctx.source_package,
        "bug_id": ctx.bug_id,
        "series": ctx.series,
        "bug_title": _wrap_untrusted(ctx, "bug_title", ctx.bug.get("title", "")),
    }

    adapters_store = ctx.evidence.get("adapters", {})
    relevant = list(check.get("adapters_required", [])) + list(check.get("adapters_optional", []))
    # Some checks need specific large fields verbatim rather than a short
    # preview (e.g. PRF-9 must see the whole debian/rules to judge cleanliness).
    keep_full_fields = _FULL_CONTENT_FIELDS_BY_CHECK.get(check.get("id", ""), set())
    for adapter_id in relevant:
        data = adapters_store.get(adapter_id)
        if data is None:
            payload[adapter_id] = {"status": "not_collected"}
        else:
            truncated = llm_evidence.truncate_adapter_data(
                data, adapter_id=adapter_id, keep_full_fields=keep_full_fields
            )
            if adapter_id == "lp-bug-api":
                truncated = _spotlight_lp_bug_api(ctx, truncated)
            payload[adapter_id] = truncated

    # For ESL-1, enhance with build hints extracted from the fetch-build log
    if check.get("id") == "ESL-1":
        fetch_build_data = adapters_store.get("fetch-build", {})
        build_log = fetch_build_data.get("build_log", "")
        if build_log:
            payload["build_hints"] = _extract_build_hints(build_log)

    # For SUM-3, surface a deterministically computed promotion status so the
    # model only has to phrase the result rather than re-derive it from a
    # (necessarily truncated) debian/control excerpt — see decisions.md
    # "Correction: already in main signal was wrong" (2026-08-05).
    if check.get("id") == "SUM-3":
        payload["promotion_status"] = _compute_promotion_status(ctx, adapters_store)

    # For CB-2, surface concrete build-time test wiring signals from
    # debian/rules and the build log so the model can decide rather than echo
    # the template TODO.
    if check.get("id") == "CB-2":
        fetch_build_data = adapters_store.get("fetch-build", {})
        packaging_data = adapters_store.get("packaging-source", {})
        payload["build_test_hints"] = _extract_build_test_hints(
            packaging_data.get("debian_rules", ""),
            fetch_build_data.get("build_log", ""),
        )

    # For CB-6, surface a compact, prioritised consumer summary so the most
    # decision-relevant reverse-dep consumers (those that actually have
    # autopkgtests) survive generic list truncation.
    if check.get("id") == "CB-6":
        payload["consumer_test_summary"] = _summarise_consumer_autopkgtests(adapters_store)

    # Always include compact bug context. Synthesis checks (e.g. SUM-6
    # security-review-needed) need the full picture, so they get a much larger
    # reporter-content cap and the accumulated section findings.
    is_synthesis = bool(check.get("synthesis"))
    snippet_cap = (
        _SYNTHESIS_REPORTER_CONTENT_CHARS if is_synthesis else _DEFAULT_REPORTER_SNIPPET_CHARS
    )
    payload["reporter_mir_content_snippet"] = _wrap_untrusted(
        ctx, "reporter_mir_content", (ctx.reporter_mir_content or "")[:snippet_cap]
    )
    if is_synthesis:
        payload["findings_so_far"] = _summarise_findings_so_far(
            ctx, max_message_len=_SYNTHESIS_FINDING_MESSAGE_CHARS
        )
    payload["bug_subscribers"] = ctx.bug.get("subscribers", [])
    payload["bug_tags"] = ctx.bug.get("tags", [])

    return payload


def _select_ev_to_ai_model_tier(prompt: str, evidence_payload: dict) -> str:
    """Select model tier for evidence-to-AI checks.

    Use the small tier by default, and upgrade to large tier when the prompt or
    serialized evidence payload exceeds conservative complexity thresholds.
    """
    prompt_len = len(prompt)
    evidence_len = len(json.dumps(evidence_payload, default=str))
    if prompt_len >= _PROMPT_LARGE_THRESHOLD_CHARS:
        return "large"
    if evidence_len >= _EVIDENCE_LARGE_THRESHOLD_CHARS:
        return "large"
    return "small"


def _maybe_refine_with_additional_evidence(
    check: dict,
    ctx: RunContext,
    response: dict,
    evidence_payload: dict,
    policy_excerpt: str,
    model_tier: str,
) -> dict:
    """Run one follow-up LLM pass when it requests additional evidence snippets."""
    import llm

    requests = _extract_additional_evidence_requests(response)
    if not requests:
        return response

    requested_evidence = _build_additional_requested_evidence(ctx, requests)
    if not requested_evidence:
        return response

    follow_up_payload = dict(evidence_payload)
    follow_up_payload["additional_evidence_requested"] = requested_evidence
    follow_up_prompt = _render_ev_to_ai_prompt(check, follow_up_payload, policy_excerpt, ctx)

    try:
        return llm.call_llm(
            follow_up_prompt, ctx, model_tier=model_tier, trace_label=f"{check['id']}-followup"
        )
    except llm.LLMError as exc:
        log.warning(
            "Follow-up LLM call failed for check %s after additional requests: %s",
            check["id"],
            exc,
        )
        return response


def _extract_additional_evidence_requests(response: dict) -> list[dict | str]:
    if not isinstance(response, dict):
        return []
    raw = response.get("additional_evidence_requests", [])
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return []
    return raw[:_MAX_ADDITIONAL_EVIDENCE_REQUESTS]


def _build_additional_requested_evidence(ctx: RunContext, requests: list[dict | str]) -> dict:
    adapters_store = ctx.evidence.get("adapters", {})
    fetch_build_data = adapters_store.get("fetch-build", {})
    build_log = fetch_build_data.get("build_log", "")
    if not isinstance(build_log, str) or not build_log:
        return {}

    snippets = _resolve_build_log_requests(build_log, requests)
    if not snippets:
        return {}
    return {"fetch-build": {"build_log_snippets": snippets}}


def _resolve_build_log_requests(build_log: str, requests: list[dict | str]) -> list[dict]:
    lines = build_log.splitlines()
    snippets: list[dict] = []
    for req in requests:
        parsed = _parse_build_log_request(req)
        if not parsed:
            continue
        req_type = parsed.get("type")
        if req_type == "line_range":
            start = int(parsed["start"])
            end = int(parsed["end"])
            snippets.append(
                {
                    "request": parsed,
                    "lines": llm_evidence.line_slice(lines, start, end),
                }
            )
            continue
        if req_type == "pattern":
            snippets.append(
                {
                    "request": parsed,
                    "matches": _build_log_pattern_matches(
                        lines,
                        parsed["pattern"],
                        int(parsed.get("max_matches", 20)),
                    ),
                }
            )
    return snippets


def _parse_build_log_request(request: dict) -> dict | None:
    if isinstance(request, dict):
        req_type = str(request.get("type", "")).strip().lower()
        if req_type == "line_range":
            try:
                start = int(request.get("start"))
                end = int(request.get("end"))
            except (TypeError, ValueError):
                return None
            if start <= 0 or end < start:
                return None
            return {"type": "line_range", "start": start, "end": end}
        if req_type == "pattern":
            pattern = str(request.get("pattern", "")).strip()
            if not pattern:
                return None
            max_matches = request.get("max_matches", 20)
            try:
                max_matches = int(max_matches)
            except (TypeError, ValueError):
                max_matches = 20
            return {
                "type": "pattern",
                "pattern": pattern,
                "max_matches": max(1, min(max_matches, 50)),
            }
        return None

    return None


def _build_log_pattern_matches(lines: list[str], pattern: str, max_matches: int) -> list[dict]:
    try:
        regex = re.compile(pattern)
    except re.error:
        return [{"error": f"invalid regex: {pattern}"}]

    matches = []
    for idx, line in enumerate(lines, start=1):
        if regex.search(line):
            matches.append({"line": idx, "text": line})
            if len(matches) >= max_matches:
                break
    return matches


def _build_policy_excerpt(check: dict, ctx: RunContext) -> str:
    """Extract relevant policy text for a check from the MIR reviewer template.

    Combines:
    - The check's ai_policy field (specific reviewer guidance)
    - The todo_refs list (what this check resolves)
    - RULE lines from the matching section in mir-reviewers-template.md
    """
    section = check.get("section", "")
    todo_refs = check.get("todo_refs", [])
    ai_policy = check.get("ai_policy", "")

    parts = []
    if ai_policy:
        parts.append(f"AI policy for this check:\n{ai_policy.strip()}")

    if todo_refs:
        parts.append(
            "TODO references this check resolves:\n" + "\n".join(f"  {t}" for t in todo_refs)
        )

    # Pull RULE lines from the reviewer template for this section
    workspace_root = getattr(ctx, "workspace_root", None)
    if workspace_root:
        template_path = Path(workspace_root) / "docs" / "MIR" / "mir-reviewers-template.md"
        if template_path.exists():
            section_text = _extract_template_section(template_path, section)
            rule_lines = [
                line for line in section_text.splitlines() if line.strip().startswith("RULE:")
            ]
            if rule_lines:
                parts.append(
                    f"Reviewer policy rules for [{section}]:\n" + "\n".join(rule_lines[:30])
                )

    return "\n\n".join(parts) if parts else f"Check {check.get('id')} in section [{section}]"


def _extract_template_section(template_path: Path, section: str) -> str:
    """Return the raw text of a named section from the MIR reviewer template."""
    try:
        text = template_path.read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(
        rf"^\[{re.escape(section)}\]\s*\n(.*?)(?=^\[|\Z)",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    return match.group(1) if match else ""


def _extract_build_test_hints(debian_rules: str, build_log: str) -> dict:
    """Extract concrete build-time test signals from debian/rules and build log.

    Surfaces the markers an MIR reviewer would look for when judging CB-2:
    - rules wiring: dh_auto_test / override_dh_auto_test, DEB_BUILD_OPTIONS
      nocheck, and explicit test runners (make check/test, pytest, meson test,
      ctest, go test, cargo test)
    - whether test failures are ignored (e.g. ``... || true`` around tests)
    - build-log evidence that tests actually ran (test/PASS/FAIL markers)

    The result is advisory evidence for the CB-2 LLM check, not a verdict.
    """
    # Lowercase and inline make variables ($(CARGO) test -> cargo test) so a
    # runner invoked through a variable still matches its plain marker.
    rules_lower = re.sub(r"\$\(([A-Za-z0-9_]+)\)", r"\1", (debian_rules or "").lower())
    log_lower = (build_log or "").lower()

    runner_markers = [
        "dh_auto_test",
        "override_dh_auto_test",
        "make check",
        "make test",
        "pytest",
        "meson test",
        "ctest",
        "go test",
        "cargo test",
    ]
    # Word-boundary matching so adjacent names cannot cross-match: plain
    # substring tests would find "go test" inside "cargo test".
    rules_runners = [
        marker
        for marker in runner_markers
        if re.search(rf"(?<![\w-]){re.escape(marker)}(?![\w-])", rules_lower)
    ]

    failures_possibly_ignored = bool(
        re.search(r"(dh_auto_test|make\s+(check|test)|pytest|ctest)[^\n]*\|\|\s*true", rules_lower)
    )

    log_runs_tests = any(
        marker in log_lower
        for marker in (
            "running tests",
            "make check",
            "make test",
            "test session starts",
            "ctest",
            "test result:",  # cargo's per-suite summary line
        )
    )
    log_pass_fail = bool(re.search(r"\b(\d+\s+passed|tests? passed|pass|fail(ed)?)\b", log_lower))

    return {
        "rules_test_runners": rules_runners,
        "rules_has_test_wiring": bool(rules_runners),
        "nocheck_in_rules": "nocheck" in rules_lower,
        "failures_possibly_ignored": failures_possibly_ignored,
        "build_log_runs_tests": log_runs_tests,
        "build_log_has_pass_fail": log_pass_fail,
    }


def _summarise_consumer_autopkgtests(adapters_store: dict) -> dict:
    """Build a compact, prioritised summary of reverse-dep consumer tests.

    Consumers that actually have autopkgtests are the decision-relevant ones for
    CB-6, so they are listed first (capped) followed by a count of the rest. The
    reverse-dep release used is surfaced so the reviewer knows what was queried.
    """
    reverse_deps = adapters_store.get("reverse-deps", {})
    consumer_tests = adapters_store.get("consumer-autopkgtests", {})

    consumers = consumer_tests.get("consumers", []) or []
    with_tests = [c for c in consumers if c.get("has_autopkgtest")]
    without_tests = [c for c in consumers if not c.get("has_autopkgtest")]

    _CAP = 15
    return {
        "reverse_deps_status": reverse_deps.get("status", "not_collected"),
        "consumer_autopkgtests_status": consumer_tests.get("status", "not_collected"),
        "reverse_deps_release": reverse_deps.get("release", ""),
        "reverse_deps_note": reverse_deps.get("note", ""),
        "consumer_autopkgtests_note": consumer_tests.get("note", ""),
        "total_consumers": len(consumers),
        "consumers_with_tests": with_tests[:_CAP],
        "consumers_with_tests_count": len(with_tests),
        "consumers_without_tests": [
            {"source": c.get("source", ""), "kind": c.get("kind", "")} for c in without_tests[:_CAP]
        ],
        "consumers_without_tests_count": len(without_tests),
    }


def _compute_promotion_status(ctx: RunContext, adapters_store: dict) -> dict:
    """Deterministically compute which built binaries still need promotion.

    Uses lp-package-api's ``current_component`` (the source's current archive
    placement for the target series, equivalent to ``rmadison``) rather than
    asking the model to infer promotion status from a debian/control excerpt
    that generic evidence truncation may cut off before any binary Package
    stanza. Binary names come from ``ctx.requested_binaries`` (resolved during
    evidence collection), falling back to dep-analysis's ``binary_packages``
    when unset (e.g. in tests that construct a bare ctx).
    """
    lp_package = adapters_store.get("lp-package-api", {})
    current_component = (
        lp_package.get("current_component", "unknown")
        if isinstance(lp_package, dict)
        else "unknown"
    )

    binaries = list(getattr(ctx, "requested_binaries", None) or [])
    if not binaries:
        dep_analysis = adapters_store.get("dep-analysis", {})
        if isinstance(dep_analysis, dict):
            binaries = list(dep_analysis.get("binary_packages", []) or [])

    already_in_main = current_component == "main"
    needs_promotion = [] if already_in_main else list(binaries)

    return {
        "current_component": current_component,
        "binaries": binaries,
        "already_in_main": already_in_main,
        "needs_promotion": needs_promotion,
    }


def _extract_build_hints(build_log: str) -> dict:
    """Extract hints from the fetch-build build log indicating embedded source usage.

    Looks for:
    - Static linking flags (-static, -Wl,--whole-archive, etc.)
    - Compiler invocations mentioning vendor, third_party, vendored paths
    - Archive operations (ar, ranlib) on potential vendor libraries
    - References to embedded source directories in build output

    Returns dict with lists of relevant lines grouped by category.
    """
    hints = {
        "static_flags": [],
        "vendor_compile_invocations": [],
        "vendor_archive_ops": [],
        "vendor_path_references": [],
    }

    if not build_log:
        return hints

    vendor_patterns = [r"vendor/", r"third_party/", r"vendored/", r"third-party"]

    for line in build_log.splitlines():
        # Look for static linking indicators
        if "-static" in line or "-Wl,--whole-archive" in line or "Static-Built-Using" in line:
            hints["static_flags"].append(line.strip())

        # Look for compiler invocations with vendor paths
        if re.search(
            r"(gcc|clang|cc|g\+\+|c\+\+|rustc|cargo).*(" + "|".join(vendor_patterns) + ")", line
        ):
            hints["vendor_compile_invocations"].append(line.strip())

        # Look for archive operations on vendor paths
        if re.search(r"(ar|ranlib|llvm-ar).*(" + "|".join(vendor_patterns) + ")", line):
            hints["vendor_archive_ops"].append(line.strip())

        # Look for general references to vendor directories
        if any(pattern in line for pattern in vendor_patterns):
            # Only add if it looks like an actionable build line
            if re.search(r"(gcc|clang|cc|rustc|cargo|ar|ranlib|g\+\+|c\+\+|ld|nm)", line):
                hints["vendor_path_references"].append(line.strip())

    # Deduplicate while preserving order
    for key in hints:
        seen = set()
        deduped = []
        for item in hints[key]:
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        hints[key] = deduped[:20]  # Cap at 20 lines per category to keep payload manageable

    return hints


def _render_ev_to_ai_prompt(
    check: dict,
    evidence_payload: dict,
    policy_excerpt: str,
    ctx,
) -> str:
    """Render the ev_to_ai.md prompt template with check-specific substitutions."""
    tool_root = getattr(ctx, "tool_root", None)
    template_path = Path(tool_root) / "prompts" / "ev_to_ai.md"
    template = template_path.read_text(encoding="utf-8")

    confidence_model = (
        ctx.catalog.get("global_policies", {})
        .get("confidence_model", {})
        .get("description", "low | medium | high")
    )

    substitutions = {
        "{{check_id}}": check.get("id", ""),
        "{{check_title}}": check.get("title", ""),
        "{{section}}": check.get("section", ""),
        "{{todo_refs}}": "\n".join(check.get("todo_refs", [])),
        "{{options}}": _render_options_for_prompt(check),
        "{{policy_excerpt}}": policy_excerpt,
        "{{evidence_json}}": json.dumps(evidence_payload, indent=2, default=str),
        "{{confidence_model}}": confidence_model,
    }
    result = template
    for placeholder, value in substitutions.items():
        result = result.replace(placeholder, value)
    return result


def _render_options_for_prompt(check: dict) -> str:
    """Describe selectable options so the model returns a ``selected_option`` id.

    Only non-Summary ev_to_ai/ai option checks are wired for option selection;
    for all other checks this returns an explicit "no options" note so the model
    falls back to returning status/severity directly.
    """
    options = check.get("options")
    if not options or check.get("mode") not in {"ev_to_ai", "ai"}:
        return "No predefined options for this check; return status/severity directly."
    if check.get("section") == "Summary":
        return "No predefined options for this check; return status/severity directly."
    lines = [
        "Select exactly one option by returning its id in the 'selected_option' field.",
        "Each option's statement will be emitted verbatim; put your reasoning in 'rationale'.",
    ]
    for opt in options:
        opt_id = str(opt.get("id", "")).strip()
        render_text = str(opt.get("render", "")).strip()
        predicate = str(opt.get("predicate", "")).strip()
        outcome = str(opt.get("outcome", "")).strip()
        lines.append(f"  - {opt_id} (outcome={outcome}): {render_text} [when: {predicate}]")
    return "\n".join(lines)


def _apply_llm_response(response: dict, check: dict, finding: Finding) -> Finding:
    """Map a validated LLM JSON response back onto a finding dict.

    Accepts partial responses — only overrides fields that are present and
    non-empty in the response.  Always marks the finding as requiring human
    confirmation regardless of what the model returns.
    """
    if not isinstance(response, dict):
        log.warning("LLM response for %s is not a dict: %r", check["id"], response)
        finding.mark_unknown(
            message=finding.message,
            todo=_default_todo_for_check(check, fallback_suffix="LLM response invalid"),
        )
        return finding

    # Option-based ev_to_ai checks are wired so the model picks one option id and
    # we emit that option's canonical template statement at its declared outcome
    # severity, keeping the draft template-faithful rather than free-form prose.
    option = _resolve_selected_option(response, check)
    if option is not None:
        applied = _apply_option_response(option, response, check, finding)
        return _enforce_human_verdict(applied, check, response)

    valid_statuses = {"ok", "not-ok", "unknown"}
    valid_severities = {"ok", "recommended", "required", "nack"}
    valid_confidences = {"low", "medium", "high"}

    status = response.get("status", "unknown")
    if status not in valid_statuses:
        status = "unknown"

    severity = response.get("severity", "ok")
    if severity not in valid_severities:
        severity = "ok"

    confidence = response.get("confidence", "medium")
    if confidence not in valid_confidences:
        confidence = "medium"
    # The model may report "high" for a clear-cut verdict; that is honoured so a
    # confident AI failure can be surfaced as a Problem/Required TODO. Human
    # confirmation is still always required (set below).

    message = (response.get("message") or "").strip()
    resolved_message = message or finding.message

    todo = (response.get("todo") or "").strip()
    rationale = (response.get("rationale") or "").strip()

    if status != "ok":
        # [Summary] option checks (e.g. SUM-5/SUM-6) must keep all variants
        # visible for human final judgment when unresolved.
        if check.get("section") == "Summary" and check.get("options"):
            todo_refs = [str(x).strip() for x in check.get("todo_refs", []) if str(x).strip()]
            if todo_refs:
                todo = "\n".join(todo_refs)

        if todo and not (todo.startswith("TODO:") or todo.startswith("TODO-")):
            prefix_inner = "" if todo.startswith("- ") else "- "
            todo = f"TODO: {prefix_inner}{todo}"
        if not todo:
            todo = _default_todo_for_check(check, fallback_suffix="review needed")
        if status == "unknown":
            finding.mark_unknown(
                message=resolved_message,
                todo=todo,
                severity=severity,
                confidence=confidence,
                rationale=rationale,
            )
        else:
            finding.fail(
                message=resolved_message,
                todo=todo,
                severity=severity,
                confidence=confidence,
                rationale=rationale,
            )
    else:
        # Prefer the catalog's canonical OK statement over free-form model prose
        # so the reviewer sees the familiar template wording; the rationale is
        # kept in its own field and composed into a parenthetical by the renderer.
        finding.succeed(resolved_message, confidence=confidence, rationale=rationale)
        canonical = _canonical_ok_statement(check)
        if canonical:
            finding.message = canonical

    finding.apply_ai_metadata(
        risk_flags=response.get("risk_flags", []),
        evidence_refs=response.get("evidence_refs", []),
        human_confirmation_required=True,
    )

    return _enforce_human_verdict(finding, check, response)


# Matches a leading "TODO:" / "TODO-X:" (possibly repeated) plus an optional
# "- " list marker, so a catalog todo_ref can be reduced to its statement text.


def _canonical_ok_statement(check: dict) -> str:
    """Return the canonical OK statement for a single-statement ev_to_ai check.

    For checks that map to exactly one template statement (most SEC/DEP/RDO
    checks), the reviewer expects the familiar template wording rather than
    free-form model prose. Returns an empty string when the check has options
    (handled separately), is a Summary decision check, has multiple candidate
    statements, or the statement is a placeholder (TBD / <...>), in which case
    the caller keeps the model's message.
    """
    if check.get("options") or check.get("section") == "Summary":
        return ""
    if check.get("mode") != "ev_to_ai":
        return ""
    todo_refs = [str(x).strip() for x in check.get("todo_refs", []) if str(x).strip()]
    if len(todo_refs) != 1:
        return ""
    statement = strip_todo_and_dash_prefix(todo_refs[0])
    if not statement or "TBD" in statement or "<" in statement:
        return ""
    return statement


def _resolve_selected_option(response: dict, check: dict) -> dict | None:
    """Return the catalog option the model selected, or None.

    Only applies to non-Summary ev_to_ai/ai option checks. The model may name
    the option by its id (e.g. "PRF-1-B") or by its todo_ref (e.g. "TODO-B").
    """
    options = check.get("options")
    if not options or check.get("mode") not in {"ev_to_ai", "ai"}:
        return None
    if check.get("section") == "Summary":
        return None
    selected = str(response.get("selected_option", "")).strip()
    if not selected:
        return None
    for opt in options:
        if str(opt.get("id", "")).strip() == selected:
            return opt
    for opt in options:
        if str(opt.get("todo_ref", "")).strip() == selected:
            return opt
    return None


def _apply_option_response(option: dict, response: dict, check: dict, finding: Finding) -> Finding:
    """Render a selected option's canonical statement at its declared outcome."""
    render_text = str(option.get("render", "")).strip()
    message = render_text[2:].strip() if render_text.startswith("- ") else render_text
    outcome = option.get("outcome", "ok")
    rationale = (response.get("rationale") or "").strip()

    confidence = response.get("confidence", "medium")
    if confidence not in {"low", "medium", "high"}:
        confidence = "medium"
    # The model's confidence is honoured (including "high" for a clear-cut
    # option selection); human confirmation is still required (set below).

    if outcome == "ok":
        finding.succeed(message=message, confidence=confidence, rationale=rationale)
    else:
        todo = render_text or str(option.get("todo_ref", "")).strip()
        if not (todo.startswith("TODO:") or todo.startswith("TODO-")):
            prefix_inner = "" if todo.startswith("- ") else "- "
            todo = f"TODO: {prefix_inner}{todo}"
        finding.fail(
            message=message,
            todo=todo,
            severity=outcome,
            confidence=confidence,
            rationale=rationale,
        )

    finding.selected_option = str(option.get("id", "")).strip()
    finding.apply_ai_metadata(
        risk_flags=response.get("risk_flags", []),
        evidence_refs=response.get("evidence_refs", []),
        human_confirmation_required=True,
    )
    return finding


def _enforce_human_verdict(finding: Finding, check: dict, response: dict) -> Finding:
    """A ``human_verdict`` check is ALWAYS a human decision point.

    The AI synthesis stays as an advisory NOTE; the finding is forced to
    unknown with the full option TODO block (e.g. SUM-5's ACK / NACK /
    ACK-under-conditions) kept verbatim so the reviewer prunes, not writes.
    This is deliberately not overridable by any model output: the overall
    verdict and the security-review call are the reviewer's to make.
    """
    if not check.get("human_verdict"):
        return finding

    todo_refs = [str(x).strip() for x in check.get("todo_refs", []) if str(x).strip()]
    todo = "\n".join(todo_refs) if todo_refs else finding.todo
    suggested = str(response.get("selected_option", "") or "").strip()
    summary = (response.get("message") or "").strip()
    rationale = (response.get("rationale") or "").strip()

    note_parts = ["AI suggestion"]
    if suggested:
        note_parts.append(suggested)
    if summary:
        note_parts.append(summary)

    finding.mark_unknown(
        message=" - ".join(note_parts),
        todo=todo,
        severity="ok",
        confidence="low",
        rationale=rationale,
    )
    finding.apply_ai_metadata(
        risk_flags=response.get("risk_flags", []),
        evidence_refs=response.get("evidence_refs", []),
        human_confirmation_required=True,
    )
    return finding


def _default_todo_for_check(check: dict, fallback_suffix: str) -> str:
    """Return a default TODO string for a check.

    Prefer catalog todo_refs so mutually-exclusive options (TODO-A/B/C) are kept
    visible for human review when the tool cannot decide.
    """
    todo_refs = [str(x).strip() for x in check.get("todo_refs", []) if str(x).strip()]
    if todo_refs:
        return "\n".join(todo_refs)
    return f"TODO: - {check.get('title', check.get('id', 'Check'))} — {fallback_suffix}"


def _adapter(ctx: RunContext, name: str) -> dict:
    """Return an adapter payload dict (empty when missing or not a dict)."""
    adapter = ctx.evidence.get("adapters", {}).get(name, {})
    return adapter if isinstance(adapter, dict) else {}


def _fact_deterministic_build_tests(check_id: str, ctx: RunContext) -> str:
    """CB-2: what the rules wiring and build log already say about build-time tests."""
    packaging = _adapter(ctx, "packaging-source")
    fetch_build = _adapter(ctx, "fetch-build")
    if packaging.get("status") != "ok":
        return ""
    hints = _extract_build_test_hints(
        packaging.get("debian_rules", ""),
        (fetch_build or {}).get("build_log", ""),
    )
    if not any(hints.values()):
        return "debian/rules wire no known test runner and the build log shows no test run"
    parts = []
    if hints["rules_has_test_wiring"]:
        parts.append("debian/rules wire test runner(s): " + ", ".join(hints["rules_test_runners"]))
    else:
        parts.append("debian/rules wire no known test runner")
    if hints["nocheck_in_rules"]:
        parts.append("'nocheck' appears in debian/rules")
    if hints["failures_possibly_ignored"]:
        parts.append("test failures are possibly ignored (e.g. '|| true' after a test target)")
    if fetch_build.get("status") == "ok":
        if hints["build_log_runs_tests"]:
            parts.append(
                "the build log shows tests running"
                + (" with pass/fail output" if hints["build_log_has_pass_fail"] else "")
            )
        else:
            parts.append("the build log shows no test run")
    else:
        parts.append("no build log available (fetch-build did not succeed)")
    return "; ".join(parts)


def _fact_ubuntu_delta(check_id: str, ctx: RunContext) -> str:
    """PRF-1: whether Ubuntu carries a delta, and its classification."""
    delta = _adapter(ctx, "debian-delta")
    packaging = _adapter(ctx, "packaging-source")
    kind = delta.get("delta_kind") or packaging.get("delta_kind")
    if not kind:
        return ""
    if kind == "sync":
        return "no Ubuntu delta: the version is a pure Debian sync"
    if kind in ("native", "unknown"):
        return "no Debian revision in the version: Ubuntu-only or native package"
    category = delta.get("delta_category") or "unknown"
    version = delta.get("version") or packaging.get("analyzed_version") or "?"
    summary = (
        f"Ubuntu carries a delta (version {version}, category '{category}');"
        if delta.get("status") == "ok"
        else "Ubuntu carries a delta;"
    )
    if delta.get("delta_summary"):
        summary += " " + str(delta["delta_summary"])
    return summary


def _fact_vendored_dirs(check_id: str, ctx: RunContext) -> str:
    """ESL-1/ESL-11: which vendored directories the source tree carries."""
    packaging = _adapter(ctx, "packaging-source")
    if packaging.get("status") != "ok":
        return ""
    vendored = packaging.get("vendored_dirs", []) or []
    if not vendored:
        return "no vendored directories found in the source tree"
    shipped = packaging.get("shipped_vendored_dirs", []) or []
    parts = ["vendored directories found: " + ", ".join(vendored[:8])]
    if shipped:
        parts.append("potentially shipped in binaries: " + ", ".join(shipped[:8]))
    else:
        parts.append("all confined to test/example/doc trees (not shipped)")
    return "; ".join(parts)


def _fact_rules_overrides(check_id: str, ctx: RunContext) -> str:
    """PRF-9: which debhelper overrides debian/rules declares."""
    packaging = _adapter(ctx, "packaging-source")
    if packaging.get("status") != "ok":
        return ""
    overrides = packaging.get("debian_rules_overrides", []) or []
    if not overrides:
        return "debian/rules declare no debhelper overrides"
    return "debian/rules override: " + ", ".join(overrides[:10])


def _fact_owning_team(check_id: str, ctx: RunContext) -> str:
    """RDO-2: who is already subscribed to the bug."""
    membership = _adapter(ctx, "lp-team-membership-api")
    subscribers = membership.get("subscribers", []) or []
    if not subscribers:
        return ""
    return "bug subscribers so far: " + ", ".join(str(s) for s in subscribers[:10])


def _fact_dup_candidates(check_id: str, ctx: RunContext) -> str:
    """RDO-1: candidate overlapping packages the archive search already found."""
    dup = _adapter(ctx, "dup-search")
    if dup.get("status") != "ok":
        return ""
    candidates = dup.get("candidates", []) or []
    if not candidates:
        reason = dup.get("llm_unavailable_reason") or "none proposed"
        return f"archive search found no candidate packages ({reason})"
    named = [
        f"{c.get('name', '?')} ({c.get('component', 'unknown')})"
        for c in candidates
        if isinstance(c, dict) and c.get("name")
    ]
    return (
        "archive search found candidate package(s) to check for functional overlap: "
        + ", ".join(named[:10])
    )


def _fact_tests_control(check_id: str, ctx: RunContext) -> str:
    """CB-3: whether an autopkgtest control exists at all."""
    packaging = _adapter(ctx, "packaging-source")
    if packaging.get("status") != "ok":
        return ""
    control = (packaging.get("debian_tests_control") or "").strip()
    return (
        "debian/tests/control is present"
        if control
        else "no debian/tests/control found in the packaging"
    )


def _fact_consumers(check_id: str, ctx: RunContext) -> str:
    """CB-6: reverse-dependency consumers and their autopkgtest statuses."""
    reverse = _adapter(ctx, "reverse-deps")
    if reverse.get("status") != "ok":
        return ""
    consumers = reverse.get("consumers", []) or []
    if not consumers:
        return "no reverse-dependency consumers found in the archive"
    parts = [
        f"{len(consumers)} reverse-dependency consumer(s): "
        + ", ".join(str(c) for c in consumers[:8])
    ]
    consumer_tests = _adapter(ctx, "consumer-autopkgtests")
    if consumer_tests.get("status") == "ok":
        entries = consumer_tests.get("consumers", []) or []
        if entries:
            parts.append("consumer autopkgtest results are collected")
        else:
            parts.append("no consumer autopkgtest results available")
    return "; ".join(parts)


def _fact_service_files(check_id: str, ctx: RunContext) -> str:
    """SEC-6/SEC-13: shipped service/apparmor surfaces."""
    packaging = _adapter(ctx, "packaging-source")
    if packaging.get("status") != "ok":
        return ""
    parts = []
    services = packaging.get("service_files", []) or []
    parts.append("systemd unit files: " + (", ".join(services[:8]) if services else "none found"))
    apparmor = packaging.get("apparmor_profiles", []) or []
    parts.append("apparmor profiles: " + (", ".join(apparmor[:8]) if apparmor else "none found"))
    return "; ".join(parts)


def _fact_crypto_scan(check_id: str, ctx: RunContext) -> str:
    """SEC-12: deprecated-crypto pattern scan results (best-effort, not proof)."""
    packaging = _adapter(ctx, "packaging-source")
    if packaging.get("status") != "ok":
        return ""
    hits = packaging.get("crypto_pattern_hits", []) or []
    if not hits:
        return "deprecated-crypto pattern scan found no indicators (not an exhaustive proof)"
    return f"deprecated-crypto pattern scan found {len(hits)} hit(s), e.g. " + "; ".join(hits[:3])


def _fact_runtime_deps(check_id: str, ctx: RunContext) -> str:
    """SEC-5/7/9/11: the runtime dependency set the dep scans work from."""
    dep = _adapter(ctx, "dep-analysis")
    if dep.get("status") != "ok":
        return ""
    packages = dep.get("runtime_dep_packages", []) or []
    if not packages:
        return "no runtime dependencies outside the source package itself"
    return "runtime dependencies: " + ", ".join(str(p) for p in packages[:12])


def _fact_dependency_coverage(check_id: str, ctx: RunContext) -> str:
    """DEP-2/DEP-4: which dependencies carry autopkgtest coverage."""
    coverage = _adapter(ctx, "dependency-autopkgtests")
    if coverage.get("status") != "ok":
        return ""
    entries = coverage.get("dependency_coverage", []) or []
    if not entries:
        return ""
    with_tests = [
        str(e.get("package", "?"))
        for e in entries
        if isinstance(e, dict) and e.get("has_autopkgtest")
    ]
    return (
        f"{len(with_tests)} of {len(entries)} in-main runtime dependenc"
        f"{'y has' if len(entries) == 1 else 'ies have'} autopkgtest coverage"
        + (": " + ", ".join(with_tests[:8]) if with_tests else "")
    )


def _fact_open_bugs(check_id: str, ctx: RunContext) -> str:
    """URF-6: already-known open bugs in Ubuntu and Debian."""
    parts = []
    lp = _adapter(ctx, "lp-bug-search-api")
    if lp.get("status") == "ok":
        open_bugs = lp.get("open_bugs", []) or []
        parts.append(f"{len(open_bugs)} open Ubuntu bug(s)")
    bts = _adapter(ctx, "debian-bts")
    if bts.get("status") == "ok":
        parts.append(
            f"{len(bts.get('open_bugs', []) or [])} open Debian bug(s) "
            f"({len(bts.get('rc_bugs', []) or [])} RC)"
        )
    return "; ".join(parts)


def _fact_ui_surfaces(check_id: str, ctx: RunContext) -> str:
    """URF-8: the deterministic UI signals the check starts from."""
    packaging = _adapter(ctx, "packaging-source")
    if packaging.get("status") != "ok":
        return ""
    parts = []
    if packaging.get("has_desktop_file"):
        parts.append("a .desktop file is shipped")
    else:
        parts.append("no .desktop file found")
    sections = packaging.get("binary_sections", []) or []
    if sections:
        parts.append("binary Sections: " + ", ".join(sections[:6]))
    return "; ".join(parts)


def _fact_language_gate(check_id: str, ctx: RunContext) -> str:
    """ESL-5/ESL-6/CB-9/URF-2: the declared language detection summary."""
    from utils.language_detection import language_detection_summary

    packaging = _adapter(ctx, "packaging-source")
    if packaging.get("status") != "ok":
        return ""
    if check_id in ("CB-9", "ESL-5", "ESL-6"):
        return "go detection: " + language_detection_summary(packaging, "go")
    return "rust detection: " + language_detection_summary(packaging, "rust")


# Curated deterministic facts per check: when the LLM is unavailable (outage
# or --no-llm), each degraded finding still carries what the collected
# evidence already answers for it, so the reviewer starts from facts rather
# than a bare TODO. Checks not listed render without a rationale (their
# question genuinely needs the model's judgement over the evidence).
_DEGRADED_FACT_BUILDERS: dict[str, Callable[[str, RunContext], str]] = {
    "RDO-1": _fact_dup_candidates,
    "RDO-2": _fact_owning_team,
    "CB-2": _fact_deterministic_build_tests,
    "CB-3": _fact_tests_control,
    "CB-6": _fact_consumers,
    "CB-9": _fact_language_gate,
    "DEP-2": _fact_dependency_coverage,
    "DEP-4": _fact_dependency_coverage,
    "ESL-1": _fact_vendored_dirs,
    "ESL-5": _fact_language_gate,
    "ESL-6": _fact_language_gate,
    "ESL-11": _fact_vendored_dirs,
    "PRF-1": _fact_ubuntu_delta,
    "PRF-9": _fact_rules_overrides,
    "SEC-5": _fact_runtime_deps,
    "SEC-6": _fact_service_files,
    "SEC-7": _fact_runtime_deps,
    "SEC-9": _fact_runtime_deps,
    "SEC-11": _fact_runtime_deps,
    "SEC-12": _fact_crypto_scan,
    "SEC-13": _fact_service_files,
    "URF-2": _fact_language_gate,
    "URF-6": _fact_open_bugs,
    "URF-8": _fact_ui_surfaces,
}


def _fallback_rationale_for_check(check: dict, ctx: RunContext) -> str:
    """Return a deterministic-evidence rationale for a check when the LLM failed.

    The curated per-check builders in ``_DEGRADED_FACT_BUILDERS`` summarize
    what the already-collected evidence answers for the check's question
    (e.g. CB-2's rules wiring, PRF-1's delta classification, RDO-1's dup
    candidates), so a degraded run still starts the reviewer from facts
    rather than a bare TODO. Returns "" for checks with no curated facts.
    """
    check_id = check.get("id")
    builder = _DEGRADED_FACT_BUILDERS.get(check_id)
    if builder is None:
        return ""
    fact = builder(check_id, ctx)
    if not fact:
        return ""
    return f"LLM unavailable; deterministic facts: {fact}"


def _summarise_findings_so_far(
    ctx, max_message_len: int = _DEFAULT_FINDING_MESSAGE_CHARS
) -> list[dict]:
    """Return a compact summary of findings already evaluated in this run."""
    results = []
    for f in getattr(ctx, "findings", []):
        results.append(
            {
                "id": f.id,
                "section": f.section,
                "status": f.status,
                "severity": f.severity,
                "message": (f.message or "")[:max_message_len],
            }
        )
    return results
