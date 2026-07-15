"""Tests for fixed review/report catalog composition."""

import sys
from pathlib import Path

import pytest

TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import catalog  # noqa: E402


def test_review_role_preserves_existing_catalog():
    legacy = catalog.load_catalog(TOOL_ROOT / "catalog.yaml", WORKSPACE_ROOT)
    review = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "review")

    assert review == legacy


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

    assert len(by_id) == 53
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
    }


def test_unknown_catalog_role_fails(capsys):
    with pytest.raises(SystemExit, match="1"):
        catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "unknown")

    assert "Unknown catalog role" in capsys.readouterr().err


def test_report_catalog_validation_rejects_unrendered_item():
    report = catalog.load_catalog_for_role(TOOL_ROOT, WORKSPACE_ROOT, "report")
    report["metadata"]["reporter_template_blueprint"] = ["[Availability]"]

    errors = catalog.validate_report_catalog(report)

    assert any("blueprint omits items" in error for error in errors)
