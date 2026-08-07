"""Focused unit tests for reporter/evaluator.py helper functions."""

import sys
from pathlib import Path
from types import SimpleNamespace

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from reporter.evaluator import (  # noqa: E402
    _build_tests,
    _build_tests_without_log,
    _dynamic_default,
    _human_statement,
    _maybe_write_evidence,
    _question_from_item,
    _unavailable,
)
from reporter.models import ReadinessEffect  # noqa: E402
from reporter.text_utils import ensure_bulleted, substitute_source  # noqa: E402


def test_human_statement_substitutes_same_as_source_case_insensitively():
    item = {"template": "TODO: Upstream Name is TBD"}

    assert _human_statement(item, "same as source", "rust-ntpd") == "Upstream Name is rust-ntpd"
    assert _human_statement(item, "  Same As Source  ", "rust-ntpd") == "Upstream Name is rust-ntpd"


def test_human_statement_keeps_other_free_text_unchanged():
    item = {"template": "TODO: Upstream Name is TBD"}

    result = _human_statement(item, "ntpd-rs", "rust-ntpd")

    assert result == "Upstream Name is ntpd-rs"


def test_human_statement_preserves_the_catalog_templates_own_leading_dash():
    item = {"template": "TODO: - Upstream Name is TBD"}

    result = _human_statement(item, "ntpd-rs", "rust-ntpd")

    assert result == "- Upstream Name is ntpd-rs"


def test_human_statement_deadline_template_fills_the_single_tbd_completely():
    """Regression test: REP-RATIONALE-008's template used to have two 'TBD'
    slots ('no later than TBD due to TBD') fed by one free-text answer, so
    the second always stayed literal. The template now has exactly one."""
    item = {"template": "TODO: - Required in main no later than TBD"}

    result = _human_statement(item, "the feature freeze of 27.04", "rust-ntpd")

    assert result == "- Required in main no later than the feature freeze of 27.04"
    assert "TBD" not in result


def test_ensure_bulleted_adds_dash_to_plain_text():
    assert ensure_bulleted("Some free-form statement.") == "- Some free-form statement."


def test_ensure_bulleted_does_not_double_dash_already_bulleted_text():
    assert ensure_bulleted("- Already bulleted.") == "- Already bulleted."


def test_ensure_bulleted_handles_leading_whitespace_before_existing_dash():
    assert (
        ensure_bulleted("  - Indented but already bulleted.")
        == "  - Indented but already bulleted."
    )


def test_build_tests_reports_observed_markers_from_the_log():
    ctx = SimpleNamespace(
        evidence={"adapters": {"fetch-build": {"build_log": "running dh_auto_test\nPASS"}}}
    )

    statement, refs, rationale = _build_tests({}, ctx)

    assert statement == "Build-time test execution was observed (dh_auto_test)."
    assert refs == ["fetch-build:build_log"]
    assert rationale


def test_build_tests_reports_no_markers_found_in_the_log():
    ctx = SimpleNamespace(evidence={"adapters": {"fetch-build": {"build_log": "just a build"}}})

    statement, refs, rationale = _build_tests({}, ctx)

    assert statement == "No build-time test execution was identified in the collected build log."
    assert refs == ["fetch-build:build_log"]


def test_build_tests_falls_back_to_debian_rules_when_log_is_unavailable():
    """Regression test: a missing build log (e.g. a carried-over architecture
    whose original build log could not be resolved) must not collapse into an
    uninformative TODO when debian/rules already reveals whether build-time
    tests are disabled."""
    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "fetch-build": {"build_log": ""},
                "packaging-source": {"debian_rules_overrides": ["dh_auto_install"]},
            }
        }
    )

    statement, refs, rationale = _build_tests({}, ctx)

    assert statement is not None
    assert "does not override the default dh_auto_test target" in statement
    assert refs == ["packaging-source:debian_rules_overrides"]
    assert rationale


def test_build_tests_falls_back_to_debian_rules_reporting_an_override():
    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "fetch-build": {"build_log": ""},
                "packaging-source": {"debian_rules_overrides": ["dh_auto_test"]},
            }
        }
    )

    statement, refs, rationale = _build_tests({}, ctx)

    assert statement is not None
    assert "overrides the default dh_auto_test target" in statement
    assert refs == ["packaging-source:debian_rules_overrides"]


def test_build_tests_without_log_stays_unavailable_when_packaging_source_missing():
    ctx = SimpleNamespace(evidence={"adapters": {"fetch-build": {"build_log": ""}}})

    statement, refs, rationale = _build_tests_without_log(ctx)

    assert statement is None
    assert refs == []
    assert rationale == "No build log was available"


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
    ctx = SimpleNamespace(
        source_package="rust-ntpd", evidence={"adapters": {}}, catalog={"items": []}
    )
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
        catalog={"items": []},
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


def test_question_from_item_list_only_adds_note_without_changing_statement():
    ctx = SimpleNamespace(
        source_package="rust-ntpd",
        catalog={"items": []},
        evidence={
            "adapters": {
                "packaging-source": {
                    "binary_package_names": ["ntpd-rs", "ntpd-rs-metrics"],
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
                    "id": "specific-packages",
                    "label": "A specific subset of binary packages (list them below)",
                    "statement": "- Specific binary packages built by TBDSRC, listed below, "
                    "need to be in main.",
                    "spell_out_filter": "list_only",
                },
            ],
            "options_source": {"adapter": "packaging-source", "field": "binary_package_names"},
        },
    }

    question = _question_from_item(item, ctx)

    option = question.options[0]
    assert option.label == "A specific subset of binary packages (list them below)"
    assert option.statement.startswith("- Specific binary packages")
    assert option.list_note == ("The packages built by this source are: ntpd-rs, ntpd-rs-metrics")


def test_question_from_item_list_only_no_note_when_evidence_unavailable():
    ctx = SimpleNamespace(
        source_package="rust-ntpd",
        catalog={"items": []},
        evidence={"adapters": {}},
    )
    item = {
        "id": "REP-RATIONALE-004",
        "question": {
            "kind": "single_choice",
            "prompt": "Which binary packages need promotion to main?",
            "options": [
                {
                    "id": "specific-packages",
                    "label": "A specific subset of binary packages (list them below)",
                    "statement": "- Specific binary packages built by TBDSRC, listed below, "
                    "need to be in main.",
                    "spell_out_filter": "list_only",
                },
            ],
            "options_source": {"adapter": "packaging-source", "field": "binary_package_names"},
        },
    }

    question = _question_from_item(item, ctx)

    assert question.options[0].list_note == ""


def test_question_from_item_marks_option_with_equals_followup():
    ctx = SimpleNamespace(
        source_package="rust-ntpd",
        evidence={"adapters": {}},
        catalog={
            "items": [
                {
                    "id": "REP-RATIONALE-006",
                    "applicability": {"item": "REP-RATIONALE-005", "equals": "niche"},
                }
            ]
        },
    )
    item = {
        "id": "REP-RATIONALE-005",
        "question": {
            "kind": "single_choice",
            "prompt": "Broad or niche?",
            "options": [
                {"id": "broad", "label": "Broad", "statement": "Broadly useful."},
                {"id": "niche", "label": "Niche", "statement": "Serves a niche."},
            ],
        },
    }

    question = _question_from_item(item, ctx)

    by_id = {option.id: option for option in question.options}
    assert by_id["niche"].leads_to_followup is True
    assert by_id["broad"].leads_to_followup is False


def test_question_from_item_marks_all_options_followup_for_truthy_condition():
    ctx = SimpleNamespace(
        source_package="rust-ntpd",
        evidence={"adapters": {}},
        catalog={
            "items": [
                {
                    "id": "REP-QA-TEST-006",
                    "applicability": {"item": "REP-QA-TEST-005", "truthy": True},
                }
            ]
        },
    )
    item = {
        "id": "REP-QA-TEST-005",
        "question": {
            "kind": "single_choice",
            "prompt": "How can this be tested?",
            "options": [
                {"id": "A-team-hardware", "label": "Team hardware", "statement": "x"},
                {"id": "X-exhausted", "label": "Exhausted", "statement": "y"},
            ],
        },
    }

    question = _question_from_item(item, ctx)

    assert all(option.leads_to_followup for option in question.options)


def test_question_from_item_no_hint_when_no_downstream_item_references_it():
    ctx = SimpleNamespace(
        source_package="rust-ntpd", evidence={"adapters": {}}, catalog={"items": []}
    )
    item = {
        "id": "REP-MAINT-006",
        "question": {
            "kind": "single_choice",
            "prompt": "Will this affect other teams?",
            "options": [{"id": "no-impact", "label": "No impact", "statement": "x"}],
        },
    }

    question = _question_from_item(item, ctx)

    assert question.options[0].leads_to_followup is False


def _maint_001_item():
    return {
        "id": "REP-MAINT-001",
        "question": {
            "kind": "single_choice",
            "prompt": "Is the already-subscribed team the owning team?",
            "options": [
                {
                    "id": "confirm-subscribed",
                    "label": "Keep the already-subscribed team",
                    "statement": "- Confirmed.",
                    "unavailable_if": {
                        "not": {"evidence": "team-mapping.subscribed_teams", "truthy": True}
                    },
                    "unavailable_reason": "No team is currently subscribed to this package.",
                },
                {"id": "new-team", "label": "A different team", "statement": "- New team."},
            ],
        },
    }


def test_option_locked_when_evidence_condition_is_true():
    ctx = SimpleNamespace(
        source_package="foo",
        catalog={"items": []},
        evidence={"adapters": {"team-mapping": {"subscribed_teams": []}}},
    )

    question = _question_from_item(_maint_001_item(), ctx)

    by_id = {option.id: option for option in question.options}
    assert by_id["confirm-subscribed"].locked_reason == (
        "No team is currently subscribed to this package."
    )
    assert by_id["new-team"].locked_reason == ""


def test_option_not_locked_when_evidence_condition_is_false():
    ctx = SimpleNamespace(
        source_package="foo",
        catalog={"items": []},
        evidence={"adapters": {"team-mapping": {"subscribed_teams": ["ubuntu-server"]}}},
    )

    question = _question_from_item(_maint_001_item(), ctx)

    by_id = {option.id: option for option in question.options}
    assert by_id["confirm-subscribed"].locked_reason == ""
