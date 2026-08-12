"""Tests for bounded reporter AI suggestions and mandatory confirmation."""

import sys
from pathlib import Path
from types import SimpleNamespace

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from reporter import ai  # noqa: E402
from reporter.models import (  # noqa: E402
    Answer,
    Provenance,
    QuestionKind,
    QuestionOption,
    QuestionSpec,
    ReadinessEffect,
    StatementState,
)


class ConfirmingWizard:
    def __init__(self, accept=True):
        self.accept = accept
        self.questions = []
        self.notes = []
        self.lock_yes_reasons = []

    def confirm_suggestion(self, *, question_id, suggestion, rationale, lock_yes_reason=None):
        self.questions.append(("confirm", suggestion, rationale))
        self.lock_yes_reasons.append(lock_yes_reason)
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


def _fallback_question_multiline():
    """A multiline fallback question, matching how every real catalog item hit
    by the "<Label>: <answer>" duplication bug (feedback item 1a) is actually
    declared (`question.kind: multiline`) - `_fallback_question()` above uses
    `TEXT`, which never exercised the buggy code path. `deferrable=True`
    matches how `evaluator._question_from_item` always builds an ev_to_ai
    fallback question in production."""
    return QuestionSpec(
        id="REP-AI-001",
        prompt="Assess something",
        kind=QuestionKind.MULTILINE,
        deferrable=True,
    )


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


def _bg_002_item():
    return {
        "id": "REP-BG-002",
        "section": "Background information",
        "mode": "ev_to_ai",
        "readiness": "clear",
        "template": "TODO: - Upstream Name is TBD",
        "ai_policy": "State the upstream project's name.",
        "adapters_required": ["upstream-tracker", "packaging-source"],
        "writes_evidence": {"adapter": "upstream-tracker", "field": "upstream_url"},
    }


def _bg_002_ctx(token="token"):
    return SimpleNamespace(
        llm_token=token,
        no_llm=False,
        untrusted_nonce="nonce",
        source_package="ntpd-rs",
        evidence={
            "adapters": {
                "upstream-tracker": {"status": "ok", "upstream_url": "", "upstream_name": ""},
                "packaging-source": {
                    "status": "ok",
                    "debian_control": (
                        "Source: rust-ntpd\nHomepage: https://github.com/pendulum-project/ntpd-rs\n"
                    ),
                },
            }
        },
    )


def _bg_002_fallback_question():
    return QuestionSpec(
        id="REP-BG-002", prompt="What is the upstream project name?", kind=QuestionKind.TEXT
    )


def test_rep_bg_002_accepted_ai_suggestion_names_the_upstream_project(monkeypatch):
    """Regression test for feedback item 3: REP-BG-002 is ev_to_ai and can
    suggest a project name grounded in the verified upstream URL plus
    debian/control, which the reporter can accept as-is."""
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "statement": "The upstream project is ntpd-rs (pendulum-project/ntpd-rs on GitHub).",
            "rationale": "debian/control's Homepage names the ntpd-rs GitHub project.",
            "evidence_refs": ["packaging-source:debian_control"],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_bg_002_item(), _bg_002_ctx(), wizard, _bg_002_fallback_question())

    assert result.provenance == Provenance.AI_CONFIRMED
    assert "ntpd-rs" in result.statement
    assert wizard.questions[0][0] == "confirm"


def test_rep_bg_002_human_fallback_still_backfills_upstream_url():
    """writes_evidence must still fire when REP-BG-002's ev_to_ai flow falls
    back to asking the reporter directly (e.g. no LLM credential configured)
    -- a regression risk from moving this item off the human_only dispatch
    branch, which used to be the only caller of this backfill."""

    class URLAnsweringWizard:
        def ask(self, question):
            return Answer(
                question_id=question.id,
                value="https://github.com/pendulum-project/ntpd-rs",
                raw_input="https://github.com/pendulum-project/ntpd-rs",
            )

        def show_note(self, text, detail=""):
            pass

    ctx = _bg_002_ctx(token="")

    result = ai.evaluate_ai_item(
        _bg_002_item(),
        ctx,
        URLAnsweringWizard(),
        _bg_002_fallback_question(),
    )

    assert result.provenance == Provenance.HUMAN
    assert (
        ctx.evidence["adapters"]["upstream-tracker"]["upstream_url"]
        == "https://github.com/pendulum-project/ntpd-rs"
    )


class EditingWizard:
    """Fake wizard whose confirm_suggestion returns the reporter's edited text."""

    def __init__(self, edited_text):
        self.edited_text = edited_text
        self.questions = []

    def confirm_suggestion(self, *, question_id, suggestion, rationale, lock_yes_reason=None):
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
    assert result.statement == "- Original suggestion, plus a reporter addendum."
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


def test_multiline_human_fallback_bullets_answer_without_label_duplication(monkeypatch):
    """Regression test for feedback item 1a: a multiline ev_to_ai item whose
    catalog `template` still carries a descriptive label (e.g.
    "Packaging complexity and maintainability assessment: TBD", kept for the
    generated doc/rule_context, see docs/MIR/mir-reporters-template-body.include)
    must not glue that label onto the reporter's own complete answer when
    falling back to a human question - the answer alone becomes the bullet,
    exactly like the AI-confirmed path's `ensure_bulleted(suggestion)`."""

    def fail(*_args, **_kwargs):
        raise AssertionError("LLM must not be called without a credential")

    monkeypatch.setattr(ai.llm, "call_llm", fail)
    wizard = ConfirmingWizard()

    result = ai.evaluate_ai_item(_item(), _ctx(token=""), wizard, _fallback_question_multiline())

    assert result.provenance == Provenance.HUMAN
    assert result.statement == "- human correction"
    assert "Assessment" not in result.statement


def test_text_kind_human_fallback_still_splices_natural_template(monkeypatch):
    """A short `kind: text` fill-in (e.g. REP-BG-002's "Upstream Name is TBD")
    is a natural sentence lead-in, not a redundant restated label - it must
    keep splicing the answer into the template, unlike the multiline case
    above."""

    def fail(*_args, **_kwargs):
        raise AssertionError("LLM must not be called without a credential")

    monkeypatch.setattr(ai.llm, "call_llm", fail)
    wizard = ConfirmingWizard()

    result = ai.evaluate_ai_item(_item(), _ctx(token=""), wizard, _fallback_question())

    assert result.provenance == Provenance.HUMAN
    assert result.statement == "- Assessment: human correction"


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


def _autopkgtest_followup_item():
    return {
        "id": "REP-QA-TEST-004",
        "section": "Quality assurance - testing",
        "mode": "ev_to_ai",
        "readiness": "blocker",
        "template": "TODO: - Overall automated and end-to-end test adequacy: TBD",
        "ai_policy": "Assess test adequacy using debian/tests/control.",
        "adapters_required": ["autopkgtest-db", "packaging-source"],
        "autopkgtest_log_followup": True,
    }


def _autopkgtest_ctx():
    return SimpleNamespace(
        llm_token="token",
        no_llm=False,
        untrusted_nonce="nonce",
        source_package="python-invoke",
        evidence={
            "adapters": {
                "autopkgtest-db": {
                    "status": "ok",
                    "series": "stonking",
                    "test_results": [
                        {"arch": "amd64", "run_id": "20260723_004254_70601@"},
                        {"arch": "arm64", "run_id": "20260723_004300_70602@"},
                    ],
                },
                "packaging-source": {"status": "ok", "debian_tests_control": "Test-Command: ..."},
            }
        },
    )


def test_autopkgtest_log_followup_upgrades_low_confidence_to_high(monkeypatch):
    responses = iter(
        [
            {
                "confidence": "low",
                "rationale": "Cannot tell from debian/tests/control alone.",
                "evidence_refs": [],
            },
            {
                "confidence": "high",
                "statement": "Autopkgtests exercise real functionality and pass.",
                "rationale": "The fetched logs show a substantial pytest run passing.",
                "evidence_refs": [],
            },
        ]
    )
    call_count = 0

    def _fake_call_llm(*_args, **_kwargs):
        nonlocal call_count
        call_count += 1
        return next(responses)

    monkeypatch.setattr(ai.llm, "call_llm", _fake_call_llm)
    monkeypatch.setattr(
        "evidence.host_adapters.fetch_autopkgtest_log_excerpt",
        lambda *_args, **_kwargs: {
            "line_count": 10,
            "head": [],
            "tail": [],
            "highlighted_lines": [],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(
        _autopkgtest_followup_item(), _autopkgtest_ctx(), wizard, _fallback_question()
    )

    assert call_count == 2
    assert result.provenance == Provenance.AI_CONFIRMED
    assert result.statement == "- Autopkgtests exercise real functionality and pass."
    assert wizard.notes == []


def test_autopkgtest_log_followup_not_attempted_without_flag(monkeypatch):
    call_count = 0

    def _fake_call_llm(*_args, **_kwargs):
        nonlocal call_count
        call_count += 1
        return {
            "confidence": "low",
            "rationale": "Cannot tell.",
            "evidence_refs": [],
        }

    monkeypatch.setattr(ai.llm, "call_llm", _fake_call_llm)

    def _unexpected_fetch(*_args, **_kwargs):
        raise AssertionError("must not fetch logs for items without the opt-in flag")

    monkeypatch.setattr("evidence.host_adapters.fetch_autopkgtest_log_excerpt", _unexpected_fetch)
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert call_count == 1
    assert result.provenance == Provenance.HUMAN


def test_autopkgtest_log_followup_falls_back_when_no_logs_fetchable(monkeypatch):
    call_count = 0

    def _fake_call_llm(*_args, **_kwargs):
        nonlocal call_count
        call_count += 1
        return {
            "confidence": "low",
            "rationale": "Cannot tell from debian/tests/control alone.",
            "evidence_refs": [],
        }

    monkeypatch.setattr(ai.llm, "call_llm", _fake_call_llm)
    monkeypatch.setattr(
        "evidence.host_adapters.fetch_autopkgtest_log_excerpt", lambda *_args, **_kwargs: None
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(
        _autopkgtest_followup_item(), _autopkgtest_ctx(), wizard, _fallback_question()
    )

    # Only the initial call: logs could not be fetched, so no follow-up round happens.
    assert call_count == 1
    assert result.provenance == Provenance.HUMAN
    assert wizard.notes


def test_requires_reporter_decision_locks_yes(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "statement": "Restic and backuppc provide overlapping backup functionality.",
            "rationale": "Both are backup tools per apt-cache search.",
            "requires_reporter_decision": True,
            "evidence_refs": [],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert wizard.lock_yes_reasons == [
        "this suggestion does not fully answer the question on its own; edit it into "
        "a final statement or answer it yourself"
    ]
    # ConfirmingWizard always "accepts" regardless of locking (it's a fake); the real
    # TerminalWizard is the one that actually refuses "yes" - covered in
    # tests/test_reporter_wizard.py. This test only checks the reason is threaded through.
    assert result.provenance == Provenance.AI_CONFIRMED


def test_deferral_phrase_in_statement_locks_yes_even_without_the_flag(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "statement": "One deprecated-algorithm hit was found, which the reporter should "
            "confirm is not actively used.",
            "rationale": "One crypto_pattern_hit found.",
            "evidence_refs": [],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert wizard.lock_yes_reasons[0] is not None
    assert "confirm, verify, or decide" in wizard.lock_yes_reasons[0]


def test_plain_decisive_statement_does_not_lock_yes(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "statement": "No package in main provides overlapping functionality.",
            "rationale": "No candidates were found in main.",
            "requires_reporter_decision": False,
            "evidence_refs": [],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    ai.evaluate_ai_item(_item(), _ctx(), wizard, _fallback_question())

    assert wizard.lock_yes_reasons == [None]


def test_lock_yes_reason_helper_directly():
    assert ai._lock_yes_reason("A plain decisive claim.", requires_decision=False) is None
    assert ai._lock_yes_reason("Anything.", requires_decision=True) is not None
    assert (
        ai._lock_yes_reason("The reporter should verify this.", requires_decision=False) is not None
    )


def test_missing_required_adapter_skips_llm_and_asks_human_with_reason(monkeypatch):
    """Regression test: an ev_to_ai item must never let the model guess from
    missing/errored evidence (e.g. claiming FHS compliance when lintian never
    ran because fetch-build failed)."""

    def fail(*_args, **_kwargs):
        raise AssertionError("LLM must not be called when required evidence is unavailable")

    monkeypatch.setattr(ai.llm, "call_llm", fail)
    ctx = _ctx()
    ctx.evidence["adapters"]["binary-package-inspection"] = {
        "status": "error",
        "message": "upstream dependency failed: fetch-build",
    }
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_item(), ctx, wizard, _fallback_question())

    assert result.provenance == Provenance.HUMAN
    assert "binary-package-inspection" in result.rationale
    assert "upstream dependency failed: fetch-build" in result.rationale
    assert wizard.notes
    assert "could not confidently assess" in wizard.notes[0][0]


def test_missing_required_adapter_entirely_absent_still_skips_llm(monkeypatch):
    def fail(*_args, **_kwargs):
        raise AssertionError("LLM must not be called when required evidence is unavailable")

    monkeypatch.setattr(ai.llm, "call_llm", fail)
    ctx = _ctx()
    del ctx.evidence["adapters"]["binary-package-inspection"]
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(_item(), ctx, wizard, _fallback_question())

    assert result.provenance == Provenance.HUMAN
    assert "binary-package-inspection" in result.rationale


def test_required_adapters_unavailable_reason_helper_directly():
    ctx = _ctx()
    ctx.evidence["adapters"]["binary-package-inspection"] = {"status": "ok"}

    assert ai._required_adapters_unavailable_reason(_item(), ctx) == ""

    ctx.evidence["adapters"]["binary-package-inspection"] = {
        "status": "error",
        "message": "boom",
    }
    reason = ai._required_adapters_unavailable_reason(_item(), ctx)
    assert "binary-package-inspection" in reason
    assert "boom" in reason


def _options_item():
    """A synthetic ev_to_ai item with catalog-declared options, mirroring the
    reviewer catalog's ev_to_ai + options shape (checks/llm_eval.py) ported
    to the reporter role (feedback item 1a/1c/1d, phase 2)."""
    return {
        "id": "REP-UI-TEST",
        "section": "UI standards",
        "mode": "ev_to_ai",
        "readiness": "warning",
        "ai_policy": "Judge whether this is a user-facing desktop program.",
        "adapters_required": ["packaging-source"],
        "question": {
            "kind": "single_choice",
            "prompt": "Is this a user-facing desktop program with a desktop file?",
            "options": [
                {
                    "id": "not-ui",
                    "label": "Not a user-facing desktop program",
                    "ai_predicate": "library, CLI tool, daemon, or -dev/-doc/-debug package",
                    "statement": "- Not an end-user application, no need for a Desktop file.",
                    "readiness": "clear",
                    "todo_ref": "TODO-A: - not part of the UI for extra checks",
                },
                {
                    "id": "ui-missing-desktop",
                    "label": "User-facing desktop program without a desktop file",
                    "ai_predicate": "user-facing desktop program that does NOT ship a "
                    ".desktop file",
                    "statement": "- Part of the UI but no valid .desktop file is shipped.",
                    "readiness": "warning",
                    "todo_ref": "TODO-C: - part of the UI, no desktop file",
                },
            ],
        },
    }


def _options_fallback_question():
    return QuestionSpec(
        id="REP-UI-TEST",
        prompt="Is this a user-facing desktop program with a desktop file?",
        kind=QuestionKind.SINGLE_CHOICE,
        options=(
            QuestionOption(
                "not-ui",
                "Not a user-facing desktop program",
                "- Not an end-user application, no need for a Desktop file.",
                readiness=ReadinessEffect.CLEAR,
                todo_ref="TODO-A: - not part of the UI for extra checks",
            ),
            QuestionOption(
                "ui-missing-desktop",
                "User-facing desktop program without a desktop file",
                "- Part of the UI but no valid .desktop file is shipped.",
                readiness=ReadinessEffect.WARNING,
                todo_ref="TODO-C: - part of the UI, no desktop file",
            ),
        ),
    )


def _options_ctx(token="token"):
    return SimpleNamespace(
        llm_token=token,
        no_llm=False,
        untrusted_nonce="nonce",
        source_package="libfoo",
        evidence={"adapters": {"packaging-source": {"status": "ok"}}},
    )


def test_ai_options_item_selects_and_confirms_canonical_statement(monkeypatch):
    """Regression test for feedback items 1a/1c/1d, phase 2: an ev_to_ai item
    with catalog-declared ``options`` lets the model pick one id instead of
    writing free prose - the option's own pre-written statement is what gets
    suggested, confirmed, and rendered (no label-duplication risk at all,
    since there is no free-form template splice in this path)."""
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "selected_option": "not-ui",
            "rationale": "packaging-source shows a library, no GUI toolkit dependency.",
            "evidence_refs": ["packaging-source:binary_sections"],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(
        _options_item(), _options_ctx(), wizard, _options_fallback_question()
    )

    assert result.provenance == Provenance.AI_CONFIRMED
    assert result.statement == "- Not an end-user application, no need for a Desktop file."
    assert result.selected_option == "not-ui"
    assert result.readiness == ReadinessEffect.CLEAR


def test_ai_options_item_honors_per_option_readiness_override(monkeypatch):
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "selected_option": "ui-missing-desktop",
            "rationale": "GTK dependency plus a desktop-facing binary, but no .desktop file.",
            "evidence_refs": [],
        },
    )
    wizard = ConfirmingWizard(accept=True)

    result = ai.evaluate_ai_item(
        _options_item(), _options_ctx(), wizard, _options_fallback_question()
    )

    assert result.statement == "- Part of the UI but no valid .desktop file is shipped."
    assert result.selected_option == "ui-missing-desktop"
    assert result.readiness == ReadinessEffect.WARNING


def test_ai_options_item_rejects_unmatched_selected_option(monkeypatch):
    """An LLM response naming an option id that isn't declared must be treated
    as an invalid response and fall back to asking the reporter directly -
    never silently accepted or crash."""
    monkeypatch.setattr(
        ai.llm,
        "call_llm",
        lambda *_args, **_kwargs: {
            "confidence": "high",
            "selected_option": "does-not-exist",
            "rationale": "x",
            "evidence_refs": [],
        },
    )

    class ChoiceWizard(ConfirmingWizard):
        def ask(self, question):
            self.questions.append(("human", question.id))
            return Answer(question_id=question.id, value="not-ui", raw_input="not-ui")

    wizard = ChoiceWizard()

    result = ai.evaluate_ai_item(
        _options_item(), _options_ctx(), wizard, _options_fallback_question()
    )

    assert result.provenance == Provenance.HUMAN
    assert result.statement == "- Not an end-user application, no need for a Desktop file."


def test_options_human_fallback_uses_canonical_statement_and_readiness():
    """No LLM credential -> the single_choice fallback question (built from
    the same catalog options) resolves via the chosen option's own statement
    and readiness override, never via free-text template splicing."""

    class ChoiceWizard:
        def ask(self, question):
            return Answer(question_id=question.id, value="ui-missing-desktop", raw_input="2")

        def show_note(self, text, detail=""):
            pass

    result = ai.evaluate_ai_item(
        _options_item(), _options_ctx(token=""), ChoiceWizard(), _options_fallback_question()
    )

    assert result.provenance == Provenance.HUMAN
    assert result.statement == "- Part of the UI but no valid .desktop file is shipped."
    assert result.selected_option == "ui-missing-desktop"
    assert result.readiness == ReadinessEffect.WARNING


def test_multiline_fallback_uses_item_declared_readiness_not_always_clear(monkeypatch):
    """Regression test: _ask_human previously hardcoded readiness=CLEAR for
    every fallback answer regardless of the item's own catalog-declared
    readiness (warning/blocker), silently dropping it from the readiness
    summary whenever an ev_to_ai item fell back to a human answer (which is
    the common case whenever no LLM credential is configured)."""

    def fail(*_args, **_kwargs):
        raise AssertionError("LLM must not be called without a credential")

    monkeypatch.setattr(ai.llm, "call_llm", fail)
    wizard = ConfirmingWizard()

    result = ai.evaluate_ai_item(_item(), _ctx(token=""), wizard, _fallback_question_multiline())

    assert result.provenance == Provenance.HUMAN
    assert result.readiness == ReadinessEffect.WARNING


def test_deferred_multiline_fallback_becomes_needs_input_not_dropped(monkeypatch):
    """Regression test for feedback item 1b: a reporter who cannot resolve an
    ev_to_ai fallback question now (":defer") must land in
    StatementState.NEEDS_INPUT - never NOT_APPLICABLE, which would silently
    drop the item from the draft with no trace at all."""

    def fail(*_args, **_kwargs):
        raise AssertionError("LLM must not be called without a credential")

    monkeypatch.setattr(ai.llm, "call_llm", fail)

    class DeferringWizard:
        def ask(self, question):
            assert question.deferrable is True
            assert question.required is True
            return None

        def show_note(self, text, detail=""):
            pass

    result = ai.evaluate_ai_item(
        _item(), _ctx(token=""), DeferringWizard(), _fallback_question_multiline()
    )

    assert result.state == StatementState.NEEDS_INPUT
    assert result.readiness == ReadinessEffect.WARNING
    assert result.rationale


def test_optional_ev_to_ai_item_skip_stays_not_applicable(monkeypatch):
    """An *optional* ev_to_ai question (e.g. REP-BG-002) left blank is a
    genuine "nothing to add" skip, not a deferral - it must stay
    NOT_APPLICABLE (silently omitted), unlike the required-and-deferred case
    above."""

    def fail(*_args, **_kwargs):
        raise AssertionError("LLM must not be called without a credential")

    monkeypatch.setattr(ai.llm, "call_llm", fail)

    class SkippingWizard:
        def ask(self, question):
            assert question.required is False
            return None

        def show_note(self, text, detail=""):
            pass

    optional_question = QuestionSpec(
        id="REP-AI-001", prompt="Correct assessment", kind=QuestionKind.TEXT, required=False
    )

    result = ai.evaluate_ai_item(_item(), _ctx(token=""), SkippingWizard(), optional_question)

    assert result.state == StatementState.NOT_APPLICABLE
