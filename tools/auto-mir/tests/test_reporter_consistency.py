"""Tests for deterministic and bounded AI reporter consistency validation."""

import sys
from pathlib import Path
from types import SimpleNamespace

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from reporter import consistency  # noqa: E402
from reporter.models import (  # noqa: E402
    Answer,
    Provenance,
    ReadinessEffect,
    StatementResult,
    StatementState,
)


def _result(
    *,
    item_id="REP-1",
    state=StatementState.RESOLVED,
    readiness=ReadinessEffect.CLEAR,
    statement="Resolved statement",
    rationale="",
):
    return StatementResult(
        id=item_id,
        section="Rationale",
        state=state,
        readiness=readiness,
        statement=statement,
        provenance=Provenance.HUMAN if state == StatementState.RESOLVED else None,
        rationale=rationale,
        human_confirmed=state == StatementState.RESOLVED,
    )


class Wizard:
    def __init__(self):
        self.questions = []

    def ask(self, question):
        self.questions.append(question)
        return Answer(question_id=question.id, value="Reporter correction.")


def test_deterministic_consistency_blocks_unresolved_blocker():
    result = StatementResult(
        id="REP-BLOCKER",
        section="Maintenance/Owner",
        state=StatementState.UNAVAILABLE,
        readiness=ReadinessEffect.BLOCKER,
        statement="TODO: owning team",
        rationale="No answer",
    )

    report = consistency.validate_results([result])

    assert report.ready is False
    assert [issue.item_id for issue in report.errors] == ["REP-BLOCKER"]


def test_deterministic_consistency_warns_on_nonblocking_evidence_concern():
    report = consistency.validate_results(
        [_result(item_id="REP-WARN", readiness=ReadinessEffect.WARNING, rationale="Check this")]
    )

    assert report.ready is True
    assert report.warnings[0].category == "evidence-concern"


def test_ai_consistency_accepts_known_ids_and_prompts_correction(monkeypatch):
    result = _result(item_id="REP-1")
    ctx = SimpleNamespace(
        statement_results=[result],
        llm_token="token",
        no_llm=False,
        untrusted_nonce="nonce",
    )
    monkeypatch.setattr(
        consistency.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "issues": [
                {
                    "item_id": "REP-1",
                    "category": "missing-explanation",
                    "explanation": "The claim needs context.",
                    "follow_up_question": "Provide the missing context.",
                },
                {
                    "item_id": "UNKNOWN",
                    "category": "contradiction",
                    "explanation": "Ignored",
                    "follow_up_question": "Ignored",
                },
            ]
        },
    )
    wizard = Wizard()

    report = consistency.run_consistency_pass(ctx, wizard)

    assert report.ai_checked is True
    assert len(wizard.questions) == 1
    assert "Reporter correction." in result.statement
    assert result.provenance == Provenance.HUMAN


def test_human_correction_replaces_statement_instead_of_appending(monkeypatch):
    """The reporter's answer to a consistency follow-up is an authoritative
    override, not an addendum sitting alongside the tool's earlier text."""
    result = _result(
        item_id="REP-1",
        statement=(
            "Autopkgtests exist and pass on all architectures, they are "
            "providing sufficient coverage for all general functions."
        ),
    )
    ctx = SimpleNamespace(
        statement_results=[result],
        llm_token="token",
        no_llm=False,
        untrusted_nonce="nonce",
    )
    monkeypatch.setattr(
        consistency.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "issues": [
                {
                    "item_id": "REP-1",
                    "category": "unsupported-claim",
                    "explanation": "The statement contradicts its own rationale.",
                    "follow_up_question": "Can you confirm sufficient coverage?",
                }
            ]
        },
    )
    wizard = Wizard()

    consistency.run_consistency_pass(ctx, wizard)

    assert result.statement == "- Reporter correction."
    assert "Autopkgtests exist and pass" not in result.statement


def test_no_llm_runs_deterministic_consistency_only(monkeypatch):
    ctx = SimpleNamespace(statement_results=[_result()], llm_token="", no_llm=False)

    def fail(*_args, **_kwargs):
        raise AssertionError("LLM must not run")

    monkeypatch.setattr(consistency.llm, "call_llm", fail)

    report = consistency.run_consistency_pass(ctx, Wizard())

    assert report.ready is True
    assert report.ai_checked is False
