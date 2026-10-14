"""Tests for reporter-specific question and statement contracts."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reporter.models import (  # noqa: E402
    Provenance,
    QuestionKind,
    QuestionOption,
    QuestionSpec,
    ReadinessEffect,
    StatementResult,
    StatementState,
)


def test_choice_question_requires_options():
    with pytest.raises(ValueError, match="requires at least one option"):
        QuestionSpec(id="REP-1", prompt="Choose", kind=QuestionKind.SINGLE_CHOICE)


def test_question_option_readiness_defaults_to_none():
    option = QuestionOption("clean", "No concerns")

    assert option.readiness is None


def test_question_option_accepts_explicit_readiness_override():
    option = QuestionOption("concern", "There is a concern", readiness=ReadinessEffect.BLOCKER)

    assert option.readiness == ReadinessEffect.BLOCKER


def test_question_option_locked_reason_defaults_to_empty():
    option = QuestionOption("confirm-subscribed", "Keep the already-subscribed team")

    assert option.locked_reason == ""


def test_question_option_accepts_locked_reason():
    option = QuestionOption(
        "confirm-subscribed",
        "Keep the already-subscribed team",
        locked_reason="No team is currently subscribed to this package.",
    )

    assert option.locked_reason == "No team is currently subscribed to this package."


def test_non_choice_question_rejects_options():
    with pytest.raises(ValueError, match="cannot define options"):
        QuestionSpec(
            id="REP-1",
            prompt="Explain",
            kind=QuestionKind.TEXT,
            options=(QuestionOption("a", "A"),),
        )


def test_question_rejects_case_insensitive_duplicate_option_ids():
    with pytest.raises(ValueError, match="duplicate option ids"):
        QuestionSpec(
            id="REP-1",
            prompt="Choose",
            kind=QuestionKind.SINGLE_CHOICE,
            options=(QuestionOption("A", "First"), QuestionOption("a", "Second")),
        )


def test_resolved_statement_requires_text_and_provenance():
    with pytest.raises(ValueError, match="must include text"):
        StatementResult(
            id="REP-1",
            section="Availability",
            state=StatementState.RESOLVED,
            readiness=ReadinessEffect.CLEAR,
            provenance=Provenance.DETERMINISTIC,
        )

    with pytest.raises(ValueError, match="must include provenance"):
        StatementResult(
            id="REP-1",
            section="Availability",
            state=StatementState.RESOLVED,
            readiness=ReadinessEffect.CLEAR,
            statement="Package exists in universe.",
        )


def test_ai_statement_requires_explicit_human_confirmation():
    with pytest.raises(ValueError, match="explicitly human-confirmed"):
        StatementResult(
            id="REP-1",
            section="Rationale",
            state=StatementState.RESOLVED,
            readiness=ReadinessEffect.CLEAR,
            statement="No duplicate was identified.",
            provenance=Provenance.AI_CONFIRMED,
        )


def test_confirmed_ai_statement_is_valid():
    result = StatementResult(
        id="REP-1",
        section="Rationale",
        state=StatementState.RESOLVED,
        readiness=ReadinessEffect.WARNING,
        statement="No duplicate was identified.",
        provenance=Provenance.AI_CONFIRMED,
        human_confirmed=True,
        evidence_refs=["dup-search:candidates"],
        answer_refs=["REP-1-confirmation"],
    )

    assert result.human_confirmed is True
    assert result.provenance == Provenance.AI_CONFIRMED
