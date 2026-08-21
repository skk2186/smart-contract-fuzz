#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

from slither.slither import Slither

from abstract_values import (
    collect_state_variables,
    contains_unknown,
    ensure_predicate,
    exact_constant,
    negate_predicate,
    unknown_expression,
)


class PredicateParseError(ValueError):
    pass


TOKEN_PATTERN = re.compile(
    r"""
    (?P<WS>\s+)
    |(?P<AND>&&)
    |(?P<OR>\|\|)
    |(?P<EQ>==)
    |(?P<NE>!=)
    |(?P<LE><=)
    |(?P<GE>>=)
    |(?P<LT><)
    |(?P<GT>>)
    |(?P<NOT>!)
    |(?P<LPAREN>\()
    |(?P<RPAREN>\))
    |(?P<COMMA>,)
    |(?P<NUMBER>0[xX][0-9a-fA-F]+|\d+)
    |(?P<ID>[A-Za-z_][A-Za-z0-9_\.]*)
    """,
    re.VERBOSE,
)


COMPARISON_OPERATORS = {
    "EQ": "eq",
    "NE": "ne",
    "LT": "lt",
    "LE": "le",
    "GT": "gt",
    "GE": "ge",
}


def remove_comments(source: str) -> str:
    source = re.sub(
        r"/\*.*?\*/",
        " ",
        source,
        flags=re.DOTALL,
    )

    source = re.sub(
        r"//[^\n]*",
        " ",
        source,
    )

    return source


def source_content(item: Any) -> str:
    mapping = getattr(
        item,
        "source_mapping",
        None,
    )

    if mapping is None:
        return ""

    content = getattr(
        mapping,
        "content",
        "",
    )

    return content or ""


def state_variable_key(variable: Any) -> str:
    canonical_name = getattr(
        variable,
        "canonical_name",
        None,
    )

    if canonical_name:
        return str(canonical_name)

    return str(variable.name)


def function_key(function: Any) -> str:
    return str(function.full_name)


class TokenStream:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: list[tuple[str, str]] = []
        self.position = 0
        self._tokenize()

    def _tokenize(self) -> None:
        position = 0

        while position < len(self.source):
            match = TOKEN_PATTERN.match(
                self.source,
                position,
            )

            if match is None:
                snippet = self.source[
                    position:position + 30
                ]

                raise PredicateParseError(
                    "Unsupported token near: "
                    f"{snippet!r}"
                )

            token_type = match.lastgroup
            token_value = match.group(0)
            position = match.end()

            if token_type == "WS":
                continue

            if token_type is None:
                raise PredicateParseError(
                    "Token without type"
                )

            self.tokens.append(
                (token_type, token_value)
            )

    def peek(
        self,
        token_type: str | None = None,
    ) -> tuple[str, str] | bool | None:
        if self.position >= len(self.tokens):
            return None if token_type is None else False

        token = self.tokens[self.position]

        if token_type is None:
            return token

        return token[0] == token_type

    def consume(
        self,
        token_type: str | None = None,
    ) -> tuple[str, str]:
        if self.position >= len(self.tokens):
            raise PredicateParseError(
                "Unexpected end of expression"
            )

        token = self.tokens[self.position]

        if (
            token_type is not None
            and token[0] != token_type
        ):
            raise PredicateParseError(
                f"Expected {token_type}, "
                f"found {token[0]} ({token[1]!r})"
            )

        self.position += 1
        return token

    def at_end(self) -> bool:
        return self.position >= len(self.tokens)


class PredicateParser:
    def __init__(
        self,
        source: str,
        resolve_identifier: Callable[
            [str],
            dict[str, Any],
        ],
        resolve_call: Callable[
            [str],
            dict[str, Any],
        ],
    ) -> None:
        self.source = source
        self.stream = TokenStream(source)
        self.resolve_identifier = resolve_identifier
        self.resolve_call = resolve_call

    def parse(
        self,
        *,
        as_predicate: bool = True,
    ) -> dict[str, Any]:
        result = self.parse_or()

        if not self.stream.at_end():
            token = self.stream.peek()

            raise PredicateParseError(
                "Unexpected trailing token: "
                f"{token}"
            )

        if as_predicate:
            return ensure_predicate(result)

        return result

    def parse_or(self) -> dict[str, Any]:
        left = self.parse_and()

        while self.stream.peek("OR"):
            self.stream.consume("OR")
            right = self.parse_and()

            left = {
                "op": "or",
                "left": ensure_predicate(left),
                "right": ensure_predicate(right),
            }

        return left

    def parse_and(self) -> dict[str, Any]:
        left = self.parse_comparison()

        while self.stream.peek("AND"):
            self.stream.consume("AND")
            right = self.parse_comparison()

            left = {
                "op": "and",
                "left": ensure_predicate(left),
                "right": ensure_predicate(right),
            }

        return left

    def parse_comparison(self) -> dict[str, Any]:
        left = self.parse_unary()
        token = self.stream.peek()

        if (
            isinstance(token, tuple)
            and token[0] in COMPARISON_OPERATORS
        ):
            token_type, _ = self.stream.consume()
            right = self.parse_unary()

            return {
                "op": COMPARISON_OPERATORS[
                    token_type
                ],
                "left": left,
                "right": right,
            }

        return left

    def parse_unary(self) -> dict[str, Any]:
        if self.stream.peek("NOT"):
            self.stream.consume("NOT")

            return {
                "op": "not",
                "value": ensure_predicate(
                    self.parse_unary()
                ),
            }

        return self.parse_primary()

    def parse_primary(self) -> dict[str, Any]:
        if self.stream.peek("LPAREN"):
            self.stream.consume("LPAREN")
            expression = self.parse_or()
            self.stream.consume("RPAREN")
            return expression

        if self.stream.peek("NUMBER"):
            _, value = self.stream.consume(
                "NUMBER"
            )

            integer = int(
                value,
                16 if value.lower().startswith(
                    "0x"
                ) else 10,
            )

            return exact_constant(integer)

        if self.stream.peek("ID"):
            _, identifier = self.stream.consume(
                "ID"
            )

            if identifier == "true":
                return exact_constant(True)

            if identifier == "false":
                return exact_constant(False)

            if self.stream.peek("LPAREN"):
                return self.parse_call(identifier)

            return self.resolve_identifier(
                identifier
            )

        token = self.stream.peek()

        raise PredicateParseError(
            f"Unsupported primary token: {token}"
        )

    def parse_call(
        self,
        identifier: str,
    ) -> dict[str, Any]:
        self.stream.consume("LPAREN")

        if identifier == "address":
            if not self.stream.peek("NUMBER"):
                return self.consume_unknown_call(
                    identifier,
                    "Only address(0) is supported",
                )

            _, number = self.stream.consume(
                "NUMBER"
            )

            self.stream.consume("RPAREN")

            value = int(
                number,
                16 if number.lower().startswith(
                    "0x"
                ) else 10,
            )

            if value != 0:
                return unknown_expression(
                    f"address({number})",
                    "Only address(0) is supported",
                )

            return exact_constant(
                "0x0000000000000000000000000000000000000000"
            )

        if self.stream.peek("RPAREN"):
            self.stream.consume("RPAREN")
            return self.resolve_call(identifier)

        return self.consume_unknown_call(
            identifier,
            "Calls with arguments are unsupported",
        )

    def consume_unknown_call(
        self,
        identifier: str,
        reason: str,
    ) -> dict[str, Any]:
        depth = 1
        fragments = [identifier, "("]

        while (
            not self.stream.at_end()
            and depth > 0
        ):
            token_type, token_value = (
                self.stream.consume()
            )

            fragments.append(token_value)

            if token_type == "LPAREN":
                depth += 1
            elif token_type == "RPAREN":
                depth -= 1

        return unknown_expression(
            "".join(fragments),
            reason,
        )


class ContractPredicateExtractor:
    def __init__(
        self,
        source_path: Path,
        contract_name: str,
    ) -> None:
        self.source_path = source_path
        self.slither = Slither(str(source_path))

        contracts = [
            contract
            for contract in self.slither.contracts
            if contract.name == contract_name
        ]

        if len(contracts) != 1:
            names = sorted(
                contract.name
                for contract in self.slither.contracts
            )

            raise ValueError(
                f"Expected exactly one contract named "
                f"{contract_name!r}; found "
                f"{len(contracts)}. Available: {names}"
            )

        self.contract = contracts[0]

        self.state_variables_by_name: dict[
            str,
            str | None,
        ] = {}

        self.state_variable_objects: dict[
            str,
            Any,
        ] = {}

        self.functions_by_name: dict[
            str,
            list[Any],
        ] = {}

        self._index_contract()

    def accessible_state_variables(
        self,
    ) -> list[Any]:
        """
        Collect state variables accessible from the target contract.

        Different Slither versions may expose inherited state
        variables differently through state_variables and
        state_variables_ordered. Therefore, explicitly traverse the
        inheritance hierarchy and deduplicate by canonical name.
        """
        candidates: list[Any] = []

        for attribute_name in (
            "state_variables_ordered",
            "state_variables",
        ):
            values = getattr(
                self.contract,
                attribute_name,
                [],
            )

            if values:
                candidates.extend(values)

        contracts_to_visit = [
            self.contract,
            *self.contract.inheritance,
        ]

        for contract in contracts_to_visit:
            declared_variables = getattr(
                contract,
                "state_variables_declared",
                [],
            )

            if declared_variables:
                candidates.extend(
                    declared_variables
                )

        result: list[Any] = []
        seen_canonical_names: set[str] = set()

        for variable in candidates:
            canonical_name = state_variable_key(
                variable
            )

            if canonical_name in seen_canonical_names:
                continue

            seen_canonical_names.add(
                canonical_name
            )
            result.append(variable)

        return result

    def _index_contract(self) -> None:
        state_keys_by_source_name: dict[
            str,
            list[str],
        ] = {}

        for variable in (
            self.accessible_state_variables()
        ):
            source_name = str(variable.name)
            canonical_name = state_variable_key(
                variable
            )

            state_keys_by_source_name.setdefault(
                source_name,
                [],
            ).append(canonical_name)

            self.state_variable_objects[
                canonical_name
            ] = variable

        for (
            source_name,
            canonical_names,
        ) in state_keys_by_source_name.items():
            unique_names = list(
                dict.fromkeys(canonical_names)
            )

            if len(unique_names) == 1:
                self.state_variables_by_name[
                    source_name
                ] = unique_names[0]
            else:
                # The same source-level name resolves to multiple
                # inherited variables, so simple textual resolution
                # is unsafe.
                self.state_variables_by_name[
                    source_name
                ] = None

        for function in self.contract.functions:
            self.functions_by_name.setdefault(
                str(function.name),
                [],
            ).append(function)

    def resolve_identifier(
        self,
        identifier: str,
    ) -> dict[str, Any]:
        normalized = identifier

        if normalized.startswith("this."):
            normalized = normalized.split(
                "."
            )[-1]

        key = self.state_variables_by_name.get(
            normalized
        )

        if key:
            return {
                "kind": "state_variable",
                "name": key,
                "source_name": normalized,
            }

        if (
            normalized
            in self.state_variables_by_name
            and key is None
        ):
            return unknown_expression(
                identifier,
                "Ambiguous inherited state variable",
            )

        return unknown_expression(
            identifier,
            "Identifier is not a uniquely resolved "
            "state variable",
        )

    def resolve_call(
        self,
        call_name: str,
        stack: tuple[str, ...],
    ) -> dict[str, Any]:
        normalized = call_name.split(".")[-1]

        state_key = (
            self.state_variables_by_name.get(
                normalized
            )
        )

        if state_key:
            return {
                "kind": "state_variable",
                "name": state_key,
                "source_name": normalized,
                "resolved_from": "public_getter",
            }

        candidates = [
            function
            for function in self.functions_by_name.get(
                normalized,
                [],
            )
            if len(function.parameters) == 0
        ]

        if len(candidates) != 1:
            return unknown_expression(
                f"{call_name}()",
                "Zero-argument getter could not be "
                "uniquely resolved",
            )

        function = candidates[0]
        key = function_key(function)

        if key in stack:
            return unknown_expression(
                f"{call_name}()",
                "Recursive getter call",
            )

        return self.parse_function_return(
            function,
            stack + (key,),
            as_predicate=False,
        )

    def parse_expression(
        self,
        expression_source: str,
        stack: tuple[str, ...],
        *,
        as_predicate: bool,
    ) -> dict[str, Any]:
        parser = PredicateParser(
            expression_source,
            resolve_identifier=(
                self.resolve_identifier
            ),
            resolve_call=lambda name: (
                self.resolve_call(
                    name,
                    stack,
                )
            ),
        )

        return parser.parse(
            as_predicate=as_predicate
        )

    def find_return_expression(
        self,
        function: Any,
    ) -> str | None:
        content = remove_comments(
            source_content(function)
        )

        matches = re.findall(
            r"\breturn\s+(.+?);",
            content,
            flags=re.DOTALL,
        )

        if len(matches) != 1:
            return None

        return matches[0].strip()

    def parse_function_return(
        self,
        function: Any,
        stack: tuple[str, ...] = (),
        *,
        as_predicate: bool = False,
    ) -> dict[str, Any]:
        expression_source = (
            self.find_return_expression(function)
        )

        if expression_source is None:
            return unknown_expression(
                function_key(function),
                "Function must contain exactly one "
                "return expression",
            )

        try:
            return self.parse_expression(
                expression_source,
                stack,
                as_predicate=as_predicate,
            )
        except PredicateParseError as error:
            return unknown_expression(
                expression_source,
                str(error),
            )

    def simple_value_expression(
        self,
        source: str,
        parameters: set[str],
    ) -> dict[str, Any]:
        value = source.strip()

        while (
            value.startswith("(")
            and value.endswith(")")
        ):
            value = value[1:-1].strip()

        if value == "true":
            return exact_constant(True)

        if value == "false":
            return exact_constant(False)

        if re.fullmatch(
            r"0[xX][0-9a-fA-F]+|\d+",
            value,
        ):
            return exact_constant(
                int(
                    value,
                    16 if value.lower().startswith(
                        "0x"
                    ) else 10,
                )
            )

        address_match = re.fullmatch(
            r"address\s*\(\s*0\s*\)",
            value,
        )

        if address_match:
            return exact_constant(
                "0x0000000000000000000000000000000000000000"
            )

        cast_match = re.fullmatch(
            r"(?:u?int(?:8|16|32|64|128|256)?|"
            r"bytes\d+)\s*\(\s*(\d+)\s*\)",
            value,
        )

        if cast_match:
            return exact_constant(
                int(cast_match.group(1))
            )

        if value in parameters:
            return {
                "kind": "parameter",
                "name": value,
            }

        state_key = (
            self.state_variables_by_name.get(
                value
            )
        )

        if state_key:
            return {
                "kind": "state_variable",
                "name": state_key,
                "source_name": value,
            }

        return unknown_expression(
            value,
            "Unsupported assignment expression",
        )

    def extract_function_writes(
        self,
        function: Any,
    ) -> list[dict[str, Any]]:
        content = remove_comments(
            source_content(function)
        )

        parameters = {
            str(parameter.name)
            for parameter in function.parameters
            if parameter.name
        }

        matches: list[
            tuple[int, dict[str, Any]]
        ] = []

        for source_name, canonical_name in (
            self.state_variables_by_name.items()
        ):
            if canonical_name is None:
                continue

            pattern = re.compile(
                rf"""
                (?<![A-Za-z0-9_\.])
                {re.escape(source_name)}
                \s*
                (?P<operator>\+=|-=|=(?!=))
                \s*
                (?P<rhs>[^;]+)
                ;
                """,
                re.VERBOSE | re.DOTALL,
            )

            for match in pattern.finditer(content):
                rhs_source = (
                    match.group("rhs").strip()
                )

                matches.append(
                    (
                        match.start(),
                        {
                            "variable": canonical_name,
                            "source_name": source_name,
                            "operator": match.group(
                                "operator"
                            ),
                            "expression": (
                                self.simple_value_expression(
                                    rhs_source,
                                    parameters,
                                )
                            ),
                            "source": (
                                f"{source_name} "
                                f"{match.group('operator')} "
                                f"{rhs_source}"
                            ),
                        },
                    )
                )

        matches.sort(key=lambda item: item[0])

        return [
            item[1]
            for item in matches
        ]

    def default_initial_value(
        self,
        variable: Any,
    ) -> dict[str, Any]:
        expression = getattr(
            variable,
            "expression",
            None,
        )

        if expression is not None:
            parsed = self.simple_value_expression(
                str(expression),
                set(),
            )

            if not contains_unknown(parsed):
                return parsed

        type_name = str(variable.type)

        if type_name == "bool":
            return exact_constant(False)

        if type_name.startswith(
            ("uint", "int", "enum")
        ):
            return exact_constant(0)

        if type_name.startswith(
            "address"
        ):
            return exact_constant(
                "0x0000000000000000000000000000000000000000"
            )

        return unknown_expression(
            type_name,
            "No scalar default model",
        )

    def extract(self) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        functions: dict[str, Any] = {}
        initial_state: dict[str, Any] = {}
        state_variable_types: dict[str, str] = {}

        for canonical_name, variable in (
            self.state_variable_objects.items()
        ):
            initial_state[canonical_name] = (
                self.default_initial_value(
                    variable
                )
            )

            state_variable_types[
                canonical_name
            ] = str(variable.type)

        for function in self.contract.functions:
            if (
                function.visibility
                not in {"public", "external"}
            ):
                continue

            if getattr(
                function,
                "is_constructor",
                False,
            ):
                continue

            key = function_key(function)

            functions[key] = {
                "declared_in": str(
                    function.contract_declarer.name
                ),
                "parameters": [
                    {
                        "name": str(parameter.name),
                        "type": str(parameter.type),
                    }
                    for parameter in function.parameters
                ],
                "writes": (
                    self.extract_function_writes(
                        function
                    )
                ),
            }

            if not str(function.name).startswith(
                "echidna_"
            ):
                continue

            expression_source = (
                self.find_return_expression(
                    function
                )
            )

            predicate = (
                self.parse_function_return(
                    function,
                    (key,),
                    as_predicate=True,
                )
            )

            predicate = ensure_predicate(
                predicate
            )

            violation = negate_predicate(
                predicate
            )

            properties[key] = {
                "source_expression": (
                    expression_source
                ),
                "supported": not (
                    contains_unknown(predicate)
                ),
                "property_predicate": predicate,
                "violation_predicate": violation,
                "state_variables": sorted(
                    collect_state_variables(
                        predicate
                    )
                ),
            }

        return {
            "schema_version": "2.0",
            "method_version": "Full-v2.0-core",
            "source": str(self.source_path),
            "contract": self.contract.name,
            "properties": properties,
            "initial_state": initial_state,
            "state_variable_types": state_variable_types,
            "functions": functions,
        }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract Echidna property predicates and "
            "their violation predicates."
        )
    )

    parser.add_argument(
        "source",
        type=Path,
    )

    parser.add_argument(
        "--contract",
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    extractor = ContractPredicateExtractor(
        arguments.source.resolve(),
        arguments.contract,
    )

    result = extractor.extract()

    serialized = json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
        sort_keys=False,
    )

    if arguments.output:
        arguments.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        arguments.output.write_text(
            serialized + "\n",
            encoding="utf-8",
            newline="\n",
        )
    else:
        sys.stdout.write(
            serialized + "\n"
        )


if __name__ == "__main__":
    main()
