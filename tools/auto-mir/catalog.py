"""Catalog loading helpers for auto-mir."""

from __future__ import annotations

import string
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


# Check-level messages required for migrated checks.
# Placeholder sets are strict minima for each template key.
_REQUIRED_MESSAGE_TEMPLATES: dict[str, dict[str, set[str]]] = {
    "SUM-1": {
        "ok_message": {"source_package"},
        "not_ok_message": set(),
        "not_ok_todo": set(),
    },
    "SUM-2": {
        "ok_message": set(),
        "nack_message": set(),
        "nack_todo": set(),
    },
    "SUM-4": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_message": {"subscribed_teams"},
        "not_ok_message": set(),
        "not_ok_todo": set(),
    },
    "DEP-1": {
        "unknown_adapter_message": set(),
        "unknown_adapter_todo": set(),
        "not_ok_message": {"deps"},
        "not_ok_todo": {"deps"},
        "ok_message": set(),
    },
    "SEC-3": {
        "ok_message": set(),
        "unknown_message": set(),
        "blocker_message": {"dep"},
        "blocker_todo": set(),
    },
    "SEC-4": {
        "ok_message": set(),
        "unknown_message": set(),
        "blocker_message": {"dep"},
        "blocker_todo": set(),
    },
    "CB-7": {
        "ok_message": set(),
        "unknown_message": set(),
        "blocker_message": {"dep"},
        "blocker_todo": set(),
    },
    "CB-1": {
        "hint_local_ok": set(),
        "hint_local_failed": set(),
        "hint_local_unavailable": set(),
        "unknown_no_lp_message": {"local_hint"},
        "unknown_no_lp_todo": {"local_hint"},
        "unknown_no_builds_message": {"local_hint"},
        "unknown_no_builds_todo": {"local_hint"},
        "not_ok_message": {"failed_builds"},
        "not_ok_todo": set(),
        "ok_message": {"passing_arches"},
        "ok_local_suffix": set(),
    },
    "CB-8": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_not_python_message": set(),
        "ok_message": set(),
        "not_ok_message": set(),
        "not_ok_todo": set(),
    },
    "SEC-2": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "mitigated_message": set(),
        "mitigated_todo": set(),
        "not_ok_message": set(),
        "not_ok_todo": set(),
        "ok_message": set(),
    },
    "SEC-8": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "not_ok_dep_message": {"dep"},
        "not_ok_source_message": {"pattern"},
        "not_ok_todo": set(),
        "ok_message": set(),
    },
    "SEC-10": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "not_ok_dev_message": {"dep"},
        "not_ok_runtime_message": {"dep"},
        "not_ok_todo": set(),
        "ok_message": set(),
    },
    "ESL-1": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "not_ok_message": {"embedded_dirs"},
        "not_ok_todo": {"embedded_dirs"},
        "ok_built_using_message": set(),
        "ok_message": set(),
        "llm_unavailable_message": {"error"},
    },
    "ESL-2": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_message": set(),
        "ok_justified_message": set(),
        "not_ok_detail_binaries": {"binaries"},
        "not_ok_detail_hints": {"hints"},
        "not_ok_message": {"detail"},
        "not_ok_todo": set(),
    },
    "ESL-3": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_message": set(),
        "ok_toolchain_message": {"entries"},
        "not_ok_message": {"entries"},
        "not_ok_todo": {"entries"},
    },
    "ESL-4": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_go_message": set(),
        "ok_not_go_message": set(),
    },
    "ESL-7": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_not_go_message": set(),
        "ok_shared_message": set(),
        "recommended_message": set(),
        "recommended_todo": set(),
        "unknown_build_mode_message": set(),
        "unknown_build_mode_todo": set(),
    },
    "ESL-8": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_rust_message": set(),
        "ok_not_rust_message": set(),
    },
    "ESL-9": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_not_rust_message": set(),
        "ok_message": set(),
        "not_ok_message": set(),
        "not_ok_todo": set(),
    },
    "ESL-10": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_not_rust_message": set(),
        "not_ok_message": {"problems"},
        "not_ok_todo": {"problems"},
        "ok_message": set(),
    },
    "DEP-3": {
        "unknown_packaging_message": set(),
        "unknown_packaging_todo": set(),
        "unknown_dep_analysis_message": set(),
        "unknown_dep_analysis_todo": set(),
        "ok_no_auto_included_message": set(),
        "not_ok_offending_message": {"auto_included", "offending_deps"},
        "not_ok_offending_todo": {"details", "offending_deps"},
        "ok_safe_message": {"auto_included"},
    },
}


def _validate_check_messages(check: dict, index: int, errors: list[str]) -> None:
    """Validate a single check's message templates, appending any errors."""
    # Validate check-level message templates when present
    if "messages" in check:
        if not isinstance(check["messages"], dict):
            errors.append(f"Check {check.get('id', index)}: messages must be a dictionary")
        else:
            for msg_key, msg_template in check["messages"].items():
                if not isinstance(msg_template, str):
                    errors.append(
                        f"Check {check.get('id', index)}: messages.{msg_key} must be a string"
                    )
                    continue
                try:
                    # Parse for basic format string validity.
                    for _literal, _field_name, _fmt, _conv in string.Formatter().parse(
                        msg_template
                    ):
                        pass
                except ValueError as exc:
                    errors.append(
                        f"Check {check.get('id', index)}: messages.{msg_key} format error: {exc}"
                    )

    # Enforce strict templates/placeholders for migrated checks.
    check_id = str(check.get("id", ""))
    mode_required_templates: dict[str, set[str]] = {}
    mode = check.get("mode")
    if mode in {"ev_to_ai", "ai"}:
        mode_required_templates["llm_unavailable_message"] = {"error"}
    elif mode == "human_only":
        mode_required_templates["human_only_message"] = set()
        mode_required_templates["human_only_todo"] = {"title"}

    required_templates = dict(_REQUIRED_MESSAGE_TEMPLATES.get(check_id, {}))
    required_templates.update(mode_required_templates)

    if required_templates:
        messages = check.get("messages")
        if not isinstance(messages, dict):
            errors.append(f"Check {check_id}: missing required messages map")
        else:
            for msg_key, required_fields in required_templates.items():
                template = messages.get(msg_key)
                if not isinstance(template, str):
                    errors.append(
                        f"Check {check_id}: missing required message template '{msg_key}'"
                    )
                    continue
                fields_found = {
                    field_name
                    for _literal, field_name, _fmt, _conv in string.Formatter().parse(template)
                    if field_name
                }
                missing_fields = sorted(required_fields - fields_found)
                if missing_fields:
                    errors.append(
                        f"Check {check_id}: messages.{msg_key} missing placeholders: "
                        + ", ".join(missing_fields)
                    )


def _validate_checks(catalog: dict) -> list[str]:
    """Validate the 'checks' section and return any errors."""
    errors: list[str] = []
    checks = catalog.get("checks", [])
    if not isinstance(checks, list):
        errors.append("'checks' must be a list")
        return errors

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
                    f"{check['blocker_class']}. "
                    f"Must be one of: {', '.join(sorted(valid_blockers))}"
                )

        # Check for duplicate IDs
        if "id" in check:
            if check["id"] in check_ids:
                errors.append(f"Duplicate check ID: {check['id']}")
            check_ids.add(check["id"])

        # Validate adapters_required if present
        if "adapters_required" in check:
            if not isinstance(check["adapters_required"], list):
                errors.append(f"Check {check.get('id', i)}: adapters_required must be a list")

        _validate_check_messages(check, i, errors)

    return errors


def _validate_adapters(catalog: dict) -> list[str]:
    """Validate the 'evidence_adapters' section and return any errors."""
    errors: list[str] = []
    adapters = catalog.get("evidence_adapters", [])
    if not isinstance(adapters, list):
        errors.append("'evidence_adapters' must be a list")
        return errors

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

    return errors


def _validate_adapter_references(catalog: dict) -> list[str]:
    """Validate that all adapters referenced by checks are defined."""
    errors: list[str] = []
    checks = catalog.get("checks", [])
    adapters = catalog.get("evidence_adapters", [])
    if not (isinstance(checks, list) and isinstance(adapters, list)):
        return errors

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
    errors: list[str] = []

    # Check required top-level sections
    required_sections = {"metadata", "global_policies", "checks", "evidence_adapters"}
    for section in required_sections:
        if section not in catalog:
            errors.append(f"Missing required section: {section}")

    errors.extend(_validate_checks(catalog))
    errors.extend(_validate_adapters(catalog))
    errors.extend(_validate_adapter_references(catalog))

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
