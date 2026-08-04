"""Focused unit tests for reporter/evaluator.py helper functions."""

import sys
from pathlib import Path
from types import SimpleNamespace

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from reporter.evaluator import (  # noqa: E402
    _dynamic_default,
    _human_statement,
    _maybe_write_evidence,
    _question_from_item,
)


def test_human_statement_substitutes_same_as_source_case_insensitively():
    item = {"template": "TODO: Upstream Name is TBD"}

    assert _human_statement(item, "same as source", "rust-ntpd") == "Upstream Name is rust-ntpd"
    assert _human_statement(item, "  Same As Source  ", "rust-ntpd") == "Upstream Name is rust-ntpd"


def test_human_statement_keeps_other_free_text_unchanged():
    item = {"template": "TODO: Upstream Name is TBD"}

    result = _human_statement(item, "ntpd-rs", "rust-ntpd")

    assert result == "Upstream Name is ntpd-rs"


def test_maybe_write_evidence_backfills_empty_adapter_field_from_url_answer():
    item = {"writes_evidence": {"adapter": "upstream-tracker", "field": "upstream_url"}}
    ctx = SimpleNamespace(evidence={"adapters": {"upstream-tracker": {"upstream_url": ""}}})

    _maybe_write_evidence(item, ctx, "https://github.com/pendulum-project/ntpd-rs")

    assert (
        ctx.evidence["adapters"]["upstream-tracker"]["upstream_url"]
        == "https://github.com/pendulum-project/ntpd-rs"
    )


def test_maybe_write_evidence_ignores_non_url_answers():
    item = {"writes_evidence": {"adapter": "upstream-tracker", "field": "upstream_url"}}
    ctx = SimpleNamespace(evidence={"adapters": {"upstream-tracker": {"upstream_url": ""}}})

    _maybe_write_evidence(item, ctx, "ntpd-rs")

    assert ctx.evidence["adapters"]["upstream-tracker"]["upstream_url"] == ""


def test_maybe_write_evidence_never_overwrites_an_existing_value():
    item = {"writes_evidence": {"adapter": "upstream-tracker", "field": "upstream_url"}}
    ctx = SimpleNamespace(
        evidence={"adapters": {"upstream-tracker": {"upstream_url": "https://existing.example"}}}
    )

    _maybe_write_evidence(item, ctx, "https://typed-by-human.example")

    assert (
        ctx.evidence["adapters"]["upstream-tracker"]["upstream_url"] == "https://existing.example"
    )


def test_maybe_write_evidence_no_op_without_declaration():
    ctx = SimpleNamespace(evidence={"adapters": {}})

    _maybe_write_evidence({}, ctx, "https://example.invalid")

    assert ctx.evidence["adapters"] == {}


def test_dynamic_default_resolves_from_adapter_field():
    ctx = SimpleNamespace(evidence={"adapters": {"upstream-tracker": {"upstream_name": "ntpd-rs"}}})

    assert (
        _dynamic_default({"adapter": "upstream-tracker", "field": "upstream_name"}, ctx)
        == "ntpd-rs"
    )


def test_dynamic_default_returns_none_when_field_empty_or_missing():
    ctx = SimpleNamespace(evidence={"adapters": {"upstream-tracker": {"upstream_name": ""}}})

    assert _dynamic_default({"adapter": "upstream-tracker", "field": "upstream_name"}, ctx) is None
    assert _dynamic_default(None, ctx) is None


def test_question_from_item_uses_dynamic_default_when_no_static_default():
    ctx = SimpleNamespace(evidence={"adapters": {"upstream-tracker": {"upstream_name": "ntpd-rs"}}})
    item = {
        "id": "REP-BG-002",
        "question": {
            "kind": "text",
            "prompt": "What is the upstream project name?",
            "default_source": {"adapter": "upstream-tracker", "field": "upstream_name"},
        },
    }

    question = _question_from_item(item, ctx)

    assert question.default == "ntpd-rs"
