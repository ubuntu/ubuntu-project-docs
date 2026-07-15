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
from reporter.consistency import ConsistencyIssue, ConsistencyReport  # noqa: E402
from reporter.evaluator import _question_from_item, _show_preface, evaluate_items  # noqa: E402
from reporter.models import Answer, Provenance, StatementState  # noqa: E402
from reporter.render import write_outputs  # noqa: E402
from utils.secrets import SecretRedactor  # noqa: E402


class FakeWizard:
    def __init__(self, value="human-provided explanation"):
        self.value = value
        self.asked: list[str] = []

    def ask(self, question):
        self.asked.append(question.id)
        return Answer(question_id=question.id, value=self.value, raw_input=self.value)


class ChoiceWizard(FakeWizard):
    values = {
        "REP-RATIONALE-005": "niche",
        "REP-RATIONALE-007": "no-deadline",
        "REP-QA-MAINT-004": "team-access",
        "REP-QA-TEST-005": ["A-team-hardware", "E-simulator"],
        "REP-DEP-002": "separate",
    }

    def ask(self, question):
        self.asked.append(question.id)
        value = self.values.get(question.id, self.value)
        return Answer(question_id=question.id, value=value, raw_input=str(value))


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
            "sbuild": {"status": "ok", "build_log": "dh_auto_test\npytest"},
            "packaging-source": {"status": "ok", "debian_watch": "version=4"},
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
    assert all(
        result.state in {StatementState.RESOLVED, StatementState.NOT_APPLICABLE}
        for result in results
    )
    assert any(result.provenance == Provenance.DETERMINISTIC for result in results)
    assert any(result.provenance == Provenance.HUMAN for result in results)
    assert "REP-RATIONALE-001" in wizard.asked
    source = next(result for result in results if result.id == "REP-AVAIL-001")
    assert "universe" in source.statement


def test_reporter_render_writes_draft_and_structured_report(tmp_path):
    ctx = _ctx(tmp_path)
    results = evaluate_items(ctx, FakeWizard())

    write_outputs(ctx, results)

    draft = ctx.reporter_draft_path.read_text(encoding="utf-8")
    assert "[Availability]" in draft
    assert "[Maintenance/Owner]" in draft
    assert "RULE:" not in draft
    assert "TBDSRC" not in draft
    assert "Ready for submission: yes" in draft

    report = json.loads(ctx.report_path.read_text(encoding="utf-8"))
    assert report["role"] == "report"
    assert report["source_package"] == "libfoo"
    assert report["readiness"]["ready"] is True
    assert len(report["statements"]) == len(ctx.catalog["items"])


def test_missing_deterministic_evidence_remains_honest_and_not_ready(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["lp-package-api"] = {"status": "error"}
    results = evaluate_items(ctx, FakeWizard())

    write_outputs(ctx, results)

    source = next(result for result in results if result.id == "REP-AVAIL-001")
    assert source.state == StatementState.UNAVAILABLE
    assert source.statement.startswith("TODO:")
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


def test_question_from_item_appends_dynamic_options_from_evidence(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["dep-analysis"]["binary_packages"] = ["ntpd-rs", "ntpd-rs-metrics"]
    item = {
        "id": "REP-RATIONALE-004",
        "question": {
            "kind": "multi_choice",
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

    option_ids = [option.id for option in question.options]
    assert option_ids == ["__all_binaries__", "ntpd-rs", "ntpd-rs-metrics"]
    assert question.options[0].exclusive is True
    assert question.options[1].exclusive is False


def test_question_from_item_skips_options_source_values_already_declared(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.evidence["adapters"]["dep-analysis"]["binary_packages"] = ["ntpd-rs"]
    item = {
        "id": "REP-RATIONALE-004",
        "question": {
            "kind": "multi_choice",
            "prompt": "Which binary packages need promotion?",
            "options": [{"id": "ntpd-rs", "label": "ntpd-rs (already listed)"}],
            "options_source": {"adapter": "dep-analysis", "field": "binary_packages"},
        },
    }

    question = _question_from_item(item, ctx)

    assert [option.id for option in question.options] == ["ntpd-rs"]


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


def test_reporter_choice_conditions_and_multi_choice_are_catalog_driven(tmp_path):
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
    assert by_id["REP-QA-TEST-005"].selected_option == [
        "A-team-hardware",
        "E-simulator",
    ]
    assert "required hardware" in by_id["REP-QA-TEST-005"].statement
    assert "simulator" in by_id["REP-QA-TEST-005"].statement
