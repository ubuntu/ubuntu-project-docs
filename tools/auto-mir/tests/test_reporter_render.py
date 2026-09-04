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


# ---------------------------------------------------------------------------
# Draft layout (feedback item 1a/1b): the draft carries only computed
# statements, and its blank lines are structural. Blueprint RULE/TODO prose
# and blueprint '' separators exist for the human template and the
# interactive Context block, never for the generated report.
# ---------------------------------------------------------------------------


def _layout_fixture():
    """Two sections where every source of stray/missing blank lines is present.

    Section one: a suppressed (not-applicable) item and RULE/TODO prose
    between blueprint '' separators; section two: a blueprint-referenced item
    plus an unreferenced ("extra") item, which used to be appended after the
    section's trailing separator and thereby ate the blank line before the
    next header.
    """
    items = [
        {"id": "REP-A", "section": "Security", "title": "A", "mode": "deterministic"},
        {"id": "REP-SKIP", "section": "Security", "title": "Skipped", "mode": "deterministic"},
        {"id": "REP-B", "section": "Dependencies", "title": "B", "mode": "deterministic"},
        {"id": "REP-EXTRA", "section": "Dependencies", "title": "Extra", "mode": "deterministic"},
    ]
    blueprint = [
        "",
        "[Security]",
        "RULE[sec-tagged]: a tagged clause opener",
        "RULE: continuation prose",
        {"item": "REP-A"},
        "",
        "TODO: - a checklist alternative",
        {"item": "REP-SKIP"},
        "",
        "",
        "[Dependencies]",
        "RULE: more prose",
        {"item": "REP-B"},
        "",
    ]
    resolved = {
        "REP-A": "- Security statement.",
        "REP-B": "- Dependency statement.",
        "REP-EXTRA": "- Extra dependency statement.",
    }
    by_id = {
        item_id: StatementResult(
            id=item_id,
            section="Security" if item_id == "REP-A" else "Dependencies",
            state=StatementState.RESOLVED,
            readiness=ReadinessEffect.CLEAR,
            statement=statement,
            provenance=Provenance.DETERMINISTIC,
        )
        for item_id, statement in resolved.items()
    }
    by_id["REP-SKIP"] = StatementResult(
        id="REP-SKIP",
        section="Security",
        state=StatementState.NOT_APPLICABLE,
        readiness=ReadinessEffect.CLEAR,
    )
    return _synthetic_ctx(items, blueprint), by_id


def test_build_draft_emits_no_template_scaffolding():
    ctx, by_id = _layout_fixture()

    draft = _build_draft(ctx, by_id)

    assert "RULE" not in draft
    assert "TODO" not in draft


def test_build_draft_has_no_consecutive_blank_lines():
    ctx, by_id = _layout_fixture()

    lines = _build_draft(ctx, by_id).splitlines()

    doubled = [
        index
        for index in range(1, len(lines))
        if not lines[index].strip() and not lines[index - 1].strip()
    ]
    assert not doubled, f"blank lines doubled at {doubled}: {lines}"


def test_build_draft_separates_every_section_with_one_blank_line():
    ctx, by_id = _layout_fixture()

    lines = _build_draft(ctx, by_id).splitlines()

    headers = [index for index, line in enumerate(lines) if line.startswith("[")]
    assert headers
    for index in headers:
        assert lines[index - 1] == "", f"missing blank line before {lines[index]!r}"


def test_build_draft_keeps_unreferenced_results_inside_their_section():
    ctx, by_id = _layout_fixture()

    draft = _build_draft(ctx, by_id)
    lines = draft.splitlines()

    extra_index = lines.index("- Extra dependency statement.")
    assert lines[extra_index - 1] == "- Dependency statement."
    assert extra_index == len(lines) - 1


def test_lint_draft_rejects_leaked_rule_or_todo_line():
    catalog = {"metadata": {"section_markers": ["[Security]"]}, "items": [{"id": "REP-A"}]}
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
    for leaked in ("RULE[sec-tagged]: policy prose", "RULE: policy prose", "TODO: - checklist"):
        draft = f"[Security]\n- All good.\n{leaked}\n"
        try:
            _lint_draft(draft, catalog, by_id)
        except ValueError as exc:
            assert "template text" in str(exc)
        else:
            raise AssertionError(f"expected _lint_draft to reject {leaked!r}")


def test_lint_draft_rejects_layout_defects():
    catalog = {
        "metadata": {"section_markers": ["[Security]", "[Dependencies]"]},
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
    good = "[Security]\n- All good.\n\n[Dependencies]\n- Fine.\n"
    _lint_draft(good, catalog, by_id)  # must not raise

    for bad, expected in (
        ("[Security]\n- All good.\n[Dependencies]\n- Fine.\n", "blank line before section"),
        ("[Security]\n- All good.\n\n\n[Dependencies]\n- Fine.\n", "consecutive blank lines"),
        ("[Security]\n- All good.\n\n[Dependencies]\n- Fine.\n\n", "end with a blank line"),
    ):
        try:
            _lint_draft(bad, catalog, by_id)
        except ValueError as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"expected _lint_draft to reject: {bad!r}")


def test_build_draft_lists_a_deterministic_action_finding_under_left_to_clarify():
    """Feedback item 1c: a deterministic finding that still asks the reporter
    for something ("no recent build was confirmed - provide a reference") is
    outstanding work, not a settled statement, so it belongs in the clarify
    block with its own evidence-derived wording, not a generic question."""
    items = [{"id": "REP-BUILD", "section": "Maintenance/Owner", "title": "Recent build"}]
    blueprint = ["[Maintenance/Owner]", {"item": "REP-BUILD"}]
    ctx = _synthetic_ctx(items, blueprint)
    by_id = {
        "REP-BUILD": StatementResult(
            id="REP-BUILD",
            section="Maintenance/Owner",
            state=StatementState.NEEDS_INPUT,
            readiness=ReadinessEffect.WARNING,
            statement="- No Launchpad build within the last three months was confirmed.",
            provenance=Provenance.DETERMINISTIC,
            rationale="Provide a recent archive, test-rebuild, PPA, or local sbuild reference.",
        )
    }

    draft = _build_draft(ctx, by_id)
    lines = draft.splitlines()

    heading = lines.index("Left to clarify:")
    assert lines[heading + 1] == "- No Launchpad build within the last three months was confirmed."
    assert lines[heading + 2] == (
        "  (Provide a recent archive, test-rebuild, PPA, or local sbuild reference.)"
    )
    # No generic question/TODO scaffolding for an item that already has a
    # concrete evidence-derived finding.
    assert "Reason:" not in draft
