"""Focused unit tests for reporter/render.py draft formatting helpers."""

import sys
from pathlib import Path
from types import SimpleNamespace

TOOL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOL_ROOT))

from reporter.models import (  # noqa: E402
    Provenance,
    ReadinessEffect,
    StatementResult,
    StatementState,
)
from reporter.render import _build_draft, _lint_draft, _with_hanging_indent  # noqa: E402


def test_with_hanging_indent_leaves_single_line_text_unchanged():
    assert _with_hanging_indent("- One-line statement.") == "- One-line statement."


def test_with_hanging_indent_indents_continuation_lines():
    text = "- First line of a multi-select answer.\n- Second option also selected."

    result = _with_hanging_indent(text)

    lines = result.split("\n")
    assert lines[0] == "- First line of a multi-select answer."
    assert lines[1] == "  - Second option also selected."


def test_with_hanging_indent_skips_blank_continuation_lines():
    text = "- First line.\n\n- Third line after a blank one."

    result = _with_hanging_indent(text)

    lines = result.split("\n")
    assert lines[1] == ""
    assert lines[2] == "  - Third line after a blank one."


def _synthetic_ctx(items, blueprint):
    return SimpleNamespace(
        source_package="libfoo",
        series="devel",
        catalog={
            "metadata": {
                "reporter_template_blueprint": blueprint,
                "section_markers": [
                    entry for entry in blueprint if isinstance(entry, str) and entry.startswith("[")
                ],
            },
            "items": items,
        },
    )


def test_build_draft_groups_unresolved_item_under_left_to_clarify_for_its_section():
    """Regression test for feedback item 1b: an item the tool could not
    resolve (here: a plain free-text ev_to_ai fallback deferral) must appear
    under a "Left to clarify:" block at the end of its own section, never
    mixed inline with confident resolved bullets."""
    items = [
        {
            "id": "REP-RESOLVED",
            "section": "Security",
            "title": "Resolved thing",
            "mode": "ev_to_ai",
            "template": "TODO: - TBD",
        },
        {
            "id": "REP-CLARIFY",
            "section": "Security",
            "title": "Exposure and mitigation assessment",
            "mode": "ev_to_ai",
            "template": "TODO: - Security exposure and proportional mitigation assessment: TBD",
            "question": {"prompt": "Assess security-sensitive behavior and mitigations."},
        },
    ]
    blueprint = [
        "[Security]",
        "RULE: some policy",
        {"item": "REP-RESOLVED"},
        {"item": "REP-CLARIFY"},
        "",
    ]
    ctx = _synthetic_ctx(items, blueprint)
    by_id = {
        "REP-RESOLVED": StatementResult(
            id="REP-RESOLVED",
            section="Security",
            state=StatementState.RESOLVED,
            readiness=ReadinessEffect.CLEAR,
            statement="- No privileged operations were identified.",
            provenance=Provenance.DETERMINISTIC,
        ),
        "REP-CLARIFY": StatementResult(
            id="REP-CLARIFY",
            section="Security",
            state=StatementState.NEEDS_INPUT,
            readiness=ReadinessEffect.WARNING,
            rationale="The reporter deferred this question.",
        ),
    }

    draft = _build_draft(ctx, by_id)

    assert "- No privileged operations were identified." in draft
    assert "Left to clarify:" in draft
    assert "- Assess security-sensitive behavior and mitigations." in draft
    assert "TODO: - Security exposure and proportional mitigation assessment: TBD" in draft
    assert "(Reason: The reporter deferred this question.)" in draft
    # The resolved bullet must come before the clarify block, and the clarify
    # block must come before the section's own trailing blank-line separator.
    resolved_index = draft.index("- No privileged operations were identified.")
    clarify_index = draft.index("Left to clarify:")
    assert resolved_index < clarify_index


def test_build_draft_left_to_clarify_lists_each_option_todo_ref():
    """An unresolved options-based item (see reporter.ai's ev_to_ai + options
    support) must list each option's own TODO-lettered alternative, matching
    the original human template structure, instead of a single generic
    placeholder line."""
    items = [
        {
            "id": "REP-UI-CLARIFY",
            "section": "UI standards",
            "title": "Desktop file applicability",
            "mode": "ev_to_ai",
            "template": "TODO: - TBD",
            "question": {
                "prompt": "Is this a user-facing desktop program with a desktop file?",
                "options": [
                    {
                        "id": "not-ui",
                        "todo_ref": "TODO-A: - not part of the UI for extra checks",
                    },
                    {
                        "id": "ui-missing-desktop",
                        "todo_ref": "TODO-C: - part of the UI, no desktop file",
                    },
                ],
            },
        }
    ]
    blueprint = ["[UI standards]", "RULE: some policy", {"item": "REP-UI-CLARIFY"}, ""]
    ctx = _synthetic_ctx(items, blueprint)
    by_id = {
        "REP-UI-CLARIFY": StatementResult(
            id="REP-UI-CLARIFY",
            section="UI standards",
            state=StatementState.NEEDS_INPUT,
            readiness=ReadinessEffect.WARNING,
            rationale="The reporter deferred this question.",
        ),
    }

    draft = _build_draft(ctx, by_id)

    assert "TODO-A: - not part of the UI for extra checks" in draft
    assert "TODO-C: - part of the UI, no desktop file" in draft
    # The bare fallback template line must not also appear alongside the
    # per-option TODO-lettered alternatives.
    assert "TODO: - TBD" not in draft


def test_build_draft_omits_left_to_clarify_when_nothing_unresolved():
    items = [
        {
            "id": "REP-A",
            "section": "Security",
            "title": "A",
            "mode": "ev_to_ai",
            "template": "TODO: - TBD",
        },
    ]
    blueprint = ["[Security]", {"item": "REP-A"}, ""]
    ctx = _synthetic_ctx(items, blueprint)
    by_id = {
        "REP-A": StatementResult(
            id="REP-A",
            section="Security",
            state=StatementState.RESOLVED,
            readiness=ReadinessEffect.CLEAR,
            statement="- All good.",
            provenance=Provenance.DETERMINISTIC,
        ),
    }

    draft = _build_draft(ctx, by_id)

    assert "Left to clarify" not in draft


def test_lint_draft_rejects_raw_tbd_outside_left_to_clarify_block():
    catalog = {
        "metadata": {"section_markers": ["[Security]"]},
        "items": [{"id": "REP-A"}],
    }
    by_id = {
        "REP-A": StatementResult(
            id="REP-A",
            section="Security",
            state=StatementState.RESOLVED,
            readiness=ReadinessEffect.CLEAR,
            statement="- All good.",
            provenance=Provenance.DETERMINISTIC,
        )
    }
    good_draft = "[Security]\n- All good.\n"
    _lint_draft(good_draft, catalog, by_id)  # must not raise

    bad_draft = "[Security]\n- Something is TBD.\n"
    try:
        _lint_draft(bad_draft, catalog, by_id)
    except ValueError as exc:
        assert "TBD" in str(exc)
    else:
        raise AssertionError("expected _lint_draft to reject a raw TBD outside Left to clarify")


def test_lint_draft_allows_raw_tbd_inside_left_to_clarify_block():
    catalog = {
        "metadata": {"section_markers": ["[Security]"]},
        "items": [{"id": "REP-A"}],
    }
    by_id = {
        "REP-A": StatementResult(
            id="REP-A",
            section="Security",
            state=StatementState.NEEDS_INPUT,
            readiness=ReadinessEffect.WARNING,
        )
    }
    draft = "[Security]\n\nLeft to clarify:\n- Some question\n  TODO: - Something: TBD\n"

    _lint_draft(draft, catalog, by_id)  # must not raise
