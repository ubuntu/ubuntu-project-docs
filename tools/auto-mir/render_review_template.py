#!/usr/bin/env python3
"""Render the MIR reviewer template from catalog.yaml.

This script regenerates the **human-readable MIR reviewer template**
(``docs/MIR/mir-reviewers-template.md``) from the canonical source-of-truth
stored in ``metadata.review_template_blueprint`` in ``catalog.yaml``.  It is a
*documentation maintenance* tool, not part of the runtime auto-mir pipeline.

Role vs. the ``render/`` package
---------------------------------
``render_review_template.py`` (this file)
    Offline utility.  Reads ``catalog.yaml``, expands TODO references, and
    emits a plain-text ``.include`` fragment for ``{literalinclude}`` in
    the Sphinx docs.  Run manually when the reviewer template or catalog
    TODO refs change.

``render/__init__.py`` (the runtime renderer)
    Called by the auto-mir pipeline (Stage 5).  Takes the findings produced
    by check evaluation and renders a reviewer *draft* ready to post on the
    Launchpad bug.  Does NOT use ``review_template_blueprint`` from the catalog.

The canonical reviewer template source lives in
``metadata.review_template_blueprint`` and is rendered to an output file.
TODO lines are emitted from check entries via ``{check, todo_ref}`` references.

The output is the content inside the ``{code-block} text`` fence, stripping
the fence markers, ``:linenos:`` and the surrounding preamble. The result is
a plain-text ``.include`` file suitable for ``{literalinclude}`` in a Sphinx
document.
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


def _render_from_blueprint(catalog_data: dict) -> str:
    """Render the reviewer template body from the catalog blueprint.

    Scans for the ``{code-block} text`` fence in the blueprint and emits only
    the content between the opening and closing fences, skipping the
    ``:linenos:`` directive line immediately after the opening fence.
    Produces a plain-text ``.include`` file for ``{literalinclude}`` in Sphinx.
    """
    metadata = catalog_data.get("metadata", {})
    blueprint = metadata.get("review_template_blueprint")
    if not isinstance(blueprint, list) or not blueprint:
        raise RuntimeError("Catalog is missing metadata.review_template_blueprint.")

    checks = _check_map(catalog_data)

    lines: list[str] = []
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
            "Could not locate '```{code-block} text' fence in blueprint."
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
            "Defaults to docs/MIR/mir-reviewers-template-body.include."
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
        template_text = _render_from_blueprint(catalog_data)
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
    else:
        output_rel = "docs/MIR/mir-reviewers-template-body.include"

    output_path = workspace_root / output_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template_text, encoding="utf-8")

    print(f"Rendered reviewer template: {output_path}")
    if args.strict:
        print("Catalog TODO refs are consistent with the reviewer template.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
