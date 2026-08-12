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


def test_single_choice_renders_shortcut_marker_for_exclusive_options():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["all"]), write_line=output.append)
    question = QuestionSpec(
        id="REP-SCOPE",
        prompt="Which binaries need promotion?",
        kind=QuestionKind.SINGLE_CHOICE,
        options=(
            QuestionOption("all", "All binaries", exclusive=True),
            QuestionOption("ntpd-rs", "ntpd-rs"),
        ),
    )

    wizard.ask(question)

    assert any("(shortcut)" in line for line in output)
    assert not any("(shortcut)" in line for line in output if "ntpd-rs" in line)


def test_single_choice_shows_list_note_under_option():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["specific-packages"]), write_line=output.append)
    question = QuestionSpec(
        id="REP-RATIONALE-004",
        prompt="Which binary packages need promotion?",
        kind=QuestionKind.SINGLE_CHOICE,
        options=(
            QuestionOption(
                "specific-packages",
                "A specific subset of binary packages (list them below)",
                "- Specific binary packages, listed below, need to be in main.",
                list_note="The packages built by this source are: foo, foo-doc",
            ),
        ),
    )

    wizard.ask(question)

    assert any("The packages built by this source are: foo, foo-doc" in line for line in output)


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


def test_multiline_uses_editor_when_available():
    """A usable editor is tried first, before the raw terminal fallback."""
    calls = []

    def _fake_edit_text(initial_text, comment_lines):
        calls.append((initial_text, comment_lines))
        return "edited via external editor"

    def _unexpected_read(_prompt):
        raise AssertionError("must not fall back to raw terminal entry when editor works")

    wizard = TerminalWizard(
        read_line=_unexpected_read, write_line=lambda _line: None, edit_text=_fake_edit_text
    )
    question = QuestionSpec(
        id="REP-RATIONALE",
        prompt="Enter rationale",
        kind=QuestionKind.MULTILINE,
        rule_context="RULE: some rule",
        hint="some hint",
    )

    answer = wizard.ask(question)

    assert answer.value == "edited via external editor"
    assert calls
    comment_lines = calls[0][1]
    assert "Context:" in comment_lines
    assert any(line == "   RULE: some rule" for line in comment_lines)
    assert any("Hint: some hint" in line for line in comment_lines)
    # The Context header must be its own comment line, never sharing a line
    # with the first RULE - otherwise only the header line gets the '#'
    # prefix from the editor and every subsequent RULE/TODO line leaks
    # unprefixed straight into the effective answer text.
    assert not any(line.startswith("Context: RULE") for line in comment_lines)


def test_multiline_comment_lines_indents_every_rule_and_todo_line_separately():
    """Regression test: a multi-line rule_context (several RULE lines plus
    the item's own TODO line, joined by catalog._apply_reporter_rule_context_
    defaults) must render as one indented comment line per RULE/TODO, each a
    separate list element - not one element containing embedded newlines,
    which utils.editor.edit_text would only '#'-prefix on its first physical
    line, leaking the rest straight into the effective answer text."""
    wizard = TerminalWizard()
    question = QuestionSpec(
        id="REP-RATIONALE-001",
        prompt="Why is this source package required in Ubuntu main?",
        kind=QuestionKind.MULTILINE,
        rule_context=(
            "RULE: Main inclusion needs demonstrated Ubuntu demand, correct "
            "understanding of main versus universe, and no better supported "
            "alternative.\n"
            "RULE: Reuse an existing MIR with a new series task when prior "
            "package content, reasoning, and circumstances remain applicable; "
            "otherwise reference the prior MIR and explain the difference.\n"
            "RULE: State the exact binary promotion scope and a well-founded "
            "major-release deadline, if any; wishes without a definite "
            "deadline should be identified as such.\n"
            "TODO: - The package TBDSRC is required in Ubuntu main for TBD"
        ),
    )

    comment_lines = wizard._multiline_comment_lines(question)

    assert comment_lines == [
        "Why is this source package required in Ubuntu main?",
        "",
        "Context:",
        "   RULE: Main inclusion needs demonstrated Ubuntu demand, correct "
        "understanding of main versus universe, and no better supported "
        "alternative.",
        "   RULE: Reuse an existing MIR with a new series task when prior "
        "package content, reasoning, and circumstances remain applicable; "
        "otherwise reference the prior MIR and explain the difference.",
        "   RULE: State the exact binary promotion scope and a well-founded "
        "major-release deadline, if any; wishes without a definite deadline "
        "should be identified as such.",
        "   TODO: - The package TBDSRC is required in Ubuntu main for TBD",
        "",
        "Lines starting with '#' are ignored and will not be included.",
    ]


def test_multiline_editor_file_never_leaks_unprefixed_rule_or_todo_lines(monkeypatch):
    """End-to-end regression test through the real utils.editor.edit_text:
    every RULE/TODO line from a multi-line rule_context must come back
    '#'-prefixed in the generated file, matching git-rebase-style commentary,
    so none of it could ever be mistaken for part of the answer."""
    import subprocess
    from unittest.mock import patch

    from utils import editor

    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setenv("EDITOR", "fake-editor")

    wizard = TerminalWizard()
    question = QuestionSpec(
        id="REP-RATIONALE-001",
        prompt="Why is this source package required in Ubuntu main?",
        kind=QuestionKind.MULTILINE,
        rule_context="RULE: first rule.\nRULE: second rule.\nTODO: - TBDSRC needs TBD",
    )
    comment_lines = wizard._multiline_comment_lines(question)

    seen_contents = []

    def _fake_run(command, check=False):
        temp_path = Path(command[-1])
        seen_contents.append(temp_path.read_text(encoding="utf-8"))
        return subprocess.CompletedProcess(command, 0)

    with patch("utils.editor.subprocess.run", side_effect=_fake_run):
        editor.edit_text("", comment_lines)

    file_lines = seen_contents[0].splitlines()
    for line in file_lines:
        if "RULE:" in line or "TODO:" in line:
            assert line.startswith("#"), f"leaked unprefixed policy line: {line!r}"
    assert "# Context:" in file_lines
    assert "#    RULE: first rule." in file_lines
    assert "#    RULE: second rule." in file_lines
    assert "#    TODO: - TBDSRC needs TBD" in file_lines


def test_multiline_editor_answer_is_recorded_in_console_and_log(caplog):
    output: list[str] = []
    wizard = TerminalWizard(
        read_line=_reader([]),
        write_line=output.append,
        edit_text=lambda *_args, **_kwargs: "the reporter's editor answer",
    )
    question = QuestionSpec(
        id="REP-RATIONALE", prompt="Enter rationale", kind=QuestionKind.MULTILINE
    )

    with caplog.at_level("INFO", logger="auto_mir.reporter"):
        answer = wizard.ask(question)

    assert answer.value == "the reporter's editor answer"
    assert "Answer recorded as:" in output
    assert "    the reporter's editor answer" in output
    assert any(
        "Answer recorded as: the reporter's editor answer" in record.getMessage()
        for record in caplog.records
    )


def test_confirm_suggestion_edit_answer_is_recorded_in_console_and_log(caplog):
    output: list[str] = []
    wizard = TerminalWizard(
        read_line=_reader(["edit"]),
        write_line=output.append,
        edit_text=lambda *_args, **_kwargs: "revised via editor",
    )

    with caplog.at_level("INFO", logger="auto_mir.reporter"):
        answer = wizard.confirm_suggestion(
            question_id="REP-CONFIRM", suggestion="Original text.", rationale=""
        )

    assert answer.value == "revised via editor"
    assert "Answer recorded as:" in output
    assert any(
        "Answer recorded as: revised via editor" in record.getMessage() for record in caplog.records
    )


def test_multiline_required_reopens_editor_on_empty_result():
    responses = iter(["", "second attempt text"])

    def _fake_edit_text(_initial_text, _comment_lines):
        return next(responses)

    output: list[str] = []
    wizard = TerminalWizard(
        read_line=lambda _p: (_ for _ in ()).throw(AssertionError("no raw fallback expected")),
        write_line=output.append,
        edit_text=_fake_edit_text,
    )
    question = QuestionSpec(
        id="REP-RATIONALE", prompt="Enter rationale", kind=QuestionKind.MULTILINE
    )

    answer = wizard.ask(question)

    assert answer.value == "second attempt text"
    assert any("Reopening the editor" in line for line in output)


def test_multiline_optional_skipped_when_editor_returns_empty():
    wizard = TerminalWizard(
        read_line=lambda _p: (_ for _ in ()).throw(AssertionError("no raw fallback expected")),
        write_line=lambda _line: None,
        edit_text=lambda _initial, _comments: "",
    )
    question = QuestionSpec(
        id="REP-BG",
        prompt="Additional context?",
        kind=QuestionKind.MULTILINE,
        required=False,
    )

    assert wizard.ask(question) is None


def test_deferrable_multiline_editor_defer_sentinel_returns_none_without_reopening():
    """Regression test for feedback item 1b: a deferrable, *required*
    multiline question must let the reporter say ":defer" instead of being
    forced to answer or looping the editor forever."""
    calls = []

    def _edit_text(_initial_text, _comment_lines):
        calls.append(1)
        if len(calls) > 1:
            raise AssertionError("editor must not reopen after an explicit :defer")
        return ":defer"

    wizard = TerminalWizard(
        read_line=lambda _p: (_ for _ in ()).throw(AssertionError("no raw fallback expected")),
        write_line=lambda _line: None,
        edit_text=_edit_text,
    )
    question = QuestionSpec(
        id="REP-DEFER",
        prompt="Assess something",
        kind=QuestionKind.MULTILINE,
        required=True,
        deferrable=True,
    )

    assert wizard.ask(question) is None
    assert calls == [1]


def test_non_deferrable_required_multiline_ignores_defer_as_literal_text():
    """ ":defer" must only be special when the question opts in via
    ``deferrable=True`` - a human_only question (never deferrable) treats it
    as ordinary answer text."""
    wizard = TerminalWizard(
        read_line=lambda _p: (_ for _ in ()).throw(AssertionError("no raw fallback expected")),
        write_line=lambda _line: None,
        edit_text=lambda _initial, _comments: ":defer",
    )
    question = QuestionSpec(
        id="REP-RATIONALE-NOT-DEFERRABLE",
        prompt="Explain",
        kind=QuestionKind.MULTILINE,
        required=True,
    )

    answer = wizard.ask(question)

    assert answer is not None
    assert answer.value == ":defer"


def test_deferrable_raw_multiline_defer_sentinel_on_first_line():
    """No usable editor (falls back to raw terminal entry): ":defer" on the
    first line of a deferrable question returns None, matching the
    ":cancel" convention already used for aborting."""
    wizard = TerminalWizard(
        read_line=_reader([":defer"]),
        write_line=lambda _line: None,
        edit_text=lambda *_a, **_k: None,
    )
    question = QuestionSpec(
        id="REP-DEFER-RAW",
        prompt="Assess something",
        kind=QuestionKind.MULTILINE,
        required=True,
        deferrable=True,
    )

    assert wizard.ask(question) is None


def test_deferrable_single_choice_defer_sentinel_returns_none():
    wizard = TerminalWizard(read_line=_reader([":defer"]), write_line=lambda _line: None)
    question = QuestionSpec(
        id="REP-CHOICE-DEFER",
        prompt="Pick one",
        kind=QuestionKind.SINGLE_CHOICE,
        required=True,
        deferrable=True,
        options=(QuestionOption("a", "Option A"), QuestionOption("b", "Option B")),
    )

    assert wizard.ask(question) is None


def test_multiline_falls_back_to_raw_terminal_when_editor_unavailable():
    wizard = TerminalWizard(
        read_line=_reader(["raw terminal answer", "."]),
        write_line=lambda _line: None,
        edit_text=lambda _initial, _comments: None,
    )
    question = QuestionSpec(
        id="REP-RATIONALE", prompt="Enter rationale", kind=QuestionKind.MULTILINE
    )

    answer = wizard.ask(question)

    assert answer.value == "raw terminal answer"


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
    assert any("edit = keep most of it" in line for line in output)


def test_ai_suggestion_uses_title_and_indent_for_statement_and_reasoning():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["yes"]), write_line=output.append)

    wizard.confirm_suggestion(
        question_id="REP-CONFIRM",
        suggestion="No equivalent package in main was identified.",
        rationale="The candidates provide different functionality.",
    )

    statement_index = output.index("Suggested statement:")
    assert output[statement_index + 1] == "    No equivalent package in main was identified."
    reasoning_index = output.index("Reasoning:")
    assert output[reasoning_index + 1] == "    The candidates provide different functionality."


def test_ai_suggestion_reject_returns_false():
    wizard = TerminalWizard(read_line=_reader(["no"]), write_line=lambda _line: None)

    answer = wizard.confirm_suggestion(
        question_id="REP-CONFIRM", suggestion="Suggested text.", rationale=""
    )

    assert answer.value is False


def test_ai_suggestion_edit_returns_reporter_revised_text():
    output: list[str] = []
    wizard = TerminalWizard(
        read_line=_reader(["edit", "revised first line", "."]),
        write_line=output.append,
    )

    answer = wizard.confirm_suggestion(
        question_id="REP-CONFIRM",
        suggestion="Original suggested text.",
        rationale="Because of evidence X.",
    )

    assert answer.value == "revised first line"
    assert any("Original suggested text." in line for line in output)


def test_ai_suggestion_edit_uses_editor_with_suggestion_and_rationale():
    calls = []

    def _fake_edit_text(initial_text, comment_lines):
        calls.append((initial_text, comment_lines))
        return "revised via editor"

    wizard = TerminalWizard(
        read_line=_reader(["edit"]),
        write_line=lambda _line: None,
        edit_text=_fake_edit_text,
    )

    answer = wizard.confirm_suggestion(
        question_id="REP-CONFIRM",
        suggestion="Original suggested text.",
        rationale="Because of evidence X.",
    )

    assert answer.value == "revised via editor"
    initial_text, comment_lines = calls[0]
    assert initial_text == "Original suggested text."
    assert any("Because of evidence X." in line for line in comment_lines)


def test_ai_suggestion_invalid_response_reprompts():
    wizard = TerminalWizard(read_line=_reader(["maybe", "yes"]), write_line=lambda _line: None)

    answer = wizard.confirm_suggestion(
        question_id="REP-CONFIRM", suggestion="Suggested text.", rationale=""
    )

    assert answer.value is True


def test_locked_confirm_suggestion_rejects_yes_and_shows_reason():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["yes", "no"]), write_line=output.append)

    answer = wizard.confirm_suggestion(
        question_id="REP-CONFIRM",
        suggestion="Suggested text.",
        rationale="",
        lock_yes_reason="it still defers a decision to the reporter",
    )

    assert answer.value is False
    assert any("unavailable" in line and "still defers" in line for line in output)


def test_locked_confirm_suggestion_still_allows_edit():
    wizard = TerminalWizard(
        read_line=_reader(["edit", "revised", "."]), write_line=lambda _line: None
    )

    answer = wizard.confirm_suggestion(
        question_id="REP-CONFIRM",
        suggestion="Suggested text.",
        rationale="",
        lock_yes_reason="locked",
    )

    assert answer.value == "revised"


def test_unlocked_confirm_suggestion_shows_plain_yes_option():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["yes"]), write_line=output.append)

    wizard.confirm_suggestion(question_id="REP-CONFIRM", suggestion="Text.", rationale="")

    assert any(line.startswith("Options: yes = use this statement as-is;") for line in output)


def test_locked_single_choice_option_is_marked_and_rejected():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["1", "2"]), write_line=output.append)
    question = QuestionSpec(
        id="REP-MAINT-001",
        prompt="Owning team?",
        kind=QuestionKind.SINGLE_CHOICE,
        options=(
            QuestionOption(
                "confirm-subscribed",
                "Keep the already-subscribed team",
                "- Confirmed.",
                locked_reason="No team is currently subscribed to this package.",
            ),
            QuestionOption("new-team", "A different team", "- New team."),
        ),
    )

    answer = wizard.ask(question)

    assert answer.value == "new-team"
    assert any("(unavailable: No team is currently subscribed" in line for line in output)
    assert any("currently unavailable" in line for line in output)


def test_rule_context_and_answer_guidance_are_rendered():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["an answer"]), write_line=output.append)
    question = QuestionSpec(
        id="REP-X",
        prompt="Explain it",
        kind=QuestionKind.TEXT,
        rule_context="RULE: packages must justify inclusion.",
        answer_guidance="This is recorded verbatim in the [Rationale] section.",
    )

    wizard.ask(question)

    assert any("RULE: packages must justify inclusion." in line for line in output)
    assert any("recorded verbatim" in line for line in output)


def test_rule_context_and_hint_use_title_and_indent():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["an answer"]), write_line=output.append)
    question = QuestionSpec(
        id="REP-X",
        prompt="Explain it",
        kind=QuestionKind.TEXT,
        rule_context="RULE: packages must justify inclusion.",
        hint="Keep it concise.",
    )

    wizard.ask(question)

    assert "Context:" in output
    context_index = output.index("Context:")
    assert output[context_index + 1] == "    RULE: packages must justify inclusion."
    assert "Hint:" in output
    hint_index = output.index("Hint:")
    assert output[hint_index + 1] == "    Keep it concise."


def test_optional_question_without_explicit_guidance_gets_default_skip_note():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader([""]), write_line=output.append)
    question = QuestionSpec(
        id="REP-Y", prompt="Anything else?", kind=QuestionKind.TEXT, required=False
    )

    wizard.ask(question)

    assert any("optional" in line.casefold() for line in output)


def test_optional_question_shows_skip_note_even_with_custom_answer_guidance():
    """Regression test: a custom answer_guidance used to silently suppress
    the generic 'leave empty to skip' note entirely, leaving the reporter
    with no clear way to say 'nothing to add' for that specific question."""
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader([""]), write_line=output.append)
    question = QuestionSpec(
        id="REP-Y",
        prompt="Anything else?",
        kind=QuestionKind.TEXT,
        required=False,
        answer_guidance="Focus on aspects not already covered elsewhere.",
    )

    wizard.ask(question)

    assert any("Focus on aspects not already covered elsewhere." in line for line in output)
    assert any("leave the answer empty to skip" in line.casefold() for line in output)


def test_optional_multiline_editor_hint_shows_skip_note_even_with_custom_guidance():
    calls = []

    def _fake_edit_text(initial_text, comment_lines):
        calls.append(comment_lines)
        return None  # simulate no usable editor; we only care about the comment lines

    wizard = TerminalWizard(
        read_line=_reader(["."]), write_line=lambda _line: None, edit_text=_fake_edit_text
    )
    question = QuestionSpec(
        id="REP-Y",
        prompt="Anything else?",
        kind=QuestionKind.MULTILINE,
        required=False,
        answer_guidance="Focus on aspects not already covered elsewhere.",
    )

    wizard.ask(question)

    comment_lines = calls[0]
    assert any("Focus on aspects not already covered elsewhere." in line for line in comment_lines)
    assert any("leave the answer empty to skip" in line.casefold() for line in comment_lines)


def test_option_statements_are_echoed_next_to_labels():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["1"]), write_line=output.append)
    question = QuestionSpec(
        id="REP-Z",
        prompt="Choose",
        kind=QuestionKind.SINGLE_CHOICE,
        options=(QuestionOption("a", "Option A", "The package does A."),),
    )

    wizard.ask(question)

    assert any("recorded as: The package does A." in line for line in output)


def test_option_with_followup_shows_hint():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader(["1"]), write_line=output.append)
    question = QuestionSpec(
        id="REP-Z",
        prompt="Choose",
        kind=QuestionKind.SINGLE_CHOICE,
        options=(
            QuestionOption("a", "Option A", "The package does A.", leads_to_followup=True),
            QuestionOption("b", "Option B", "The package does B."),
        ),
    )

    wizard.ask(question)

    hint_lines = [line for line in output if "will ask for more detail next" in line]
    assert len(hint_lines) == 1


def test_show_note_prints_evidence_derived_context():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader([]), write_line=output.append)

    wizard.show_note("Team foo-bugs is already subscribed.", "Detected via team-mapping.")

    assert "Note:" in output
    assert any("Team foo-bugs is already subscribed." in line for line in output)
    assert "Reasoning:" in output
    assert any("Detected via team-mapping." in line for line in output)


def test_show_note_ignores_empty_text():
    output: list[str] = []
    wizard = TerminalWizard(read_line=_reader([]), write_line=output.append)

    wizard.show_note("")

    assert output == []
