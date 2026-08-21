#!/usr/bin/env python3

from __future__ import annotations

import copy
import re
from typing import Any


TRUE = "TRUE"
FALSE = "FALSE"
MAYBE = "MAYBE"
UNKNOWN = "UNKNOWN"


TRUTH_TO_VIOLATION_CLASS = {
    TRUE: "MUST_VIOLATE",
    MAYBE: "MAY_VIOLATE",
    UNKNOWN: "UNKNOWN",
    FALSE: "CANNOT_VIOLATE",
}


def exact(value: Any) -> dict[str, Any]:
    return {
        "kind": "exact",
        "value": value,
    }


def interval(
    lower: int,
    upper: int,
    type_name: str = "",
) -> dict[str, Any]:
    return {
        "kind": "interval",
        "lower": lower,
        "upper": upper,
        "type": type_name,
    }


def boolean_set(
    values: list[bool],
) -> dict[str, Any]:
    return {
        "kind": "bool_set",
        "values": sorted(set(values)),
    }


def unknown(
    reason: str,
    source: str = "",
) -> dict[str, Any]:
    result = {
        "kind": "unknown",
        "reason": reason,
    }

    if source:
        result["source"] = source

    return result


def is_numeric_exact(
    value: dict[str, Any],
) -> bool:
    return (
        value.get("kind") == "exact"
        and isinstance(
            value.get("value"),
            int,
        )
        and not isinstance(
            value.get("value"),
            bool,
        )
    )


def normalize_model_value(
    expression: dict[str, Any],
) -> dict[str, Any]:
    kind = expression.get("kind")

    if kind == "constant":
        return exact(
            copy.deepcopy(
                expression.get("value")
            )
        )

    if kind == "unknown":
        return unknown(
            expression.get(
                "reason",
                "Unknown initial expression",
            ),
            expression.get("source", ""),
        )

    return unknown(
        "Unsupported initial-state expression",
        str(expression),
    )


def parse_integer_type(
    type_name: str,
) -> tuple[str, int] | None:
    normalized = type_name.strip()

    unsigned_match = re.fullmatch(
        r"uint(\d*)",
        normalized,
    )

    if unsigned_match:
        bits = int(
            unsigned_match.group(1) or 256
        )
        return "uint", bits

    signed_match = re.fullmatch(
        r"int(\d*)",
        normalized,
    )

    if signed_match:
        bits = int(
            signed_match.group(1) or 256
        )
        return "int", bits

    return None


def abstract_parameter(
    type_name: str,
) -> dict[str, Any]:
    normalized = type_name.strip()

    if normalized == "bool":
        return boolean_set(
            [False, True]
        )

    integer_type = parse_integer_type(
        normalized
    )

    if integer_type:
        category, bits = integer_type

        if category == "uint":
            return interval(
                0,
                2 ** bits - 1,
                normalized,
            )

        return interval(
            -(2 ** (bits - 1)),
            2 ** (bits - 1) - 1,
            normalized,
        )

    if normalized.startswith("address"):
        return interval(
            0,
            2 ** 160 - 1,
            normalized,
        )

    bytes_match = re.fullmatch(
        r"bytes(\d+)",
        normalized,
    )

    if bytes_match:
        byte_count = int(
            bytes_match.group(1)
        )

        return interval(
            0,
            2 ** (8 * byte_count) - 1,
            normalized,
        )

    return unknown(
        f"Unsupported parameter type: {type_name}"
    )


def value_to_interval(
    value: dict[str, Any],
) -> tuple[int, int] | None:
    if is_numeric_exact(value):
        integer = int(value["value"])
        return integer, integer

    if value.get("kind") == "interval":
        lower = value.get("lower")
        upper = value.get("upper")

        if (
            isinstance(lower, int)
            and isinstance(upper, int)
        ):
            return lower, upper

    return None


def evaluate_value(
    expression: dict[str, Any],
    state: dict[str, dict[str, Any]],
    parameter_types: dict[str, str],
) -> dict[str, Any]:
    kind = expression.get("kind")

    if kind == "constant":
        return exact(
            copy.deepcopy(
                expression.get("value")
            )
        )

    if kind == "state_variable":
        variable_name = expression.get("name")

        if variable_name not in state:
            return unknown(
                "State variable has no abstract value",
                str(variable_name),
            )

        return copy.deepcopy(
            state[variable_name]
        )

    if kind == "parameter":
        parameter_name = str(
            expression.get("name", "")
        )

        parameter_type = parameter_types.get(
            parameter_name
        )

        if parameter_type is None:
            return unknown(
                "Parameter type not available",
                parameter_name,
            )

        return abstract_parameter(
            parameter_type
        )

    if kind == "unknown":
        return unknown(
            expression.get(
                "reason",
                "Unknown expression",
            ),
            expression.get("source", ""),
        )

    return unknown(
        "Unsupported value expression",
        str(expression),
    )


def abstract_arithmetic(
    left: dict[str, Any],
    right: dict[str, Any],
    operator: str,
    variable_type: str,
) -> dict[str, Any]:
    left_interval = value_to_interval(left)
    right_interval = value_to_interval(right)

    if (
        left_interval is None
        or right_interval is None
    ):
        return unknown(
            f"Unsupported arithmetic operands for {operator}"
        )

    left_lower, left_upper = left_interval
    right_lower, right_upper = right_interval

    if operator == "+=":
        lower = left_lower + right_lower
        upper = left_upper + right_upper

    elif operator == "-=":
        lower = left_lower - right_upper
        upper = left_upper - right_lower

    else:
        return unknown(
            f"Unsupported assignment operator: {operator}"
        )

    integer_type = parse_integer_type(
        variable_type
    )

    if integer_type:
        category, bits = integer_type

        if category == "uint":
            type_lower = 0
            type_upper = 2 ** bits - 1
        else:
            type_lower = -(2 ** (bits - 1))
            type_upper = 2 ** (bits - 1) - 1

        if (
            lower < type_lower
            or upper > type_upper
        ):
            return unknown(
                "Arithmetic may overflow or underflow; "
                "compiler-version semantics are not "
                "modeled in 1B"
            )

    if lower == upper:
        return exact(lower)

    return interval(
        lower,
        upper,
        variable_type,
    )


def apply_function_writes(
    state: dict[str, dict[str, Any]],
    function_signature: str,
    function_data: dict[str, Any],
    state_variable_types: dict[str, str],
) -> list[dict[str, Any]]:
    parameter_types = {
        str(parameter.get("name", "")): str(
            parameter.get("type", "")
        )
        for parameter in function_data.get(
            "parameters",
            [],
        )
    }

    trace: list[dict[str, Any]] = []

    for write in function_data.get(
        "writes",
        [],
    ):
        variable_name = str(
            write.get("variable", "")
        )

        operator = str(
            write.get("operator", "")
        )

        before = copy.deepcopy(
            state.get(
                variable_name,
                unknown(
                    "No previous abstract state",
                    variable_name,
                ),
            )
        )

        right_value = evaluate_value(
            write.get("expression", {}),
            state,
            parameter_types,
        )

        if operator == "=":
            after = right_value

        elif operator in {"+=", "-="}:
            after = abstract_arithmetic(
                before,
                right_value,
                operator,
                state_variable_types.get(
                    variable_name,
                    "",
                ),
            )

        else:
            after = unknown(
                f"Unsupported write operator: {operator}"
            )

        state[variable_name] = after

        trace.append(
            {
                "function": function_signature,
                "variable": variable_name,
                "operator": operator,
                "before": before,
                "right": right_value,
                "after": copy.deepcopy(after),
                "source": write.get(
                    "source",
                    "",
                ),
            }
        )

    return trace


def invert_truth(
    truth: str,
) -> str:
    return {
        TRUE: FALSE,
        FALSE: TRUE,
        MAYBE: MAYBE,
        UNKNOWN: UNKNOWN,
    }[truth]


def compare_equal(
    left: dict[str, Any],
    right: dict[str, Any],
) -> str:
    if (
        left.get("kind") == "unknown"
        or right.get("kind") == "unknown"
    ):
        return UNKNOWN

    if (
        left.get("kind") == "exact"
        and right.get("kind") == "exact"
    ):
        return (
            TRUE
            if left.get("value")
            == right.get("value")
            else FALSE
        )

    if left.get("kind") == "bool_set":
        values = set(
            left.get("values", [])
        )

        if right.get("kind") == "exact":
            right_value = right.get("value")

            if right_value not in values:
                return FALSE

            return (
                TRUE
                if len(values) == 1
                else MAYBE
            )

    if right.get("kind") == "bool_set":
        return compare_equal(
            right,
            left,
        )

    left_interval = value_to_interval(left)
    right_interval = value_to_interval(right)

    if (
        left_interval is not None
        and right_interval is not None
    ):
        left_lower, left_upper = left_interval
        right_lower, right_upper = (
            right_interval
        )

        if (
            left_upper < right_lower
            or right_upper < left_lower
        ):
            return FALSE

        if (
            left_lower == left_upper
            and right_lower == right_upper
            and left_lower == right_lower
        ):
            return TRUE

        return MAYBE

    return UNKNOWN


def compare_order(
    left: dict[str, Any],
    right: dict[str, Any],
    operator: str,
) -> str:
    left_interval = value_to_interval(left)
    right_interval = value_to_interval(right)

    if (
        left_interval is None
        or right_interval is None
    ):
        return UNKNOWN

    left_lower, left_upper = left_interval
    right_lower, right_upper = right_interval

    if operator == "lt":
        if left_upper < right_lower:
            return TRUE
        if left_lower >= right_upper:
            return FALSE

    elif operator == "le":
        if left_upper <= right_lower:
            return TRUE
        if left_lower > right_upper:
            return FALSE

    elif operator == "gt":
        return compare_order(
            right,
            left,
            "lt",
        )

    elif operator == "ge":
        return compare_order(
            right,
            left,
            "le",
        )

    return MAYBE


def truth_and(
    left: str,
    right: str,
) -> str:
    if FALSE in {left, right}:
        return FALSE

    if left == TRUE and right == TRUE:
        return TRUE

    if UNKNOWN in {left, right}:
        return UNKNOWN

    return MAYBE


def truth_or(
    left: str,
    right: str,
) -> str:
    if TRUE in {left, right}:
        return TRUE

    if left == FALSE and right == FALSE:
        return FALSE

    if UNKNOWN in {left, right}:
        return UNKNOWN

    return MAYBE


def evaluate_truthy(
    value: dict[str, Any],
) -> str:
    if value.get("kind") == "unknown":
        return UNKNOWN

    if value.get("kind") == "exact":
        exact_value = value.get("value")

        if isinstance(exact_value, bool):
            return (
                TRUE
                if exact_value
                else FALSE
            )

        return UNKNOWN

    if value.get("kind") == "bool_set":
        values = set(
            value.get("values", [])
        )

        if values == {True}:
            return TRUE

        if values == {False}:
            return FALSE

        if values == {False, True}:
            return MAYBE

    return UNKNOWN


def evaluate_predicate(
    predicate: dict[str, Any],
    state: dict[str, dict[str, Any]],
) -> str:
    operator = predicate.get("op")

    if operator in {
        "eq",
        "ne",
        "lt",
        "le",
        "gt",
        "ge",
    }:
        left = evaluate_value(
            predicate.get("left", {}),
            state,
            {},
        )

        right = evaluate_value(
            predicate.get("right", {}),
            state,
            {},
        )

        if operator == "eq":
            return compare_equal(
                left,
                right,
            )

        if operator == "ne":
            return invert_truth(
                compare_equal(
                    left,
                    right,
                )
            )

        return compare_order(
            left,
            right,
            operator,
        )

    if operator == "and":
        return truth_and(
            evaluate_predicate(
                predicate.get("left", {}),
                state,
            ),
            evaluate_predicate(
                predicate.get("right", {}),
                state,
            ),
        )

    if operator == "or":
        return truth_or(
            evaluate_predicate(
                predicate.get("left", {}),
                state,
            ),
            evaluate_predicate(
                predicate.get("right", {}),
                state,
            ),
        )

    if operator == "not":
        return invert_truth(
            evaluate_predicate(
                predicate.get("value", {}),
                state,
            )
        )

    if operator == "truthy":
        return evaluate_truthy(
            evaluate_value(
                predicate.get("value", {}),
                state,
                {},
            )
        )

    if operator == "falsy":
        return invert_truth(
            evaluate_truthy(
                evaluate_value(
                    predicate.get("value", {}),
                    state,
                    {},
                )
            )
        )

    return UNKNOWN


def initial_abstract_state(
    model: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        variable_name: normalize_model_value(
            expression
        )
        for variable_name, expression in (
            model.get(
                "initial_state",
                {},
            ).items()
        )
    }


def simulate_path(
    model: dict[str, Any],
    property_name: str,
    sequence: list[str],
) -> dict[str, Any]:
    properties = model.get(
        "properties",
        {},
    )

    if property_name not in properties:
        raise KeyError(
            f"Property not found: {property_name}"
        )

    property_data = properties[
        property_name
    ]

    state = initial_abstract_state(model)
    trace: list[dict[str, Any]] = []
    missing_functions: list[str] = []

    functions = model.get(
        "functions",
        {},
    )

    state_variable_types = model.get(
        "state_variable_types",
        {},
    )

    for function_signature in sequence:
        function_data = functions.get(
            function_signature
        )

        if function_data is None:
            missing_functions.append(
                function_signature
            )
            continue

        trace.extend(
            apply_function_writes(
                state,
                function_signature,
                function_data,
                state_variable_types,
            )
        )

    if missing_functions:
        violation_truth = UNKNOWN
    else:
        violation_truth = evaluate_predicate(
            property_data[
                "violation_predicate"
            ],
            state,
        )

    return {
        "sequence": sequence,
        "property": property_name,
        "violation_truth": violation_truth,
        "violation_class": (
            TRUTH_TO_VIOLATION_CLASS[
                violation_truth
            ]
        ),
        "final_state": state,
        "trace": trace,
        "missing_functions": (
            missing_functions
        ),
    }
