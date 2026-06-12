"""Tests for catalog loading and validation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalog import load_catalog, summarize_catalog, validate_catalog

# ---------------------------------------------------------------------------
# Catalog loading
# ---------------------------------------------------------------------------


def test_load_catalog_parses_yaml():
    """Catalog should load without errors."""
    catalog_path = Path(__file__).resolve().parent.parent / "catalog.yaml"
    workspace_root = Path(__file__).resolve().parent.parent.parent

    catalog = load_catalog(catalog_path, workspace_root)

    assert catalog is not None
    assert isinstance(catalog, dict)


def test_load_catalog_has_required_sections():
    """Catalog should have all required top-level sections."""
    catalog_path = Path(__file__).resolve().parent.parent / "catalog.yaml"
    workspace_root = Path(__file__).resolve().parent.parent.parent

    catalog = load_catalog(catalog_path, workspace_root)

    assert "metadata" in catalog
    assert "global_policies" in catalog
    assert "checks" in catalog
    assert "evidence_adapters" in catalog


def test_load_catalog_checks_have_required_fields():
    """All checks should have required fields."""
    catalog_path = Path(__file__).resolve().parent.parent / "catalog.yaml"
    workspace_root = Path(__file__).resolve().parent.parent.parent

    catalog = load_catalog(catalog_path, workspace_root)
    checks = catalog.get("checks", [])

    assert len(checks) > 0, "Catalog should have at least one check"

    for check in checks:
        assert "id" in check, f"Check missing 'id': {check}"
        assert "section" in check, f"Check {check['id']} missing 'section'"
        assert "title" in check, f"Check {check['id']} missing 'title'"
        assert "mode" in check, f"Check {check['id']} missing 'mode'"

        # mode should be one of the valid values
        valid_modes = {"deterministic", "ev_to_ai", "ai", "human_only"}
        assert check["mode"] in valid_modes, (
            f"Check {check['id']} has invalid mode: {check['mode']}"
        )


def test_load_catalog_adapters_have_required_fields():
    """All adapters should have required fields."""
    catalog_path = Path(__file__).resolve().parent.parent / "catalog.yaml"
    workspace_root = Path(__file__).resolve().parent.parent.parent

    catalog = load_catalog(catalog_path, workspace_root)
    adapters = catalog.get("evidence_adapters", [])

    assert len(adapters) > 0, "Catalog should have at least one adapter"

    for adapter in adapters:
        assert "id" in adapter, f"Adapter missing 'id': {adapter}"
        assert "type" in adapter, f"Adapter {adapter['id']} missing 'type'"
        assert "description" in adapter, f"Adapter {adapter['id']} missing 'description'"


# ---------------------------------------------------------------------------
# Catalog summarization
# ---------------------------------------------------------------------------


def test_summarize_catalog_counts_checks():
    """summarize_catalog should count checks correctly."""
    catalog = {
        "checks": [
            {"id": "SUM-1", "section": "Summary"},
            {"id": "SUM-2", "section": "Summary"},
            {"id": "DEP-1", "section": "Dependencies"},
        ]
    }

    summary = summarize_catalog(catalog)

    assert summary["check_count"] == 3
    assert summary["sections"]["Summary"] == 2
    assert summary["sections"]["Dependencies"] == 1


def test_summarize_catalog_handles_empty_catalog():
    """summarize_catalog should handle empty catalog gracefully."""
    catalog = {}

    summary = summarize_catalog(catalog)

    assert summary["check_count"] == 0
    assert summary["sections"] == {}


def test_summarize_catalog_counts_security_triggers():
    """summarize_catalog should count security triggers."""
    catalog = {
        "checks": [],
        "security_triggers": [
            {"id": "SEC-1"},
            {"id": "SEC-2"},
        ],
    }

    summary = summarize_catalog(catalog)

    assert summary["security_trigger_count"] == 2


def test_validate_catalog_requires_dep3_messages():
    """DEP-3 must define migrated strict message templates."""
    catalog = {
        "metadata": {},
        "global_policies": {},
        "evidence_adapters": [{"id": "dep-analysis", "type": "local_exec", "description": "d"}],
        "checks": [
            {
                "id": "DEP-3",
                "section": "Dependencies",
                "title": "No -dev/-debug/-doc packages needing exclusion",
                "mode": "deterministic",
                "adapters_required": ["dep-analysis"],
            }
        ],
    }

    errors = validate_catalog(catalog)
    assert any("DEP-3: missing required messages map" in err for err in errors)


def test_validate_catalog_dep3_placeholder_validation():
    """DEP-3 template placeholders are validated strictly."""
    catalog = {
        "metadata": {},
        "global_policies": {},
        "evidence_adapters": [{"id": "dep-analysis", "type": "local_exec", "description": "d"}],
        "checks": [
            {
                "id": "DEP-3",
                "section": "Dependencies",
                "title": "No -dev/-debug/-doc packages needing exclusion",
                "mode": "deterministic",
                "adapters_required": ["dep-analysis"],
                "messages": {
                    "unknown_packaging_message": "Could not analyse binary packages",
                    "unknown_packaging_todo": "TODO: - Check whether -dev/-debug/-doc packages need exclusion",
                    "unknown_dep_analysis_message": "Could not analyse auto-included binary dependencies",
                    "unknown_dep_analysis_todo": "TODO: - Check whether auto-included -dev/-debug/-doc packages need exclusion",
                    "ok_no_auto_included_message": "no -dev/-debug/-doc packages that need exclusion",
                    "not_ok_offending_message": "bad {auto_included}",
                    "not_ok_offending_todo": "TODO {offending_deps}",
                    "ok_safe_message": "safe {auto_included}",
                },
            }
        ],
    }

    errors = validate_catalog(catalog)
    assert any("messages.not_ok_offending_message missing placeholders" in err for err in errors)
    assert any("messages.not_ok_offending_todo missing placeholders" in err for err in errors)
