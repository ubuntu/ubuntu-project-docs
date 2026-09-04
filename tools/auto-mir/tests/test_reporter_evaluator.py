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
    _question_from_item,
    _unavailable,
)
from reporter.models import ReadinessEffect, StatementState  # noqa: E402
from reporter.text_utils import (  # noqa: E402
    debian_rules_url,
    ensure_bulleted,
    maybe_write_evidence,
    substitute_rules_url,
    substitute_source,
)


def test_human_statement_records_the_free_text_answer_verbatim():
    """Feedback item 2: a free-text answer IS the statement, because the
    reporter edited it in an editor pre-filled with the item's template. The
    tool must not merge answer and template itself - that is what produced
    "required in Ubuntu main for This is an entropy source alternative"."""
    item = {"template": "TODO: - The package TBDSRC is required in Ubuntu main for TBD"}

    result = _human_statement(
        item,
        "- The package src:rust-ntpd is required in Ubuntu main because it serves NTP.",
        "rust-ntpd",
    )

    assert result == "- The package src:rust-ntpd is required in Ubuntu main because it serves NTP."


def test_human_statement_bullets_an_answer_that_has_no_dash():
    item = {"template": "TODO: - Upstream Name is TBD"}

    assert _human_statement(item, "Upstream Name is ntpd-rs", "rust-ntpd") == (
        "- Upstream Name is ntpd-rs"
    )


def test_human_statement_prefers_the_chosen_options_own_statement():
    item = {
        "template": "TODO: - unused for a choice",
        "question": {
            "options": [
                {"id": "broad", "statement": "- TBDSRC is broadly useful."},
                {"id": "niche", "statement": "- TBDSRC serves a narrower use case."},
            ]
        },
    }

    assert _human_statement(item, "niche", "rust-ntpd") == (
        "- src:rust-ntpd serves a narrower use case."
    )


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

    assessment = _build_tests({}, ctx)
    statement, refs = assessment.statement, assessment.evidence_refs
    rationale = assessment.rationale()

    assert statement == "Build-time test execution was observed (dh_auto_test)."
    assert refs == ["fetch-build:build_log"]
    assert rationale


def test_build_tests_reports_no_markers_found_in_the_log():
    ctx = SimpleNamespace(evidence={"adapters": {"fetch-build": {"build_log": "just a build"}}})

    assessment = _build_tests({}, ctx)
    statement, refs = assessment.statement, assessment.evidence_refs

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

    assessment = _build_tests({}, ctx)
    statement, refs = assessment.statement, assessment.evidence_refs
    rationale = assessment.rationale()

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

    assessment = _build_tests({}, ctx)
    statement, refs = assessment.statement, assessment.evidence_refs

    assert statement is not None
    assert "overrides the default dh_auto_test target" in statement
    assert refs == ["packaging-source:debian_rules_overrides"]


def test_build_tests_without_log_stays_unavailable_when_packaging_source_missing():
    ctx = SimpleNamespace(evidence={"adapters": {"fetch-build": {"build_log": ""}}})

    assessment = _build_tests_without_log(ctx)
    statement, refs = assessment.statement, assessment.evidence_refs

    assert statement is None
    assert refs == []
    assert assessment.unavailable_reason == "No build log was available"


def test_maybe_write_evidence_backfills_empty_adapter_field_from_url_answer():
    item = {"writes_evidence": {"adapter": "upstream-tracker", "field": "upstream_url"}}
    ctx = SimpleNamespace(evidence={"adapters": {"upstream-tracker": {"upstream_url": ""}}})

    maybe_write_evidence(item, ctx, "https://github.com/pendulum-project/ntpd-rs")

    assert (
        ctx.evidence["adapters"]["upstream-tracker"]["upstream_url"]
        == "https://github.com/pendulum-project/ntpd-rs"
    )


def test_maybe_write_evidence_ignores_non_url_answers():
    item = {"writes_evidence": {"adapter": "upstream-tracker", "field": "upstream_url"}}
    ctx = SimpleNamespace(evidence={"adapters": {"upstream-tracker": {"upstream_url": ""}}})

    maybe_write_evidence(item, ctx, "ntpd-rs")

    assert ctx.evidence["adapters"]["upstream-tracker"]["upstream_url"] == ""


def test_maybe_write_evidence_never_overwrites_an_existing_value():
    item = {"writes_evidence": {"adapter": "upstream-tracker", "field": "upstream_url"}}
    ctx = SimpleNamespace(
        evidence={"adapters": {"upstream-tracker": {"upstream_url": "https://existing.example"}}}
    )

    maybe_write_evidence(item, ctx, "https://typed-by-human.example")

    assert (
        ctx.evidence["adapters"]["upstream-tracker"]["upstream_url"] == "https://existing.example"
    )


def test_maybe_write_evidence_no_op_without_declaration():
    ctx = SimpleNamespace(evidence={"adapters": {}})

    maybe_write_evidence({}, ctx, "https://example.invalid")

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


def test_debian_rules_url_uses_devel_branch_for_devel_and_named_branch_otherwise():
    base = "https://git.launchpad.net/ubuntu/+source/isa-support/tree/debian/rules"
    assert debian_rules_url("isa-support", None) == f"{base}?h=ubuntu/devel"
    assert debian_rules_url("isa-support", "devel") == f"{base}?h=ubuntu/devel"
    assert debian_rules_url("isa-support", "resolute") == f"{base}?h=ubuntu/resolute-devel"


def test_substitute_rules_url_replaces_placeholder_only_when_present():
    url = "https://git.launchpad.net/ubuntu/+source/isa-support/tree/debian/rules?h=ubuntu/devel"
    assert substitute_rules_url("rules at TBDRULESURL", "isa-support", "devel") == f"rules at {url}"
    assert substitute_rules_url("no placeholder", "isa-support", "devel") == "no placeholder"


def test_question_from_item_substitutes_rules_url_in_option_statement():
    ctx = SimpleNamespace(
        source_package="isa-support",
        series="resolute",
        evidence={"adapters": {}},
        catalog={"items": []},
    )
    item = {
        "id": "REP-QA-PKG-004",
        "question": {
            "kind": "single_choice",
            "prompt": "Is the packaging and build easy?",
            "options": [
                {
                    "id": "easy",
                    "label": "Packaging and build is easy",
                    "statement": "- Packaging and build is easy, link to debian/rules TBDRULESURL",
                }
            ],
        },
    }

    question = _question_from_item(item, ctx)

    assert question.options[0].statement == (
        "- Packaging and build is easy, link to debian/rules "
        "https://git.launchpad.net/ubuntu/+source/isa-support/tree/debian/rules"
        "?h=ubuntu/resolute-devel"
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


def test_unavailable_records_no_statement_only_the_reason():
    """Nothing was established, so no statement is claimed. The draft's
    "Left to clarify:" renderer rebuilds the original TODO context from the
    catalog, which stays the single source of that text."""
    item = {
        "id": "REP-BG-003",
        "section": "Background information",
        "template": "TODO: Link to package https://launchpad.net/ubuntu/+source/TBDSRC",
    }

    result = _unavailable(item, ReadinessEffect.WARNING, "no data", "rust-ntpd")

    assert result.statement == ""
    assert result.rationale == "no data"


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


def test_question_from_item_reads_leads_to_followup_flag():
    """The follow-up hint is catalog-declared per option (leads_to_followup),
    replacing the old symbolic analysis of sibling items' applicability trees."""
    ctx = SimpleNamespace(
        source_package="rust-ntpd", evidence={"adapters": {}}, catalog={"items": []}
    )
    item = {
        "id": "REP-RATIONALE-005",
        "question": {
            "kind": "single_choice",
            "prompt": "Broad or niche?",
            "options": [
                {"id": "broad", "label": "Broad", "statement": "Broadly useful."},
                {
                    "id": "niche",
                    "label": "Niche",
                    "statement": "Serves a niche.",
                    "leads_to_followup": True,
                },
            ],
        },
    }

    question = _question_from_item(item, ctx)

    by_id = {option.id: option for option in question.options}
    assert by_id["niche"].leads_to_followup is True
    assert by_id["broad"].leads_to_followup is False


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


# ---------------------------------------------------------------------------
# Assessment note/action split (feedback item 1c). "note" is context nobody
# has to act on; "action" is outstanding reporter work. Only the latter may
# affect readiness or move a statement out of the confident bullets.
# ---------------------------------------------------------------------------


def test_assessment_with_note_stays_a_confident_clear_statement():
    from reporter.evaluator import Assessment, _deterministic_result

    result = _deterministic_result(
        {"id": "REP-X", "section": "Security"},
        ReadinessEffect.WARNING,
        Assessment(statement="No CVEs were found.", note="Sourcing: tracker A and corpus B."),
    )

    assert result.state == StatementState.RESOLVED
    assert result.readiness == ReadinessEffect.CLEAR
    assert result.rationale == "Sourcing: tracker A and corpus B."


def test_assessment_with_action_keeps_readiness_and_needs_input():
    from reporter.evaluator import Assessment, _deterministic_result

    result = _deterministic_result(
        {"id": "REP-X", "section": "Maintenance/Owner"},
        ReadinessEffect.WARNING,
        Assessment(statement="No subscription was found.", action="A team must subscribe."),
    )

    assert result.state == StatementState.NEEDS_INPUT
    assert result.readiness == ReadinessEffect.WARNING
    assert result.rationale == "A team must subscribe."


def test_assessment_action_and_note_are_both_shown():
    from reporter.evaluator import Assessment

    assessment = Assessment(statement="x", action="Verify relevance.", note="Sourcing: tracker A.")

    assert assessment.rationale() == "Verify relevance. Sourcing: tracker A."


def test_clean_cve_history_leaves_the_reporter_nothing_to_do():
    """The OSS-security sourcing text is a note about what was queried; on a
    clean result it must not raise the item to warning readiness."""
    from reporter.evaluator import _EVALUATORS

    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "ubuntu-cve-tracker": {"status": "ok", "cves": []},
                "nvd-enrich": {"status": "ok", "cves": []},
            }
        }
    )

    assessment = _EVALUATORS["cve-history"]({"id": "REP-SECURITY-001"}, ctx)

    assert not assessment.action
    assert "OSS-security" in assessment.note


# ---------------------------------------------------------------------------
# Prefill derivation and the unfilled-slot safety net (feedback item 2).
# ---------------------------------------------------------------------------


def test_template_to_statement_keeps_tbd_and_drops_todo_markers():
    from reporter.text_utils import template_to_statement

    result = template_to_statement(
        "TODO: - The package TBDSRC is required in Ubuntu main for TBD", "libfoo"
    )

    assert result == "- The package src:libfoo is required in Ubuntu main for TBD"


def test_template_to_statement_indents_continuation_lines():
    from reporter.text_utils import template_to_statement

    result = template_to_statement(
        "TODO-B: - The package TBDSRC will not generally be useful for a large part of\n"
        "TODO-B:   our user base, but is important/helpful still because TBD",
        "libfoo",
    )

    assert result.splitlines() == [
        "- The package src:libfoo will not generally be useful for a large part of",
        "  our user base, but is important/helpful still because TBD",
    ]


def test_question_prefill_fills_the_first_slot_from_a_detected_default():
    from types import SimpleNamespace

    from reporter.evaluator import _question_prefill

    item = {
        "template": "TODO: Upstream Name is TBD",
        "question": {
            "kind": "multiline",
            "prompt": "What is the upstream project name?",
            "default_source": {"adapter": "upstream-tracker", "field": "upstream_name"},
        },
    }
    ctx = SimpleNamespace(
        source_package="rust-ntpd",
        evidence={"adapters": {"upstream-tracker": {"upstream_name": "ntpd-rs"}}},
    )

    assert _question_prefill(item, ctx) == "Upstream Name is ntpd-rs"


def test_question_prefill_is_empty_for_a_choice_question():
    from types import SimpleNamespace

    from reporter.evaluator import _question_prefill

    item = {
        "template": "TODO: - unused",
        "question": {"kind": "single_choice", "prompt": "Which?", "options": [{"id": "a"}]},
    }
    ctx = SimpleNamespace(source_package="libfoo", evidence={"adapters": {}})

    assert _question_prefill(item, ctx) == ""


def test_statement_left_with_a_tbd_is_carried_to_left_to_clarify():
    """A reporter may deliberately leave a slot open. That must become an
    open item, not a confident statement - and must not trip the draft
    linter's raw-TBD guard, which would abort the run at write time."""
    from reporter.evaluator import _resolved_or_open
    from reporter.models import Provenance, StatementResult

    result = _resolved_or_open(
        StatementResult(
            id="REP-X",
            section="Rationale",
            state=StatementState.RESOLVED,
            readiness=ReadinessEffect.BLOCKER,
            statement="- The package is needed because TBD",
            provenance=Provenance.HUMAN,
            human_confirmed=True,
        )
    )

    assert result.state == StatementState.NEEDS_INPUT
    assert result.statement == "- The package is needed because TBD"
    assert result.provenance is None


# ---------------------------------------------------------------------------
# Follow-up completion (catalog ``completes``): one alternative, one bullet.
# ---------------------------------------------------------------------------


def _completion_pair(child_state, child_statement):
    from reporter.models import Provenance, StatementResult

    parent = StatementResult(
        id="REP-PARENT",
        section="Maintenance/Owner",
        state=StatementState.RESOLVED,
        readiness=ReadinessEffect.CLEAR,
        statement="- A different owning team will subscribe to this package, named below.",
        selected_option="new-team",
        provenance=Provenance.HUMAN,
        human_confirmed=True,
    )
    child = StatementResult(
        id="REP-CHILD",
        section="Maintenance/Owner",
        state=child_state,
        readiness=ReadinessEffect.BLOCKER,
        statement=child_statement,
        provenance=Provenance.HUMAN if child_state == StatementState.RESOLVED else None,
        answer_refs=["REP-CHILD"],
        human_confirmed=child_state == StatementState.RESOLVED,
    )
    return parent, child


def test_completed_follow_up_replaces_the_parent_statement():
    from reporter.evaluator import _merge_into_completed_item

    parent, child = _completion_pair(
        StatementState.RESOLVED,
        "- The new owning team will be foundations-bugs and has acknowledged the commitment.",
    )

    _merge_into_completed_item({"id": "REP-CHILD", "completes": "REP-PARENT"}, child, [parent])

    assert parent.statement == (
        "- The new owning team will be foundations-bugs and has acknowledged the commitment."
    )
    assert parent.state == StatementState.RESOLVED
    assert parent.selected_option == "new-team"
    # The follow-up itself contributes no second bullet.
    assert child.state == StatementState.MERGED


def test_unfinished_follow_up_leaves_the_parent_open_too():
    from reporter.evaluator import _merge_into_completed_item

    parent, child = _completion_pair(
        StatementState.NEEDS_INPUT, "- The new owning team will be TBD and has acknowledged it."
    )

    _merge_into_completed_item({"id": "REP-CHILD", "completes": "REP-PARENT"}, child, [parent])

    assert parent.state == StatementState.NEEDS_INPUT
    assert parent.readiness == ReadinessEffect.BLOCKER
    assert "TBD" in parent.statement
