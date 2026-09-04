"""Shared text-processing helpers for reporter statement templates.

Used by both ``reporter.evaluator`` and ``reporter.ai``, which cannot import
from each other (``evaluator`` imports ``evaluate_ai_item`` from ``ai``), so
these small, dependency-free helpers live in their own module instead of
being duplicated in both.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from auto_mir import RunContext

_TODO_PREFIX_PATTERN = re.compile(r"^TODO(?:-[A-Z0-9/-]+)?:\s*")
_URL_ANSWER_PATTERN = re.compile(r"^https?://\S+$")


def strip_todo_prefix(text: str) -> str:
    """Remove the catalog ``TODO:``/``TODO-X/Y:`` marker prefix from a template.

    The ``- `` bullet after the marker is content (reporter statements keep
    their bullet), so it is not stripped here.
    """
    return _TODO_PREFIX_PATTERN.sub("", text).strip()


_TODO_AND_DASH_PATTERN = re.compile(r"^\s*(?:TODO(?:-[A-Z0-9]+)?:\s*)+(?:-\s*)?")


def template_to_statement(template: str, source_package: str) -> str:
    """Turn a catalog ``template`` into the statement text the reporter edits.

    Strips the ``TODO``/``TODO-X:`` marker from every line (the marker is
    checklist bookkeeping in the human template, not part of the sentence)
    and resolves ``TBDSRC``, while deliberately KEEPING every ``TBD``: those
    are the slots the reporter fills in the editor, and an unfilled one is
    what routes the item to "Left to clarify:".

    Multi-line templates keep their continuation lines, so an alternative
    that spans several lines is offered for completion exactly as the human
    template words it; continuation lines are indented under the leading
    bullet, matching how the draft renders a multi-line statement.
    """
    lines = [strip_todo_prefix(line) for line in str(template).splitlines()]
    kept = [line for line in lines if line]
    if not kept:
        return ""
    joined = "\n".join([kept[0], *(f"  {line}" for line in kept[1:])])
    return substitute_source(joined, source_package)


def strip_todo_and_dash_prefix(line: str) -> str:
    """Strip leading TODO markers and list dashes, leaving statement text.

    Shared by the reviewer draft renderer and the LLM response parser; both
    normalize catalog TODO lines to bare statement text.
    """
    return _TODO_AND_DASH_PATTERN.sub("", line).strip()


def ensure_bulleted(text: str) -> str:
    """Prefix ``- `` onto free-form generated text that isn't catalog-templated.

    Deterministic evaluators, AI suggestions, and consistency corrections all
    produce statement text outside of the catalog's ``template``/option
    ``statement`` strings, which already embed their own leading ``- ``. This
    keeps that same "one bullet per resolved statement" shape for text that
    doesn't go through the catalog template mechanism, without double-adding
    a dash when the text already has one.
    """
    stripped = text.lstrip()
    if stripped.startswith("- "):
        return text
    return f"- {text}"


def substitute_source(text: str, source_package: str) -> str:
    """Replace the ``TBDSRC`` catalog placeholder with the actual source package.

    Prose uses the ``src:<pkg>`` convention, matching how source packages are
    referenced in Debian/Ubuntu bug and MIR text (to disambiguate from binary
    package names appearing in the same sentence). Inside a literal
    Launchpad ``/+source/`` (or ``/source/``) URL path segment, the bare
    package name is used instead, since that is required to keep the URL
    valid.
    """
    if "TBDSRC" not in text:
        return text
    parts = text.split("TBDSRC")
    result = parts[0]
    for part in parts[1:]:
        if result.endswith(("/+source/", "/source/")):
            result += source_package
        else:
            result += f"src:{source_package}"
        result += part
    return result


def maybe_write_evidence(item: dict, ctx: RunContext, answer_value: Any) -> None:
    """Backfill an evidence adapter field from a human answer, if declared.

    Lets a later catalog item's deterministic evaluator (e.g. the upstream
    project link check) benefit from a URL the reporter already typed while
    answering an earlier, differently-worded question, instead of asking
    twice or the consistency pass flagging a false contradiction between the
    two answers. Shared by both the ``human_only`` dispatch in
    ``reporter.evaluator`` and ``ai._ask_human`` (the ``ev_to_ai`` fallback
    path), since ``writes_evidence`` is a generic item-level catalog field,
    not specific to either mode.
    """
    target = item.get("writes_evidence")
    if not isinstance(target, dict):
        return
    adapter_id = str(target.get("adapter", ""))
    field = str(target.get("field", ""))
    if not adapter_id or not field or not isinstance(answer_value, str):
        return
    candidate = answer_value.strip()
    if not _URL_ANSWER_PATTERN.match(candidate):
        return
    adapters = ctx.evidence.setdefault("adapters", {})
    adapter_data = adapters.setdefault(adapter_id, {})
    if not isinstance(adapter_data, dict) or adapter_data.get(field):
        return
    adapter_data[field] = candidate


def resolve_option_statements(
    options: list[dict], answer_value: Any, source_package: str
) -> str | None:
    """Return the canonical ``statement`` text for a chosen single_choice option.

    ``answer_value`` is the selected option id (or a list of ids for a
    multi-select answer). Returns ``None`` when ``answer_value`` does not
    resolve to any option with a non-empty ``statement`` (e.g. a plain
    ``kind: text``/``multiline`` answer with no ``options`` at all), so the
    caller can fall back to its own template-based construction.

    Shared by ``reporter.evaluator``'s ``human_only`` dispatch and
    ``reporter.ai``'s ``ev_to_ai`` fallback (single_choice items), since a
    catalog option's pre-written ``statement`` is the canonical rendered
    text either way - never spliced into the item's outer ``template``.
    """
    selected = answer_value if isinstance(answer_value, list) else [answer_value]
    option_statements = [
        substitute_source(str(option.get("statement", "")), source_package)
        for option in options
        if option.get("id") in selected and option.get("statement")
    ]
    if not option_statements:
        return None
    return "\n".join(option_statements)
