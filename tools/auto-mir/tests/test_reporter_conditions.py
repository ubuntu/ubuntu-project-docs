"""Tests for safe reporter applicability-condition evaluation."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reporter.conditions import (  # noqa: E402
    ConditionContext,
    ConditionError,
    condition_references,
    evaluate_condition,
    validate_condition_cycles,
    validate_condition_references,
)


@pytest.fixture
def context():
    return ConditionContext(
        items={
            "REP-TEST-BUILD": "missing",
            "REP-TEST-AUTO": "passing",
            "REP-HW": ["team", "upstream"],
        },
        evidence={
            "sbuild": {"status": "ok", "build_success": True},
            "autopkgtest-db": {"passing_arches": ["amd64", "arm64"]},
        },
    )


def test_item_and_evidence_leaf_comparisons(context):
    assert evaluate_condition({"item": "REP-TEST-BUILD", "equals": "missing"}, context)
    assert evaluate_condition({"item": "REP-TEST-AUTO", "in": ["passing", "failing"]}, context)
    assert evaluate_condition({"evidence": "sbuild.build_success", "truthy": True}, context)
    assert not evaluate_condition({"evidence": "sbuild.missing", "truthy": True}, context)


def test_nested_all_any_and_not(context):
    condition = {
        "all": [
            {"item": "REP-TEST-BUILD", "equals": "missing"},
            {
                "any": [
                    {"item": "REP-TEST-AUTO", "equals": "missing"},
                    {"evidence": "autopkgtest-db.passing_arches", "truthy": True},
                ]
            },
            {"not": {"evidence": "sbuild.build_success", "equals": False}},
        ]
    }

    assert evaluate_condition(condition, context)


def test_none_condition_is_unconditionally_applicable(context):
    assert evaluate_condition(None, context)


@pytest.mark.parametrize(
    ("condition", "message"),
    [
        ({}, "non-empty mapping"),
        ({"all": [], "item": "REP-1"}, "exactly one operator"),
        ({"all": []}, "non-empty list"),
        ({"item": "REP-1"}, "exactly one comparison"),
        ({"item": "REP-1", "truthy": "yes"}, "requires a boolean"),
        ({"item": "REP-1", "in": []}, "non-empty list"),
        ({"evidence": "sbuild..status", "equals": "ok"}, "empty component"),
        ({"item": "REP-1", "equals": True, "script": "run()"}, "unsupported keys"),
    ],
)
def test_malformed_conditions_are_rejected(condition, message, context):
    with pytest.raises(ConditionError, match=message):
        evaluate_condition(condition, context)


def test_condition_references_are_collected():
    condition = {
        "all": [
            {"item": "REP-1", "equals": "a"},
            {"not": {"evidence": "sbuild.status", "equals": "error"}},
        ]
    }

    assert condition_references(condition) == {
        ("item", "REP-1"),
        ("evidence", "sbuild.status"),
    }


def test_reference_validation_reports_unknown_items_and_adapters():
    condition = {
        "all": [
            {"item": "REP-UNKNOWN", "equals": "a"},
            {"evidence": "missing.status", "equals": "ok"},
        ]
    }

    errors = validate_condition_references(
        condition,
        known_items={"REP-1"},
        known_adapters={"sbuild"},
    )

    assert errors == [
        "condition references unknown adapter: missing",
        "condition references unknown item: REP-UNKNOWN",
    ]


def test_cycle_validation_detects_self_and_multi_item_cycles():
    self_cycle = {"REP-1": {"item": "REP-1", "truthy": True}}
    assert validate_condition_cycles(self_cycle) == ["condition cycle: REP-1 -> REP-1"]

    multi_cycle = {
        "REP-1": {"item": "REP-2", "truthy": True},
        "REP-2": {"item": "REP-3", "truthy": True},
        "REP-3": {"item": "REP-1", "truthy": True},
    }
    errors = validate_condition_cycles(multi_cycle)

    assert len(errors) == 1
    assert errors[0].startswith("condition cycle: ")
    assert {"REP-1", "REP-2", "REP-3"}.issubset(set(errors[0].split()))


def test_cycle_validation_accepts_acyclic_graph_and_ignores_evidence():
    conditions = {
        "REP-1": None,
        "REP-2": {"item": "REP-1", "equals": "yes"},
        "REP-3": {"evidence": "sbuild.status", "equals": "ok"},
    }

    assert validate_condition_cycles(conditions) == []
