"""Tests for utils/llm_evidence.py: shared, field-priority-aware evidence truncation."""

import sys
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from utils import llm_evidence  # noqa: E402


def test_reduce_file_listing_strips_common_prefix_without_reducing_small_list():
    listing = [
        {"path": "./src/pkg/a.py", "size": 10},
        {"path": "./src/pkg/b.py", "size": 11},
    ]

    reduced = llm_evidence.reduce_file_listing(listing)

    assert isinstance(reduced, list)
    assert reduced[0]["path"] == "a.py"
    assert reduced[1]["path"] == "b.py"


def test_reduce_file_listing_reduces_above_threshold():
    listing = [{"path": f"./tree/dir/file-{i}.txt", "size": i} for i in range(1005)]

    reduced = llm_evidence.reduce_file_listing(listing)

    assert isinstance(reduced, dict)
    assert reduced["total_paths"] == 1005
    assert reduced["shown_paths"] == llm_evidence._FILE_LISTING_REDUCTION_THRESHOLD
    assert reduced["truncated"] is True
    assert reduced["paths"][0]["path"] == "file-0.txt"


def test_truncate_adapter_data_summarizes_known_large_fields():
    data = {
        "debian_control": "x" * 500,
        "lintian_output": "E: error one\nW: warning one\nI: info\n",
    }

    result = llm_evidence.truncate_adapter_data(data)

    assert result["debian_control"] == "x" * 300 + "..."
    assert result["lintian_output"] == "[3 lines, 1 errors, 1 warnings]"


def test_truncate_adapter_data_keeps_full_fields_bounded_but_not_summarized():
    data = {"debian_rules": "y" * 50}

    result = llm_evidence.truncate_adapter_data(data, keep_full_fields={"debian_rules"})

    assert result["debian_rules"] == "y" * 50


def test_truncate_adapter_data_full_field_still_capped_on_pathological_input():
    data = {"debian_rules": "z" * 20000}

    result = llm_evidence.truncate_adapter_data(data, keep_full_fields={"debian_rules"})

    assert result["debian_rules"].startswith("z" * 12000)
    assert "truncated, total 20000 chars" in result["debian_rules"]


def test_truncate_adapter_data_a_large_low_priority_field_never_starves_a_kept_full_field():
    """Root-cause regression test: a large field early in dict/alphabetical
    order (e.g. crypto_pattern_hits) must never crowd out a small field the
    caller explicitly needs in full (e.g. debian_rules), since each field is
    truncated independently rather than via one flat serialized-payload cutoff."""
    data = {
        "crypto_pattern_hits": ["x" * 5000, "y" * 5000, "z" * 5000],
        "debian_rules": "small but important content",
    }

    result = llm_evidence.truncate_adapter_data(data, keep_full_fields={"debian_rules"})

    assert result["debian_rules"] == "small but important content"


def test_truncate_adapter_data_truncates_generic_long_strings():
    data = {"some_field": "a" * 2000}

    result = llm_evidence.truncate_adapter_data(data, max_str_len=1000)

    assert result["some_field"].startswith("a" * 1000)
    assert "truncated, total 2000 chars" in result["some_field"]


def test_truncate_adapter_data_truncates_long_lists():
    data = {"items": list(range(40))}

    result = llm_evidence.truncate_adapter_data(data)

    assert len(result["items"]) == 16
    assert result["items"][:15] == list(range(15))
    assert "plus 25 more items" in result["items"][15]["..."]


def test_truncate_adapter_data_recurses_into_nested_dicts():
    data = {"nested": {"debian_rules": "full content"}}

    result = llm_evidence.truncate_adapter_data(data, keep_full_fields={"debian_rules"})

    assert result["nested"]["debian_rules"] == "full content"


def test_truncate_adapter_data_reduces_packaging_source_file_listing():
    data = {"file_listing": [{"path": f"./a/b/f{i}.py", "size": i} for i in range(3)]}

    result = llm_evidence.truncate_adapter_data(data, adapter_id="packaging-source")

    assert result["file_listing"][0]["path"] == "f0.py"


def test_summarise_build_log_produces_head_tail_and_highlighted_lines():
    build_log = "\n".join([f"line {i}" for i in range(5)] + ["error: build failed"])

    summary = llm_evidence.summarise_build_log(build_log)

    assert summary["line_count"] == 6
    assert summary["head"][0]["text"] == "line 0"
    assert any("error" in entry["text"] for entry in summary["highlighted_lines"])


def test_line_slice_returns_empty_for_invalid_range():
    assert llm_evidence.line_slice(["a", "b"], 3, 1) == []


def test_line_slice_returns_requested_range():
    lines = ["a", "b", "c", "d"]

    result = llm_evidence.line_slice(lines, 2, 3)

    assert result == [{"line": 2, "text": "b"}, {"line": 3, "text": "c"}]
