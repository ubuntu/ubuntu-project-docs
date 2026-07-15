"""Tests for bounded reporter AI suggestions and mandatory confirmation."""

import sys
from pathlib import Path
from types import SimpleNamespace

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from reporter import ai  # noqa: E402
from reporter.models import Answer, Provenance, QuestionKind, QuestionSpec  # noqa: E402


class ConfirmingWizard:
    def __init__(self, accept=True):
        self.accept = accept
        self.questions = []

    def confirm_suggestion(self, *, question_id, suggestion, rationale):
        self.questions.append(("confirm", suggestion, rationale))
        return Answer(question_id=question_id, value=self.accept, raw_input=str(self.accept))

    def ask(self, question):
        self.questions.append(("human", question.id))
        return Answer(
            question_id=question.id, value="human correction", raw_input="human correction"
        )


def _item():
    return {
        "id": "REP-AI-001",
        "section": "Security",
        "mode": "ev_to_ai",
        "readiness": "warning",
        "template": "TODO: - Assessment: TBD",
        "ai_policy": "Assess only supplied evidence.",
        "adapters_required": ["binary-package-inspection"],
    }


def _ctx(token="token"):
    return SimpleNamespace(
        llm_token=token,
        no_llm=False,
        untrusted_nonce="nonce",
        source_package="libfoo",
        evidence={
            "adapters": {
                "binary-package-inspection": {
                    "status": "ok",
                    "systemd_units": ["foo.service"],
                }
            }
        },
    )


def _fallback_question():
    return QuestionSpec(id="REP-AI-001", prompt="Correct assessment", kind=QuestionKind.TEXT)


def test_ai_suggestion_requires_and_records_confirmation(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "suggestion": "The package installs foo.service.",
            "rationale": "The binary inspection listed that unit.",
            "evidence_refs": ["binary-package-inspection:systemd_units", "other:ignored"],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert result.provenance == Provenance.AI_CONFIRMED
    assert result.human_confirmed is True
    assert result.evidence_refs == ["binary-package-inspection:systemd_units"]
    assert wizard.questions[0][0] == "confirm"


def test_rejected_ai_suggestion_uses_human_correction(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "suggestion": "Suggested text",
            "rationale": "Evidence rationale",
            "evidence_refs": [],
        },
    )
    wizard = ConfirmingWizard(accept=False)

    result = ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert result.provenance == Provenance.HUMAN
    assert "human correction" in result.statement
    assert [entry[0] for entry in wizard.questions] == ["confirm", "human"]


def test_missing_llm_credential_goes_directly_to_human(monkeypatch):
    def fail(*_args, **_kwargs):
        raise AssertionError("LLM must not be called without a credential")

    monkeypatch.setattr(ai.llm, "call_llm", fail)
    wizard = ConfirmingWizard()

    result = ai.evaluate_ai_item(_item(), _ctx(token=""), wizard, _fallback_question())

    assert result.provenance == Provenance.HUMAN
    assert wizard.questions == [("human", "REP-AI-001")]
