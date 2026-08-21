#!/usr/bin/env python3
"""Materialize a ranked path into an Echidna corpus seed.

This is a deliberately fail-closed bridge between the V2 ranked-path JSON and
the native corpus format.  It derives exact argument requirements from simple
``require(parameter == constant)`` conditions and derives a boundary value from
the V2 violation predicate when the terminal function writes a property state
variable.  Unsupported or ambiguous cases are reported instead of silently
injecting a hand-picked value.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:  # direct execution from analyzer/ and package imports both work
    from .generate_echidna_corpus_seed import (
        SeedSpecError,
        parse_signature,
        write_seed,
    )
except ImportError:  # pragma: no cover - exercised by CLI execution
    from generate_echidna_corpus_seed import (  # type: ignore
        SeedSpecError,
        parse_signature,
        write_seed,
    )


_BINARY_RE = re.compile(r"^\s*(.+?)\s*(==|!=|>=|<=|>|<)\s*(.+?)\s*$")
_DECIMAL_RE = re.compile(r"^-?[0-9][0-9_]*$")
_HEX_RE = re.compile(r"^0x[0-9a-fA-F]+$")
_INVERT = {"==": "==", "!=": "!=", ">": "<", "<": ">", ">=": "<=", "<=": ">="}


class MaterializationError(ValueError):
    """Raised when a ranked path cannot be instantiated safely."""


def load_contract_block(data: dict[str, Any], contract: str) -> dict[str, Any]:
    block = data.get(contract)
    if isinstance(block, dict):
        return block
    if data.get("contract") == contract:
        return data
    raise MaterializationError(f"contract {contract!r} not found in ranked data")


def parse_literal(text: str) -> int | bool | None:
    value = text.strip()
    while value.startswith("(") and value.endswith(")"):
        value = value[1:-1].strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if _DECIMAL_RE.fullmatch(value):
        return int(value.replace("_", ""), 10)
    if _HEX_RE.fullmatch(value):
        return int(value, 16)
    return None


def last_parenthesized_group(text: str) -> str | None:
    close = text.rfind(")")
    if close < 0:
        return None
    depth = 0
    for index in range(close, -1, -1):
        if text[index] == ")":
            depth += 1
        elif text[index] == "(":
            depth -= 1
            if depth == 0:
                return text[index + 1 : close]
    return None


def first_argument(text: str) -> str:
    depth = 0
    for index, char in enumerate(text):
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            return text[:index].strip()
    return text.strip()


def parameter_equalities(function: Any) -> dict[str, int | bool]:
    parameters = {str(item.name) for item in function.parameters}
    result: dict[str, int | bool] = {}
    for node in function.nodes:
        if not node.expression:
            continue
        expression = str(node.expression)
        if "require" not in expression:
            continue
        group = last_parenthesized_group(expression)
        if group is None:
            continue
        match = _BINARY_RE.match(first_argument(group))
        if not match:
            continue
        left, operator, right = match.groups()
        left = left.strip()
        right = right.strip()
        if left in parameters:
            literal = parse_literal(right)
        elif right in parameters:
            literal = parse_literal(left)
            operator = _INVERT[operator]
        else:
            continue
        if literal is None or operator != "==":
            continue
        previous = result.get(left if left in parameters else right)
        if previous is not None and previous != literal:
            raise MaterializationError(
                f"conflicting exact requirements for {function.full_name}"
            )
        result[left if left in parameters else right] = literal
    return result


def parameter_uses(function: Any) -> set[str]:
    """Return parameters appearing in a node expression."""
    parameters = {str(item.name) for item in function.parameters}
    used: set[str] = set()
    for node in function.nodes:
        expression = str(node.expression) if node.expression else ""
        for parameter in parameters:
            if re.search(rf"\b{re.escape(parameter)}\b", expression):
                used.add(parameter)
    return used


def simple_violation_constraint(predicate: dict[str, Any]) -> tuple[str, int] | None:
    if predicate.get("op") not in {"gt", "ge", "lt", "le", "eq", "ne"}:
        return None
    left = predicate.get("left")
    right = predicate.get("right")
    if not isinstance(left, dict) or not isinstance(right, dict):
        return None
    if left.get("kind") != "state_variable" or right.get("kind") != "constant":
        return None
    value = right.get("value")
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return str(predicate["op"]), value


def boundary_value(predicate: dict[str, Any]) -> int | None:
    constraint = simple_violation_constraint(predicate)
    if constraint is None:
        return None
    operator, value = constraint
    if operator in {"gt", "ge"}:
        return value + 1 if operator == "gt" else value
    if operator in {"lt", "le"}:
        return value - 1 if operator == "lt" else value
    if operator == "eq":
        return value
    if operator == "ne":
        return value + 1
    return None


def safe_boundary_value(predicate: dict[str, Any]) -> int | None:
    """Return the closest value that still satisfies the original property."""
    constraint = simple_violation_constraint(predicate)
    if constraint is None:
        return None
    operator, value = constraint
    if operator == "gt":
        return value
    if operator == "ge":
        return value - 1
    if operator == "lt":
        return value
    if operator == "le":
        return value + 1
    return None


def terminal_parameter_names(
    model: dict[str, Any],
    property_name: str,
    terminal_signature: str,
) -> set[str]:
    properties = model.get("properties", {})
    property_data = properties.get(property_name, {})
    violation = property_data.get("violation_predicate", {})
    constraint = simple_violation_constraint(violation)
    if constraint is None:
        return set()
    target_state = violation.get("left", {})
    state_name = target_state.get("name")
    state_source_name = target_state.get("source_name")
    function_data = model.get("functions", {}).get(terminal_signature, {})
    names: set[str] = set()
    for write in function_data.get("writes", []):
        variable = write.get("variable")
        if variable not in {state_name, state_source_name}:
            continue
        expression = write.get("expression", {})
        if expression.get("kind") == "parameter":
            names.add(str(expression.get("name")))
    return names


def terminal_written_parameter_names(
    model: dict[str, Any],
    terminal_signature: str,
) -> set[str]:
    """Parameters written directly by the terminal function."""
    function_data = model.get("functions", {}).get(terminal_signature, {})
    return {
        str(write.get("expression", {}).get("name"))
        for write in function_data.get("writes", [])
        if write.get("expression", {}).get("kind") == "parameter"
    }


def find_functions(source: Path, contract_name: str) -> dict[str, Any]:
    try:
        from slither.slither import Slither
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise MaterializationError(
            "Slither is required; run this command in the contract-fuzz environment"
        ) from exc
    try:
        slither = Slither(str(source))
    except Exception as exc:  # pragma: no cover - compiler/environment dependent
        raise MaterializationError(f"Slither failed: {exc}") from exc
    contracts = [item for item in slither.contracts if item.name == contract_name]
    if not contracts:
        raise MaterializationError(f"contract {contract_name!r} not found in {source}")
    functions: dict[str, Any] = {}
    for function in contracts[0].functions:
        functions[function.full_name] = function
    return functions


def materialize(
    source: Path,
    contract: str,
    ranked_path: Path,
    predicate_path: Path,
    output_dir: Path,
    property_name: str | None = None,
    name: str = "seed-0001.txt",
    derive_violation_values: bool = True,
    safe_boundary_values: bool = False,
) -> dict[str, Any]:
    ranked = load_contract_block(json.loads(ranked_path.read_text()), contract)
    paths = ranked.get("paths")
    if not isinstance(paths, list) or not paths:
        raise MaterializationError("ranked path list is empty")
    path = paths[0]
    sequence = path.get("sequence")
    if not isinstance(sequence, list) or not sequence:
        raise MaterializationError("top ranked path has no sequence")
    model = json.loads(predicate_path.read_text())
    property_name = property_name or path.get("property")
    if not isinstance(property_name, str):
        properties = model.get("properties", {})
        if len(properties) != 1:
            raise MaterializationError("property must be specified for multi-property models")
        property_name = next(iter(properties))
    functions = find_functions(source, contract)
    terminal = str(sequence[-1])
    terminal_names = terminal_parameter_names(model, property_name, terminal)
    terminal_written_names = terminal_written_parameter_names(model, terminal)
    violation_predicate = model["properties"][property_name]["violation_predicate"]
    terminal_value = (
        safe_boundary_value(violation_predicate)
        if safe_boundary_values
        else boundary_value(violation_predicate)
    )
    values: list[int] = []
    value_sources: list[dict[str, Any]] = []
    for index, signature in enumerate(sequence):
        _, types = parse_signature(signature)
        function = functions.get(signature)
        if function is None:
            raise MaterializationError(f"function {signature!r} not found in {contract}")
        if len(types) != len(function.parameters):
            raise MaterializationError(f"parameter count mismatch for {signature}")
        equalities = parameter_equalities(function)
        used_parameters = parameter_uses(function)
        allowed_parameters = set(equalities)
        if index == len(sequence) - 1:
            allowed_parameters |= terminal_written_names
        unsupported = used_parameters - allowed_parameters
        if unsupported:
            raise MaterializationError(
                f"unsupported parameter use in {signature}: {sorted(unsupported)}"
            )
        for parameter, _type in zip(function.parameters, types):
            parameter_name = str(parameter.name)
            if parameter_name in equalities:
                value = equalities[parameter_name]
                if isinstance(value, bool):
                    raise MaterializationError(
                        f"boolean argument materialization is not implemented: {signature}"
                    )
                source_kind = "require_exact"
            elif (
                (derive_violation_values or safe_boundary_values)
                and index == len(sequence) - 1
                and parameter_name in terminal_names
            ):
                if terminal_value is None:
                    raise MaterializationError(
                        f"cannot derive violation boundary for {property_name}"
                    )
                value = terminal_value
                source_kind = (
                    "property_safe_boundary"
                    if safe_boundary_values
                    else "property_violation_boundary"
                )
            else:
                value = 0
                source_kind = "unconstrained_zero"
            values.append(int(value))
            value_sources.append(
                {"function": signature, "parameter": parameter_name, "value": value, "source": source_kind}
            )
    seed_path = write_seed(output_dir, list(sequence), values, name=name)
    metadata = {
        "contract": contract,
        "source": str(source),
        "property": property_name,
        "sequence": sequence,
        "values": value_sources,
        "rank": path.get("value_rank", path.get("original_rank", 1)),
        "value_mode": (
            "safe_boundary"
            if safe_boundary_values
            else "violation_boundary"
            if derive_violation_values
            else "fair_neutral"
        ),
        "seed": str(seed_path),
    }
    (output_dir / (Path(name).stem + ".metadata.json")).write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    return metadata


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--ranked", type=Path, required=True)
    parser.add_argument("--predicate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--property")
    parser.add_argument("--name", default="seed-0001.txt")
    parser.add_argument(
        "--fair",
        action="store_true",
        help="do not inject a property-violating terminal value; use neutral zero",
    )
    parser.add_argument(
        "--safe-boundary",
        action="store_true",
        help="seed the closest property-safe boundary value (e.g. 100 for value<=100)",
    )
    args = parser.parse_args(argv)
    try:
        result = materialize(
            args.source,
            args.contract,
            args.ranked,
            args.predicate,
            args.output_dir,
            property_name=args.property,
            name=args.name,
            derive_violation_values=not args.fair and not args.safe_boundary,
            safe_boundary_values=args.safe_boundary,
        )
    except (MaterializationError, SeedSpecError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
