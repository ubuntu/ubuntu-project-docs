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
    _unavailable,
)
from reporter.models import ReadinessEffect  # noqa: E402
from reporter.text_utils import substitute_source  # noqa: E402


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
    ctx = SimpleNamespace(
        source_package="rust-ntpd",
        evidence={"adapters": {"upstream-tracker": {"upstream_name": "ntpd-rs"}}},
    )
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


def test_substitute_source_uses_src_prefix_in_prose():
    assert (
        substitute_source("The package TBDSRC is required in main.", "rust-ntpd")
        == "The package src:rust-ntpd is required in main."
    )


def test_substitute_source_keeps_bare_name_inside_launchpad_source_url():
    text = "TODO: Link to package https://launchpad.net/ubuntu/+source/TBDSRC"

    assert (
        substitute_source(text, "rust-ntpd")
        == "TODO: Link to package https://launchpad.net/ubuntu/+source/rust-ntpd"
    )


def test_question_from_item_substitutes_tbdsrc_in_option_label_and_statement():
    ctx = SimpleNamespace(source_package="rust-ntpd", evidence={"adapters": {}})
    item = {
        "id": "REP-RATIONALE-005",
        "question": {
            "kind": "single_choice",
            "prompt": "Broad or niche?",
            "options": [
                {
                    "id": "broad",
                    "label": "Broadly useful for TBDSRC",
                    "statement": "The package TBDSRC will generally be useful.",
                }
            ],
        },
    }

    question = _question_from_item(item, ctx)

    assert question.options[0].label == "Broadly useful for src:rust-ntpd"
    assert question.options[0].statement == "The package src:rust-ntpd will generally be useful."


def test_unavailable_substitutes_tbdsrc_in_template():
    item = {
        "id": "REP-BG-003",
        "section": "Background information",
        "template": "TODO: Link to package https://launchpad.net/ubuntu/+source/TBDSRC",
    }

    result = _unavailable(item, ReadinessEffect.WARNING, "no data", "rust-ntpd")

    assert result.statement == (
        "TODO: Link to package https://launchpad.net/ubuntu/+source/rust-ntpd"
    )


def test_question_from_item_spells_out_all_binaries_shortcut():
    ctx = SimpleNamespace(
        source_package="rust-ntpd",
        evidence={
            "adapters": {
                "dep-analysis": {
                    "binary_packages": ["librust-ntpd-dev", "ntpd-rs", "ntpd-rs-metrics"]
                }
            }
        },
    )
    item = {
        "id": "REP-RATIONALE-004",
        "question": {
            "kind": "single_choice",
            "prompt": "Which binary packages need promotion to main?",
            "options": [
                {
                    "id": "__all_binaries__",
                    "label": "All binary packages built by this source",
                    "statement": "All binary packages built by TBDSRC need to be in main.",
                    "exclusive": True,
                    "spell_out_filter": "all",
                },
                {
                    "id": "__all_except_dev_doc_dbg__",
                    "label": "All binary packages except -dev, -doc, and -dbg(sym) packages",
                    "statement": (
                        "All binary packages built by TBDSRC, except -dev, -doc, and "
                        "debug-symbol packages, need to be in main."
                    ),
                    "exclusive": True,
                    "spell_out_filter": "exclude_dev_doc_dbg",
                },
            ],
            "options_source": {"adapter": "dep-analysis", "field": "binary_packages"},
        },
    }

    question = _question_from_item(item, ctx)

    all_option = question.options[0]
    filtered_option = question.options[1]
    assert all_option.label == (
        "All binary packages built by this source: librust-ntpd-dev, ntpd-rs, ntpd-rs-metrics"
    )
    assert filtered_option.label == (
        "All binary packages except -dev, -doc, and -dbg(sym) packages: ntpd-rs, ntpd-rs-metrics"
    )
    assert filtered_option.statement.endswith(": ntpd-rs, ntpd-rs-metrics")
