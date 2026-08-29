#!/usr/bin/env python3
"""Render the human MIR reporter template from the report role catalog."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import catalog


def _item_map(catalog_data: dict) -> dict[str, dict]:
    return {item["id"]: item for item in catalog_data.get("items", [])}


def render_reporter_template(catalog_data: dict) -> str:
    """Resolve the report blueprint to a plain-text literalinclude body."""
    blueprint = catalog_data.get("metadata", {}).get("reporter_template_blueprint")
    if not isinstance(blueprint, list) or not blueprint:
        raise RuntimeError("Reporter catalog is missing its template blueprint")
    items = _item_map(catalog_data)
    lines: list[str] = []
    for entry in blueprint:
        if isinstance(entry, str):
            lines.append(catalog.strip_rule_clause_tag(entry))
            continue
        if not isinstance(entry, dict) or set(entry) != {"item"}:
            raise RuntimeError(f"Invalid reporter blueprint entry: {entry!r}")
        item_id = entry["item"]
        if item_id not in items:
            raise RuntimeError(f"Reporter blueprint references unknown item: {item_id}")
        lines.append(str(items[item_id]["template"]))
    return "\n".join(lines) + "\n"


def validate_reporter_template(catalog_data: dict, rendered: str) -> list[str]:
    """Return structural errors for a rendered reporter body."""
    errors: list[str] = []
    lines = rendered.splitlines()
    for marker in catalog_data["metadata"]["section_markers"]:
        if lines.count(marker) != 1:
            errors.append(f"section marker must occur exactly once: {marker}")
    expected = {str(item["template"]) for item in catalog_data["items"]}
    missing = sorted(expected - set(lines))
    errors.extend(f"item template missing from output: {template}" for template in missing)
    return errors


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render reporter template from role catalog")
    parser.add_argument("--workspace-root", default=None)
    parser.add_argument(
        "--output",
        default="docs/MIR/mir-reporters-template-body.include",
    )
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
    catalog_data = catalog.load_catalog_for_role(tool_root, workspace_root, "report")
    try:
        rendered = render_reporter_template(catalog_data)
        errors = validate_reporter_template(catalog_data, rendered) if args.strict else []
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if errors:
        print("Reporter template validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 2

    output = workspace_root / args.output
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != rendered:
            print(f"Generated reporter template is missing or stale: {output}", file=sys.stderr)
            return 3
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"Rendered reporter template: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
