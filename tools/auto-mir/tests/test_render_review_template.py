"""Tests for catalog-driven human reviewer-template generation."""

import sys
from pathlib import Path

import pytest

TOOL_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = TOOL_ROOT.parent.parent
sys.path.insert(0, str(TOOL_ROOT))

import catalog  # noqa: E402
import render_review_template as renderer  # noqa: E402


def _catalog(blueprint: list, checks: list[dict] | None = None) -> dict:
    return {
        "metadata": {"review_template_blueprint": blueprint},
        "checks": checks or [],
    }


def test_render_expands_check_refs_and_preserves_order_and_whitespace():
    data = _catalog(
        [
            "preamble",
            "```{code-block} text",
            ":linenos:",
            "",
            "first  ",
            {"check": "SUM-1", "todo_ref": 0},
            {"literal": "last"},
            "```",
            "epilogue",
        ],
        [{"id": "SUM-1", "todo_refs": ["TODO: selected"]}],
    )

    assert renderer._render_from_blueprint(data) == "\nfirst  \nTODO: selected\nlast\n"


@pytest.mark.parametrize(
    ("blueprint", "message"),
    [
        (["no fence"], "exactly one"),
        (
            ["```{code-block} text", "body", "```"],
            "must enable ':linenos:'",
        ),
        (
            ["```{code-block} text", ":linenos:", "body"],
            "missing its closing fence",
        ),
        (
            [
                "```{code-block} text",
                ":linenos:",
                "body",
                "```",
                "```{code-block} text",
            ],
            "exactly one",
        ),
    ],
)
def test_render_rejects_malformed_blueprint(blueprint, message):
    with pytest.raises(RuntimeError, match=message):
        renderer._render_from_blueprint(_catalog(blueprint))


def test_render_rejects_unknown_check_and_out_of_range_ref():
    unknown = _catalog(
        [
            "```{code-block} text",
            ":linenos:",
            {"check": "SUM-1", "todo_ref": 0},
            "```",
        ]
    )
    with pytest.raises(RuntimeError, match="unknown check id"):
        renderer._render_from_blueprint(unknown)

    out_of_range = _catalog(
        unknown["metadata"]["review_template_blueprint"],
        [{"id": "SUM-1", "todo_refs": []}],
    )
    with pytest.raises(RuntimeError, match="out of range"):
        renderer._render_from_blueprint(out_of_range)


def test_strict_validation_checks_selected_refs_not_runtime_alternatives():
    data = _catalog(
        [
            "```{code-block} text",
            ":linenos:",
            {"check": "SUM-1", "todo_ref": 0},
            "```",
        ],
        [{"id": "SUM-1", "todo_refs": ["TODO: selected", "TODO: runtime alternative"]}],
    )
    rendered = renderer._render_from_blueprint(data)

    assert renderer._validate_catalog_vs_template(data, rendered) == []
    assert renderer._validate_catalog_vs_template(data, "other\n") == ["TODO: selected"]


def test_main_check_mode_detects_current_and_stale_output(monkeypatch, tmp_path):
    output_path = tmp_path / "body.include"
    data = _catalog(["```{code-block} text", ":linenos:", "body", "```"])
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text("placeholder: true\n")
    monkeypatch.setattr(renderer.catalog, "load_catalog", lambda *_args: data)

    common_args = [
        "render_review_template.py",
        "--workspace-root",
        str(tmp_path),
        "--catalog",
        "catalog.yaml",
        "--output",
        "body.include",
        "--strict",
    ]
    monkeypatch.setattr(sys, "argv", common_args)
    assert renderer.main() == 0

    monkeypatch.setattr(sys, "argv", [*common_args, "--check"])
    assert renderer.main() == 0

    output_path.write_text("stale\n")
    assert renderer.main() == 3


def test_real_catalog_renders_strictly_and_idempotently(tmp_path):
    data = catalog.load_catalog(TOOL_ROOT / "catalog.yaml", WORKSPACE_ROOT)

    first = renderer._render_from_blueprint(data)
    second = renderer._render_from_blueprint(data)

    assert first == second
    assert renderer._validate_catalog_vs_template(data, first) == []
    assert first.endswith("\n")
    assert "```" not in first
