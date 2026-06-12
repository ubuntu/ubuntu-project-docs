#!/usr/bin/env python3
"""Render the MIR reviewer template from catalog.yaml.

The canonical reviewer template source lives in
`metadata.review_template_blueprint` and is rendered to an output file.
TODO lines are emitted from check entries via `{check, todo_ref}` references.

Two output modes are supported:

- Full mode (default): renders the entire blueprint as-is, producing a
  standalone Markdown file (used for reference / diffing).

- Body-only mode (--body-only): renders only the content inside the
  ``{code-block} text`` fence, stripping the fence markers, ``:linenos:``
  and the surrounding preamble. The result is a plain-text ``.include``
  file suitable for ``{literalinclude}`` in a Sphinx document.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import catalog


def _check_map(catalog_data: dict) -> dict[str, dict[str, Any]]:
    checks = catalog_data.get("checks", [])
    return {str(check.get("id")): check for check in checks if check.get("id")}


def _resolve_item(item: Any, checks: dict[str, dict[str, Any]]) -> str:
    """Resolve a single blueprint item to its text representation."""
    if isinstance(item, str):
        return item

    if not isinstance(item, dict):
        raise RuntimeError(f"Invalid blueprint item type: {type(item)!r}")

    if "literal" in item:
        return str(item.get("literal") or "")

    check_id = str(item.get("check") or "")
    todo_ref_idx = item.get("todo_ref")
    if not check_id or not isinstance(todo_ref_idx, int):
        raise RuntimeError(f"Invalid check-ref blueprint item: {item!r}")

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


def _render_from_blueprint(catalog_data: dict, *, body_only: bool = False) -> str:
    """Render the reviewer template from the catalog blueprint.

    Args:
        catalog_data: Loaded catalog data.
        body_only: When True, emit only the content inside the
            ``{code-block} text`` fence (stripping preamble, fence markers,
            and ``:linenos:``). Produces a plain-text ``.include`` file.
            When False (default), emit the full blueprint as Markdown.
    """
    metadata = catalog_data.get("metadata", {})
    blueprint = metadata.get("review_template_blueprint")
    if not isinstance(blueprint, list) or not blueprint:
        raise RuntimeError("Catalog is missing metadata.review_template_blueprint.")

    checks = _check_map(catalog_data)

    if not body_only:
        lines: list[str] = [_resolve_item(item, checks) for item in blueprint]
        return "\n".join(lines) + "\n"

    # Body-only: scan for the ``{code-block} text`` fence and emit only
    # the content between the opening and closing fences, skipping the
    # ``:linenos:`` directive line immediately after the opening fence.
    lines = []
    in_body = False
    skip_linenos = False
    for item in blueprint:
        text = _resolve_item(item, checks)
        if not in_body:
            if text.strip() == "```{code-block} text":
                in_body = True
                skip_linenos = True
            continue
        if skip_linenos:
            skip_linenos = False
            if text.strip() == ":linenos:":
                continue
        if text.strip() == "```":
            break
        lines.append(text)

    if not lines:
        raise RuntimeError(
            "Body-only mode: could not locate '```{code-block} text' fence in blueprint."
        )

    return "\n".join(lines) + "\n"


def _catalog_todo_refs(catalog_data: dict) -> set[str]:
    refs: set[str] = set()
    for check in catalog_data.get("checks", []):
        for ref in check.get("todo_refs", []):
            text = str(ref).strip()
            if text.startswith("TODO"):
                refs.add(text)
    return refs


def _template_todo_lines(template_text: str) -> set[str]:
    todos: set[str] = set()
    for raw_line in template_text.splitlines():
        line = raw_line.strip()
        if line.startswith("TODO"):
            todos.add(line)
    return todos


def _validate_catalog_vs_template(catalog_data: dict, template_text: str) -> list[str]:
    catalog_todos = _catalog_todo_refs(catalog_data)
    template_todos = _template_todo_lines(template_text)

    missing_in_template = sorted(catalog_todos - template_todos)
    return missing_in_template


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render reviewer template from catalog with consistency checks"
    )
    parser.add_argument(
        "--workspace-root",
        default=None,
        help="Path to repository root (default: auto-detected from script location)",
    )
    parser.add_argument(
        "--catalog",
        default="tools/auto-mir/catalog.yaml",
        help="Catalog path relative to workspace root",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output path relative to workspace root. "
            "Defaults to docs/MIR/mir-reviewers-template-body.include (--body-only) "
            "or docs/MIR/mir-reviewers-template.generated.md (full mode)."
        ),
    )
    parser.add_argument(
        "--body-only",
        action="store_true",
        help=(
            "Emit only the template body (content inside the code-block fence), "
            "producing a plain-text .include file for use with Sphinx literalinclude."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if catalog TODO refs are missing from the reviewer template",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if args.workspace_root:
        workspace_root = Path(args.workspace_root).resolve()
    else:
        workspace_root = Path(__file__).resolve().parents[2]

    catalog_path = workspace_root / args.catalog
    if not catalog_path.exists():
        print(f"Catalog file not found: {catalog_path}", file=sys.stderr)
        return 1

    catalog_data = catalog.load_catalog(catalog_path, workspace_root)
    try:
        template_text = _render_from_blueprint(catalog_data, body_only=args.body_only)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    missing_todos: list[str] = []
    if args.strict:
        missing_todos = _validate_catalog_vs_template(catalog_data, template_text)

    if missing_todos and args.strict:
        joined = "\n  - ".join(missing_todos)
        print(
            f"Catalog TODO refs missing from reviewer template:\n  - {joined}",
            file=sys.stderr,
        )
        return 2

    if args.output:
        output_rel = args.output
    elif args.body_only:
        output_rel = "docs/MIR/mir-reviewers-template-body.include"
    else:
        output_rel = "docs/MIR/mir-reviewers-template.generated.md"

    output_path = workspace_root / output_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template_text, encoding="utf-8")

    print(f"Rendered reviewer template: {output_path}")
    if args.strict:
        print("Catalog TODO refs are consistent with the reviewer template.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
