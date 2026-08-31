"""Typed domain models for the MIR reporter workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class QuestionKind(StrEnum):
    """Supported terminal input shapes."""

    TEXT = "text"
    MULTILINE = "multiline"
    CONFIRM = "confirm"
    SINGLE_CHOICE = "single_choice"


class StatementState(StrEnum):
    """Resolution state for one reporter-template statement."""

    RESOLVED = "resolved"
    NEEDS_INPUT = "needs-input"
    NOT_APPLICABLE = "not-applicable"
    UNAVAILABLE = "unavailable"


class ReadinessEffect(StrEnum):
    """How an item affects readiness to submit the MIR request."""

    CLEAR = "clear"
    WARNING = "warning"
    BLOCKER = "blocker"


class Provenance(StrEnum):
    """Authority that supplied the final reporter statement."""

    DETERMINISTIC = "deterministic"
    HUMAN = "human"
    AI_CONFIRMED = "ai-confirmed"


@dataclass(frozen=True)
class QuestionOption:
    """One catalog-defined choice for a terminal question.

    ``locked_reason``, when non-empty, means the option is currently shown
    but not selectable (e.g. its catalog-declared ``unavailable_if``
    condition resolved true against evidence). It is a *resolved* runtime
    value computed by the evaluator, not something the catalog authors
    directly on this model.

    ``list_note``, when non-empty, is an informational line shown under the
    option (e.g. spelling out concrete evidence-derived names) without being
    part of the recorded ``statement`` itself.

    ``todo_ref``, when non-empty, is this option's own catalog-authored
    ``TODO-<letter>:`` reference line (mirrors the reviewer catalog's option
    ``todo_ref``). It is never shown as part of a resolved statement; it
    exists so an unresolved/deferred item can still preserve each option's
    original TODO-lettered alternative text for a "Left to clarify" block.
    """

    id: str
    label: str
    statement: str = ""
    exclusive: bool = False
    leads_to_followup: bool = False
    readiness: ReadinessEffect | None = None
    locked_reason: str = ""
    list_note: str = ""
    todo_ref: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("question option id must not be empty")
        if not self.label.strip():
            raise ValueError(f"question option {self.id!r} label must not be empty")


@dataclass(frozen=True)
class QuestionSpec:
    """Validated description of one question asked by the reporter wizard.

    ``deferrable``, when true, offers an explicit ``:defer`` escape hatch
    (see ``TerminalWizard``) so the reporter can say "I cannot resolve this
    now" instead of being forced to either answer or abort the whole run.
    Only ever set for an ``ev_to_ai`` item's human-fallback question - a
    ``human_only`` question always requires a genuine resolved answer (or
    an explicit catalog ``required: false`` skip), by design.
    """

    id: str
    prompt: str
    kind: QuestionKind
    required: bool = True
    options: tuple[QuestionOption, ...] = ()
    hint: str = ""
    default: Any = None
    rule_context: str = ""
    answer_guidance: str = ""
    deferrable: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("question id must not be empty")
        if not self.prompt.strip():
            raise ValueError(f"question {self.id!r} prompt must not be empty")

        choice_kind = self.kind == QuestionKind.SINGLE_CHOICE
        if choice_kind and not self.options:
            raise ValueError(f"question {self.id!r} requires at least one option")
        if not choice_kind and self.options:
            raise ValueError(f"question {self.id!r} cannot define options for {self.kind}")

        option_ids = [option.id.casefold() for option in self.options]
        if len(option_ids) != len(set(option_ids)):
            raise ValueError(f"question {self.id!r} has duplicate option ids")


@dataclass(frozen=True)
class Answer:
    """One normalized human answer retained for the current process only."""

    question_id: str
    value: Any


@dataclass
class StatementResult:
    """Reporter-facing result for one catalog statement.

    This deliberately does not reuse reviewer ``Finding`` severity or ACK/NACK
    semantics. An AI suggestion becomes authoritative only after the reporter
    explicitly confirms it, represented by ``Provenance.AI_CONFIRMED`` and
    ``human_confirmed=True``.
    """

    id: str
    section: str
    state: StatementState
    readiness: ReadinessEffect
    statement: str = ""
    selected_option: str | list[str] | None = None
    provenance: Provenance | None = None
    evidence_refs: list[str] = field(default_factory=list)
    answer_refs: list[str] = field(default_factory=list)
    rationale: str = ""
    human_confirmed: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("statement result id must not be empty")
        if not self.section.strip():
            raise ValueError(f"statement result {self.id!r} section must not be empty")
        if self.state == StatementState.RESOLVED:
            if not self.statement.strip():
                raise ValueError(f"resolved statement {self.id!r} must include text")
            if self.provenance is None:
                raise ValueError(f"resolved statement {self.id!r} must include provenance")
        if self.provenance == Provenance.AI_CONFIRMED and not self.human_confirmed:
            raise ValueError(f"AI statement {self.id!r} must be explicitly human-confirmed")
        if self.state != StatementState.RESOLVED and self.provenance == Provenance.AI_CONFIRMED:
            raise ValueError(f"unresolved statement {self.id!r} cannot use AI-confirmed provenance")
