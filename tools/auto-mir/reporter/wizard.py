"""Terminal wizard for reporter-owned MIR answers."""

from __future__ import annotations

import logging
from collections.abc import Callable

from reporter.models import Answer, QuestionKind, QuestionOption, QuestionSpec
from utils import editor

log = logging.getLogger("auto_mir.reporter")

_CANCEL_TOKEN = ":cancel"
_MULTILINE_SENTINEL = "."
_MULTILINE_LITERAL_DOT = r"\."


class WizardAborted(RuntimeError):
    """Raised when required terminal input is cancelled or reaches EOF."""


class TerminalWizard:
    """Ask validated reporter questions through stdin/stdout.

    Answers remain in memory for the current process only. The wizard owns no
    persistence and performs no package, network, evidence, or LLM work.
    """

    def __init__(
        self,
        *,
        read_line: Callable[[str], str] = input,
        write_line: Callable[[str], None] = print,
        edit_text: Callable[[str, list[str]], str | None] = editor.edit_text,
    ) -> None:
        self._read_line = read_line
        self._write_line = write_line
        self._edit_text = edit_text

    def ask(self, question: QuestionSpec) -> Answer | None:
        """Ask until a valid answer is provided, or return None if optional."""
        self._write_line("")
        if question.rule_context:
            self._write_titled_block("Context", question.rule_context)
        self._write_line(question.prompt)
        if question.hint:
            self._write_titled_block("Hint", question.hint)
        self._render_answer_guidance(question)

        if question.kind == QuestionKind.MULTILINE:
            return self._ask_multiline(question)

        self._render_options(question)
        while True:
            try:
                raw = self._read_line("> ").strip()
            except EOFError as exc:
                return self._handle_missing(question, "input ended", exc)

            if raw == _CANCEL_TOKEN:
                return self._handle_missing(question, "question cancelled")
            if not raw and question.default is not None:
                raw = str(question.default)
            if not raw:
                if question.required:
                    self._write_line("A response is required. Enter :cancel to abort.")
                    continue
                return None

            try:
                value = self._parse_answer(question, raw)
            except ValueError as exc:
                self._write_line(f"Invalid response: {exc}")
                continue
            return Answer(question_id=question.id, value=value, raw_input=raw)

    def confirm_suggestion(
        self,
        *,
        question_id: str,
        suggestion: str,
        rationale: str,
        lock_yes_reason: str | None = None,
    ) -> Answer:
        """Require the reporter to accept, edit, or reject one AI suggestion.

        Returns an :class:`Answer` whose ``value`` is ``True`` (use as-is),
        ``False`` (discard and answer manually), or a ``str`` containing the
        reporter's edited version of the suggested statement.

        When ``lock_yes_reason`` is set, the tool has determined the
        suggestion does not qualify as a final report statement on its own
        (e.g. it still defers a decision to the reporter). "yes" is then
        rejected and the reason is shown, so the reporter must "edit" or
        "no" instead of accidentally posting an unfinished statement as-is.
        """
        self._write_line("")
        self._write_titled_block("Suggested statement", suggestion)
        if rationale.strip():
            self._write_titled_block("Reasoning", rationale.strip())
        self._write_line("")
        yes_clause = (
            f"yes = unavailable ({lock_yes_reason})"
            if lock_yes_reason
            else "yes = use this statement as-is"
        )
        self._write_line(
            f"Options: {yes_clause}; "
            "edit = keep most of it but amend or extend it; "
            "no = discard it and answer the question yourself."
        )
        placeholder_question = QuestionSpec(
            id=question_id,
            prompt="Use this statement?",
            kind=QuestionKind.CONFIRM,
            required=True,
        )
        while True:
            try:
                raw = self._read_line("> ").strip()
            except EOFError as exc:
                self._handle_missing(placeholder_question, "input ended", exc)
                continue
            if raw == _CANCEL_TOKEN:
                self._handle_missing(placeholder_question, "question cancelled")
                continue
            normalized = raw.casefold()
            if normalized in {"y", "yes"}:
                if lock_yes_reason:
                    self._write_line(
                        f"'yes' is unavailable: {lock_yes_reason} Enter edit or no instead."
                    )
                    continue
                return Answer(question_id=question_id, value=True, raw_input=raw)
            if normalized in {"n", "no"}:
                return Answer(question_id=question_id, value=False, raw_input=raw)
            if normalized in {"e", "edit"}:
                edited = self._edit_multiline(suggestion, rationale)
                self._record_answer(edited)
                return Answer(question_id=question_id, value=edited, raw_input=raw)
            self._write_line("Invalid response: enter yes, edit, or no")

    def show_note(self, text: str, detail: str = "") -> None:
        """Display one evidence-derived note ahead of a question, if any."""
        if not text.strip():
            return
        self._write_line("")
        self._write_titled_block("Note", text.strip())
        if detail.strip():
            self._write_titled_block("Reasoning", detail.strip())

    def _record_answer(self, text: str) -> None:
        """Echo an editor-sourced answer back to the reporter and the log.

        Editor mode hands control to an external process for a while; once
        it returns, the console (and the JSON log) should say exactly what
        was recorded, so the reporter never has to wonder whether their
        edited text actually made it back into the tool.
        """
        self._write_titled_block("Answer recorded as", text)
        log.info("Answer recorded as: %s", text)

    def _write_titled_block(self, title: str, text: str) -> None:
        """Print a title line followed by its body, indented underneath.

        Used for Context/Hint/Suggested statement/Reasoning/Note blocks so
        the label and its content are visually distinct, and multi-line
        content stays clearly associated with its title.
        """
        self._write_line(f"{title}:")
        for line in text.splitlines() or [text]:
            self._write_line(f"    {line}")

    def _edit_multiline(self, prefill: str, rationale: str = "") -> str:
        comment_lines = ["You are revising the tool's suggested statement below.", ""]
        if rationale.strip():
            comment_lines.append(f"Reasoning: {rationale.strip()}")
            comment_lines.append("")
        comment_lines.append("Lines starting with '#' are ignored and will not be included.")
        edited = self._edit_text(prefill, comment_lines)
        if edited is not None:
            return edited

        # No usable editor: fall back to raw terminal entry, prefill shown for reference.
        self._write_line("")
        self._write_line("Current suggested text (revise, extend, or replace it below):")
        for line in prefill.splitlines() or [prefill]:
            self._write_line(f"  {line}")
        self._write_line("")
        question = QuestionSpec(
            id="__edit__",
            prompt="Enter your revised statement.",
            kind=QuestionKind.MULTILINE,
            required=True,
        )
        self._write_line(question.prompt)
        answer = self._ask_multiline_raw(question)
        assert answer is not None
        return str(answer.value)

    def _ask_multiline(self, question: QuestionSpec) -> Answer | None:
        self._write_line(
            "(opening your editor for a multi-line answer; save and close it when done)"
        )
        edited = self._edit_text("", self._multiline_comment_lines(question))
        while edited is not None:
            text = edited.strip()
            if text:
                self._record_answer(text)
                return Answer(question_id=question.id, value=text, raw_input=edited)
            if not question.required:
                return None
            self._write_line("A response is required. Reopening the editor.")
            edited = self._edit_text("", self._multiline_comment_lines(question))
        return self._ask_multiline_raw(question)

    def _multiline_comment_lines(self, question: QuestionSpec) -> list[str]:
        lines = [question.prompt]
        if question.rule_context:
            lines.append("")
            lines.append("Context:")
            lines.extend(f"   {line}" for line in question.rule_context.splitlines())
        if question.hint:
            lines.append(f"Hint: {question.hint}")
        if question.answer_guidance:
            lines.append(question.answer_guidance)
        if not question.required:
            lines.append(
                "This is optional. Leave the answer empty to skip; nothing will be "
                "added to the report."
            )
        lines.append("")
        lines.append("Lines starting with '#' are ignored and will not be included.")
        return lines

    def _ask_multiline_raw(self, question: QuestionSpec) -> Answer | None:
        self._write_line(
            "Enter multiple lines. A line containing only '.' finishes; "
            "enter '\\.' for a literal dot. Enter :cancel on the first line to abort."
        )
        lines: list[str] = []
        while True:
            try:
                raw = self._read_line("| ")
            except EOFError as exc:
                return self._handle_missing(question, "multiline input ended", exc)

            if not lines and raw.strip() == _CANCEL_TOKEN:
                return self._handle_missing(question, "question cancelled")
            if raw == _MULTILINE_SENTINEL:
                text = "\n".join(lines).strip()
                if text:
                    return Answer(question_id=question.id, value=text, raw_input="\n".join(lines))
                if question.required:
                    self._write_line("A response is required. Continue entering text.")
                    continue
                return None
            lines.append(_MULTILINE_SENTINEL if raw == _MULTILINE_LITERAL_DOT else raw)

    def _render_options(self, question: QuestionSpec) -> None:
        if question.kind != QuestionKind.SINGLE_CHOICE:
            return
        for index, option in enumerate(question.options, start=1):
            marker = " (shortcut)" if option.exclusive else ""
            self._write_line(f"  {index}. {option.label}{marker} [{option.id}]")
            if option.locked_reason:
                self._write_line(f"       (unavailable: {option.locked_reason})")
            if option.statement:
                self._write_line(f"       recorded as: {option.statement}")
            if option.list_note:
                self._write_line(f"       {option.list_note}")
            if option.leads_to_followup:
                self._write_line("       (selecting this will ask for more detail next)")

    def _render_answer_guidance(self, question: QuestionSpec) -> None:
        if question.answer_guidance:
            self._write_line(question.answer_guidance)
        if not question.required:
            self._write_line(
                "This is optional. Leave the answer empty to skip; nothing will be "
                "added to the report."
            )

    def _parse_answer(self, question: QuestionSpec, raw: str):
        if question.kind == QuestionKind.TEXT:
            return raw
        if question.kind == QuestionKind.CONFIRM:
            normalized = raw.casefold()
            if normalized in {"y", "yes"}:
                return True
            if normalized in {"n", "no"}:
                return False
            raise ValueError("enter yes or no")
        if question.kind == QuestionKind.SINGLE_CHOICE:
            return self._resolve_option(question.options, raw).id
        raise ValueError(f"unsupported question kind: {question.kind}")

    @staticmethod
    def _resolve_option(options: tuple[QuestionOption, ...], token: str) -> QuestionOption:
        resolved: QuestionOption | None = None
        if token.isdecimal():
            index = int(token) - 1
            if 0 <= index < len(options):
                resolved = options[index]
        if resolved is None:
            normalized = token.casefold()
            for option in options:
                if option.id.casefold() == normalized:
                    resolved = option
                    break
        if resolved is None:
            expected = ", ".join(option.id for option in options)
            raise ValueError(f"choose an option number or one of: {expected}")
        if resolved.locked_reason:
            raise ValueError(
                f"{resolved.label!r} is currently unavailable: {resolved.locked_reason} "
                "Choose a different option."
            )
        return resolved

    @staticmethod
    def _handle_missing(
        question: QuestionSpec,
        reason: str,
        cause: BaseException | None = None,
    ) -> None:
        if not question.required:
            return None
        error = WizardAborted(f"required question {question.id!r} aborted: {reason}")
        if cause is not None:
            raise error from cause
        raise error
