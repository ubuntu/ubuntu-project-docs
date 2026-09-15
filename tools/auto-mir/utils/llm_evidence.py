"""Shared, field-priority-aware evidence truncation for LLM prompts.

Both the reviewer's ``ev_to_ai``/``ai`` evaluators (``checks/llm_eval.py``)
and the reporter's AI-suggestion flow (``reporter/ai.py``) need to keep
per-adapter evidence dicts within a token budget without letting a large,
low-priority field (e.g. a raw grep dump) silently crowd out a small,
high-priority one a specific check/item actually needs in full (e.g.
``debian/rules``). This module holds the one shared implementation both use,
truncating field-by-field rather than applying a single flat character
cutoff over the whole serialized payload.
"""

from __future__ import annotations

import os
import re

_FILE_LISTING_REDUCTION_THRESHOLD = 1000

# Fields known to be large, free-form text that should collapse to a short
# summary by default rather than a generic character-count truncation, unless
# a caller's keep_full_fields says otherwise for a specific field.
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


def truncate_adapter_data(
    data: dict,
    max_str_len: int = 1000,
    adapter_id: str = "",
    keep_full_fields: set[str] | None = None,
) -> dict:
    """Return a copy of data with large outputs trimmed for LLM token budget.

    For known large fields (lintian_output, debian_*, build_log), only include
    a brief summary or first few lines. For other large strings, truncate to
    ``max_str_len`` chars.

    ``keep_full_fields`` lists field names that must NOT be summarised to a
    short preview because the caller's judgement depends on their full
    content (e.g. a check that needs the whole ``debian/rules`` to judge
    cleanliness). Such fields are still bounded by a generous cap to protect
    the token budget on pathological inputs.
    """
    keep_full_fields = keep_full_fields or set()
    # Generous upper bound for fields a caller explicitly needs in full, so
    # the token budget is still protected on pathological inputs.
    full_field_cap = 12000

    result = {}
    for key, value in data.items():
        if adapter_id == "packaging-source" and key == "file_listing" and isinstance(value, list):
            result[key] = reduce_file_listing(value)
            continue

        if key in keep_full_fields and isinstance(value, str):
            # Field the caller needs verbatim; bound only by the generous cap.
            result[key] = value[:full_field_cap] + (
                f" ... [truncated, total {len(value)} chars]" if len(value) > full_field_cap else ""
            )
        elif key in SUMMARY_FIELDS and isinstance(value, str):
            # For known large fields, just count lines/errors
            if key == "lintian_output":
                lines = value.splitlines()
                errors = sum(1 for ln in lines if ln.startswith("E: "))
                warnings = sum(1 for ln in lines if ln.startswith("W: "))
                result[key] = f"[{len(lines)} lines, {errors} errors, {warnings} warnings]"
            elif key == "build_log":
                result[key] = summarise_build_log(value)
            else:
                # Keep a 300-char preview
                result[key] = value[:300] + ("..." if len(value) > 300 else "")
        elif isinstance(value, str) and len(value) > max_str_len:
            result[key] = value[:max_str_len] + f" ... [truncated, total {len(value)} chars]"
        elif isinstance(value, dict):
            result[key] = truncate_adapter_data(
                value, max_str_len, adapter_id=adapter_id, keep_full_fields=keep_full_fields
            )
        elif isinstance(value, list) and len(value) > 30:
            # Truncate large lists to first 15 items + summary
            result[key] = value[:15] + [{"...": f"plus {len(value) - 15} more items"}]
        else:
            result[key] = value
    return result


def reduce_file_listing(file_listing: list[dict]) -> list[dict] | dict:
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


def summarise_build_log(build_log: str) -> dict:
    """Produce a compact, line-numbered build-log summary for first-pass LLM use."""
    lines = build_log.splitlines()
    line_count = len(lines)
    head = line_slice(lines, 1, min(120, line_count))
    tail_start = max(1, line_count - 119)
    tail = line_slice(lines, tail_start, line_count)

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


def line_slice(lines: list[str], start_line: int, end_line: int) -> list[dict]:
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
