"""Guard test: deterministic check evaluators must not hardcode reviewer text.

Every reviewer-facing message and TODO produced by a deterministic ``_check_*``
evaluator has to be rendered from the catalog via ``render_check_message`` so the
catalog stays the single, human-auditable source of truth for all outcomes.

This test fails if any ``_check_*`` function passes a string literal or f-string
directly as the ``message``/``todo`` argument of ``finding.succeed`` /
``finding.fail``, or assigns one to ``finding.message`` / ``finding.todo``.
"""

import ast
from pathlib import Path

DETERMINISTIC = Path(__file__).resolve().parent.parent / "checks" / "deterministic.py"


def _is_literal_text(node: ast.AST) -> bool:
    """True for a plain string literal or an f-string (reviewer text)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return True
    return isinstance(node, ast.JoinedStr)


def _is_finding_attr(node: ast.AST, attr: str) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == attr
        and isinstance(node.value, ast.Name)
        and node.value.id == "finding"
    )


def test_deterministic_checks_render_all_reviewer_text_from_catalog():
    tree = ast.parse(DETERMINISTIC.read_text(encoding="utf-8"))
    violations: list[str] = []

    for func in ast.walk(tree):
        if not (isinstance(func, ast.FunctionDef) and func.name.startswith("_check_")):
            continue

        for node in ast.walk(func):
            # finding.succeed(message, ...) / finding.fail(message, todo, ...)
            if (
                isinstance(node, ast.Call)
                and _is_finding_attr(node.func, "succeed")
                or isinstance(node, ast.Call)
                and _is_finding_attr(node.func, "fail")
            ):
                positional = node.args[:2] if node.func.attr == "fail" else node.args[:1]
                for arg in positional:
                    if _is_literal_text(arg):
                        violations.append(
                            f"{func.name}: literal passed to finding.{node.func.attr}() "
                            f"at line {node.lineno}"
                        )

            # finding.message = "..."  /  finding.todo = f"..."
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        _is_finding_attr(target, "message") or _is_finding_attr(target, "todo")
                    ) and _is_literal_text(node.value):
                        violations.append(
                            f"{func.name}: literal assigned to finding.{target.attr} "
                            f"at line {node.lineno}"
                        )

    assert not violations, (
        "Deterministic evaluators must render reviewer text via "
        "render_check_message() (catalog messages), not hardcode it:\n  "
        + "\n  ".join(sorted(violations))
    )
