"""Tests for fixed review/report catalog composition."""

import sys
from pathlib import Path

import pytest

TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import catalog  # noqa: E402


def test_review_role_composes_shared_and_review_sections():
    review = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "review")

    assert review["role"] == "review"
    assert review["checks"]
    assert review["evidence_adapters"]
    assert review["global_policies"]
    assert review["metadata"]["review_template_blueprint"]
    assert "items" not in review
    assert (TOOL_ROOT / "catalog-mir-review.yaml").exists()


def test_report_role_composes_shared_adapters_and_report_items():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")

    assert report["role"] == "report"
    assert report["items"]
    assert report["evidence_adapters"]
    assert report["global_policies"]
    assert "checks" not in report
    assert report["metadata"]["reporter_template_blueprint"]


def test_report_catalog_every_item_is_rendered_once():
    """The blueprint reproduces the historical reporter template and is
    authoritative about which items appear in it; runtime-only items may be
    intentionally absent. Every blueprint item reference must resolve to a
    real catalog item and be listed exactly once."""
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    known = {item["id"] for item in report["items"]}
    refs = [
        entry["item"]
        for entry in report["metadata"]["reporter_template_blueprint"]
        if isinstance(entry, dict)
    ]

    assert set(refs) <= known
    assert len(refs) == len(set(refs))


def test_report_catalog_has_complete_logical_item_and_hardware_choice_inventory():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}

    assert len(by_id) == 64
    hardware_options = by_id["REP-QA-TEST-005"]["question"]["options"]
    assert {option["id"] for option in hardware_options} == {
        "A-team-hardware",
        "B-budget",
        "C-testflinger",
        "D-other-team",
        "E-simulator",
        "F-upstream",
        "G-users",
        "H-manufacturer",
        "X-exhausted",
        "Z-other",
        "Y-build-autopkgtest",
    }


def test_report_catalog_binary_scope_uses_fetch_build_independent_evidence():
    """REP-RATIONALE-004's package spell-out must not require fetch-build/dep-analysis
    to have succeeded (regression test for the borgbackup2 sbuild-failure case)."""
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}

    item = by_id["REP-RATIONALE-004"]
    assert item["question"]["options_source"] == {
        "adapter": "packaging-source",
        "field": "binary_package_names",
    }
    assert item["preface_evaluator"] == "binary-packages"
    assert "REP-RATIONALE-004B" not in by_id


def test_unknown_catalog_role_fails(capsys):
    with pytest.raises(SystemExit, match="1"):
        catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "unknown")

    assert "Unknown catalog role" in capsys.readouterr().err


def test_report_catalog_validation_rejects_unknown_writes_evidence_adapter():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    by_id["REP-BG-002"]["writes_evidence"] = {"adapter": "no-such-adapter", "field": "x"}

    errors = catalog.validate_report_catalog(report)

    assert any(
        "writes_evidence references unknown adapter: no-such-adapter" in error for error in errors
    )


def test_report_catalog_validation_rejects_unknown_default_source_adapter():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    by_id["REP-BG-002"]["question"]["default_source"] = {
        "adapter": "no-such-adapter",
        "field": "x",
    }

    errors = catalog.validate_report_catalog(report)

    assert any(
        "default_source references unknown adapter: no-such-adapter" in error for error in errors
    )


def test_report_catalog_validation_rejects_template_with_more_than_one_tbd():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    by_id["REP-BG-002"]["template"] = "TODO: - Deadline is TBD due to TBD"

    errors = catalog.validate_report_catalog(report)

    assert any(
        "REP-BG-002 template must contain at most one 'TBD' placeholder" in error
        for error in errors
    )


def test_report_catalog_validation_allows_tbdsrc_alongside_a_single_tbd():
    """TBDSRC is a separate source-name substitution, not a free-text-answer
    placeholder, so it must not count toward the "at most one TBD" limit."""
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    by_id["REP-BG-002"]["template"] = "TODO: - TBDSRC needs TBD"

    errors = catalog.validate_report_catalog(report)

    assert not any("must contain at most one 'TBD' placeholder" in error for error in errors)


def test_report_catalog_validation_rejects_invalid_option_readiness():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    options = by_id["REP-QA-MAINT-004"]["question"]["options"]
    options[0]["readiness"] = "urgent"

    errors = catalog.validate_report_catalog(report)

    assert any(
        "REP-QA-MAINT-004 option no-exotic-hardware has invalid readiness" in error
        for error in errors
    )


def test_report_catalog_validation_rejects_unavailable_if_without_reason():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    options = by_id["REP-MAINT-001"]["question"]["options"]
    del options[0]["unavailable_reason"]

    errors = catalog.validate_report_catalog(report)

    assert any(
        "REP-MAINT-001 option confirm-subscribed declares unavailable_if without an "
        "unavailable_reason" in error
        for error in errors
    )


def test_report_catalog_validation_rejects_unavailable_reason_without_condition():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    options = by_id["REP-MAINT-001"]["question"]["options"]
    options[1]["unavailable_reason"] = "Orphaned reason with no condition."

    errors = catalog.validate_report_catalog(report)

    assert any(
        "REP-MAINT-001 option new-team declares unavailable_reason without an "
        "unavailable_if" in error
        for error in errors
    )


def test_report_catalog_validation_rejects_unknown_adapter_in_unavailable_if():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    options = by_id["REP-MAINT-001"]["question"]["options"]
    options[0]["unavailable_if"] = {"evidence": "no-such-adapter.field", "truthy": True}

    errors = catalog.validate_report_catalog(report)

    assert any("references unknown adapter: no-such-adapter" in error for error in errors)


def test_report_catalog_auto_derives_rule_context_from_blueprint():
    """Items without a hand-authored rule_context get their section's blueprint
    RULE line(s) plus their own template (TODO) line auto-populated, so the
    reporter sees WHY and WHAT without any hand-duplicated policy text."""
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}

    # The restored historical template has no RULE prose in [UI standards],
    # so REP-UI-001 gets no auto-derived context at all.
    assert "rule_context" not in by_id["REP-UI-001"]

    # An item that declares covers_rule_clauses gets exactly those tagged RULE
    # clauses (plus its own TODO), not the whole section's prose.
    test_plan_rule_context = by_id["REP-QA-TEST-003"]["rule_context"]
    assert test_plan_rule_context.count("RULE:") == 23
    assert test_plan_rule_context.startswith(
        "RULE: - If no build tests nor autopkgtests are included"
    )
    assert test_plan_rule_context.endswith(
        "TODO: - Testing gaps and the owning team test plan are: TBD"
    )

    # A deterministic item is never asked as a question, so it gets no rule_context.
    assert "rule_context" not in by_id["REP-DEP-001"]

    # REP-MAINT-001 has no hand-authored rule_context (its condensed text no
    # longer matches the restored RULE prose); its context is auto-derived
    # from the Maintenance section and ends with its own template tree.
    maint_rule_context = by_id["REP-MAINT-001"]["rule_context"]
    assert maint_rule_context.startswith(
        "RULE: The package must have an acceptable level of maintenance corresponding"
    )
    assert maint_rule_context.endswith("TODO-B: - I Suggest the owning team to be TBD")


def test_report_catalog_validation_rejects_item_reference_in_unavailable_if():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    options = by_id["REP-MAINT-001"]["question"]["options"]
    options[0]["unavailable_if"] = {"item": "REP-RATIONALE-005", "equals": "niche"}

    errors = catalog.validate_report_catalog(report)

    assert any(
        "unavailable_if must only reference evidence, not other items" in error for error in errors
    )


# ---------------------------------------------------------------------------
# RULE[<slug>] clause-coverage mechanism (catalog-native, no frozen fixture).
# A blueprint RULE line tagged ``RULE[<slug>]:`` starts an individually
# tracked policy clause; items declare which slug(s) they resolve via
# ``covers_rule_clauses``. This is the real, structural "catalog maps to
# rendered content" guard - replaces the old keyword-presence smoke test,
# which could pass even when a whole policy clause silently lost its
# covering item (exactly what happened with the Maintainer-field gap).
# ---------------------------------------------------------------------------


def test_strip_rule_clause_tag_normalizes_tagged_line():
    assert (
        catalog.strip_rule_clause_tag("RULE[pkg-lintian-overrides]: Explain lintian overrides.")
        == "RULE: Explain lintian overrides."
    )


def test_strip_rule_clause_tag_leaves_plain_rule_line_unchanged():
    assert (
        catalog.strip_rule_clause_tag("RULE: Plain untagged line.") == "RULE: Plain untagged line."
    )


def test_rule_clause_coverage_rejects_uncovered_clause():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    report["metadata"]["reporter_template_blueprint"].append(
        "RULE[test-uncovered-clause]: a clause nobody covers"
    )

    errors = catalog.validate_report_catalog(report)

    assert any(
        "RULE[test-uncovered-clause] in reporter_template_blueprint has no covering item" in error
        for error in errors
    )


def test_rule_clause_coverage_rejects_duplicate_slug():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    report["metadata"]["reporter_template_blueprint"].extend(
        [
            "RULE[test-dup-clause]: first declaration",
            "RULE[test-dup-clause]: second declaration",
        ]
    )

    errors = catalog.validate_report_catalog(report)

    assert any(
        "reporter_template_blueprint declares RULE[test-dup-clause] more than once" in error
        for error in errors
    )


def test_rule_clause_coverage_rejects_reference_to_unknown_slug():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    by_id["REP-BG-002"]["covers_rule_clauses"] = ["no-such-clause"]

    errors = catalog.validate_report_catalog(report)

    assert any(
        "REP-BG-002: covers_rule_clauses references unknown RULE clause: no-such-clause" in error
        for error in errors
    )


def test_rule_clause_coverage_accepts_a_covered_clause():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    report["metadata"]["reporter_template_blueprint"].append(
        "RULE[test-covered-clause]: a clause with a covering item"
    )
    by_id = {item["id"]: item for item in report["items"]}
    by_id["REP-BG-002"]["covers_rule_clauses"] = ["test-covered-clause"]

    errors = catalog.validate_report_catalog(report)

    assert not any("test-covered-clause" in error for error in errors)


def test_review_catalog_rule_clause_coverage_rejects_uncovered_clause():
    review = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "review")
    review["metadata"]["review_template_blueprint"].append(
        "RULE[test-review-uncovered]: a review clause nobody covers"
    )

    errors = catalog.validate_catalog(review)

    assert any(
        "RULE[test-review-uncovered] in review_template_blueprint has no covering item" in error
        for error in errors
    )


def test_review_catalog_rule_clause_coverage_accepts_a_covered_clause():
    review = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "review")
    review["metadata"]["review_template_blueprint"].append(
        "RULE[test-review-covered]: a review clause with a covering check"
    )
    by_id = {check["id"]: check for check in review["checks"]}
    by_id["SEC-2"]["covers_rule_clauses"] = ["test-review-covered"]

    errors = catalog.validate_catalog(review)

    assert not any("test-review-covered" in error for error in errors)


def test_adapter_registry_matches_catalog_adapter_ids():
    """The @adapter registry and catalog.yaml must name the same adapter ids.

    Replaces the AdapterID enum's 'must match catalog.yaml' duty: any drift
    (a collector without a catalog entry, or a declared adapter with no
    collector) fails here instead of at run time.
    """
    from evidence import ADAPTER_REGISTRY as registry

    shared = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")

    declared = {a["id"] for a in shared.get("evidence_adapters", [])}
    assert declared, "catalog.yaml declares no evidence adapters"
    assert declared == set(registry)


# ---------------------------------------------------------------------------
# Blueprint entry vocabulary. Every consumer (docs renderers, rule_context
# auto-derivation, the runtime reporter draft renderer) branches on the entry
# prefix, so an unrecognized prefix is a silent double failure: its prose
# vanishes from the reporter's context AND the raw line leaks into rendered
# output. Validation rejects it at catalog-load time instead.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ("[Rationale]", "section"),
        ("RULE: plain policy prose", "rule"),
        ("RULE[rationale-demand]: tagged clause opener", "rule"),
        ("TODO: - a checklist line", "todo"),
        ("TODO-A: - an alternative", "todo"),
        ("OK:", "label"),
        ("Required TODOs:", "label"),
        ("", "blank"),
        ("   ", "blank"),
        ({"item": "REP-BG-002"}, "item"),
        ("RULE   a mistyped continuation line", "text"),
        ("RULE some prose without a colon", "text"),
    ],
)
def test_classify_blueprint_entry(entry, expected):
    assert catalog.classify_blueprint_entry(entry) == expected


def test_blueprint_entry_validation_rejects_unknown_prefix():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    report["metadata"]["reporter_template_blueprint"].append("RULE   mistyped continuation")

    errors = catalog.validate_report_catalog(report)

    assert any("is not a recognized blueprint entry" in error for error in errors)


def test_review_blueprint_entry_validation_rejects_unknown_prefix():
    review = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "review")
    review["metadata"]["review_template_blueprint"].append("RULE   mistyped continuation")

    errors = catalog.validate_catalog(review)

    assert any("is not a recognized blueprint entry" in error for error in errors)


def test_real_blueprints_use_only_known_entry_kinds():
    for role, key, validate in (
        ("report", "reporter_template_blueprint", catalog.validate_report_catalog),
        ("review", "review_template_blueprint", catalog.validate_catalog),
    ):
        loaded = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, role)
        unknown = [
            entry
            for entry in loaded["metadata"][key]
            if catalog.classify_blueprint_entry(entry) == "text"
        ]
        assert not unknown, f"{key} has unclassifiable entries: {unknown}"
        assert not [error for error in validate(loaded) if "recognized blueprint entry" in error]


def test_completes_must_be_gated_on_the_item_it_completes():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    by_id["REP-BG-002"]["completes"] = "REP-BG-001"

    errors = catalog.validate_report_catalog(report)

    assert any("is not gated on that item" in error for error in errors)


def test_completes_rejects_two_completers_for_one_item():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    for item_id in ("REP-BG-001", "REP-BG-002"):
        by_id[item_id]["completes"] = "REP-BG-003"
        by_id[item_id]["applicability"] = {"item": "REP-BG-003", "equals": "x"}

    errors = catalog.validate_report_catalog(report)

    assert any("completed by more than one item" in error for error in errors)
