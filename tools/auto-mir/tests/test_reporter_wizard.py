"""Tests for the terminal-only MIR reporter wizard."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reporter.models import QuestionKind, QuestionOption, QuestionSpec  # noqa: E402
from reporter.wizard import TerminalWizard, WizardAborted  # noqa: E402


def _reader(responses):
    remaining = iter(responses)

    def read(_prompt):
        response = next(remaining)
        if isinstance(response, BaseException):
            raise response
        return response

    return read


def test_required_text_retries_empty_then_accepts():
    output: list[str] = []
    wizard = TerminalWizard(
        read_line=_reader(["", "needed by desktop image"]), write_line=output.append
    )
    question = QuestionSpec(id="REP-RAT-1", prompt="Why is it needed?", kind=QuestionKind.TEXT)

    answer = wizard.ask(question)

    assert answer is not None
    assert answer.value == "needed by desktop image"
    assert any("required" in line for line in output)


def test_optional_text_can_be_skipped():
    wizard = TerminalWizard(read_line=_reader([""]), write_line=lambda _line: None)
    question = QuestionSpec(
        id="REP-BG-1",
        prompt="Additional context?",
        kind=QuestionKind.TEXT,
        required=False,
    )

    assert wizard.ask(question) is None


def test_confirm_parses_yes_and_no():
    yes = TerminalWizard(read_line=_reader(["yes"]), write_line=lambda _line: None)
    no = TerminalWizard(read_line=_reader(["n"]), write_line=lambda _line: None)
    question = QuestionSpec(id="REP-CONFIRM", prompt="Confirm?", kind=QuestionKind.CONFIRM)

    assert yes.ask(question).value is True
    assert no.ask(question).value is False


def test_single_choice_accepts_number_and_returns_stable_option_id():
    wizard = TerminalWizard(read_line=_reader(["2"]), write_line=lambda _line: None)
    question = QuestionSpec(
        id="REP-SCOPE",
        prompt="Choose scope",
        kind=QuestionKind.SINGLE_CHOICE,
        options=(
            QuestionOption("all", "All binaries"),
            QuestionOption("selected", "Selected binaries"),
        ),
    )

    assert wizard.ask(question).value == "selected"


def test_multi_choice_deduplicates_and_preserves_order():
    wizard = TerminalWizard(
        read_line=_reader(["hardware, 1, upstream"]),
        write_line=lambda _line: None,
    )
    question = QuestionSpec(
        id="REP-TEST-PLAN",
        prompt="Select access methods",
        kind=QuestionKind.MULTI_CHOICE,
        options=(
            QuestionOption("hardware", "Team hardware"),
            QuestionOption("upstream", "Upstream testing"),
        ),
    )

    assert wizard.ask(question).value == ["hardware", "upstream"]


def test_multiline_uses_dot_sentinel_and_supports_literal_dot():
    wizard = TerminalWizard(
        read_line=_reader(["first paragraph", r"\.", "last paragraph", "."]),
        write_line=lambda _line: None,
    )
    question = QuestionSpec(
        id="REP-RATIONALE",
        prompt="Enter rationale",
        kind=QuestionKind.MULTILINE,
    )

    answer = wizard.ask(question)

    assert answer.value == "first paragraph\n.\nlast paragraph"


def test_required_eof_and_cancel_abort():
    question = QuestionSpec(id="REP-OWNER", prompt="Owning team?", kind=QuestionKind.TEXT)

    eof_wizard = TerminalWizard(read_line=_reader([EOFError()]), write_line=lambda _line: None)
    with pytest.raises(WizardAborted, match="input ended"):
        eof_wizard.ask(question)

    cancel_wizard = TerminalWizard(read_line=_reader([":cancel"]), write_line=lambda _line: None)
    with pytest.raises(WizardAborted, match="question cancelled"):
        cancel_wizard.ask(question)


def test_optional_eof_returns_none():
    wizard = TerminalWizard(read_line=_reader([EOFError()]), write_line=lambda _line: None)
    question = QuestionSpec(
        id="REP-BG",
        prompt="Additional context?",
        kind=QuestionKind.TEXT,
        required=False,
    )

    assert wizard.ask(question) is None


def test_ai_suggestion_requires_explicit_confirmation():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["yes"]), write_line=output.append)

    answer = wizard.confirm_suggestion(
        question_id="REP-DUP-CONFIRM",
        suggestion="No equivalent package in main was identified.",
        rationale="The candidates provide different functionality.",
    )

    assert answer.value is True
    assert "Suggested statement:" in output
    assert any(line.startswith("Reasoning:") for line in output)
