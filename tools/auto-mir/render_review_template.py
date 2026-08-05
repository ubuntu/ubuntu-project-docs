#!/usr/bin/env python3
"""Render the MIR reviewer template from the composed review catalog.

This script regenerates the **human-readable MIR reviewer template**
(``docs/MIR/mir-reviewers-template.md``) from the canonical source-of-truth
stored in ``metadata.review_template_blueprint`` in ``catalog-mir-review.yaml``
(composed with the shared sections in ``catalog.yaml`` via
``catalog.load_catalog_for_role``).  It is a *documentation maintenance* tool,
not part of the runtime auto-mir pipeline.

Role vs. the ``render/`` package
---------------------------------
``render_review_template.py`` (this file)
    Offline utility.  Reads the composed review catalog, expands TODO
    references, and emits a plain-text ``.include`` fragment for
    ``{literalinclude}`` in the Sphinx docs.  Supported documentation builds
    run it automatically.

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

    resolved = [_resolve_item(item, checks) for item in blueprint]
    opening_fence = "```{code-block} text"
    opening_indexes = [
        index for index, text in enumerate(resolved) if text.strip() == opening_fence
    ]
    if len(opening_indexes) != 1:
        raise RuntimeError("Blueprint must contain exactly one '```{code-block} text' fence.")

    body_start = opening_indexes[0] + 1
    if body_start >= len(resolved) or resolved[body_start].strip() != ":linenos:":
        raise RuntimeError("Reviewer template code block must enable ':linenos:'.")
    body_start += 1

    closing_index = next(
        (index for index in range(body_start, len(resolved)) if resolved[index].strip() == "```"),
        None,
    )
    if closing_index is None:
        raise RuntimeError("Reviewer template code block is missing its closing fence.")

    lines = resolved[body_start:closing_index]
    if not lines:
        raise RuntimeError("Reviewer template code block is empty.")

    return "\n".join(lines) + "\n"


def _validate_catalog_vs_template(catalog_data: dict, template_text: str) -> list[str]:
    """Return blueprint-selected TODO refs missing from rendered output.

    A check may define additional outcome-specific ``todo_refs`` for the runtime
    renderer.  The blueprint is authoritative about which refs belong in the
    static human template, so unselected runtime alternatives are not errors.
    """
    metadata = catalog_data.get("metadata", {})
    blueprint = metadata.get("review_template_blueprint", [])
    checks = _check_map(catalog_data)
    rendered_lines = set(template_text.splitlines())
    expected = {
        _resolve_item(item, checks)
        for item in blueprint
        if isinstance(item, dict) and "check" in item
    }
    return sorted(expected - rendered_lines)


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
        default=None,
        help=(
            "Catalog path relative to workspace root, for an ad-hoc/synthetic full "
            "catalog. Defaults to the composed review catalog "
            "(catalog.yaml + catalog-mir-review.yaml)."
        ),
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
        help="Fail if a blueprint-selected TODO ref is missing from the rendered body",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that the output file is current instead of rewriting it",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if args.workspace_root:
        workspace_root = Path(args.workspace_root).resolve()
    else:
        workspace_root = Path(__file__).resolve().parents[2]

    if args.catalog is None:
        catalog_data = catalog.load_catalog_for_role(
            workspace_root / "tools/auto-mir", workspace_root, "review"
        )
    else:
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

    if missing_todos:
        joined = "\n  - ".join(missing_todos)
        print(
            f"Blueprint TODO refs missing from reviewer template:\n  - {joined}",
            file=sys.stderr,
        )
        return 2

    if args.output:
        output_rel = args.output
    else:
        output_rel = "docs/MIR/mir-reviewers-template-body.include"

    output_path = workspace_root / output_rel
    if args.check:
        if not output_path.exists():
            print(f"Generated reviewer template is missing: {output_path}", file=sys.stderr)
            return 3
        if output_path.read_text(encoding="utf-8") != template_text:
            print(f"Generated reviewer template is stale: {output_path}", file=sys.stderr)
            return 3
        print(f"Generated reviewer template is current: {output_path}")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template_text, encoding="utf-8")

    print(f"Rendered reviewer template: {output_path}")
    if args.strict:
        print("Blueprint TODO refs are consistent with the reviewer template.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
