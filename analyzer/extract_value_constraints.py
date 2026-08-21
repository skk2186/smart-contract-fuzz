#!/usr/bin/env python3

"""
Extract lightweight state-value constraints from Solidity contracts.

Supported constant writes:
    gate = 7;
    stage = 1;
    enabled = true;
    owner = 0x...;

Supported requirements:
    require(gate == 7);
    require(stage != 0);
    require(enabled);
    require(!locked);
    require(value >= 100);

This is deliberately a lightweight analysis. It does not attempt to
interpret arbitrary expressions, symbolic values, mappings, arithmetic,
function calls, or interprocedural data flow.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from slither.slither import Slither


IDENTIFIER = r"[A-Za-z_][A-Za-z0-9_]*"

ASSIGNMENT_RE = re.compile(
    rf"^\s*(?P<variable>{IDENTIFIER})\s*=\s*(?P<value>.+?)\s*$"
)

BINARY_REQUIREMENT_RE = re.compile(
    rf"^\s*(?P<left>.+?)\s*"
    rf"(?P<operator>==|!=|>=|<=|>|<)\s*"
    rf"(?P<right>.+?)\s*$"
)

PLAIN_BOOLEAN_RE = re.compile(
    rf"^\s*(?P<negated>!)?\s*(?P<variable>{IDENTIFIER})\s*$"
)

INTEGER_CAST_RE = re.compile(
    r"^(?:u?int(?:8|16|24|32|40|48|56|64|72|80|88|96|104|112|120|128|"
    r"136|144|152|160|168|176|184|192|200|208|216|224|232|240|248|256)?"
    r"|bytes(?:1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|"
    r"22|23|24|25|26|27|28|29|30|31|32)"
    r"|address|bool)\s*\((?P<inner>.*)\)$"
)

HEX_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
HEX_INTEGER_RE = re.compile(r"^0x[0-9a-fA-F]+$")
DECIMAL_INTEGER_RE = re.compile(r"^-?[0-9][0-9_]*$")


@dataclass(frozen=True)
class Literal:
    """Normalized literal extracted from source text."""

    kind: str
    value: Any
    raw: str

    def to_json(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "value": self.value,
            "raw": self.raw,
        }


def normalize_expression(text: str) -> str:
    """Remove harmless outer whitespace and balanced parentheses."""

    result = text.strip()

    while (
        len(result) >= 2
        and result.startswith("(")
        and result.endswith(")")
        and outer_parentheses_cover_entire_expression(result)
    ):
        result = result[1:-1].strip()

    return result


def outer_parentheses_cover_entire_expression(text: str) -> bool:
    """Return True when the first and last parentheses form one outer pair."""

    depth = 0
    quote: str | None = None
    escaped = False

    for index, character in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue

        if character in {"'", '"'}:
            quote = character
            continue

        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1

            if depth == 0 and index != len(text) - 1:
                return False

            if depth < 0:
                return False

    return depth == 0


def parse_literal(text: str) -> Literal | None:
    """
    Parse a small set of Solidity literals.

    Returns None for symbolic or unsupported expressions.
    """

    raw = normalize_expression(text)
    lowered = raw.lower()

    if lowered == "true":
        return Literal(kind="bool", value=True, raw=raw)

    if lowered == "false":
        return Literal(kind="bool", value=False, raw=raw)

    if DECIMAL_INTEGER_RE.fullmatch(raw):
        normalized = raw.replace("_", "")

        try:
            return Literal(
                kind="int",
                value=int(normalized, 10),
                raw=raw,
            )
        except ValueError:
            return None

    if HEX_ADDRESS_RE.fullmatch(raw):
        return Literal(
            kind="address",
            value=raw.lower(),
            raw=raw,
        )

    if HEX_INTEGER_RE.fullmatch(raw):
        try:
            return Literal(
                kind="int",
                value=int(raw, 16),
                raw=raw,
            )
        except ValueError:
            return None

    cast_match = INTEGER_CAST_RE.fullmatch(raw)

    if cast_match:
        return parse_literal(cast_match.group("inner"))

    return None


def split_first_top_level_argument(text: str) -> str:
    """
    Extract the first argument of a function call.

    For:
        gate == 7, "incorrect gate"

    returns:
        gate == 7
    """

    depth = 0
    quote: str | None = None
    escaped = False

    for index, character in enumerate(text):
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue

        if character in {"'", '"'}:
            quote = character
            continue

        if character in "([{":
            depth += 1
            continue

        if character in ")]}":
            depth -= 1
            continue

        if character == "," and depth == 0:
            return text[:index].strip()

    return text.strip()


def extract_require_condition(expression: str) -> str | None:
    """
    Extract the condition from Slither's textual require expression.

    Handles both common forms:
        require(gate == 7, "message")
        require(bool,string)(gate == 7, "message")
    """

    text = expression.strip()
    require_index = text.find("require")

    if require_index < 0:
        return None

    suffix = text[require_index + len("require"):].strip()

    if not suffix.startswith("("):
        return None

    groups: list[str] = []
    depth = 0
    start: int | None = None
    quote: str | None = None
    escaped = False

    for index, character in enumerate(suffix):
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue

        if character in {"'", '"'}:
            quote = character
            continue

        if character == "(":
            if depth == 0:
                start = index + 1

            depth += 1
            continue

        if character == ")":
            depth -= 1

            if depth == 0 and start is not None:
                groups.append(suffix[start:index].strip())
                start = None

            if depth < 0:
                return None

    if not groups:
        return None

    # With Slither output such as require(bool,string)(...), the final
    # parenthesized group contains the actual arguments.
    arguments = groups[-1]
    return split_first_top_level_argument(arguments)


def invert_operator(operator: str) -> str:
    """Invert an operator when the constant appears on the left."""

    mapping = {
        "==": "==",
        "!=": "!=",
        ">": "<",
        "<": ">",
        ">=": "<=",
        "<=": ">=",
    }

    return mapping[operator]


def parse_requirement(
    condition: str,
    state_variables: set[str],
) -> dict[str, Any] | None:
    """
    Parse one simple require condition into normalized JSON data.
    """

    normalized = normalize_expression(condition)

    boolean_match = PLAIN_BOOLEAN_RE.fullmatch(normalized)

    if boolean_match:
        variable = boolean_match.group("variable")

        if variable not in state_variables:
            return None

        negated = boolean_match.group("negated") is not None
        literal = Literal(
            kind="bool",
            value=not negated,
            raw="false" if negated else "true",
        )

        return {
            "variable": variable,
            "operator": "==",
            "value": literal.to_json(),
            "condition": normalized,
        }

    binary_match = BINARY_REQUIREMENT_RE.fullmatch(normalized)

    if not binary_match:
        return None

    left = normalize_expression(binary_match.group("left"))
    right = normalize_expression(binary_match.group("right"))
    operator = binary_match.group("operator")

    left_is_state = left in state_variables
    right_is_state = right in state_variables

    left_literal = parse_literal(left)
    right_literal = parse_literal(right)

    if left_is_state and right_literal is not None:
        return {
            "variable": left,
            "operator": operator,
            "value": right_literal.to_json(),
            "condition": normalized,
        }

    if right_is_state and left_literal is not None:
        return {
            "variable": right,
            "operator": invert_operator(operator),
            "value": left_literal.to_json(),
            "condition": normalized,
        }

    return None


def append_unique(
    items: list[dict[str, Any]],
    item: dict[str, Any],
) -> None:
    """Append a dictionary only when an equivalent item is absent."""

    if item not in items:
        items.append(item)


def function_record() -> dict[str, Any]:
    return {
        "constant_writes": {},
        "requirements": [],
        "unsupported_writes": [],
        "unsupported_requirements": [],
    }


def analyze_function(
    function: Any,
    state_variables: set[str],
) -> dict[str, Any]:
    record = function_record()

    for node in function.nodes:
        if node.expression is None:
            continue

        expression = str(node.expression).strip()

        require_condition = extract_require_condition(expression)

        if require_condition is not None:
            requirement = parse_requirement(
                require_condition,
                state_variables,
            )

            if requirement is not None:
                append_unique(
                    record["requirements"],
                    requirement,
                )
            else:
                unsupported = {
                    "condition": require_condition,
                    "node_expression": expression,
                }

                append_unique(
                    record["unsupported_requirements"],
                    unsupported,
                )

            continue

        assignment_match = ASSIGNMENT_RE.fullmatch(expression)

        if assignment_match is None:
            continue

        variable = assignment_match.group("variable")

        if variable not in state_variables:
            continue

        value_text = assignment_match.group("value")

        # Avoid accidentally interpreting comparison expressions as writes.
        if any(
            operator in value_text
            for operator in ("==", "!=", ">=", "<=")
        ):
            continue

        literal = parse_literal(value_text)

        if literal is None:
            unsupported = {
                "variable": variable,
                "expression": value_text.strip(),
                "node_expression": expression,
            }

            append_unique(
                record["unsupported_writes"],
                unsupported,
            )
            continue

        writes = record["constant_writes"].setdefault(
            variable,
            [],
        )

        literal_json = literal.to_json()

        if literal_json not in writes:
            writes.append(literal_json)

    return record


def analyze_contract(contract: Any) -> dict[str, Any]:
    state_variables = {
        variable.name
        for variable in contract.state_variables
    }

    functions: dict[str, Any] = {}

    for function in contract.functions_declared:
        if function.is_constructor:
            continue

        functions[function.full_name] = analyze_function(
            function,
            state_variables,
        )

    return {
        "state_variables": sorted(state_variables),
        "functions": functions,
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract lightweight constant state writes and simple "
            "require constraints from Solidity contracts."
        )
    )

    parser.add_argument(
        "source",
        type=Path,
        help="Path to the Solidity source file.",
    )

    parser.add_argument(
        "--contract",
        help=(
            "Analyze only the named contract. By default, all "
            "non-interface contracts are analyzed."
        ),
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    source = arguments.source.resolve()

    if not source.is_file():
        print(
            f"Error: source file does not exist: {source}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        slither = Slither(str(source))
    except Exception as error:
        print(
            f"Error: Slither analysis failed: {error}",
            file=sys.stderr,
        )
        raise SystemExit(1) from error

    result: dict[str, Any] = {}

    for contract in slither.contracts:
        if getattr(contract, "is_interface", False):
            continue

        if (
            arguments.contract is not None
            and contract.name != arguments.contract
        ):
            continue

        result[contract.name] = analyze_contract(contract)

    if arguments.contract is not None and not result:
        print(
            f"Error: contract not found: {arguments.contract}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    json.dump(
        result,
        sys.stdout,
        indent=2,
        ensure_ascii=False,
        sort_keys=False,
    )

    print()


if __name__ == "__main__":
    main()
