"""LLM-based check evaluators for auto-mir.

Contains ev_to_ai, ai, and human_only evaluators, plus all LLM helper
functions for prompt rendering, evidence assembly, and response mapping.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

from checks.messages import render_check_message_or_default
from checks.registry import evaluator
from models import Finding
from utils import llm_sanitize

log = logging.getLogger("auto_mir.checks.llm_eval")

_PROMPT_LARGE_THRESHOLD_CHARS = 24000
_EVIDENCE_LARGE_THRESHOLD_CHARS = 12000
_FILE_LISTING_REDUCTION_THRESHOLD = 1000
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


@evaluator("ev_to_ai")
def _eval_ev_to_ai(check: dict, ctx, finding: Finding) -> Finding:
    """Evaluate a check by combining collected evidence with an LLM call.

    Assembles the evidence payload relevant to this check, renders the
    ev_to_ai.md prompt template, calls the LLM, and maps the response back
    to a finding dict.  Falls back to a manual-review TODO on any failure.
    """
    import llm

    evidence_payload = _build_evidence_payload(check, ctx)
    policy_excerpt = _build_policy_excerpt(check, ctx)
    prompt = _render_ev_to_ai_prompt(check, evidence_payload, policy_excerpt, ctx)

    # Synthesis checks always use the large tier; their inputs are intentionally
    # large and they reason over the whole run. Other ev_to_ai checks select the
    # tier from prompt/evidence complexity, with the one-shot larger-budget retry
    # in call_llm() as the backstop when a reasoning model overflows.
    if check.get("synthesis"):
        model_tier = "large"
    else:
        model_tier = _select_ev_to_ai_model_tier(prompt, evidence_payload)

    try:
        response = llm.call_llm(prompt, ctx, model_tier=model_tier, trace_label=check["id"])
    except llm.LLMError as exc:
        log.warning("LLM call failed for check %s: %s", check["id"], exc)
        _apply_llm_unavailable_fallback(
            check,
            finding,
            exc,
            fallback_suffix="manual review needed (LLM unavailable)",
        )
        # Even when the model is unavailable, surface any deterministic evidence
        # already gathered (e.g. dup-search candidates for RDO-1) so the reviewer
        # is not left with a bare TODO.
        finding.rationale = _fallback_rationale_for_check(check, ctx)
        return finding

    response = _maybe_refine_with_additional_evidence(
        check,
        ctx,
        response,
        evidence_payload,
        policy_excerpt,
        model_tier,
    )

    return _apply_llm_response(response, check, finding)


@evaluator("ai")
def _eval_ai(check: dict, ctx, finding: Finding) -> Finding:
    """Evaluate checks that require pure AI synthesis over the full findings set.

    Uses the same LLM path as ev_to_ai but passes the full evidence store rather
    than check-specific adapters.  Used for checks like SUM-5 (overall verdict).
    """
    import llm

    # For pure-AI checks, pass all available context (findings so far + bug metadata).
    # Synthesis checks (e.g. SUM-5 overall verdict) must see essentially all the
    # information, so include the full reporter MIR content and larger per-finding
    # messages rather than the compact per-check budgets.
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
    policy_excerpt = _build_policy_excerpt(check, ctx)
    prompt = _render_ev_to_ai_prompt(check, full_evidence, policy_excerpt, ctx)

    try:
        # Pure AI synthesis works over cross-check aggregate context and should
        # always use the large model tier.
        response = llm.call_llm(prompt, ctx, model_tier="large", trace_label=check["id"])
    except llm.LLMError as exc:
        log.warning("LLM call failed for check %s: %s", check["id"], exc)
        _apply_llm_unavailable_fallback(
            check,
            finding,
            exc,
            fallback_suffix="requires AI synthesis",
        )
        return finding

    return _apply_llm_response(response, check, finding)


@evaluator("human_only")
def _eval_human_only(check: dict, ctx, finding: Finding) -> Finding:
    """Evaluate checks that require human judgment only."""
    finding.mark_unknown(
        message=render_check_message_or_default(
            check,
            "human_only_message",
            "Human review required",
        ),
        todo=render_check_message_or_default(
            check,
            "human_only_todo",
            f"TODO: - {check.get('title', 'Check')} — reviewer judgment needed",
            title=check.get("title", "Check"),
        ),
    )
    return finding


def _apply_llm_unavailable_fallback(
    check: dict,
    finding: Finding,
    error: Exception,
    *,
    fallback_suffix: str,
) -> None:
    """Apply the standard unknown/low-confidence fallback for LLM outages."""
    finding.mark_unknown(
        message=render_check_message_or_default(
            check,
            "llm_unavailable_message",
            f"LLM unavailable: {error}",
            error=str(error),
        ),
        todo=_default_todo_for_check(check, fallback_suffix=fallback_suffix),
    )


def _wrap_untrusted(ctx, label: str, text: str) -> str:
    """Wrap attacker-controllable text in a per-run untrusted-data envelope.

    Uses the run's nonce (ctx.untrusted_nonce) so injected content cannot forge
    the closing delimiter. Falls back to a fresh nonce if the context predates
    nonce assignment (e.g. in unit tests).
    """
    nonce = getattr(ctx, "untrusted_nonce", None) or llm_sanitize.make_nonce()
    return llm_sanitize.wrap_untrusted(label, text, nonce)


def _spotlight_lp_bug_api(ctx, data: dict) -> dict:
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


def _build_evidence_payload(check: dict, ctx) -> dict:
    """Build a compact evidence dict for the adapters required by this check.

    Only includes adapter outputs listed in adapters_required/adapters_optional
    for the check, plus basic package/bug metadata.  Large raw strings are
    truncated to keep prompt size manageable.

    For ESL-1 specifically, also extracts build hints from sbuild to detect
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
            truncated = _truncate_adapter_data(
                data, adapter_id=adapter_id, keep_full_fields=keep_full_fields
            )
            if adapter_id == "lp-bug-api":
                truncated = _spotlight_lp_bug_api(ctx, truncated)
            payload[adapter_id] = truncated

    # For ESL-1, enhance with build hints extracted from sbuild log
    if check.get("id") == "ESL-1":
        sbuild_data = adapters_store.get("sbuild", {})
        build_log = sbuild_data.get("build_log", "")
        if build_log:
            payload["build_hints"] = _extract_build_hints(build_log)

    # For CB-2, surface concrete build-time test wiring signals from
    # debian/rules and the build log so the model can decide rather than echo
    # the template TODO.
    if check.get("id") == "CB-2":
        sbuild_data = adapters_store.get("sbuild", {})
        packaging_data = adapters_store.get("packaging-source", {})
        payload["build_test_hints"] = _extract_build_test_hints(
            packaging_data.get("debian_rules", ""),
            sbuild_data.get("build_log", ""),
        )

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


def _truncate_adapter_data(
    data: dict,
    max_str_len: int = 1000,
    adapter_id: str = "",
    keep_full_fields: set[str] | None = None,
) -> dict:
    """Return a copy of data with large outputs trimmed for LLM token budget.

    For known large fields (lintian_output, debian_*, build_log), only include
    a brief summary or first few lines. For other large strings, truncate to 1000 chars.

    ``keep_full_fields`` lists field names that must NOT be summarised to a short
    preview because the evaluating check needs their full content (e.g. PRF-9
    needs the whole debian/rules to judge cleanliness). Such fields are still
    bounded by a generous cap to protect the token budget.
    """
    keep_full_fields = keep_full_fields or set()
    # Generous upper bound for fields a check explicitly needs in full, so the
    # token budget is still protected on pathological inputs.
    FULL_FIELD_CAP = 12000
    SUMMARY_FIELDS = {
        "lintian_output",  # lintian full output
        "debian_control",  # control file
        "debian_rules",  # rules file
        "debian_watch",
        "debian_copyright",
        "debian_tests_control",
        "raw_output",  # component-mismatches raw output
        "build_log",
    }

    result = {}
    for k, v in data.items():
        if adapter_id == "packaging-source" and k == "file_listing" and isinstance(v, list):
            result[k] = _reduce_file_listing(v)
            continue

        if k in keep_full_fields and isinstance(v, str):
            # Field the check needs verbatim; bound only by the generous cap.
            result[k] = v[:FULL_FIELD_CAP] + (
                f" ... [truncated, total {len(v)} chars]" if len(v) > FULL_FIELD_CAP else ""
            )
        elif k in SUMMARY_FIELDS and isinstance(v, str):
            # For known large fields, just count lines/errors
            if k == "lintian_output":
                lines = v.splitlines()
                errors = sum(1 for ln in lines if ln.startswith("E: "))
                warnings = sum(1 for ln in lines if ln.startswith("W: "))
                result[k] = f"[{len(lines)} lines, {errors} errors, {warnings} warnings]"
            elif k == "build_log":
                result[k] = _summarise_build_log(v)
            else:
                # Keep a 300-char preview
                result[k] = v[:300] + ("..." if len(v) > 300 else "")
        elif isinstance(v, str) and len(v) > max_str_len:
            result[k] = v[:max_str_len] + f" ... [truncated, total {len(v)} chars]"
        elif isinstance(v, dict):
            result[k] = _truncate_adapter_data(
                v, max_str_len, adapter_id=adapter_id, keep_full_fields=keep_full_fields
            )
        elif isinstance(v, list) and len(v) > 30:
            # Truncate large lists to first 15 items + summary
            result[k] = v[:15] + [{"...": f"plus {len(v) - 15} more items"}]
        else:
            result[k] = v
    return result


def _reduce_file_listing(file_listing: list[dict]) -> list[dict] | dict:
    """Reduce packaging file listings while preserving path signal for LLMs.

    - Always strip a shared leading path prefix when all entries share one.
    - Keep full listing until threshold, then cap to threshold with summary.
    """
    if not file_listing:
        return []

    common_prefix = _common_path_prefix(
        [str(item.get("path", "")) for item in file_listing if isinstance(item, dict)]
    )
    stripped_entries = [_strip_listing_entry_prefix(item, common_prefix) for item in file_listing]

    if len(stripped_entries) <= _FILE_LISTING_REDUCTION_THRESHOLD:
        return stripped_entries

    return {
        "total_paths": len(stripped_entries),
        "shown_paths": _FILE_LISTING_REDUCTION_THRESHOLD,
        "common_prefix_stripped": common_prefix,
        "paths": stripped_entries[:_FILE_LISTING_REDUCTION_THRESHOLD],
        "truncated": True,
    }


def _strip_listing_entry_prefix(entry: object, common_prefix: str) -> object:
    if not isinstance(entry, dict):
        return entry
    path = entry.get("path")
    if not isinstance(path, str) or not common_prefix:
        return entry
    stripped = _strip_common_prefix(path, common_prefix)
    updated = dict(entry)
    updated["path"] = stripped
    return updated


def _common_path_prefix(paths: list[str]) -> str:
    normalized = [p for p in (_normalize_listed_path(x) for x in paths) if p]
    if len(normalized) < 2:
        return ""

    try:
        raw = os.path.commonpath(normalized)
    except ValueError:
        return ""

    if not raw or raw == ".":
        return ""

    prefix = raw.rstrip("/")
    if not prefix:
        return ""
    if all(_normalize_listed_path(p).startswith(prefix + "/") for p in paths if p):
        return prefix + "/"
    return ""


def _normalize_listed_path(path: str) -> str:
    if not isinstance(path, str):
        return ""
    normalized = path.strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.strip("/")


def _strip_common_prefix(path: str, prefix: str) -> str:
    normalized = _normalize_listed_path(path)
    pref = prefix
    if pref.endswith("/"):
        pref = pref[:-1]
    if pref and normalized.startswith(pref + "/"):
        return normalized[len(pref) + 1 :]
    return normalized


def _summarise_build_log(build_log: str) -> dict:
    """Produce a compact, line-numbered build-log summary for first-pass LLM use."""
    lines = build_log.splitlines()
    line_count = len(lines)
    head = _line_slice(lines, 1, min(120, line_count))
    tail_start = max(1, line_count - 119)
    tail = _line_slice(lines, tail_start, line_count)

    highlight_regex = re.compile(
        r"error|failed|failure|fatal|traceback|undefined reference|test.*fail",
        re.IGNORECASE,
    )
    highlighted = []
    for idx, line in enumerate(lines, start=1):
        if highlight_regex.search(line):
            highlighted.append(
                {
                    "line": idx,
                    "text": line,
                }
            )
        if len(highlighted) >= 80:
            break

    return {
        "line_count": line_count,
        "head": head,
        "tail": tail,
        "highlighted_lines": highlighted,
        "follow_up_request_examples": [
            "line 300-400",
            "pattern foo.*",
        ],
    }


def _line_slice(lines: list[str], start_line: int, end_line: int) -> list[dict]:
    if start_line > end_line:
        return []
    start_idx = max(1, start_line)
    end_idx = min(len(lines), end_line)
    return [
        {
            "line": i,
            "text": lines[i - 1],
        }
        for i in range(start_idx, end_idx + 1)
    ]


def _maybe_refine_with_additional_evidence(
    check: dict,
    ctx,
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


def _build_additional_requested_evidence(ctx, requests: list[dict | str]) -> dict:
    adapters_store = ctx.evidence.get("adapters", {})
    sbuild_data = adapters_store.get("sbuild", {})
    build_log = sbuild_data.get("build_log", "")
    if not isinstance(build_log, str) or not build_log:
        return {}

    snippets = _resolve_build_log_requests(build_log, requests)
    if not snippets:
        return {}
    return {"sbuild": {"build_log_snippets": snippets}}


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
                    "lines": _line_slice(lines, start, end),
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


def _parse_build_log_request(request: dict | str) -> dict | None:
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

    if not isinstance(request, str):
        return None

    text = request.strip()
    if not text:
        return None

    range_match = re.search(r"line(?:s)?\s+(\d+)\s*-\s*(\d+)", text, flags=re.IGNORECASE)
    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))
        if start > 0 and end >= start:
            return {"type": "line_range", "start": start, "end": end}

    pattern_match = re.search(r"pattern\s+(.+)$", text, flags=re.IGNORECASE)
    if pattern_match:
        pattern = pattern_match.group(1).strip()
        if pattern:
            return {"type": "pattern", "pattern": pattern, "max_matches": 20}

    return {"type": "pattern", "pattern": text, "max_matches": 20}


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


def _build_policy_excerpt(check: dict, ctx) -> str:
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

    header = f"[{section}]"
    lines = text.splitlines()
    in_section = False
    collected: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == header:
            in_section = True
            continue
        if in_section:
            if stripped.startswith("[") and stripped.endswith("]") and stripped != header:
                break
            collected.append(line)
    return "\n".join(collected)


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
    rules_lower = (debian_rules or "").lower()
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
    rules_runners = [marker for marker in runner_markers if marker in rules_lower]

    failures_possibly_ignored = bool(
        re.search(r"(dh_auto_test|make\s+(check|test)|pytest|ctest)[^\n]*\|\|\s*true", rules_lower)
    )

    log_runs_tests = any(
        marker in log_lower
        for marker in ("running tests", "make check", "make test", "test session starts", "ctest")
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


def _extract_build_hints(build_log: str) -> dict:
    """Extract hints from sbuild build log indicating embedded source usage.

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
    template_path = tool_root and (Path(tool_root) / "prompts" / "ev_to_ai.md")

    if template_path and Path(template_path).exists():
        template = Path(template_path).read_text(encoding="utf-8")
    else:
        template = _load_fallback_prompt()

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
        return _apply_option_response(option, response, check, finding)

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

    finding.status = status
    finding.severity = severity
    finding.confidence = confidence

    message = (response.get("message") or "").strip()
    if message:
        finding.message = message

    todo = (response.get("todo") or "").strip()
    rationale = (response.get("rationale") or "").strip()
    finding.rationale = rationale

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
        finding.todo = todo
    else:
        # Prefer the catalog's canonical OK statement over free-form model prose
        # so the reviewer sees the familiar template wording; the rationale is
        # kept in its own field and composed into a parenthetical by the renderer.
        canonical = _canonical_ok_statement(check)
        if canonical:
            finding.message = canonical
        finding.todo = ""

    risk_flags = response.get("risk_flags", [])
    if isinstance(risk_flags, list) and risk_flags:
        finding.risk_flags = risk_flags

    ev_refs = response.get("evidence_refs", [])
    if isinstance(ev_refs, list) and ev_refs:
        finding.evidence_refs = ev_refs

    # Always require human confirmation for AI-derived findings
    finding.human_confirmation_required = True

    return finding


# Matches a leading "TODO:" / "TODO-X:" (possibly repeated) plus an optional
# "- " list marker, so a catalog todo_ref can be reduced to its statement text.
_TODO_PREFIX_RE = re.compile(r"^\s*(?:TODO(?:-[A-Z0-9]+)?:\s*)+(?:-\s*)?")


def _strip_todo_prefix_text(line: str) -> str:
    """Strip leading TODO markers and list dashes, leaving the statement text."""
    return _TODO_PREFIX_RE.sub("", line).strip()


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
    statement = _strip_todo_prefix_text(todo_refs[0])
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

    finding.rationale = rationale
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

    ev_refs = response.get("evidence_refs", [])
    if isinstance(ev_refs, list) and ev_refs:
        finding.evidence_refs = ev_refs
    risk_flags = response.get("risk_flags", [])
    if isinstance(risk_flags, list) and risk_flags:
        finding.risk_flags = risk_flags
    finding.human_confirmation_required = True
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


def _fallback_rationale_for_check(check: dict, ctx) -> str:
    """Return a deterministic-evidence rationale for a check when the LLM failed.

    Currently specialises RDO-1: even without the model, the dup-search adapter
    has already found candidate overlapping packages, so surface them (with their
    components) rather than leaving only a bare TODO. Returns "" for checks with
    no such fallback.
    """
    if check.get("id") != "RDO-1":
        return ""
    dup = ctx.evidence.get("adapters", {}).get("dup-search", {})
    if not isinstance(dup, dict) or dup.get("status") != "ok":
        return ""
    candidates = dup.get("candidates", []) or []
    if not candidates:
        return ""
    named = [
        f"{c.get('name', '?')} ({c.get('component', 'unknown')})"
        for c in candidates
        if isinstance(c, dict) and c.get("name")
    ]
    if not named:
        return ""
    return (
        "LLM unavailable; archive search found candidate package(s) to check for functional "
        "overlap: " + ", ".join(named[:10])
    )


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


# Fallback prompt — used when prompts/ev_to_ai.md cannot be resolved from the
# run context. Loaded from prompts/ev_to_ai_fallback.md next to this package so
# it stays versioned alongside the primary template.
_FALLBACK_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "ev_to_ai_fallback.md"


def _load_fallback_prompt() -> str:
    """Read the on-disk fallback prompt template."""
    return _FALLBACK_PROMPT_PATH.read_text(encoding="utf-8")
