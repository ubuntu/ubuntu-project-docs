"""Dependency-free terminal wizard for reporter-owned MIR answers."""

from __future__ import annotations

from collections.abc import Callable

from reporter.models import Answer, QuestionKind, QuestionOption, QuestionSpec

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
    ) -> None:
        self._read_line = read_line
        self._write_line = write_line

    def ask(self, question: QuestionSpec) -> Answer | None:
        """Ask until a valid answer is provided, or return None if optional."""
        self._write_line("")
        self._write_line(question.prompt)
        if question.hint:
            self._write_line(f"Hint: {question.hint}")

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
    ) -> Answer:
        """Require the reporter to accept or reject one AI suggestion."""
        self._write_line("")
        self._write_line("Suggested statement:")
        self._write_line(suggestion)
        if rationale.strip():
            self._write_line(f"Reasoning: {rationale.strip()}")
        question = QuestionSpec(
            id=question_id,
            prompt="Use this statement?",
            kind=QuestionKind.CONFIRM,
            required=True,
        )
        answer = self.ask(question)
        assert answer is not None
        return answer

    def _ask_multiline(self, question: QuestionSpec) -> Answer | None:
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
        if question.kind not in {QuestionKind.SINGLE_CHOICE, QuestionKind.MULTI_CHOICE}:
            return
        for index, option in enumerate(question.options, start=1):
            self._write_line(f"  {index}. {option.label} [{option.id}]")
        if question.kind == QuestionKind.MULTI_CHOICE:
            self._write_line("Select one or more options, separated by commas.")

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
        if question.kind == QuestionKind.MULTI_CHOICE:
            selected: list[str] = []
            for token in (part.strip() for part in raw.split(",")):
                if not token:
                    continue
                option_id = self._resolve_option(question.options, token).id
                if option_id not in selected:
                    selected.append(option_id)
            if not selected:
                raise ValueError("select at least one option")
            return selected
        raise ValueError(f"unsupported question kind: {question.kind}")

    @staticmethod
    def _resolve_option(options: tuple[QuestionOption, ...], token: str) -> QuestionOption:
        if token.isdecimal():
            index = int(token) - 1
            if 0 <= index < len(options):
                return options[index]
        normalized = token.casefold()
        for option in options:
            if option.id.casefold() == normalized:
                return option
        expected = ", ".join(option.id for option in options)
        raise ValueError(f"choose an option number or one of: {expected}")

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
