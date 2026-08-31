"""Catalog loading helpers for auto-mir."""

from __future__ import annotations

import re
import string
import sys
from pathlib import Path
from typing import Any

from utils.dependencies import ubuntu_package_for

# Opt-in tag on a blueprint ``RULE:`` line that starts a new, individually
# tracked policy clause: ``RULE[<slug>]: <text>``. The tag is a machine-
# readable coverage annotation ONLY - it must never appear in rendered docs
# or reporter-facing rule_context text, so every consumer normalizes it back
# to plain ``RULE:`` via ``strip_rule_clause_tag`` before using the line for
# anything other than clause-slug discovery.
_RULE_CLAUSE_TAG_PATTERN = re.compile(r"^RULE\[[a-z][a-z0-9_-]*\]:")


def strip_rule_clause_tag(line: str) -> str:
    """Normalize a possibly-tagged ``RULE[<slug>]:`` line back to plain ``RULE:``.

    A following plain ``RULE:`` continuation line is returned unchanged. Every
    consumer of blueprint RULE text (rendering, rule_context auto-derivation,
    the drift guard) must call this first so the tag never leaks into
    anything a reporter/reviewer actually reads.
    """
    return _RULE_CLAUSE_TAG_PATTERN.sub("RULE:", line, count=1)


def _blueprint_section_rules(blueprint: Any) -> dict[str, list[str]]:
    """Return each reporter template section's ``RULE:`` lines, keyed by section.

        ``metadata.reporter_template_blueprint`` already interleaves ``'[Section]'``
        markers, ``'RULE: ...'`` policy lines, and ``item: REP-XXX`` entries in the
    exact order the rendered template uses. RULE prose can appear anywhere in
        a section (the historical template interleaves rules and TODO lines), so
        this is the existing, single source of truth for which policy rules apply
        to which items - no separate copy of the policy text needs to be authored
        per item.
    """
    section_rules: dict[str, list[str]] = {}
    current_section: str | None = None
    if not isinstance(blueprint, list):
        return section_rules
    for entry in blueprint:
        if isinstance(entry, str):
            stripped = entry.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                current_section = stripped[1:-1]
                section_rules.setdefault(current_section, [])
            elif stripped.startswith(("RULE:", "RULE[")) and current_section:
                section_rules[current_section].append(strip_rule_clause_tag(stripped))
    return section_rules


def _apply_reporter_rule_context_defaults(catalog: dict) -> None:
    """Auto-populate ``rule_context`` for items that don't already set one.

    Every ``human_only``/``ev_to_ai`` item without an explicit ``rule_context``
    gets its section's blueprint ``RULE:`` line(s) plus its own ``template``
    (the ``TODO: ...`` placeholder it resolves) joined together, so the
    reporter sees both WHY (policy) and WHAT (what this item resolves) without
    any hand-duplicated text. Items that already declare ``rule_context`` are
    left untouched.
    """
    blueprint = catalog.get("metadata", {}).get("reporter_template_blueprint")
    section_rules = _blueprint_section_rules(blueprint)
    for item in catalog.get("items", []):
        if not isinstance(item, dict) or item.get("mode") not in {"human_only", "ev_to_ai"}:
            continue
        if str(item.get("rule_context", "")).strip():
            continue
        rules = section_rules.get(str(item.get("section", "")), [])
        if not rules:
            continue
        lines = list(rules)
        template = str(item.get("template", "")).strip()
        if template:
            lines.append(template)
        item["rule_context"] = "\n".join(lines)


# Opt-in tag on a blueprint ``RULE:`` line that starts a new, individually
# tracked policy clause: ``RULE[<slug>]: <text>``. A plain ``RULE:`` line
# (no bracket) continues attaching to the most recently opened clause, exactly
# like the existing untagged multi-line RULE blocks already render - so
# tagging a clause never changes the rendered include-file output, only adds
# a coverage contract checked at catalog-load time. Clauses are opt-in on
# purpose: only policy statements the maintainers actively want to guarantee
# have a covering item need a slug; untagged RULE prose remains ordinary,
# unchecked context text.
_RULE_CLAUSE_PATTERN = re.compile(r"^RULE\[(?P<slug>[a-z][a-z0-9_-]*)\]:.*$")


def _blueprint_rule_clause_slugs(blueprint: Any) -> list[str]:
    """Return every ``RULE[<slug>]:`` identifier declared in a template blueprint.

    Order is preserved and duplicates are NOT deduplicated here - the caller
    decides how to report a duplicate slug as a validation error.
    """
    slugs: list[str] = []
    if not isinstance(blueprint, list):
        return slugs
    for entry in blueprint:
        if not isinstance(entry, str):
            continue
        match = _RULE_CLAUSE_PATTERN.match(entry.strip())
        if match:
            slugs.append(match.group("slug"))
    return slugs


def _validate_rule_clause_coverage(
    catalog: dict,
    blueprint_key: str,
    items: list,
    item_field: str = "covers_rule_clauses",
) -> list[str]:
    """Validate that every tagged ``RULE[<slug>]:`` clause has a covering item.

    Fails if: a slug is declared more than once in the blueprint, an item's
    ``covers_rule_clauses`` references a slug that was never declared, or a
    declared slug has zero covering items. This is the real, structural
    "does the catalog map to the rendered content" contract - unlike a
    frozen historic-template fixture, it is entirely self-contained in the
    catalog files and evolves naturally as RULE lines and items change.
    """
    errors: list[str] = []
    blueprint = catalog.get("metadata", {}).get(blueprint_key)
    slugs = _blueprint_rule_clause_slugs(blueprint)

    seen: set[str] = set()
    duplicates: set[str] = set()
    for slug in slugs:
        if slug in seen:
            duplicates.add(slug)
        seen.add(slug)
    for slug in sorted(duplicates):
        errors.append(f"{blueprint_key} declares RULE[{slug}] more than once")

    declared_slugs = set(slugs)
    covering: dict[str, list[str]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", "?"))
        refs = item.get(item_field)
        if refs is None:
            continue
        if not isinstance(refs, list):
            errors.append(f"{item_id}: {item_field} must be a list")
            continue
        for slug in refs:
            if slug not in declared_slugs:
                errors.append(f"{item_id}: {item_field} references unknown RULE clause: {slug}")
                continue
            covering.setdefault(slug, []).append(item_id)

    uncovered = sorted(declared_slugs - covering.keys())
    for slug in uncovered:
        errors.append(f"RULE[{slug}] in {blueprint_key} has no covering item ({item_field})")

    return errors


def _load_yaml_strict(handle: Any, yaml_module: Any) -> dict:
    """Load one YAML mapping while rejecting duplicate keys.

    PyYAML's default safe loader silently keeps the last value for duplicate
    mapping keys. Catalog keys are policy and runtime configuration, so a
    duplicate must fail with its source location instead of shadowing data.
    """

    class StrictSafeLoader(yaml_module.SafeLoader):
        pass

    def construct_mapping(loader: Any, node: Any, deep: bool = False) -> dict:
        loader.flatten_mapping(node)
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError as exc:
                raise yaml_module.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found an unhashable mapping key",
                    key_node.start_mark,
                ) from exc
            if duplicate:
                raise yaml_module.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping

    StrictSafeLoader.add_constructor(
        yaml_module.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping,
    )
    loaded = yaml_module.load(handle, Loader=StrictSafeLoader)
    if not isinstance(loaded, dict):
        raise yaml_module.constructor.ConstructorError(
            None,
            None,
            "catalog root must be a mapping",
            None,
        )
    return loaded


def load_catalog(catalog_path: Path, workspace_root: Path) -> dict:
    """Load a complete, standalone catalog YAML file and return its structure.

    The file must carry every section ``validate_catalog`` requires (this is
    the contract used for ad-hoc/synthetic full catalogs and CLI overrides;
    role-composed loading goes through ``load_catalog_for_role`` instead). The
    host CLI depends on YAML parsing, so emit a precise error if PyYAML is
    missing rather than failing later during analysis.
    """
    try:
        import yaml
    except ImportError:
        package = ubuntu_package_for("pyyaml")
        print(
            f"auto-mir requires PyYAML on the host. Install it with: sudo apt install {package}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        with catalog_path.open("r", encoding="utf-8") as handle:
            loaded = _load_yaml_strict(handle, yaml)
    except yaml.YAMLError as exc:
        print(f"Catalog YAML error in {catalog_path}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    # Validate catalog structure
    errors = validate_catalog(loaded)
    if errors:
        print("Catalog validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        raise SystemExit(1)

    return loaded


def _load_yaml_path(path: Path) -> dict:
    """Strictly load one YAML mapping with the host dependency diagnostic."""
    try:
        import yaml
    except ImportError:
        package = ubuntu_package_for("pyyaml")
        print(
            f"auto-mir requires PyYAML on the host. Install it with: sudo apt install {package}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        with path.open("r", encoding="utf-8") as handle:
            return _load_yaml_strict(handle, yaml)
    except (OSError, yaml.YAMLError) as exc:
        print(f"Catalog YAML error in {path}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


# Top-level sections catalog.yaml (the shared file) is allowed to hold. Both
# role catalogs merge these in; anything else appearing in catalog.yaml would
# silently leak into both roles, so loading rejects unexpected sections there.
_SHARED_SECTIONS = ("global_policies", "evidence_adapters")

# Role-only catalog file holding each role's real content directly (checks and
# reviewer-template blueprint for "review"; items and reporter-template
# blueprint for "report").
_ROLE_CATALOG_FILENAMES = {
    "review": "catalog-mir-review.yaml",
    "report": "catalog-mir-report.yaml",
}


def load_catalog_for_role(tool_root: Path, workspace_root: Path, role: str) -> dict:
    """Load the composed catalog view for ``review`` or ``report``.

    Both roles are assembled the same way: the shared sections declared in
    ``catalog.yaml`` (confidence model, evidence adapters) are merged with the
    role-only content declared directly in ``catalog-mir-review.yaml`` or
    ``catalog-mir-report.yaml``. Neither side may override the other's keys.
    """
    role_filename = _ROLE_CATALOG_FILENAMES.get(role)
    if role_filename is None:
        print(f"Unknown catalog role: {role}", file=sys.stderr)
        raise SystemExit(1)

    shared = _load_yaml_path(tool_root / "catalog.yaml")
    unexpected = sorted(set(shared) - set(_SHARED_SECTIONS))
    if unexpected:
        print(
            "catalog.yaml must only hold shared sections; found unexpected: "
            + ", ".join(unexpected),
            file=sys.stderr,
        )
        raise SystemExit(1)

    role_only = _load_yaml_path(tool_root / role_filename)
    if role_only.get("role") != role:
        print(
            f"Invalid {role} catalog composition: {role_filename} must declare role: {role}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    composed = {section: shared[section] for section in _SHARED_SECTIONS if section in shared}
    for key, value in role_only.items():
        if key in composed:
            print(
                f"{role} catalog attempts to override shared section: {key}",
                file=sys.stderr,
            )
            raise SystemExit(1)
        composed[key] = value

    errors = validate_catalog(composed) if role == "review" else validate_report_catalog(composed)
    if errors:
        print(f"{role.capitalize()} catalog validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        raise SystemExit(1)
    if role == "report":
        _apply_reporter_rule_context_defaults(composed)
    return composed


def validate_report_catalog(catalog: dict) -> list[str]:
    """Validate the reporter item and blueprint contract."""
    errors: list[str] = []
    if catalog.get("role") != "report":
        errors.append("reporter catalog role must be 'report'")
    items = catalog.get("items")
    if not isinstance(items, list) or not items:
        return [*errors, "reporter catalog items must be a non-empty list"]

    item_ids: set[str] = set()
    adapter_ids = {
        adapter.get("id")
        for adapter in catalog.get("evidence_adapters", [])
        if isinstance(adapter, dict)
    }
    valid_modes = {"deterministic", "human_only", "ev_to_ai"}
    valid_readiness = {"clear", "warning", "blocker"}
    conditions_by_item: dict[str, dict | None] = {}
    option_conditions: list[tuple[str, dict]] = []
    section_rules = _blueprint_section_rules(
        catalog.get("metadata", {}).get("reporter_template_blueprint")
    )
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"reporter item {index} must be a mapping")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"reporter item {index} missing id")
            continue
        if item_id in item_ids:
            errors.append(f"duplicate reporter item id: {item_id}")
        item_ids.add(item_id)
        conditions_by_item[item_id] = item.get("applicability")
        for field in ("section", "title", "mode", "template"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"reporter item {item_id} missing {field}")
        template = item.get("template")
        # A single free-text answer can only fill one TBD slot; branch-tree
        # templates (single_choice, deterministic) are exempt because their
        # answers resolve via option statements or evaluator output, not via
        # TBD substitution into the template.
        question_kind = (
            (item.get("question") or {}).get("kind")
            if isinstance(item.get("question"), dict)
            else None
        )
        if (
            question_kind in {"text", "multiline"}
            and isinstance(template, str)
            and template.replace("TBDSRC", "").count("TBD") > 1
        ):
            errors.append(
                f"reporter item {item_id} template must contain at most one 'TBD' "
                "placeholder (a single free-text answer can only fill one slot; a "
                "second 'TBD' silently stays unfilled in the rendered statement)"
            )
        if item.get("mode") not in valid_modes:
            errors.append(f"reporter item {item_id} has invalid mode: {item.get('mode')}")
        if item.get("readiness", "clear") not in valid_readiness:
            errors.append(f"reporter item {item_id} has invalid readiness")
        for context_field in ("rule_context", "answer_guidance", "preface_evaluator"):
            if context_field in item and not isinstance(item[context_field], str):
                errors.append(f"reporter item {item_id} {context_field} must be a string")
        explicit_rule_context = item.get("rule_context")
        if isinstance(explicit_rule_context, str) and explicit_rule_context.strip():
            allowed_rules = set(section_rules.get(str(item.get("section", "")), []))
            for line in explicit_rule_context.splitlines():
                stripped_line = line.strip()
                if stripped_line.startswith("RULE:") and stripped_line not in allowed_rules:
                    errors.append(
                        f"reporter item {item_id} rule_context line does not match any "
                        f"blueprint RULE for section [{item.get('section', '')}]: "
                        f"{stripped_line!r} (hand-authored rule_context must stay a verbatim "
                        "copy of a blueprint RULE line, or be removed so it is auto-derived)"
                    )
        if item.get("mode") in {"human_only", "ev_to_ai"} and not isinstance(
            item.get("question"), dict
        ):
            errors.append(f"interactive reporter item {item_id} requires a question")
        if item.get("mode") == "ev_to_ai" and not str(item.get("ai_policy", "")).strip():
            errors.append(f"AI reporter item {item_id} requires ai_policy")
        if "autopkgtest_log_followup" in item and not isinstance(
            item["autopkgtest_log_followup"], bool
        ):
            errors.append(f"reporter item {item_id} autopkgtest_log_followup must be a bool")
        question = item.get("question", {})
        options = question.get("options", []) if isinstance(question, dict) else []
        if options:
            option_ids: set[str] = set()
            for option in options:
                option_id = option.get("id") if isinstance(option, dict) else None
                if not isinstance(option_id, str) or not option_id:
                    errors.append(f"reporter item {item_id} has option without id")
                    continue
                if option_id in option_ids:
                    errors.append(f"reporter item {item_id} repeats option: {option_id}")
                option_ids.add(option_id)
                if not str(option.get("label", "")).strip():
                    errors.append(f"reporter item {item_id} option {option_id} missing label")
                if not str(option.get("statement", "")).strip():
                    errors.append(f"reporter item {item_id} option {option_id} missing statement")
                if "exclusive" in option and not isinstance(option["exclusive"], bool):
                    errors.append(
                        f"reporter item {item_id} option {option_id} exclusive must be a bool"
                    )
                for optional_text_field in ("todo_ref", "ai_predicate"):
                    if optional_text_field in option and not isinstance(
                        option[optional_text_field], str
                    ):
                        errors.append(
                            f"reporter item {item_id} option {option_id} {optional_text_field} "
                            "must be a string"
                        )
                if "readiness" in option and option["readiness"] not in valid_readiness:
                    errors.append(
                        f"reporter item {item_id} option {option_id} has invalid readiness"
                    )
                if "spell_out_filter" in option and option["spell_out_filter"] not in {
                    "all",
                    "exclude_dev_doc_dbg",
                    "list_only",
                }:
                    errors.append(
                        f"reporter item {item_id} option {option_id} spell_out_filter must be "
                        "'all', 'exclude_dev_doc_dbg', or 'list_only'"
                    )
                unavailable_if = option.get("unavailable_if")
                unavailable_reason = option.get("unavailable_reason")
                if unavailable_if is not None and not isinstance(unavailable_if, dict):
                    errors.append(
                        f"reporter item {item_id} option {option_id} unavailable_if must be a "
                        "mapping"
                    )
                elif unavailable_if is not None:
                    option_conditions.append((f"{item_id}.{option_id}", unavailable_if))
                if unavailable_if is not None and not str(unavailable_reason or "").strip():
                    errors.append(
                        f"reporter item {item_id} option {option_id} declares unavailable_if "
                        "without an unavailable_reason"
                    )
                if unavailable_reason is not None and unavailable_if is None:
                    errors.append(
                        f"reporter item {item_id} option {option_id} declares "
                        "unavailable_reason without an unavailable_if"
                    )
        options_source = question.get("options_source") if isinstance(question, dict) else None
        _validate_adapter_field_ref(item_id, "options_source", options_source, adapter_ids, errors)
        default_source = question.get("default_source") if isinstance(question, dict) else None
        _validate_adapter_field_ref(item_id, "default_source", default_source, adapter_ids, errors)
        _validate_adapter_field_ref(
            item_id, "writes_evidence", item.get("writes_evidence"), adapter_ids, errors
        )
        if item.get("mode") == "deterministic" and not item.get("evaluator"):
            errors.append(f"deterministic reporter item {item_id} requires an evaluator")
        for adapter_field in ("adapters_required", "adapters_optional"):
            references = item.get(adapter_field, [])
            if not isinstance(references, list):
                errors.append(f"reporter item {item_id} {adapter_field} must be a list")
                continue
            for adapter_id in references:
                if adapter_id not in adapter_ids:
                    errors.append(
                        f"reporter item {item_id} references unknown adapter: {adapter_id}"
                    )

    blueprint = catalog.get("metadata", {}).get("reporter_template_blueprint")
    if not isinstance(blueprint, list) or not blueprint:
        errors.append("reporter template blueprint must be a non-empty list")
    else:
        referenced: set[str] = set()
        for entry in blueprint:
            if isinstance(entry, dict):
                item_id = entry.get("item")
                if item_id not in item_ids:
                    errors.append(f"reporter blueprint references unknown item: {item_id}")
                elif item_id in referenced:
                    errors.append(f"reporter blueprint repeats item: {item_id}")
                referenced.add(item_id)
    from reporter.conditions import (
        condition_references,
        validate_condition_cycles,
        validate_condition_references,
    )

    for item_id, condition in conditions_by_item.items():
        errors.extend(
            f"reporter item {item_id}: {error}"
            for error in validate_condition_references(
                condition,
                known_items=item_ids,
                known_adapters={str(adapter_id) for adapter_id in adapter_ids if adapter_id},
            )
        )
    errors.extend(validate_condition_cycles(conditions_by_item))
    known_adapter_ids = {str(adapter_id) for adapter_id in adapter_ids if adapter_id}
    for label, condition in option_conditions:
        errors.extend(
            f"reporter option {label}: {error}"
            for error in validate_condition_references(
                condition, known_items=item_ids, known_adapters=known_adapter_ids
            )
        )
        if any(reference_type == "item" for reference_type, _ in condition_references(condition)):
            errors.append(
                f"reporter option {label} unavailable_if must only reference evidence, "
                "not other items (options are locked before any item answers exist)"
            )
    errors.extend(_validate_rule_clause_coverage(catalog, "reporter_template_blueprint", items))
    return errors


def _validate_adapter_field_ref(
    item_id: str, label: str, ref: Any, adapter_ids: set[str], errors: list[str]
) -> None:
    """Validate one optional ``{adapter, field}`` evidence reference.

    Shared by ``options_source``, ``default_source``, and ``writes_evidence``,
    which all point a reporter item at one field of one evidence adapter.
    """
    if ref is None:
        return
    valid_source = (
        isinstance(ref, dict)
        and isinstance(ref.get("adapter"), str)
        and isinstance(ref.get("field"), str)
    )
    if not valid_source:
        errors.append(f"reporter item {item_id} {label} must define adapter and field strings")
        return
    if ref["adapter"] not in adapter_ids:
        errors.append(
            f"reporter item {item_id} {label} references unknown adapter: {ref['adapter']}"
        )


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
        "unknown_no_lp_message": set(),
        "unknown_no_lp_todo": set(),
        "unknown_no_builds_message": set(),
        "unknown_no_builds_todo": set(),
        "not_ok_message": {"failed_builds"},
        "not_ok_todo": set(),
        "ok_message": {"passing_arches"},
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
        "ok_same_request_message": {"auto_included", "same_request_deps"},
    },
    "PRF-2": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_message": set(),
        "ok_no_shared_message": set(),
        "not_ok_message": set(),
        "not_ok_todo": set(),
    },
    "PRF-3": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_message": set(),
        "ok_native_message": set(),
        "not_ok_message": set(),
        "not_ok_todo": set(),
    },
    "PRF-6": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "ok_message": set(),
        "very_behind_message": {"archive", "upstream"},
        "somewhat_behind_message": {"archive", "upstream"},
        "behind_todo": set(),
        "version_lag_message": {"archive", "upstream"},
        "unknown_lag_message": set(),
        "version_lag_todo": set(),
    },
    "PRF-8": {
        "unknown_message": set(),
        "not_ok_errors_message": {"errors"},
        "not_ok_errors_todo": set(),
        "not_ok_many_message": {"count"},
        "not_ok_many_todo": set(),
        "minor_message": {"count"},
        "minor_todo": {"count"},
        "ok_message": set(),
    },
    "URF-1": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "not_ok_errors_message": {"errors"},
        "not_ok_errors_todo": set(),
        "warnings_message": {"count", "sample"},
        "warnings_todo": set(),
        "warnings_rationale": {"count", "sample"},
        "ok_message": set(),
    },
    "URF-3": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "not_ok_message": set(),
        "not_ok_todo": set(),
        "ok_message": set(),
    },
    "URF-4": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "not_ok_message": {"hits"},
        "not_ok_todo": set(),
        "ok_message": set(),
    },
    "URF-5": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "source_binaries": {"files"},
        "source_lintian": set(),
        "source_tree": {"hits"},
        "source_rules": set(),
        "systemd_message": {"source"},
        "systemd_todo": set(),
        "not_ok_message": {"source"},
        "not_ok_todo": set(),
        "ok_message": set(),
    },
    "URF-7": {
        "unknown_message": set(),
        "unknown_todo": set(),
        "not_ok_message": {"dep"},
        "not_ok_todo": set(),
        "ok_message": set(),
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

    # A negated_statement (used by the renderer to phrase a confirmed problem,
    # e.g. "does FTBFS currently") must be a non-empty string when present.
    negated = check.get("negated_statement")
    if negated is not None and not (isinstance(negated, str) and negated.strip()):
        errors.append(f"Check {check_id}: negated_statement must be a non-empty string")


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
        _validate_check_options(check, i, errors)

    return errors


# Outcomes an option can resolve to. "ok" renders as an OK statement with no
# TODO; the others render as TODO/Problem lines at the matching severity.
_VALID_OPTION_OUTCOMES = {"ok", "recommended", "required", "nack"}


def _validate_check_options(check: dict, index: int, errors: list[str]) -> None:
    """Validate option lists for AI-evaluated option checks.

    ev_to_ai/ai checks that expose ``options`` are wired so the model selects
    one option id and the renderer emits that option's canonical ``render``
    statement at the ``outcome`` severity. To keep the output template-faithful
    (rather than free-form model prose) every such option must declare both a
    ``render`` string and a valid ``outcome``. Summary-section decision checks
    (ACK/NACK verdict, security review) keep all variants visible and are exempt.
    Deterministic option checks render via their ``messages`` map and are exempt.
    """
    options = check.get("options")
    if not options:
        return
    check_id = str(check.get("id", index))
    if check.get("mode") not in {"ev_to_ai", "ai"}:
        return
    if check.get("section") == "Summary":
        return
    if not isinstance(options, list):
        errors.append(f"Check {check_id}: options must be a list")
        return
    for opt in options:
        if not isinstance(opt, dict):
            errors.append(f"Check {check_id}: each option must be a mapping")
            continue
        opt_id = opt.get("id", "?")
        if not opt.get("render"):
            errors.append(f"Check {check_id}: option {opt_id} missing required 'render' statement")
        outcome = opt.get("outcome")
        if outcome not in _VALID_OPTION_OUTCOMES:
            errors.append(
                f"Check {check_id}: option {opt_id} has invalid outcome '{outcome}'. "
                f"Must be one of: {', '.join(sorted(_VALID_OPTION_OUTCOMES))}"
            )


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
    errors.extend(
        _validate_rule_clause_coverage(
            catalog, "review_template_blueprint", catalog.get("checks", [])
        )
    )

    return errors


def summarize_catalog(loaded: dict) -> dict:
    """Return lightweight counts that are useful in evidence and debug output."""
    checks = loaded.get("checks", loaded.get("items", []))
    section_counts = {}
    for check in checks:
        section = check.get("section", "unknown")
        section_counts[section] = section_counts.get(section, 0) + 1

    return {
        "check_count": len(checks),
        "item_count": len(loaded.get("items", [])),
        "security_trigger_count": len(loaded.get("security_triggers", [])),
        "sections": section_counts,
    }
