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
    assert review["security_triggers"]
    assert review["render_policy"]
    assert review["fallback_policy"]
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
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    expected = {item["id"] for item in report["items"]}
    actual = {
        entry["item"]
        for entry in report["metadata"]["reporter_template_blueprint"]
        if isinstance(entry, dict)
    }

    assert actual == expected


def test_report_catalog_has_complete_logical_item_and_hardware_choice_inventory():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}

    assert len(by_id) == 54
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


def test_report_catalog_validation_rejects_unrendered_item():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    report["metadata"]["reporter_template_blueprint"] = ["[Availability]"]

    errors = catalog.validate_report_catalog(report)

    assert any("blueprint omits items" in error for error in errors)


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


def test_report_catalog_validation_rejects_template_missing_dash():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    by_id["REP-BG-002"]["template"] = "TODO: Upstream Name is TBD"

    errors = catalog.validate_report_catalog(report)

    assert any(
        "REP-BG-002 template must embed its own '- ' bullet marker" in error for error in errors
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


def test_report_catalog_validation_rejects_option_statement_missing_dash():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    options = by_id["REP-RATIONALE-007"]["question"]["options"]
    options[0]["statement"] = "The package TBDSRC is required in Ubuntu main by a deadline."

    errors = catalog.validate_report_catalog(report)

    assert any(
        "REP-RATIONALE-007 option required-by statement must start with '- '" in error
        for error in errors
    )


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


def test_report_catalog_validation_rejects_item_reference_in_unavailable_if():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    by_id = {item["id"]: item for item in report["items"]}
    options = by_id["REP-MAINT-001"]["question"]["options"]
    options[0]["unavailable_if"] = {"item": "REP-RATIONALE-005", "equals": "niche"}

    errors = catalog.validate_report_catalog(report)

    assert any(
        "unavailable_if must only reference evidence, not other items" in error for error in errors
    )
