"""Catalog loading helpers for auto-mir."""

from __future__ import annotations

import sys
from pathlib import Path


def load_catalog(catalog_path: Path, workspace_root: Path) -> dict:
    """Load catalog.yaml and return the parsed structure.

    The host CLI depends on YAML parsing, so emit a precise error if PyYAML is
    missing rather than failing later during analysis.
    """
    try:
        import yaml
    except ImportError:
        print(
            "auto-mir requires PyYAML on the host. Install it with: sudo apt install python3-yaml",
            file=sys.stderr,
        )
        raise SystemExit(1)

    with catalog_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)

    # Validate catalog structure
    errors = validate_catalog(loaded)
    if errors:
        print("Catalog validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        raise SystemExit(1)

    return loaded


def validate_catalog(catalog: dict) -> list[str]:
    """Validate catalog structure and return list of errors.
    
    Args:
        catalog: Parsed catalog dictionary
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check required top-level sections
    required_sections = {"metadata", "global_policies", "checks", "evidence_adapters"}
    for section in required_sections:
        if section not in catalog:
            errors.append(f"Missing required section: {section}")
    
    # Validate checks
    checks = catalog.get("checks", [])
    if not isinstance(checks, list):
        errors.append("'checks' must be a list")
    else:
        check_ids = set()
        for i, check in enumerate(checks):
            if not isinstance(check, dict):
                errors.append(f"Check {i} is not a dictionary")
                continue
            
            # Required fields
            required_fields = {"id", "section", "title", "mode"}
            for field in required_fields:
                if field not in check:
                    errors.append(f"Check {i} missing required field: {field}")
            
            # Validate mode
            if "mode" in check:
                valid_modes = {"deterministic", "ev_to_ai", "ai", "human_only"}
                if check["mode"] not in valid_modes:
                    errors.append(
                        f"Check {check.get('id', i)} has invalid mode: {check['mode']}. "
                        f"Must be one of: {', '.join(sorted(valid_modes))}"
                    )
            
            # Validate blocker_class if present
            if "blocker_class" in check:
                valid_blockers = {"hard", "soft", "none"}
                if check["blocker_class"] not in valid_blockers:
                    errors.append(
                        f"Check {check.get('id', i)} has invalid blocker_class: "
                        f"{check['blocker_class']}. Must be one of: {', '.join(sorted(valid_blockers))}"
                    )
            
            # Check for duplicate IDs
            if "id" in check:
                if check["id"] in check_ids:
                    errors.append(f"Duplicate check ID: {check['id']}")
                check_ids.add(check["id"])
            
            # Validate adapters_required if present
            if "adapters_required" in check:
                if not isinstance(check["adapters_required"], list):
                    errors.append(
                        f"Check {check.get('id', i)}: adapters_required must be a list"
                    )
    
    # Validate evidence_adapters
    adapters = catalog.get("evidence_adapters", [])
    if not isinstance(adapters, list):
        errors.append("'evidence_adapters' must be a list")
    else:
        adapter_ids = set()
        for i, adapter in enumerate(adapters):
            if not isinstance(adapter, dict):
                errors.append(f"Adapter {i} is not a dictionary")
                continue
            
            # Required fields
            required_fields = {"id", "type", "description"}
            for field in required_fields:
                if field not in adapter:
                    errors.append(f"Adapter {i} missing required field: {field}")
            
            # Validate type
            if "type" in adapter:
                valid_types = {"api", "web", "local_exec", "heuristic"}
                if adapter["type"] not in valid_types:
                    errors.append(
                        f"Adapter {adapter.get('id', i)} has invalid type: {adapter['type']}. "
                        f"Must be one of: {', '.join(sorted(valid_types))}"
                    )
            
            # Check for duplicate IDs
            if "id" in adapter:
                if adapter["id"] in adapter_ids:
                    errors.append(f"Duplicate adapter ID: {adapter['id']}")
                adapter_ids.add(adapter["id"])
    
    # Validate that all referenced adapters exist
    if isinstance(checks, list) and isinstance(adapters, list):
        defined_adapters = {a.get("id") for a in adapters if isinstance(a, dict) and "id" in a}
        for check in checks:
            if not isinstance(check, dict):
                continue
            for adapter_list_field in ["adapters_required", "adapters_optional"]:
                if adapter_list_field in check and isinstance(check[adapter_list_field], list):
                    for adapter_id in check[adapter_list_field]:
                        if adapter_id not in defined_adapters:
                            errors.append(
                                f"Check {check.get('id', '?')} references undefined adapter: "
                                f"{adapter_id} (in {adapter_list_field})"
                            )
    
    return errors


def validate_catalog(catalog: dict) -> list[str]:
    """Validate catalog structure and return list of errors.
    
    Args:
        catalog: Parsed catalog dictionary
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check required top-level sections
    required_sections = {"metadata", "global_policies", "checks", "evidence_adapters"}
    for section in required_sections:
        if section not in catalog:
            errors.append(f"Missing required section: {section}")
    
    # Validate checks
    checks = catalog.get("checks", [])
    if not isinstance(checks, list):
        errors.append("'checks' must be a list")
    else:
        check_ids = set()
        for i, check in enumerate(checks):
            if not isinstance(check, dict):
                errors.append(f"Check {i} is not a dictionary")
                continue
            
            # Required fields
            required_fields = {"id", "section", "title", "mode"}
            for field in required_fields:
                if field not in check:
                    errors.append(f"Check {i} missing required field: {field}")
            
            # Validate mode
            if "mode" in check:
                valid_modes = {"deterministic", "ev_to_ai", "ai", "human_only"}
                if check["mode"] not in valid_modes:
                    errors.append(
                        f"Check {check.get('id', i)} has invalid mode: {check['mode']}. "
                        f"Must be one of: {', '.join(sorted(valid_modes))}"
                    )
            
            # Validate blocker_class if present
            if "blocker_class" in check:
                valid_blockers = {"hard", "soft", "none"}
                if check["blocker_class"] not in valid_blockers:
                    errors.append(
                        f"Check {check.get('id', i)} has invalid blocker_class: "
                        f"{check['blocker_class']}. Must be one of: {', '.join(sorted(valid_blockers))}"
                    )
            
            # Check for duplicate IDs
            if "id" in check:
                if check["id"] in check_ids:
                    errors.append(f"Duplicate check ID: {check['id']}")
                check_ids.add(check["id"])
            
            # Validate adapters_required if present
            if "adapters_required" in check:
                if not isinstance(check["adapters_required"], list):
                    errors.append(
                        f"Check {check.get('id', i)}: adapters_required must be a list"
                    )
    
    # Validate evidence_adapters
    adapters = catalog.get("evidence_adapters", [])
    if not isinstance(adapters, list):
        errors.append("'evidence_adapters' must be a list")
    else:
        adapter_ids = set()
        for i, adapter in enumerate(adapters):
            if not isinstance(adapter, dict):
                errors.append(f"Adapter {i} is not a dictionary")
                continue
            
            # Required fields
            required_fields = {"id", "type", "description"}
            for field in required_fields:
                if field not in adapter:
                    errors.append(f"Adapter {i} missing required field: {field}")
            
            # Validate type
            if "type" in adapter:
                valid_types = {"api", "web", "local_exec", "heuristic"}
                if adapter["type"] not in valid_types:
                    errors.append(
                        f"Adapter {adapter.get('id', i)} has invalid type: {adapter['type']}. "
                        f"Must be one of: {', '.join(sorted(valid_types))}"
                    )
            
            # Check for duplicate IDs
            if "id" in adapter:
                if adapter["id"] in adapter_ids:
                    errors.append(f"Duplicate adapter ID: {adapter['id']}")
                adapter_ids.add(adapter["id"])
    
    # Validate that all referenced adapters exist
    if isinstance(checks, list) and isinstance(adapters, list):
        defined_adapters = {a.get("id") for a in adapters if isinstance(a, dict) and "id" in a}
        for check in checks:
            if not isinstance(check, dict):
                continue
            for adapter_list_field in ["adapters_required", "adapters_optional"]:
                if adapter_list_field in check and isinstance(check[adapter_list_field], list):
                    for adapter_id in check[adapter_list_field]:
                        if adapter_id not in defined_adapters:
                            errors.append(
                                f"Check {check.get('id', '?')} references undefined adapter: "
                                f"{adapter_id} (in {adapter_list_field})"
                            )
    
    return errors


def summarize_catalog(loaded: dict) -> dict:
    """Return lightweight counts that are useful in evidence and debug output."""
    checks = loaded.get("checks", [])
    section_counts = {}
    for check in checks:
        section = check.get("section", "unknown")
        section_counts[section] = section_counts.get(section, 0) + 1

    return {
        "check_count": len(checks),
        "security_trigger_count": len(loaded.get("security_triggers", [])),
        "sections": section_counts,
    }
