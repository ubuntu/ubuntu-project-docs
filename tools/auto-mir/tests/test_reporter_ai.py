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
        self.notes = []

    def confirm_suggestion(self, *, question_id, suggestion, rationale):
        self.questions.append(("confirm", suggestion, rationale))
        return Answer(question_id=question_id, value=self.accept, raw_input=str(self.accept))

    def ask(self, question):
        self.questions.append(("human", question.id))
        return Answer(
            question_id=question.id, value="human correction", raw_input="human correction"
        )

    def show_note(self, text, detail=""):
        self.notes.append((text, detail))


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
            "confidence": "high",
            "statement": "The package installs foo.service.",
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
            "confidence": "high",
            "statement": "Suggested text",
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


class EditingWizard:
    """Fake wizard whose confirm_suggestion returns the reporter's edited text."""

    def __init__(self, edited_text):
        self.edited_text = edited_text
        self.questions = []

    def confirm_suggestion(self, *, question_id, suggestion, rationale):
        self.questions.append(("confirm", suggestion, rationale))
        return Answer(question_id=question_id, value=self.edited_text, raw_input="edit")

    def ask(self, question):  # pragma: no cover - not expected to be called
        raise AssertionError("edited suggestions must not fall back to a manual question")


def test_edited_ai_suggestion_keeps_ai_confirmed_provenance(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "statement": "Original suggestion.",
            "rationale": "Because of the evidence.",
            "evidence_refs": ["binary-package-inspection:systemd_units"],
        },
    )
    wizard = EditingWizard(edited_text="Original suggestion, plus a reporter addendum.")

    result = ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert result.provenance == Provenance.AI_CONFIRMED
    assert result.human_confirmed is True
    assert result.statement == "Original suggestion, plus a reporter addendum."
    assert result.rationale == "Because of the evidence."


def test_evidence_payload_keeps_full_content_field_from_being_crowded_out(monkeypatch):
    """A large, low-priority field must never crowd out a field the item
    needs in full (regression test for the flat 30000-char cutoff bug)."""
    captured_prompts = []

    def _capture_call_llm(prompt, *_args, **_kwargs):
        captured_prompts.append(prompt)
        return {"confidence": "high", "statement": "x", "rationale": "y", "evidence_refs": []}

    monkeypatch.setattr(ai.llm, "call_llm", _capture_call_llm)
    item = {
        "id": "REP-QA-PKG-004",
        "section": "Quality assurance - packaging",
        "mode": "ev_to_ai",
        "readiness": "warning",
        "template": "TODO: - Assessment: TBD",
        "ai_policy": "Assess packaging complexity.",
        "adapters_required": ["packaging-source"],
    }
    ctx = SimpleNamespace(
        llm_token="token",
        no_llm=False,
        untrusted_nonce="nonce",
        source_package="libfoo",
        evidence={
            "adapters": {
                "packaging-source": {
                    "status": "ok",
                    "crypto_pattern_hits": ["x" * 5000, "y" * 5000, "z" * 5000],
                    "debian_rules": "small but important debian/rules content",
                }
            }
        },
    )
    wizard = ConfirmingWizard(accept=True)

    ai.evaluate_ai_item(item, ctx, wizard, _fallback_question())

    assert len(captured_prompts) == 1
    assert "small but important debian/rules content" in captured_prompts[0]


def test_low_confidence_skips_confirmation_and_asks_human_with_rationale(monkeypatch):
    """A low-confidence response must never be offered via yes/edit/no as if
    it were a final statement; it should show the rationale as a note and go
    straight to the human question."""
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "low",
            "rationale": "The evidence does not clearly show one way or the other.",
            "evidence_refs": [],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert not any(entry[0] == "confirm" for entry in wizard.questions)
    assert wizard.notes
    assert "does not clearly show" in wizard.notes[0][1]
    assert result.provenance == Provenance.HUMAN
    assert result.statement == "- Assessment: human correction"
    assert result.rationale == "The evidence does not clearly show one way or the other."


def test_high_confidence_missing_statement_falls_back_to_human(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "rationale": "Some rationale.",
            "evidence_refs": [],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert result.provenance == Provenance.HUMAN
    assert not any(entry[0] == "confirm" for entry in wizard.questions)


def test_high_confidence_hedge_phrase_rejected_and_falls_back_to_human(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "statement": "The packaging appears to use standard tooling.",
            "rationale": "Some rationale.",
            "evidence_refs": [],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert result.provenance == Provenance.HUMAN
    assert not any(entry[0] == "confirm" for entry in wizard.questions)


def test_invalid_confidence_value_falls_back_to_human(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "medium",
            "statement": "x",
            "rationale": "y",
            "evidence_refs": [],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert result.provenance == Provenance.HUMAN
