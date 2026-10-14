"""Safe, declarative applicability conditions for reporter catalog items."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ConditionError(ValueError):
    """Raised when a reporter condition is malformed or cyclic."""


@dataclass(frozen=True)
class ConditionContext:
    """Values visible to condition evaluation.

    ``items`` maps stable reporter item IDs to normalized outcomes or selected
    option IDs. ``evidence`` is the adapter result mapping stored beneath
    ``ctx.evidence['adapters']``.
    """

    items: dict[str, Any]
    evidence: dict[str, Any]


def evaluate_condition(condition: dict[str, Any] | None, context: ConditionContext) -> bool:
    """Evaluate one validated condition without interpreting code or expressions."""
    if condition is None:
        return True
    _validate_node(condition)

    if "all" in condition:
        return all(evaluate_condition(child, context) for child in condition["all"])
    if "any" in condition:
        return any(evaluate_condition(child, context) for child in condition["any"])
    if "not" in condition:
        return not evaluate_condition(condition["not"], context)
    if "item" in condition:
        actual = context.items.get(condition["item"])
        return _compare(actual, condition)

    actual = _resolve_evidence_path(context.evidence, condition["evidence"])
    return _compare(actual, condition)


def validate_condition_references(
    condition: dict[str, Any] | None,
    *,
    known_items: set[str],
    known_adapters: set[str],
) -> list[str]:
    """Return unknown item/adapter references from one condition."""
    if condition is None:
        return []
    try:
        _validate_node(condition)
    except ConditionError as exc:
        return [str(exc)]

    errors: list[str] = []
    for reference_type, reference in condition_references(condition):
        if reference_type == "item" and reference not in known_items:
            errors.append(f"condition references unknown item: {reference}")
        elif reference_type == "evidence":
            adapter = reference.split(".", 1)[0]
            if adapter not in known_adapters:
                errors.append(f"condition references unknown adapter: {adapter}")
    return sorted(errors)


def condition_references(condition: dict[str, Any]) -> set[tuple[str, str]]:
    """Return all stable item and evidence-path references in a condition."""
    _validate_node(condition)
    references: set[tuple[str, str]] = set()
    if "all" in condition or "any" in condition:
        key = "all" if "all" in condition else "any"
        for child in condition[key]:
            references.update(condition_references(child))
    elif "not" in condition:
        references.update(condition_references(condition["not"]))
    elif "item" in condition:
        references.add(("item", condition["item"]))
    else:
        references.add(("evidence", condition["evidence"]))
    return references


def validate_condition_cycles(conditions_by_item: dict[str, dict[str, Any] | None]) -> list[str]:
    """Return cycle errors for reporter item-to-item applicability references."""
    graph: dict[str, set[str]] = {}
    for item_id, condition in conditions_by_item.items():
        if condition is None:
            graph[item_id] = set()
            continue
        try:
            references = condition_references(condition)
        except ConditionError as exc:
            return [f"item {item_id}: {exc}"]
        graph[item_id] = {
            reference
            for reference_type, reference in references
            if reference_type == "item" and reference in conditions_by_item
        }

    visiting: set[str] = set()
    visited: set[str] = set()
    errors: list[str] = []

    def visit(item_id: str, path: list[str]) -> None:
        if item_id in visiting:
            cycle_start = path.index(item_id)
            cycle = path[cycle_start:] + [item_id]
            message = "condition cycle: " + " -> ".join(cycle)
            if message not in errors:
                errors.append(message)
            return
        if item_id in visited:
            return
        visiting.add(item_id)
        path.append(item_id)
        for dependency in sorted(graph.get(item_id, set())):
            visit(dependency, path)
        path.pop()
        visiting.remove(item_id)
        visited.add(item_id)

    for item_id in sorted(graph):
        visit(item_id, [])
    return errors


def _validate_node(condition: Any) -> None:
    if not isinstance(condition, dict) or not condition:
        raise ConditionError("condition must be a non-empty mapping")

    operators = [key for key in ("all", "any", "not", "item", "evidence") if key in condition]
    if len(operators) != 1:
        raise ConditionError("condition must define exactly one operator")

    operator = operators[0]
    allowed = {
        "all": {"all"},
        "any": {"any"},
        "not": {"not"},
        "item": {"item", "equals", "in", "truthy"},
        "evidence": {"evidence", "equals", "in", "truthy"},
    }[operator]
    unknown = set(condition) - allowed
    if unknown:
        raise ConditionError(f"condition contains unsupported keys: {', '.join(sorted(unknown))}")

    if operator in {"all", "any"}:
        children = condition[operator]
        if not isinstance(children, list) or not children:
            raise ConditionError(f"condition '{operator}' requires a non-empty list")
        for child in children:
            _validate_node(child)
        return
    if operator == "not":
        _validate_node(condition[operator])
        return

    reference = condition[operator]
    if not isinstance(reference, str) or not reference.strip():
        raise ConditionError(f"condition '{operator}' requires a non-empty string")
    if operator == "evidence" and any(not part for part in reference.split(".")):
        raise ConditionError("evidence path contains an empty component")

    comparisons = [key for key in ("equals", "in", "truthy") if key in condition]
    if len(comparisons) != 1:
        raise ConditionError("condition leaf must define exactly one comparison")
    if "in" in condition and (not isinstance(condition["in"], list) or not condition["in"]):
        raise ConditionError("condition 'in' requires a non-empty list")
    if "truthy" in condition and not isinstance(condition["truthy"], bool):
        raise ConditionError("condition 'truthy' requires a boolean")


def _compare(actual: Any, condition: dict[str, Any]) -> bool:
    if "equals" in condition:
        return actual == condition["equals"]
    if "in" in condition:
        return actual in condition["in"]
    return bool(actual) is condition["truthy"]


def _resolve_evidence_path(evidence: dict[str, Any], path: str) -> Any:
    current: Any = evidence
    for component in path.split("."):
        if not isinstance(current, dict) or component not in current:
            return None
        current = current[component]
    return current
