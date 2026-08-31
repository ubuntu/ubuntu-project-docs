#!/usr/bin/env python3
"""Render the human MIR template include files from the role catalogs.

One documentation-maintenance script for both roles (not part of the
runtime auto-mir pipeline): it reads the composed role catalog and resolves
``metadata.review_template_blueprint`` / ``metadata.reporter_template_blueprint``
to the plain-text ``.include`` body that ``{literalinclude}`` embeds in the
Sphinx docs. Supported documentation builds run it automatically.

Role vs. the ``render/`` package
---------------------------------
``render_template.py`` (this file)
    Offline utility. Resolves blueprint entries (literal strings, tagged
    RULE lines, item templates, check TODO references) and emits an include
    fragment. Supported documentation builds run it automatically.

``render/__init__.py`` (the runtime renderer)
    Called by the auto-mir pipeline (Stage 5). Takes the findings produced
    by check evaluation and renders a reviewer *draft* ready to post on the
    Launchpad bug. Does NOT use the template blueprints from the catalog.

Both blueprints store body-only content (no fences, no ``:linenos:``, no
page preamble - the hand-written ``docs/MIR/*.md`` pages carry those), so
rendering is uniform: every string entry passes through
``catalog.strip_rule_clause_tag``, every mapping entry is resolved per role.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import catalog

DEFAULT_OUTPUTS = {
    "review": "docs/MIR/mir-reviewers-template-body.include",
    "report": "docs/MIR/mir-reporters-template-body.include",
}
BLUEPRINT_KEYS = {
    "review": "review_template_blueprint",
    "report": "reporter_template_blueprint",
}


def _resolve_item(entry: Any, items: dict[str, dict]) -> str:
    item_id = entry["item"]
    if item_id not in items:
        raise RuntimeError(f"Reporter blueprint references unknown item: {item_id}")
    return str(items[item_id]["template"])


def _resolve_check_ref(entry: Any, checks: dict[str, dict[str, Any]]) -> str:
    check_id = str(entry.get("check") or "")
    todo_ref_idx = entry.get("todo_ref")
    if not check_id or not isinstance(todo_ref_idx, int):
        raise RuntimeError(f"Invalid check-ref blueprint item: {entry!r}")

    check = checks.get(check_id)
    if not check:
        raise RuntimeError(f"Blueprint references unknown check id: {check_id}")

    refs = check.get("todo_refs", [])
    if not isinstance(refs, list) or todo_ref_idx < 0 or todo_ref_idx >= len(refs):
        raise RuntimeError(
            f"Blueprint todo_ref index out of range for check {check_id}: {todo_ref_idx}"
        )

    ref_text = str(refs[todo_ref_idx])
    if not ref_text.startswith("TODO"):
        raise RuntimeError(
            f"Blueprint todo_ref points to non-TODO entry for check {check_id}: {ref_text!r}"
        )
    return ref_text


def render_template(catalog_data: dict, role: str) -> str:
    """Resolve a role blueprint to a plain-text literalinclude body."""
    blueprint_key = BLUEPRINT_KEYS[role]
    blueprint = catalog_data.get("metadata", {}).get(blueprint_key)
    if not isinstance(blueprint, list) or not blueprint:
        raise RuntimeError(f"{role} catalog is missing metadata.{blueprint_key}")
    items = {item["id"]: item for item in catalog_data.get("items", [])}
    checks = {
        str(check.get("id")): check for check in catalog_data.get("checks", []) if check.get("id")
    }

    lines: list[str] = []
    for entry in blueprint:
        if isinstance(entry, str):
            lines.append(catalog.strip_rule_clause_tag(entry))
            continue
        if not isinstance(entry, dict):
            raise RuntimeError(f"Invalid blueprint item type: {type(entry)!r}")
        if "item" in entry:
            lines.append(_resolve_item(entry, items))
        elif "literal" in entry:
            lines.append(str(entry.get("literal") or ""))
        elif "check" in entry:
            lines.append(_resolve_check_ref(entry, checks))
        else:
            raise RuntimeError(f"Invalid blueprint item: {entry!r}")
    return "\n".join(lines) + "\n"


def validate_reporter_template(catalog_data: dict, rendered: str) -> list[str]:
    """Return structural errors for a rendered reporter body.

    The blueprint is authoritative about which items appear in the human
    template (it reproduces the historical template text), so only section
    marker structure is re-checked here; unknown or repeated blueprint item
    references are already rejected at catalog-load time.
    """
    errors: list[str] = []
    lines = rendered.splitlines()
    for marker in catalog_data["metadata"]["section_markers"]:
        if lines.count(marker) != 1:
            errors.append(f"section marker must occur exactly once: {marker}")
    return errors


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a human MIR template include file")
    parser.add_argument("role", choices=sorted(DEFAULT_OUTPUTS))
    parser.add_argument("--workspace-root", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    workspace_root = (
        Path(args.workspace_root).resolve()
        if args.workspace_root
        else Path(__file__).resolve().parents[2]
    )
    tool_root = workspace_root / "tools/auto-mir"
    catalog_data = catalog.load_catalog_for_role(tool_root, workspace_root, args.role)
    try:
        rendered = render_template(catalog_data, args.role)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.strict and args.role == "report":
        errors = validate_reporter_template(catalog_data, rendered)
        if errors:
            print("Reporter template validation errors:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 2

    output = workspace_root / (args.output or DEFAULT_OUTPUTS[args.role])
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != rendered:
            print(f"Generated {args.role} template is missing or stale: {output}", file=sys.stderr)
            return 3
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"Rendered {args.role} template: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
