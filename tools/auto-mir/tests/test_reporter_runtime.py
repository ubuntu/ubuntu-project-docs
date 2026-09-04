"""Tests for reporter evaluation, intake, and artifact rendering."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import catalog  # noqa: E402
from reporter import pipeline  # noqa: E402
from reporter.consistency import ConsistencyIssue, ConsistencyReport, validate_results  # noqa: E402
from reporter.evaluator import _question_from_item, _show_preface, evaluate_items  # noqa: E402
from reporter.models import (  # noqa: E402
    Answer,
    Provenance,
    QuestionKind,
    ReadinessEffect,
    StatementState,
)
from reporter.render import write_outputs  # noqa: E402
from utils.secrets import SecretRedactor  # noqa: E402


class FakeWizard:
    def __init__(self, value="human-provided explanation"):
        self.value = value
        self.asked: list[str] = []

    def _answer_value(self, question):
        # The real wizard only returns option ids for single_choice
        # questions; free text would be template-substituted and is not a
        # production path. Answer the first option id by default.
        if question.kind == QuestionKind.SINGLE_CHOICE:
            return question.options[0].id
        return self.value

    def ask(self, question):
        self.asked.append(question.id)
        value = self._answer_value(question)
        return Answer(question_id=question.id, value=value)

    def show_note(self, text, detail=""):
        pass


class ChoiceWizard(FakeWizard):
    values = {
        "REP-RATIONALE-005": "niche",
        "REP-RATIONALE-007": "no-deadline",
        "REP-QA-MAINT-004": "team-access",
        "REP-QA-TEST-005": "E-simulator",
        "REP-DEP-002": "separate",
    }

    def _answer_value(self, question):
        return self.values.get(question.id, super()._answer_value(question))


def _ctx(tmp_path):
    report_catalog = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    evidence = {
        "adapters": {
            "lp-package-api": {
                "status": "ok",
                "ubuntu_publish_history": [{"component": "universe"}],
            },
            "lp-build-api": {
                "status": "ok",
                "builds": [
                    {
                        "arch_tag": "amd64",
                        "build_state": "Successfully built",
                        "date_created": "2099-01-01T00:00:00+00:00",
                        "web_link": "https://launchpad.net/+build/1",
                    },
                    {
                        "arch_tag": "arm64",
                        "build_state": "Successfully built",
                        "date_created": "2099-01-01T00:00:00+00:00",
                        "web_link": "https://launchpad.net/+build/2",
                    },
                ],
            },
            "lp-mir-history": {"status": "ok", "prior_mir_bugs": []},
            "ubuntu-cve-tracker": {"status": "ok", "cves": []},
            "nvd-enrich": {"status": "ok", "cves": []},
            "lp-bug-search-api": {"status": "ok", "critical_bugs": []},
            "debian-bts": {"status": "ok", "rc_bugs": []},
            "fetch-build": {"status": "ok", "build_log": "dh_auto_test\npytest"},
            "packaging-source": {
                "status": "ok",
                "debian_watch": "version=4",
                "delta_kind": "sync",
                "source_maintainer": "Some Maintainer <maintainer@debian.org>",
            },
            "autopkgtest-db": {
                "status": "ok",
                "has_autopkgtest": True,
                "passing_arches": ["amd64"],
                "failing_arches": [],
            },
            "lintian": {"status": "ok", "lintian_errors": [], "lintian_warnings": []},
            "dep-analysis": {"status": "ok", "in_scope_deps_not_in_main": []},
            "team-mapping": {"status": "ok", "subscribed_teams": ["foundations-bugs"]},
            "upstream-tracker": {"status": "ok", "upstream_url": "https://example.test"},
            "deb-metadata": {
                "status": "ok",
                "deb_packages": [
                    {
                        "package": "libfoo",
                        "built_using": ["golang-github-test (= 1.0)"],
                        "static_built_using": [],
                    }
                ],
            },
            "binary-package-inspection": {
                "status": "ok",
                "setuid_setgid_binaries": [],
                "sbin_executables": [],
                "systemd_units": [],
                "cron_jobs": [],
                "apparmor_profiles": [],
                "desktop_files": [],
                "translation_files": [],
                "plugin_candidates": [],
            },
        },
        "catalog_summary": {},
        "collection_summary": {},
    }
    return SimpleNamespace(
        source_package="libfoo",
        series="devel",
        catalog=report_catalog,
        evidence=evidence,
        output_dir=tmp_path,
        guest_name="mir-report-libfoo",
        secret_redactor=SecretRedactor(),
        llm_calls_by_model={},
        llm_estimated_tokens={},
        report_path=None,
        reporter_draft_path=None,
        statement_results=[],
    )


def test_reporter_items_mix_deterministic_evidence_and_human_answers(tmp_path):
    ctx = _ctx(tmp_path)
    wizard = FakeWizard()

    results = evaluate_items(ctx, wizard)

    assert len(results) == len(ctx.catalog["items"])
    # NEEDS_INPUT is also expected here: a deterministic evaluator that found
    # a fact the reporter still has to act on (no recent build, no subscribed
    # team) resolves the fact but leaves the work open.
    assert all(
        result.state
        in {
            StatementState.RESOLVED,
            StatementState.NOT_APPLICABLE,
            StatementState.NEEDS_INPUT,
        }
        for result in results
    )
    assert any(result.provenance == Provenance.DETERMINISTIC for result in results)
    assert any(result.provenance == Provenance.HUMAN for result in results)
    assert "REP-RATIONALE-001" in wizard.asked
    source = next(result for result in results if result.id == "REP-AVAIL-001")
    assert "universe" in source.statement
    assert source.statement.startswith("- ")


def test_evaluate_items_logs_progress_for_every_catalog_item(tmp_path, caplog):
    ctx = _ctx(tmp_path)
    total = len(ctx.catalog["items"])

    with caplog.at_level("INFO", logger="auto_mir.reporter"):
        evaluate_items(ctx, FakeWizard())

    progress_messages = [
        record.getMessage() for record in caplog.records if record.getMessage().startswith("[")
    ]
    assert len(progress_messages) == total
    assert progress_messages[0] == (
        f"[1/{total}] Evaluating REP-AVAIL-001: Source package availability (deterministic)"
    )
    assert progress_messages[-1].startswith(f"[{total}/{total}] Evaluating ")


def test_deterministic_reporter_statements_all_get_a_leading_bullet(tmp_path):
    """Deterministic evaluators return hand-written prose without a leading
    bullet; ``evaluate_items`` must add exactly one, matching how catalog
    templates and option statements already embed their own ``- ``."""
    ctx = _ctx(tmp_path)

    results = evaluate_items(ctx, FakeWizard())

    deterministic_resolved = [
        result
        for result in results
        if result.provenance == Provenance.DETERMINISTIC and result.state == StatementState.RESOLVED
    ]
    assert deterministic_resolved
    for result in deterministic_resolved:
        assert result.statement.startswith("- "), result.id
        assert not result.statement.startswith("- - "), result.id


def test_reporter_render_writes_draft_and_structured_report(tmp_path):
    """Most catalog items marked ``readiness: blocker``/``warning`` have no
    per-option override (Phase 15 intentionally only added one to
    REP-QA-MAINT-004/REP-MAINT-006), so a generic wizard answer keeps their
    declared readiness rather than a false-positive CLEAR -- meaning this
    default run is genuinely not "ready" until a human reviews those items."""
    ctx = _ctx(tmp_path)
    results = evaluate_items(ctx, FakeWizard())

    write_outputs(ctx, results)

    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    assert "[Availability]" in draft
    assert "[Maintenance/Owner]" in draft
    assert "RULE:" not in draft
    assert "TBDSRC" not in draft
    assert "Ready for submission" not in draft

    report = json.loads(ctx.report_path.read_text(encoding="utf-8"))
    assert report["role"] == "report"
    assert report["source_package"] == "libfoo"
    assert report["readiness"]["ready"] is False
    assert "REP-RATIONALE-001" in report["readiness"]["blockers"]
    assert len(report["statements"]) == len(ctx.catalog["items"])


def test_reporter_draft_indents_continuation_lines_of_a_multi_line_answer(tmp_path):
    """A human multi-line free-text answer becomes one statement with
    embedded newlines; the rendered draft must indent every line after the
    first so they visually continue the same leading bullet."""
    ctx = _ctx(tmp_path)
    wizard = FakeWizard(
        value="Team hardware access is thoroughly documented.\n"
        "A simulator provides a secondary confirmation path."
    )

    results = evaluate_items(ctx, wizard)
    write_outputs(ctx, results)

    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    assert "Team hardware access is thoroughly documented." in draft
    assert "\n  A simulator provides a secondary confirmation path." in draft


def test_missing_deterministic_evidence_remains_honest_and_not_ready(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["lp-package-api"] = {"status": "error"}
    results = evaluate_items(ctx, FakeWizard())

    write_outputs(ctx, results)

    source = next(result for result in results if result.id == "REP-AVAIL-001")
    assert source.state == StatementState.UNAVAILABLE
    assert source.statement == ""
    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    # The item is not silently dropped: its original catalog TODO context is
    # rebuilt under the clarify block.
    assert "Left to clarify:" in draft
    report = json.loads(ctx.report_path.read_text(encoding="utf-8"))
    assert report["readiness"]["ready"] is False
    assert "REP-AVAIL-001" in report["readiness"]["unresolved"]


def test_consistency_error_forces_not_ready_rendering(tmp_path):
    ctx = _ctx(tmp_path)
    results = evaluate_items(ctx, FakeWizard())
    ctx.consistency_report = ConsistencyReport(
        ready=False,
        errors=[ConsistencyIssue("REP-MAINT-001", "contradiction", "Ownership conflict")],
    )

    write_outputs(ctx, results)

    report = json.loads(ctx.report_path.read_text(encoding="utf-8"))
    assert report["readiness"]["ready"] is False
    assert "REP-MAINT-001" in report["readiness"]["blockers"]


def test_readiness_summary_only_lists_items_still_genuinely_unresolved(tmp_path):
    """Regression test: previously, every item declared readiness:
    blocker/warning in the catalog stayed listed in the draft summary
    forever, even once the reporter had fully answered it with no leftover
    TODO marker. With a real consistency report (the normal production
    path), only genuinely unresolved/placeholder/contradictory items should
    remain listed."""
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["dep-analysis"] = {"status": "error", "message": "boom"}
    results = evaluate_items(ctx, FakeWizard())
    ctx.statement_results = results
    ctx.consistency_report = validate_results(results)

    write_outputs(ctx, results)

    report = json.loads(ctx.report_path.read_text(encoding="utf-8"))
    # REP-RATIONALE-001 is readiness: blocker in the catalog but was fully
    # answered by FakeWizard with no TODO marker left -- it must not be
    # re-listed as still blocking.
    assert "REP-RATIONALE-001" not in report["readiness"]["blockers"]
    assert "REP-RATIONALE-001" not in report["readiness"]["warnings"]
    # REP-QA-PKG-005 (readiness: blocker, deterministic) becomes genuinely
    # unavailable because dep-analysis errored -- a real remaining gap that
    # must stay listed.
    assert "REP-QA-PKG-005" in report["readiness"]["blockers"]


def test_readiness_summary_is_absent_from_the_draft_file(tmp_path):
    """The readiness summary must never end up in reporter-draft.txt: a
    submitter who copy-pastes the whole draft to Launchpad should not risk
    posting a stale "Ready for submission"/TODO-count line alongside it."""
    ctx = _ctx(tmp_path)
    results = evaluate_items(ctx, FakeWizard())
    ctx.statement_results = results
    ctx.consistency_report = validate_results(results)

    write_outputs(ctx, results)

    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    lines = draft.splitlines()

    assert "[Auto-MIR readiness summary]" not in draft
    assert "Ready for submission" not in draft
    assert "Remaining TODOs" not in draft
    # The draft now starts directly with the header, then the first section.
    first_section_index = next(i for i, line in enumerate(lines) if line == "[Availability]")
    assert lines[0] == f"MIR report for source package: {ctx.source_package}"
    assert first_section_index > 0


def test_readiness_summary_console_log_lists_only_must_resolve_items(tmp_path, caplog):
    """The trimmed console/log-only readiness summary lists "must resolve"
    TODOs, labelled by section/title, but never the "recommended,
    non-blocking" section: those are almost always already resolved by the
    end of the interactive session, and the few genuine leftovers are easy
    to spot directly in the draft (still a bare "TODO: -" line)."""
    ctx = _ctx(tmp_path)
    results = evaluate_items(ctx, FakeWizard())
    ctx.statement_results = results
    ctx.consistency_report = validate_results(results)

    with caplog.at_level("INFO", logger="auto_mir.reporter"):
        write_outputs(ctx, results)

    messages = [record.getMessage() for record in caplog.records]
    assert "[Auto-MIR readiness summary]" in messages
    assert any(message.startswith("Ready for submission: ") for message in messages)
    assert "Remaining TODOs (must resolve before submission):" in messages
    assert not any(
        "Remaining TODOs (recommended, non-blocking):" in message for message in messages
    )
    # Every listed id is labelled by its section/title, not shown bare.
    for message in messages:
        stripped = message.strip()
        if stripped.startswith("REP-"):
            assert " -- " in stripped


class NotingWizard(FakeWizard):
    def __init__(self, value="human-provided explanation"):
        super().__init__(value)
        self.notes: list[tuple[str, str]] = []

    def show_note(self, text, detail=""):
        self.notes.append((text, detail))


def test_preface_evaluator_surfaces_deterministic_note_before_question(tmp_path):
    ctx = _ctx(tmp_path)
    wizard = NotingWizard()
    item = {
        "id": "REP-RATIONALE-001",
        "section": "Rationale",
        "evaluator": "source-availability",
        "preface_evaluator": "source-availability",
    }

    _show_preface(item, ctx, wizard)

    assert wizard.notes
    assert "universe" in wizard.notes[0][0]


def test_preface_evaluator_silent_when_unavailable(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["lp-package-api"] = {"status": "error"}
    wizard = NotingWizard()
    item = {"id": "REP-RATIONALE-001", "preface_evaluator": "source-availability"}

    _show_preface(item, ctx, wizard)

    assert wizard.notes == []


def test_preface_evaluator_absent_is_a_no_op(tmp_path):
    ctx = _ctx(tmp_path)
    wizard = NotingWizard()

    _show_preface({"id": "REP-X"}, ctx, wizard)

    assert wizard.notes == []


def test_lintian_fhs_summary_preface_reports_error_and_warning_counts(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": ["E: fhs-violation"],
        "lintian_warnings": [],
    }
    wizard = NotingWizard()

    _show_preface({"id": "REP-STD-001", "preface_evaluator": "lintian-fhs-summary"}, ctx, wizard)

    assert wizard.notes
    assert "1 error(s)" in wizard.notes[0][0]
    assert "fhs-violation" in wizard.notes[0][1]


def test_lintian_fhs_summary_preface_explains_unavailability(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["lintian"] = {
        "status": "error",
        "message": "upstream dependency failed: fetch-build",
    }
    wizard = NotingWizard()

    _show_preface({"id": "REP-STD-001", "preface_evaluator": "lintian-fhs-summary"}, ctx, wizard)

    assert wizard.notes
    assert "upstream dependency failed: fetch-build" in wizard.notes[0][0]


def test_std_001_option_a_locked_when_lintian_reports_errors(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": ["E: fhs-violation"],
        "lintian_warnings": [],
    }
    item = next(item for item in ctx.catalog["items"] if item["id"] == "REP-STD-001")

    question = _question_from_item(item, ctx)

    by_id = {option.id: option for option in question.options}
    assert by_id["A-no-violations"].locked_reason != ""
    assert by_id["B-violations"].locked_reason == ""


def test_std_001_option_a_available_when_lintian_is_clean(tmp_path):
    ctx = _ctx(tmp_path)
    item = next(item for item in ctx.catalog["items"] if item["id"] == "REP-STD-001")

    question = _question_from_item(item, ctx)

    by_id = {option.id: option for option in question.options}
    assert by_id["A-no-violations"].locked_reason == ""


def test_maint_001_lock_survives_followup_marking(tmp_path):
    """Regression test: _mark_followup_options used to rebuild every option
    without carrying over locked_reason/list_note, so a locked option (e.g.
    REP-MAINT-001's confirm-subscribed, whose sibling REP-MAINT-001B makes
    'new-team' a followup-triggering option) would silently lose its lock
    the moment ANY option in the same question led to a follow-up."""
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["team-mapping"]["subscribed_teams"] = []
    item = next(item for item in ctx.catalog["items"] if item["id"] == "REP-MAINT-001")

    question = _question_from_item(item, ctx)

    by_id = {option.id: option for option in question.options}
    assert by_id["confirm-subscribed"].locked_reason != ""
    assert by_id["new-team"].leads_to_followup is True


def test_question_from_item_folds_preface_into_hint_for_editor_visibility(tmp_path):
    """A preface_evaluator's finding must also reach the question's own hint,
    not just the console-only pre-question note, so it is visible in the
    editor's commented-out hint area too (feedback: evidence-gated multiline
    questions were being asked with no visible context once inside the
    editor)."""
    ctx = _ctx(tmp_path)
    item = {
        "id": "REP-RATIONALE-001",
        "preface_evaluator": "source-availability",
        "question": {"kind": "multiline", "prompt": "Explain it"},
    }

    question = _question_from_item(item, ctx)

    assert "universe" in question.hint


def test_question_from_item_hint_empty_when_no_preface_evaluator(tmp_path):
    ctx = _ctx(tmp_path)
    item = {"id": "REP-X", "question": {"kind": "multiline", "prompt": "Explain it"}}

    question = _question_from_item(item, ctx)

    assert question.hint == ""


def test_failing_autopkgtest_question_shows_which_architectures_fail(tmp_path):
    """Regression test: REP-QA-TEST-007 used to ask reporters to explain
    failing autopkgtests with zero visibility into which architectures were
    actually failing, once thrown into the editor."""
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["autopkgtest-db"] = {
        "status": "ok",
        "has_autopkgtest": True,
        "passing_arches": ["amd64", "amd64v3", "s390x"],
        "failing_arches": ["arm64", "armhf", "i386", "ppc64el"],
    }
    item = next(item for item in ctx.catalog["items"] if item["id"] == "REP-QA-TEST-007")

    question = _question_from_item(item, ctx)

    assert "arm64" in question.hint
    assert "i386" in question.hint


def test_dependency_routing_shows_out_of_main_deps_before_asking(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["dep-analysis"]["in_scope_deps_not_in_main"] = ["libbar", "libbaz"]

    class NotingChoiceWizard(NotingWizard, ChoiceWizard):
        pass

    wizard = NotingChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-DEP-002" in wizard.asked
    preface_texts = " ".join(text for text, _detail in wizard.notes)
    assert "libbar" in preface_texts
    assert "libbaz" in preface_texts
    assert by_id["REP-DEP-002"].statement.startswith(
        "- Further dependencies outside main are handled by separate MIR bugs"
    )


def test_question_from_item_does_not_append_options_source_values_as_options(tmp_path):
    """``options_source`` no longer expands into individually-selectable
    options (that shape is now a ``single_choice`` + free-text follow-up
    item instead); it is only used to compute the shortcut spell-out list."""
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["dep-analysis"]["binary_packages"] = ["ntpd-rs", "ntpd-rs-metrics"]
    item = {
        "id": "REP-RATIONALE-004",
        "question": {
            "kind": "single_choice",
            "prompt": "Which binary packages need promotion?",
            "options": [
                {
                    "id": "__all_binaries__",
                    "label": "All binaries",
                    "statement": "All binary packages built by TBDSRC need to be in main.",
                    "exclusive": True,
                }
            ],
            "options_source": {"adapter": "dep-analysis", "field": "binary_packages"},
        },
    }

    question = _question_from_item(item, ctx)

    assert [option.id for option in question.options] == ["__all_binaries__"]
    assert question.options[0].exclusive is True


def test_question_from_item_options_source_still_drives_shortcut_spell_out(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["dep-analysis"]["binary_packages"] = ["ntpd-rs"]
    item = {
        "id": "REP-RATIONALE-004",
        "question": {
            "kind": "single_choice",
            "prompt": "Which binary packages need promotion?",
            "options": [
                {
                    "id": "__all_binaries__",
                    "label": "All binaries",
                    "statement": "All binary packages built by TBDSRC need to be in main.",
                    "exclusive": True,
                    "spell_out_filter": "all",
                }
            ],
            "options_source": {"adapter": "dep-analysis", "field": "binary_packages"},
        },
    }

    question = _question_from_item(item, ctx)

    assert [option.id for option in question.options] == ["__all_binaries__"]
    assert question.options[0].label == "All binaries: ntpd-rs"


def test_reporter_intake_defaults_to_devel_without_prompt(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.series = None
    wizard = FakeWizard("noble")

    pipeline.intake(ctx, wizard)

    assert ctx.series == "devel"
    assert wizard.asked == []


def test_reporter_intake_preserves_explicit_series(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.series = "noble"
    wizard = FakeWizard()

    pipeline.intake(ctx, wizard)

    assert ctx.series == "noble"
    assert wizard.asked == []


def test_reporter_choice_conditions_are_catalog_driven(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["dep-analysis"]["in_scope_deps_not_in_main"] = ["libbar"]
    wizard = ChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-RATIONALE-006" in wizard.asked
    assert "REP-RATIONALE-008" not in wizard.asked
    assert "REP-DEP-002" in wizard.asked
    assert "REP-DEP-003" in wizard.asked
    assert by_id["REP-RATIONALE-005"].selected_option == "niche"
    assert by_id["REP-QA-TEST-005"].selected_option == "E-simulator"
    assert "simulator" in by_id["REP-QA-TEST-005"].statement


def test_test_access_items_skipped_when_automated_testing_is_healthy(tmp_path):
    ctx = _ctx(tmp_path)

    class NoExoticHardwareWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-QA-MAINT-004": "no-exotic-hardware"}

    wizard = NoExoticHardwareWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-QA-TEST-005" not in wizard.asked
    assert "REP-QA-TEST-006" not in wizard.asked
    assert by_id["REP-QA-TEST-005"].state == StatementState.NOT_APPLICABLE
    assert by_id["REP-QA-TEST-006"].state == StatementState.NOT_APPLICABLE


def test_test_access_items_asked_when_autopkgtests_are_missing(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["autopkgtest-db"]["has_autopkgtest"] = False

    class NoExoticHardwareWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-QA-MAINT-004": "no-exotic-hardware"}

    wizard = NoExoticHardwareWizard()

    evaluate_items(ctx, wizard)

    assert "REP-QA-TEST-005" in wizard.asked


def test_hardware_access_elaboration_skipped_when_no_exotic_hardware(tmp_path):
    ctx = _ctx(tmp_path)

    class NoExoticHardwareWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-QA-MAINT-004": "no-exotic-hardware"}

    wizard = NoExoticHardwareWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-QA-MAINT-002" not in wizard.asked
    assert by_id["REP-QA-MAINT-002"].state == StatementState.NOT_APPLICABLE


def test_hardware_access_elaboration_asked_after_team_access_choice(tmp_path):
    """REP-QA-MAINT-004 (the canonical choice) must be asked before, and
    gate, REP-QA-MAINT-002 (the elaboration) instead of both asking an
    unlinked, overlapping question."""
    ctx = _ctx(tmp_path)
    wizard = ChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert wizard.asked.index("REP-QA-MAINT-004") < wizard.asked.index("REP-QA-MAINT-002")
    assert "REP-QA-MAINT-002" in wizard.asked
    assert by_id["REP-QA-MAINT-002"].state == StatementState.RESOLVED


def test_hardware_access_elaboration_asked_for_other_special_situation(tmp_path):
    ctx = _ctx(tmp_path)

    class OtherSpecialWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-QA-MAINT-004": "other-special"}

    wizard = OtherSpecialWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-QA-MAINT-002" in wizard.asked
    assert by_id["REP-QA-MAINT-002"].state == StatementState.RESOLVED


def test_exotic_hardware_clean_answer_does_not_block_readiness(tmp_path):
    ctx = _ctx(tmp_path)

    class NoExoticHardwareWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-QA-MAINT-004": "no-exotic-hardware"}

    wizard = NoExoticHardwareWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-QA-MAINT-004"].readiness == ReadinessEffect.CLEAR


def test_exotic_hardware_team_access_answer_still_blocks_readiness(tmp_path):
    ctx = _ctx(tmp_path)
    wizard = ChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-QA-MAINT-004"].readiness == ReadinessEffect.BLOCKER


def test_exotic_hardware_other_special_answer_still_blocks_readiness(tmp_path):
    ctx = _ctx(tmp_path)

    class OtherSpecialWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-QA-MAINT-004": "other-special"}

    wizard = OtherSpecialWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-QA-MAINT-004"].readiness == ReadinessEffect.BLOCKER


def test_cross_team_impact_no_impact_answer_does_not_block_readiness(tmp_path):
    ctx = _ctx(tmp_path)

    class NoImpactWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-MAINT-006": "no-impact"}

    wizard = NoImpactWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-MAINT-006"].readiness == ReadinessEffect.CLEAR


def test_cross_team_impact_coordinated_answer_does_not_block_readiness(tmp_path):
    ctx = _ctx(tmp_path)

    class CoordinatedWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-MAINT-006": "coordinated-impact"}

    wizard = CoordinatedWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-MAINT-006"].readiness == ReadinessEffect.CLEAR


def test_cross_team_impact_coordination_pending_answer_blocks_readiness(tmp_path):
    ctx = _ctx(tmp_path)

    class PendingWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-MAINT-006": "coordination-pending"}

    wizard = PendingWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-MAINT-006"].readiness == ReadinessEffect.BLOCKER
    assert "in progress" in by_id["REP-MAINT-006"].statement


def test_readiness_summary_reflects_option_override_blockers(tmp_path):
    """Per-option readiness overrides must actually surface in the rendered
    readiness summary, not just on the individual StatementResult."""
    ctx = _ctx(tmp_path)
    wizard = ChoiceWizard()

    results = evaluate_items(ctx, wizard)
    write_outputs(ctx, results)

    report = json.loads(ctx.report_path.read_text(encoding="utf-8"))
    assert "REP-QA-MAINT-004" in report["readiness"]["blockers"]


def test_vendored_maintenance_question_skipped_without_vendored_code(tmp_path):
    ctx = _ctx(tmp_path)
    wizard = ChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-MAINT-003" not in wizard.asked
    assert by_id["REP-MAINT-003"].state == StatementState.NOT_APPLICABLE


def test_vendored_maintenance_question_asked_with_vendored_code(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["packaging-source"]["shipped_vendored_dirs"] = ["third_party/zlib"]
    wizard = ChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-MAINT-003" in wizard.asked
    assert by_id["REP-MAINT-003"].state == StatementState.RESOLVED


def test_rust_vendoring_ok_when_cargo_lock_present():
    from reporter.evaluator import _rust_vendoring

    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "packaging-source": {"status": "ok", "cargo_lock_present": True},
            }
        }
    )
    assessment = _rust_vendoring({}, ctx)
    statement, refs = assessment.statement, assessment.evidence_refs
    rationale = assessment.rationale()
    assert "tracks its vendored dependencies via a committed Cargo.lock" in statement
    assert rationale == ""
    assert refs


def test_rust_vendoring_flags_missing_cargo_lock():
    from reporter.evaluator import _rust_vendoring

    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "packaging-source": {"status": "ok", "cargo_lock_present": False},
            }
        }
    )
    assessment = _rust_vendoring({}, ctx)
    statement = assessment.statement
    rationale = assessment.rationale()
    assert "no committed Cargo.lock" in statement
    assert rationale


def test_rust_vendoring_unavailable_when_adapter_errored():
    from reporter.evaluator import _rust_vendoring

    ctx = SimpleNamespace(evidence={"adapters": {"packaging-source": {"status": "error"}}})
    assessment = _rust_vendoring({}, ctx)
    statement = assessment.statement
    assert statement is None
    assert assessment.unavailable_reason


def test_rust_vendoring_item_not_applicable_for_non_rust_packages(tmp_path):
    ctx = _ctx(tmp_path)
    wizard = ChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-MAINT-007"].state == StatementState.NOT_APPLICABLE


def test_rust_vendoring_item_flags_missing_cargo_lock_for_rust_packages(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["packaging-source"]["is_rust_package"] = True
    ctx.evidence["adapters"]["packaging-source"]["cargo_lock_present"] = False
    wizard = ChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    # A missing Cargo.lock is something the reporter still has to fix, so the
    # finding is carried into the draft's "Left to clarify:" block (NEEDS_INPUT)
    # rather than presented as a settled statement.
    assert by_id["REP-MAINT-007"].state == StatementState.NEEDS_INPUT
    assert by_id["REP-MAINT-007"].readiness == ReadinessEffect.BLOCKER
    assert "no committed Cargo.lock" in by_id["REP-MAINT-007"].statement
    assert "Cargo.lock file is expected" in by_id["REP-MAINT-007"].rationale


def test_micro_library_item_skipped_for_non_library_packages(tmp_path):
    ctx = _ctx(tmp_path)
    wizard = ChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-QA-TEST-008" not in wizard.asked
    assert by_id["REP-QA-TEST-008"].state == StatementState.NOT_APPLICABLE


def test_micro_library_item_asked_when_evidence_shows_a_library(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["packaging-source"]["is_library_package"] = True
    wizard = ChoiceWizard()

    evaluate_items(ctx, wizard)

    assert "REP-QA-TEST-008" in wizard.asked


def test_micro_library_item_is_required_when_applicable():
    """Regression test for the Phase 5 coverage audit: RULE 4 in
    [Quality assurance - testing] requires a minimal library's wider
    solution-level testing to be "identified explicitly" - a
    `required: false` item could silently skip that identification. This
    item must stay required once its applicability condition is met."""
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}

    assert by_id["REP-QA-TEST-008"].get("required", True) is True


def test_license_lifetime_followup_skipped_when_no_concern_selected(tmp_path):
    ctx = _ctx(tmp_path)

    class NoConcernWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-STD-002": "A-no-concerns"}

    wizard = NoConcernWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-STD-002B" not in wizard.asked
    assert by_id["REP-STD-002B"].state == StatementState.NOT_APPLICABLE


def test_license_lifetime_followup_asked_when_concern_selected(tmp_path):
    ctx = _ctx(tmp_path)

    class ConcernWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-STD-002": "B-concerns"}

    wizard = ConcernWizard()

    evaluate_items(ctx, wizard)

    assert "REP-STD-002B" in wizard.asked


def test_binary_scope_specific_packages_followup_skipped_for_shortcut(tmp_path):
    ctx = _ctx(tmp_path)

    class AllBinariesWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-RATIONALE-004": "__all_binaries__"}

    wizard = AllBinariesWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-RATIONALE-004-SPECIFIC" not in wizard.asked
    assert by_id["REP-RATIONALE-004-SPECIFIC"].state == StatementState.NOT_APPLICABLE


def test_binary_scope_specific_packages_followup_asked_when_selected(tmp_path):
    ctx = _ctx(tmp_path)

    class SpecificPackagesWizard(ChoiceWizard):
        values = {
            **ChoiceWizard.values,
            "REP-RATIONALE-004": "specific-packages",
            "REP-RATIONALE-004-SPECIFIC": "ntpd-rs, ntpd-rs-metrics",
        }

    wizard = SpecificPackagesWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-RATIONALE-004-SPECIFIC" in wizard.asked
    assert "ntpd-rs, ntpd-rs-metrics" in by_id["REP-RATIONALE-004-SPECIFIC"].statement


def test_binary_packages_preface_surfaces_known_package_list(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["packaging-source"]["binary_package_names"] = [
        "ntpd-rs",
        "ntpd-rs-metrics",
    ]

    class NotingChoiceWizard(NotingWizard, ChoiceWizard):
        pass

    wizard = NotingChoiceWizard()

    evaluate_items(ctx, wizard)

    preface_texts = " ".join(text for text, _detail in wizard.notes)
    assert "ntpd-rs" in preface_texts
    assert "ntpd-rs-metrics" in preface_texts


def test_test_access_other_option_still_triggers_details_followup(tmp_path):
    ctx = _ctx(tmp_path)

    class OtherAccessWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-QA-TEST-005": "Z-other"}

    wizard = OtherAccessWizard()

    evaluate_items(ctx, wizard)

    assert "REP-QA-TEST-006" in wizard.asked


def test_owning_team_followup_skipped_when_keeping_subscribed_team(tmp_path):
    ctx = _ctx(tmp_path)

    class NotingChoiceWizard(NotingWizard, ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-MAINT-001": "confirm-subscribed"}

    wizard = NotingChoiceWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    preface_texts = " ".join(text for text, _detail in wizard.notes)
    assert "foundations-bugs" in preface_texts
    assert "REP-MAINT-001B" not in wizard.asked
    assert by_id["REP-MAINT-001B"].state == StatementState.NOT_APPLICABLE


def test_owning_team_followup_asked_when_new_team_selected(tmp_path):
    ctx = _ctx(tmp_path)

    class NewTeamWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-MAINT-001": "new-team"}

    wizard = NewTeamWizard()

    evaluate_items(ctx, wizard)

    assert "REP-MAINT-001B" in wizard.asked


def test_upstream_name_preface_surfaces_detected_url(tmp_path):
    ctx = _ctx(tmp_path)

    class NotingChoiceWizard(NotingWizard, ChoiceWizard):
        pass

    wizard = NotingChoiceWizard()

    evaluate_items(ctx, wizard)

    preface_texts = " ".join(text for text, _detail in wizard.notes)
    assert "https://example.test" in preface_texts


def test_background_catchall_is_omitted_when_left_empty(tmp_path):
    ctx = _ctx(tmp_path)

    class EmptyBackgroundWizard(ChoiceWizard):
        def ask(self, question):
            self.asked.append(question.id)
            if question.id == "REP-BG-001":
                return None
            value = self.values.get(question.id, self._answer_value(question))
            return Answer(question_id=question.id, value=value)

    wizard = EmptyBackgroundWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-BG-001"].state == StatementState.NOT_APPLICABLE

    write_outputs(ctx, results)
    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    assert "The package description and additional background" not in draft


def test_testing_gaps_question_is_optional_and_omitted_when_skipped(tmp_path):
    """REP-QA-TEST-003 must be skippable (leave the answer empty) without
    implying a gap exists, and never block readiness when skipped."""
    ctx = _ctx(tmp_path)
    report_catalog = ctx.catalog
    item = next(item for item in report_catalog["items"] if item["id"] == "REP-QA-TEST-003")
    assert item.get("required") is False

    class NoTestingGapsWizard(ChoiceWizard):
        def ask(self, question):
            self.asked.append(question.id)
            if question.id == "REP-QA-TEST-003":
                return None
            value = self.values.get(question.id, self._answer_value(question))
            return Answer(question_id=question.id, value=value)

    wizard = NoTestingGapsWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-QA-TEST-003"].state == StatementState.NOT_APPLICABLE
    assert by_id["REP-QA-TEST-003"].readiness == ReadinessEffect.CLEAR

    write_outputs(ctx, results)
    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    assert "Testing gaps and the owning team test plan" not in draft


def test_ui_not_end_user_facing_gate_auto_resolves_desktop_and_translation(tmp_path):
    """Regression test for feedback items 1c/1d: a package judged not
    end-user-facing must get BOTH its desktop-file and translation
    statements automatically (no re-asking, no risk of contradicting
    itself), and the actual TODO-C wording the user asked for must appear."""
    ctx = _ctx(tmp_path)

    class NotUiWizard(ChoiceWizard):
        values = {**ChoiceWizard.values, "REP-UI-001": "not-end-user-facing"}

    wizard = NotUiWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert "REP-UI-002" not in wizard.asked
    assert "REP-UI-003" not in wizard.asked
    assert by_id["REP-UI-002"].state == StatementState.NOT_APPLICABLE
    assert by_id["REP-UI-003"].state == StatementState.NOT_APPLICABLE
    assert by_id["REP-UI-002-NOT-APPLICABLE"].state == StatementState.RESOLVED
    assert "no Desktop file is needed" in by_id["REP-UI-002-NOT-APPLICABLE"].statement
    assert by_id["REP-UI-003-NOT-APPLICABLE"].state == StatementState.RESOLVED
    assert (
        by_id["REP-UI-003-NOT-APPLICABLE"].statement
        == "- Application is not end-user facing (does not need translation)."
    )

    write_outputs(ctx, results)
    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    assert "[UI standards]" in draft
    assert "no Desktop file is needed" in draft
    assert "Application is not end-user facing (does not need translation)." in draft
    assert "assessment:" not in draft.casefold()


def test_ui_end_user_facing_asks_desktop_and_translation_separately(tmp_path):
    """When end-user facing, desktop-file and translation are independently
    resolved (the missing-desktop-file / has-translation combination proves
    they are not coupled to a single yes/no)."""
    ctx = _ctx(tmp_path)

    class UiWizard(ChoiceWizard):
        values = {
            **ChoiceWizard.values,
            "REP-UI-001": "end-user-facing",
            "REP-UI-002": "missing-desktop-file",
            "REP-UI-003": "has-translation",
        }

    wizard = UiWizard()

    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert by_id["REP-UI-002-NOT-APPLICABLE"].state == StatementState.NOT_APPLICABLE
    assert by_id["REP-UI-003-NOT-APPLICABLE"].state == StatementState.NOT_APPLICABLE
    assert (
        by_id["REP-UI-002"].statement
        == "- This package is end-user facing but does not ship a desktop file."
    )
    assert by_id["REP-UI-002"].readiness == ReadinessEffect.WARNING
    assert (
        by_id["REP-UI-003"].statement
        == "- Translation is present, via a standard intltool/gettext or similar "
        "build and runtime internationalization system."
    )
    assert by_id["REP-UI-003"].readiness == ReadinessEffect.CLEAR

    write_outputs(ctx, results)
    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    assert "does not ship a desktop file" in draft
    assert "Translation is present" in draft
    assert "assessment:" not in draft.casefold()


def _maintainer_field_evidence(*, delta_kind, source_maintainer, version="1.0-1ubuntu1"):
    return {
        "status": "ok",
        "delta_kind": delta_kind,
        "source_maintainer": source_maintainer,
        "analyzed_version": version,
    }


def test_lintian_overrides_ok_when_no_entries():
    from reporter.evaluator import _lintian_overrides

    ctx = SimpleNamespace(
        evidence={
            "adapters": {"packaging-source": {"status": "ok", "lintian_override_entries": []}}
        }
    )
    assessment = _lintian_overrides({}, ctx)
    statement, refs = assessment.statement, assessment.evidence_refs
    rationale = assessment.rationale()
    assert statement == "Lintian overrides are absent or already explained by a comment."
    assert rationale == ""
    assert refs


def test_lintian_overrides_ok_when_all_commented():
    from reporter.evaluator import _lintian_overrides

    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "packaging-source": {
                    "status": "ok",
                    "lintian_override_entries": [{"tag": "some-tag", "has_comment": True}],
                }
            }
        }
    )
    assessment = _lintian_overrides({}, ctx)
    statement = assessment.statement
    rationale = assessment.rationale()
    assert statement == "Lintian overrides are absent or already explained by a comment."
    assert rationale == ""


def test_lintian_overrides_flags_uncommented_entry():
    from reporter.evaluator import _lintian_overrides

    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "packaging-source": {
                    "status": "ok",
                    "lintian_override_entries": [
                        {"tag": "some-tag", "has_comment": True},
                        {"tag": "another-tag", "has_comment": False},
                    ],
                }
            }
        }
    )
    assessment = _lintian_overrides({}, ctx)
    statement = assessment.statement
    rationale = assessment.rationale()
    assert "another-tag" in statement
    assert "some-tag" not in statement
    assert rationale


def test_lintian_overrides_unavailable_when_adapter_errored():
    from reporter.evaluator import _lintian_overrides

    ctx = SimpleNamespace(evidence={"adapters": {"packaging-source": {"status": "error"}}})
    assessment = _lintian_overrides({}, ctx)
    statement = assessment.statement
    assert statement is None
    assert assessment.unavailable_reason


def test_reporter_lintian_override_followup_not_applicable_when_all_commented(tmp_path):
    """Default fixture has no lintian overrides - REP-QA-PKG-008 must resolve to
    the plain OK statement and REP-QA-PKG-009's explanation question must never
    fire."""
    ctx = _ctx(tmp_path)
    wizard = FakeWizard()
    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert (
        by_id["REP-QA-PKG-008"].statement
        == "- Lintian overrides are absent or already explained by a comment."
    )
    assert by_id["REP-QA-PKG-008"].readiness == ReadinessEffect.CLEAR
    assert by_id["REP-QA-PKG-009"].state == StatementState.NOT_APPLICABLE
    assert "REP-QA-PKG-009" not in wizard.asked


def test_reporter_lintian_override_followup_fires_when_uncommented(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["packaging-source"]["lintian_override_entries"] = [
        {"tag": "some-tag", "has_comment": False}
    ]
    ctx.evidence["adapters"]["packaging-source"]["lintian_uncommented_override_tags"] = ["some-tag"]
    wizard = FakeWizard(value="some-tag is needed because upstream ships a false positive.")
    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    # The gap itself is handed to the follow-up item below, so the detecting
    # statement carries only a cross-reference note and stays readiness-clear.
    assert by_id["REP-QA-PKG-008"].state == StatementState.RESOLVED
    assert by_id["REP-QA-PKG-008"].readiness == ReadinessEffect.CLEAR
    assert "some-tag" in by_id["REP-QA-PKG-008"].statement
    assert "following item" in by_id["REP-QA-PKG-008"].rationale
    assert "REP-QA-PKG-009" in wizard.asked
    followup = by_id["REP-QA-PKG-009"]
    assert followup.state == StatementState.RESOLVED
    assert "some-tag is needed" in followup.statement


def test_maintainer_field_ok_when_no_delta():
    from reporter.evaluator import _maintainer_field

    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "packaging-source": _maintainer_field_evidence(
                    delta_kind="sync", source_maintainer="Debian Person <p@debian.org>"
                )
            }
        }
    )
    assessment = _maintainer_field({}, ctx)
    statement, refs = assessment.statement, assessment.evidence_refs
    rationale = assessment.rationale()
    assert statement == "debian/control defines a correct Maintainer field"
    assert rationale == ""
    assert refs


def test_maintainer_field_ok_when_delta_and_ubuntu_developers():
    from reporter.evaluator import _maintainer_field

    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "packaging-source": _maintainer_field_evidence(
                    delta_kind="ubuntu_delta",
                    source_maintainer="Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>",
                )
            }
        }
    )
    assessment = _maintainer_field({}, ctx)
    statement = assessment.statement
    rationale = assessment.rationale()
    assert statement == "debian/control defines a correct Maintainer field"
    assert rationale == ""


def test_maintainer_field_flags_delta_with_wrong_maintainer():
    from reporter.evaluator import _maintainer_field

    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "packaging-source": _maintainer_field_evidence(
                    delta_kind="ubuntu_delta",
                    source_maintainer="Eric Berry <eric.berry@canonical.com>",
                    version="1.0-1ubuntu2",
                )
            }
        }
    )
    assessment = _maintainer_field({}, ctx)
    statement = assessment.statement
    rationale = assessment.rationale()
    assert "needs attention" in statement
    assert "1.0-1ubuntu2" in statement
    assert "Eric Berry" in statement
    assert rationale


def test_maintainer_field_unavailable_when_delta_kind_unknown():
    from reporter.evaluator import _maintainer_field

    ctx = SimpleNamespace(
        evidence={
            "adapters": {
                "packaging-source": _maintainer_field_evidence(
                    delta_kind="unknown", source_maintainer=""
                )
            }
        }
    )
    assessment = _maintainer_field({}, ctx)
    statement = assessment.statement
    assert statement is None
    assert assessment.unavailable_reason


def test_maintainer_field_unavailable_when_adapter_errored():
    from reporter.evaluator import _maintainer_field

    ctx = SimpleNamespace(evidence={"adapters": {"packaging-source": {"status": "error"}}})
    assessment = _maintainer_field({}, ctx)
    statement = assessment.statement
    assert statement is None
    assert assessment.unavailable_reason


def test_reporter_maintainer_followup_not_applicable_when_no_delta(tmp_path):
    """Default fixture has no Ubuntu delta - REP-QA-PKG-006 must resolve to the
    plain OK statement and REP-QA-PKG-007's escalation question must never
    fire."""
    ctx = _ctx(tmp_path)
    wizard = FakeWizard()
    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    assert (
        by_id["REP-QA-PKG-006"].statement == "- debian/control defines a correct Maintainer field"
    )
    assert by_id["REP-QA-PKG-006"].readiness == ReadinessEffect.CLEAR
    assert by_id["REP-QA-PKG-007"].state == StatementState.NOT_APPLICABLE
    assert "REP-QA-PKG-007" not in wizard.asked


def test_reporter_maintainer_followup_fires_when_delta_and_wrong_maintainer(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["packaging-source"] = _maintainer_field_evidence(
        delta_kind="ubuntu_delta",
        source_maintainer="Eric Berry <eric.berry@canonical.com>",
    )
    wizard = FakeWizard(value="Will run update-maintainer before upload.")
    results = evaluate_items(ctx, wizard)
    by_id = {result.id: result for result in results}

    # As with the lintian-override pair, the resolution plan is the follow-up
    # item's job; the detecting statement only points at it.
    assert by_id["REP-QA-PKG-006"].state == StatementState.RESOLVED
    assert by_id["REP-QA-PKG-006"].readiness == ReadinessEffect.CLEAR
    assert "needs attention" in by_id["REP-QA-PKG-006"].statement
    assert "following item" in by_id["REP-QA-PKG-006"].rationale
    assert "REP-QA-PKG-007" in wizard.asked
    followup = by_id["REP-QA-PKG-007"]
    assert followup.state == StatementState.RESOLVED
    assert followup.readiness == ReadinessEffect.BLOCKER
    assert "update-maintainer" in followup.statement


def test_cve_history_statement_carries_sourcing_note():
    """G5 alignment: the reporter-facing security-history statement names the
    sources actually consulted (Ubuntu tracker + cvelistV5/NVD covering
    Debian-relevant identifiers; oss-security only on manual flag), mirroring
    the reviewer SEC-1's already-reasoned position - so no reporter is asked to
    hand-check Debian or NVD separately."""
    ctx = _ctx(tmp_path=None)
    ctx.evidence["adapters"]["ubuntu-cve-tracker"] = {"status": "ok", "cves": []}
    ctx.evidence["adapters"]["nvd-enrich"] = {"status": "ok", "cves": []}

    from reporter.evaluator import _EVALUATORS

    assessment = _EVALUATORS["cve-history"]({"id": "REP-SECURITY-001"}, ctx)
    statement, refs = assessment.statement, assessment.evidence_refs
    rationale = assessment.rationale()

    assert "No package-associated CVEs" in statement
    assert "cvelistV5/NVD" in rationale
    assert "Debian-relevant" in rationale
    assert "OSS-security" in rationale
    assert refs == ["ubuntu-cve-tracker:cves", "nvd-enrich:cves"]


def test_built_using_surface_item_states_the_declared_entries():
    """G4: the reporter now surfaces binary-level Built-Using/Static-Built-Using
    facts (collected by deb-metadata, which report runs already support via
    fetch-build). Facts only - the statement lists what the binaries declare;
    the commitment judgement stays with the human items."""
    from reporter.evaluator import _EVALUATORS

    ctx = _ctx(tmp_path=None)
    ctx.evidence["adapters"]["deb-metadata"] = {
        "status": "ok",
        "deb_packages": [
            {"built_using": ["golang-github-x (= 1.2)"], "static_built_using": ["rust-y (= 0.9)"]},
        ],
    }
    assessment = _EVALUATORS["built-using-surface"]({"id": "REP-MAINT-008"}, ctx)
    statement, refs = assessment.statement, assessment.evidence_refs
    rationale = assessment.rationale()

    assert "golang-github-x (= 1.2)" in statement
    assert "rust-y (= 0.9)" in statement
    assert refs == ["deb-metadata:deb_packages"]
    assert "obligations" in rationale


def test_built_using_surface_item_clean_when_no_entries():
    from reporter.evaluator import _EVALUATORS

    ctx = _ctx(tmp_path=None)
    ctx.evidence["adapters"]["deb-metadata"] = {"status": "ok", "deb_packages": []}

    assessment = _EVALUATORS["built-using-surface"]({"id": "REP-MAINT-008"}, ctx)
    statement = assessment.statement
    rationale = assessment.rationale()

    assert "declare no Built-Using" in statement
    assert rationale == ""


def test_built_using_surface_item_unavailable_when_metadata_fails():
    from reporter.evaluator import _EVALUATORS

    ctx = _ctx(tmp_path=None)
    ctx.evidence["adapters"]["deb-metadata"] = {"status": "error", "message": "boom"}

    assessment = _EVALUATORS["built-using-surface"]({"id": "REP-MAINT-008"}, ctx)
    statement = assessment.statement

    assert statement is None
    assert "unavailable" in assessment.unavailable_reason


def test_built_using_surface_lands_in_the_draft_under_maintenance():
    """The item is blueprint-absent (runtime-only): the refactor's draft builder
    appends such resolved statements at their section's end."""
    import tempfile

    ctx = _ctx(Path(tempfile.mkdtemp()))
    results = evaluate_items(ctx, FakeWizard())
    write_outputs(ctx, results)

    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    maint = draft.index("[Maintenance/Owner]")
    background = draft.index("[Background information]")
    section = draft[maint:background]
    assert "Built binaries declare Built-Using/Static-Built-Using:" in section
    assert "golang-github-test (= 1.0)" in section
