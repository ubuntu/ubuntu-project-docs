"""Tests for catalog loading and validation."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from catalog import load_catalog, load_catalog_for_role, summarize_catalog, validate_catalog

# ---------------------------------------------------------------------------
# Catalog loading
# ---------------------------------------------------------------------------


def test_load_catalog_parses_yaml():
    """The composed review catalog should load without errors."""
    tool_root = Path(__file__).resolve().parent.parent
    workspace_root = tool_root.parent.parent

    catalog = load_catalog_for_role(tool_root, workspace_root, "review")

    assert catalog is not None
    assert isinstance(catalog, dict)


def test_load_catalog_rejects_duplicate_keys(tmp_path, capsys):
    """Catalog policy must not be silently shadowed by duplicate YAML keys."""
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text("metadata: {}\nmetadata: {}\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        load_catalog(catalog_path, tmp_path)

    assert exc_info.value.code == 1
    error = capsys.readouterr().err
    assert "found duplicate key 'metadata'" in error
    assert str(catalog_path) in error


def test_load_catalog_rejects_non_mapping_root(tmp_path, capsys):
    """A catalog root must be a mapping rather than a YAML sequence."""
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text("- metadata\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        load_catalog(catalog_path, tmp_path)

    assert exc_info.value.code == 1
    assert "catalog root must be a mapping" in capsys.readouterr().err


def test_load_catalog_has_required_sections():
    """The composed review catalog should have all required top-level sections."""
    tool_root = Path(__file__).resolve().parent.parent
    workspace_root = tool_root.parent.parent

    catalog = load_catalog_for_role(tool_root, workspace_root, "review")

    assert "metadata" in catalog
    assert "global_policies" in catalog
    assert "checks" in catalog
    assert "evidence_adapters" in catalog


def test_load_catalog_checks_have_required_fields():
    """All checks should have required fields."""
    tool_root = Path(__file__).resolve().parent.parent
    workspace_root = tool_root.parent.parent

    catalog = load_catalog_for_role(tool_root, workspace_root, "review")
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
    tool_root = Path(__file__).resolve().parent.parent
    workspace_root = tool_root.parent.parent

    catalog = load_catalog_for_role(tool_root, workspace_root, "review")
    adapters = catalog.get("evidence_adapters", [])

    assert len(adapters) > 0, "Catalog should have at least one adapter"

    for adapter in adapters:
        assert "id" in adapter, f"Adapter missing 'id': {adapter}"
        assert "type" in adapter, f"Adapter {adapter['id']} missing 'type'"
        assert "description" in adapter, f"Adapter {adapter['id']} missing 'description'"


def test_synthesis_checks_are_marked():
    """SUM-5 and SUM-6 must carry the synthesis flag so they run last."""
    tool_root = Path(__file__).resolve().parent.parent
    workspace_root = tool_root.parent.parent

    catalog = load_catalog_for_role(tool_root, workspace_root, "review")
    by_id = {c["id"]: c for c in catalog.get("checks", [])}

    assert by_id["SUM-5"].get("synthesis") is True
    assert by_id["SUM-6"].get("synthesis") is True


def test_rdo_3_uses_ev_to_ai_with_lp_bug_api():
    """RDO-3 should route through ev_to_ai and keep the lp-bug-api adapter."""
    tool_root = Path(__file__).resolve().parent.parent
    workspace_root = tool_root.parent.parent

    catalog = load_catalog_for_role(tool_root, workspace_root, "review")
    by_id = {c["id"]: c for c in catalog.get("checks", [])}

    rdo_3 = by_id["RDO-3"]
    assert rdo_3["mode"] == "ev_to_ai"
    assert "lp-bug-api" in rdo_3.get("adapters_required", [])
    assert not rdo_3.get("synthesis")


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
                "required_messages": {"ok_safe_message": ["auto_included"]},
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
                    "unknown_packaging_todo": (
                        "TODO: - Check whether -dev/-debug/-doc packages need exclusion"
                    ),
                    "unknown_dep_analysis_message": (
                        "Could not analyse auto-included binary dependencies"
                    ),
                    "unknown_dep_analysis_todo": (
                        "TODO: - Check whether auto-included -dev/-debug/-doc packages need exclusion"
                    ),
                    "ok_no_auto_included_message": (
                        "no -dev/-debug/-doc packages that need exclusion"
                    ),
                    "not_ok_offending_message": "bad {auto_included}",
                    "not_ok_offending_todo": "TODO {offending_deps}",
                    "ok_safe_message": "safe {auto_included}",
                },
                "required_messages": {
                    "unknown_packaging_message": [],
                    "unknown_packaging_todo": [],
                    "unknown_dep_analysis_message": [],
                    "unknown_dep_analysis_todo": [],
                    "ok_no_auto_included_message": [],
                    "not_ok_offending_message": ["auto_included", "offending_deps"],
                    "not_ok_offending_todo": ["details", "offending_deps"],
                    "ok_safe_message": ["auto_included"],
                },
            }
        ],
    }

    errors = validate_catalog(catalog)
    assert any("messages.not_ok_offending_message missing placeholders" in err for err in errors)
    assert any("messages.not_ok_offending_todo missing placeholders" in err for err in errors)


def test_validate_catalog_sum3_llm_placeholder_validation():
    """SUM-3 LLM fallback message must include the {error} placeholder."""
    catalog = {
        "metadata": {},
        "global_policies": {},
        "evidence_adapters": [
            {"id": "component-mismatches", "type": "local_exec", "description": "d"}
        ],
        "checks": [
            {
                "id": "SUM-3",
                "section": "Summary",
                "title": "Binary packages to promote",
                "mode": "ev_to_ai",
                "adapters_required": ["component-mismatches"],
                "messages": {
                    "llm_unavailable_message": "LLM unavailable",
                },
            }
        ],
    }

    errors = validate_catalog(catalog)
    assert any("messages.llm_unavailable_message missing placeholders" in err for err in errors)


def _option_check_catalog(options):
    return {
        "metadata": {},
        "global_policies": {},
        "evidence_adapters": [{"id": "packaging-source", "type": "local_exec", "description": "d"}],
        "checks": [
            {
                "id": "OPT-1",
                "section": "Packaging red flags",
                "title": "Option check",
                "mode": "ev_to_ai",
                "adapters_required": ["packaging-source"],
                "messages": {"llm_unavailable_message": "LLM unavailable: {error}"},
                "options": options,
            }
        ],
    }


def test_validate_catalog_option_requires_render_and_outcome():
    """Non-Summary ev_to_ai options must declare render and a valid outcome."""
    errors = validate_catalog(
        _option_check_catalog(
            [
                {"id": "OPT-1-A", "todo_ref": "TODO-A", "outcome": "ok"},  # missing render
                {"id": "OPT-1-B", "todo_ref": "TODO-B", "render": "- ok"},  # missing outcome
            ]
        )
    )
    assert any("option OPT-1-A missing required 'render'" in err for err in errors)
    assert any("option OPT-1-B has invalid outcome" in err for err in errors)


def test_validate_catalog_option_accepts_valid_render_and_outcome():
    """A well-formed ev_to_ai option check passes validation."""
    errors = validate_catalog(
        _option_check_catalog(
            [
                {"id": "OPT-1-A", "todo_ref": "TODO-A", "render": "- fine", "outcome": "ok"},
            ]
        )
    )
    assert not any("OPT-1" in err for err in errors)


def test_validate_catalog_real_catalog_options_are_wellformed():
    """The shipped catalog's ev_to_ai option checks all declare render+outcome."""
    tool_root = Path(__file__).resolve().parent.parent
    workspace_root = tool_root.parent.parent

    loaded = load_catalog_for_role(tool_root, workspace_root, "review")
    assert validate_catalog(loaded) == []


def test_validate_catalog_human_only_placeholder_validation():
    """A human-only check's TODO template must include the {title} placeholder."""
    catalog = {
        "metadata": {},
        "global_policies": {},
        "evidence_adapters": [{"id": "lp-bug-api", "type": "api", "description": "d"}],
        "checks": [
            {
                "id": "HUM-1",
                "section": "Common blockers",
                "title": "Some human-only judgment",
                "mode": "human_only",
                "adapters_required": ["lp-bug-api"],
                "messages": {
                    "human_only_message": "Human review required",
                    "human_only_todo": "TODO: reviewer judgment needed",
                },
            }
        ],
    }

    errors = validate_catalog(catalog)
    assert any("messages.human_only_todo missing placeholders" in err for err in errors)
