#!/usr/bin/env python3

from __future__ import annotations

from copy import deepcopy
from typing import Any


PREDICATE_OPERATORS = {
    "eq",
    "ne",
    "lt",
    "le",
    "gt",
    "ge",
    "and",
    "or",
    "not",
    "truthy",
    "falsy",
}


def is_predicate(node: Any) -> bool:
    return (
        isinstance(node, dict)
        and node.get("op") in PREDICATE_OPERATORS
    )


def ensure_predicate(node: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a value expression such as a boolean state variable into
    an explicit predicate.
    """
    if is_predicate(node):
        return node

    return {
        "op": "truthy",
        "value": node,
    }


def negate_predicate(
    predicate: dict[str, Any],
) -> dict[str, Any]:
    """
    Deterministically negate a supported predicate.

    Examples:
        x == 1  -> x != 1
        x <= 5  -> x > 5
        A && B  -> !A || !B
        !A      -> A
    """
    predicate = ensure_predicate(
        deepcopy(predicate)
    )

    operator = predicate.get("op")

    comparison_negations = {
        "eq": "ne",
        "ne": "eq",
        "lt": "ge",
        "le": "gt",
        "gt": "le",
        "ge": "lt",
    }

    if operator in comparison_negations:
        result = deepcopy(predicate)
        result["op"] = comparison_negations[operator]
        return result

    if operator == "and":
        return {
            "op": "or",
            "left": negate_predicate(
                predicate["left"]
            ),
            "right": negate_predicate(
                predicate["right"]
            ),
        }

    if operator == "or":
        return {
            "op": "and",
            "left": negate_predicate(
                predicate["left"]
            ),
            "right": negate_predicate(
                predicate["right"]
            ),
        }

    if operator == "not":
        return ensure_predicate(
            deepcopy(predicate["value"])
        )

    if operator == "truthy":
        return {
            "op": "falsy",
            "value": deepcopy(predicate["value"]),
        }

    if operator == "falsy":
        return {
            "op": "truthy",
            "value": deepcopy(predicate["value"]),
        }

    return {
        "op": "not",
        "value": deepcopy(predicate),
    }


def contains_unknown(node: Any) -> bool:
    if isinstance(node, dict):
        if node.get("kind") == "unknown":
            return True

        return any(
            contains_unknown(value)
            for value in node.values()
        )

    if isinstance(node, list):
        return any(
            contains_unknown(value)
            for value in node
        )

    return False


def collect_state_variables(
    node: Any,
) -> set[str]:
    result: set[str] = set()

    if isinstance(node, dict):
        if (
            node.get("kind") == "state_variable"
            and isinstance(node.get("name"), str)
        ):
            result.add(node["name"])

        for value in node.values():
            result.update(
                collect_state_variables(value)
            )

    elif isinstance(node, list):
        for value in node:
            result.update(
                collect_state_variables(value)
            )

    return result


def exact_constant(value: Any) -> dict[str, Any]:
    return {
        "kind": "constant",
        "value": value,
    }


def unknown_expression(
    source: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "kind": "unknown",
        "source": source,
        "reason": reason,
    }
