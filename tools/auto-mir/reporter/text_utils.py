"""Shared text-processing helpers for reporter statement templates.

Used by both ``reporter.evaluator`` and ``reporter.ai``, which cannot import
from each other (``evaluator`` imports ``evaluate_ai_item`` from ``ai``), so
these small, dependency-free helpers live in their own module instead of
being duplicated in both.
"""

from __future__ import annotations

import re

_TODO_PREFIX_PATTERN = re.compile(r"^TODO(?:-[A-Z0-9/-]+)?:\s*")


def strip_todo_prefix(text: str) -> str:
    """Remove the catalog ``TODO:``/``TODO-X/Y:`` marker prefix from a template."""
    return _TODO_PREFIX_PATTERN.sub("", text).strip()


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
