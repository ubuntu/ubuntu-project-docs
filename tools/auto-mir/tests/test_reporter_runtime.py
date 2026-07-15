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
from reporter.evaluator import evaluate_items  # noqa: E402
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
                    {"arch_tag": "amd64", "build_state": "Successfully built"},
                    {"arch_tag": "arm64", "build_state": "Successfully built"},
                ],
            },
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


def test_reporter_intake_prompts_for_series(tmp_path):
    ctx = _ctx(tmp_path)
    ctx.series = None
    wizard = FakeWizard("noble")

    pipeline.intake(ctx, wizard)

    assert ctx.series == "noble"
    assert wizard.asked == ["report-series"]
