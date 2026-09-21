import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from slither.slither import Slither


PRAGMA_PATTERN = re.compile(
    r"pragma\s+solidity\s+([^;]+);"
)


def extract_solidity_pragma(
    source_path: Path,
    fallback: str | None = None,
) -> str:
    text = source_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    match = PRAGMA_PATTERN.search(text)

    if match:
        return match.group(1).strip()

    if fallback:
        return fallback.strip()

    raise ValueError(
        f"No Solidity pragma found in {source_path}"
    )


def property_proxy_mutability(function) -> str:
    """
    A proxy that calls an external pure function cannot safely be
    declared pure because it reads the target contract reference.

    Therefore:
    - source view/pure -> proxy view
    - source nonpayable/payable -> proxy non-view
    """
    if (
        getattr(function, "view", False)
        or getattr(function, "pure", False)
    ):
        return " view"

    return ""


def sanitize_identifier(value: str) -> str:
    result = re.sub(r"[^a-zA-Z0-9_]", "_", value)

    if not result:
        raise ValueError("Empty Solidity identifier")

    if result[0].isdigit():
        result = "_" + result

    return result


def property_function_base_name(name: str) -> str:
    return name.split("(", 1)[0]


def property_function_names_match(
    candidate: str,
    requested: str,
) -> bool:
    candidate = candidate.strip()
    requested = requested.strip()

    if "(" in requested:
        return candidate == requested

    return (
        candidate == requested
        or property_function_base_name(candidate) == requested
    )


def parameter_declaration(
    solidity_type: str,
    parameter_name: str,
) -> str:
    """
    生成 Harness 函数参数。

    当前原型支持：
    - uint/int
    - address
    - bool
    - bytes1~bytes32
    - bytes/string
    - 一维或多维数组

    mapping 和 function 类型暂不支持。
    """
    if "mapping" in solidity_type:
        raise ValueError(
            f"Unsupported mapping parameter: {solidity_type}"
        )

    if solidity_type.startswith("function"):
        raise ValueError(
            f"Unsupported function parameter: {solidity_type}"
        )

    requires_memory = (
        solidity_type in {"bytes", "string"}
        or "[" in solidity_type
    )

    if requires_memory:
        return f"{solidity_type} memory {parameter_name}"

    return f"{solidity_type} {parameter_name}"


def find_contract(slither: Slither, contract_name: str):
    for contract in slither.contracts:
        if contract.name == contract_name:
            return contract

    available = ", ".join(
        contract.name for contract in slither.contracts
    )
    raise ValueError(
        f"Contract {contract_name!r} not found. "
        f"Available contracts: {available}"
    )


def collect_target_functions(contract) -> dict[str, Any]:
    """
    收集目标合约所有可外部调用的函数，包含继承而来的函数
    过滤构造函数、fallback、receive，仅保留 public/external 可见性
    返回以 full_name 为键的函数字典
    """
    result = {}

    for function in contract.functions:
        if getattr(function, "is_constructor", False):
            continue

        if getattr(function, "is_fallback", False):
            continue

        if getattr(function, "is_receive", False):
            continue

        if function.visibility not in {
            "public",
            "external",
        }:
            continue

        result[function.full_name] = function

    return result


def build_function_map(contract) -> dict[str, Any]:
    return collect_target_functions(contract)


def resolve_property_function(
    function_map: dict[str, Any],
    requested: str,
) -> tuple[str, Any]:
    candidates = []

    for full_name, function in function_map.items():
        function_name = getattr(function, "name", "")
        if not (
            full_name.startswith("echidna_")
            or function_name.startswith("echidna_")
        ):
            continue

        if "(" in requested:
            matches = full_name == requested
        else:
            matches = (
                full_name == requested
                or property_function_base_name(full_name)
                == requested
                or function_name == requested
            )

        if matches:
            candidates.append((full_name, function))

    if not candidates:
        raise ValueError(
            f"Requested property {requested!r} was not found "
            "in the target contract"
        )

    if len(candidates) > 1:
        names = ", ".join(
            full_name
            for full_name, _ in candidates
        )
        raise ValueError(
            f"Requested property {requested!r} is ambiguous: {names}"
        )

    full_name, function = candidates[0]

    if function.parameters:
        raise ValueError(
            f"Selected property {full_name} has parameters; "
            "the current Harness does not support property parameters"
        )

    return full_name, function


def find_property_functions(contract) -> list[Any]:
    properties = []

    for function in collect_target_functions(contract).values():
        if not function.name.startswith("echidna_"):
            continue

        if function.parameters:
            continue

        properties.append(function)

    return properties


def build_sequence_function(
    sequence_index: int,
    sequence: list[str],
    function_map: dict[str, Any],
    function_prefix: str,
) -> str:
    harness_parameters: list[str] = []
    calls: list[str] = []

    for call_index, signature in enumerate(sequence):
        if signature not in function_map:
            raise ValueError(
                f"Function signature not found: {signature}"
            )

        function = function_map[signature]
        argument_names: list[str] = []

        for parameter_index, parameter in enumerate(
            function.parameters
        ):
            parameter_name = (
                f"arg_{sequence_index}_"
                f"{call_index}_{parameter_index}"
            )
            solidity_type = str(parameter.type)

            harness_parameters.append(
                parameter_declaration(
                    solidity_type,
                    parameter_name,
                )
            )
            argument_names.append(parameter_name)

        arguments = ", ".join(argument_names)

        calls.append(
            f"        target.{function.name}({arguments});"
        )

    sequence_text = " -> ".join(sequence)
    parameter_text = ", ".join(harness_parameters)

    function_name = sanitize_identifier(
        f"{function_prefix}_sequence_{sequence_index}"
    )

    call_text = "\n".join(calls)

    return f"""
    /*
     * Generated sequence:
     * {sequence_text}
     */
    function {function_name}({parameter_text}) public {{
{call_text}
    }}
"""


def build_property_proxy(function) -> str:
    function_name = function.name
    mutability = property_proxy_mutability(function)

    return f"""
    function {function_name}()
        public{mutability}
        returns (bool)
    {{
        return target.{function_name}();
    }}
"""


def load_paths(
    sequence_json: Path,
    contract_name: str,
    top_k: int,
    property_function: str | None = None,
) -> list[list[str]]:
    with sequence_json.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if contract_name not in data:
        raise ValueError(
            f"Contract {contract_name!r} not found in "
            f"{sequence_json}"
        )

    contract_data = data[contract_name]
    path_entries = contract_data.get("paths", [])

    if not path_entries:
        raise ValueError(
            f"No paths found for {contract_name}"
        )

    if property_function is not None:
        sequence_property = contract_data.get("property_function")

        if not isinstance(sequence_property, str):
            raise ValueError(
                "Per-property sequence JSON must record "
                "property_function"
            )

        if not property_function_names_match(
            sequence_property,
            property_function,
        ):
            raise ValueError(
                "Sequence JSON property_function "
                f"{sequence_property!r} does not match "
                f"requested property {property_function!r}"
            )

    paths = []

    for entry in path_entries:
        if property_function is not None:
            entry_property = entry.get("property_function")

            if not isinstance(entry_property, str):
                raise ValueError(
                    "Per-property sequence path is missing "
                    "property_function"
                )

            if not property_function_names_match(
                entry_property,
                property_function,
            ):
                raise ValueError(
                    "Sequence path property_function "
                    f"{entry_property!r} does not match "
                    f"requested property {property_function!r}"
                )

        sequence = entry.get("sequence", [])

        if len(sequence) < 2:
            continue

        paths.append(sequence)

        if len(paths) >= top_k:
            break

    if not paths:
        raise ValueError(
            "No usable transaction sequences found"
        )

    return paths


def relative_import_path(
    source_file: Path,
    output_file: Path,
) -> str:
    relative = os.path.relpath(
        source_file.resolve(),
        output_file.parent.resolve(),
    )

    relative = relative.replace(os.sep, "/")

    if not relative.startswith("."):
        relative = "./" + relative

    return relative


def generate_harness(
    source_file: Path,
    sequence_json: Path,
    target_contract_name: str,
    harness_contract_name: str,
    output_file: Path,
    function_prefix: str,
    top_k: int,
    solidity_pragma: str | None = None,
    property_function: str | None = None,
) -> None:
    slither = Slither(str(source_file))
    target_contract = find_contract(
        slither,
        target_contract_name,
    )

    constructor = target_contract.constructor

    if constructor and constructor.parameters:
        raise ValueError(
            "Contracts with constructor parameters are not "
            "supported in the current prototype"
        )

    function_map = build_function_map(target_contract)

    selected_property_name = None

    if property_function is not None:
        selected_property_name, selected_property = (
            resolve_property_function(
                function_map,
                property_function,
            )
        )
        property_functions = [selected_property]
    else:
        property_functions = find_property_functions(
            target_contract
        )

        if not property_functions:
            raise ValueError(
                "No zero-argument echidna_ property found"
            )

    paths = load_paths(
        sequence_json,
        target_contract_name,
        top_k,
        property_function=selected_property_name,
    )

    sequence_functions = []

    for index, sequence in enumerate(paths, start=1):
        sequence_functions.append(
            build_sequence_function(
                sequence_index=index,
                sequence=sequence,
                function_map=function_map,
                function_prefix=function_prefix,
            )
        )

    property_proxies = [
        build_property_proxy(function)
        for function in property_functions
    ]

    import_path = relative_import_path(
        source_file,
        output_file,
    )
    pragma_expression = extract_solidity_pragma(
        source_file,
        fallback=solidity_pragma,
    )

    harness_contract_name = sanitize_identifier(
        harness_contract_name
    )

    target_property_comment = ""
    if selected_property_name is not None:
        target_property_comment = (
            f"    // Target property: {selected_property_name}\n"
        )

    source = f"""// SPDX-License-Identifier: MIT
pragma solidity {pragma_expression};

import "{import_path}";

contract {harness_contract_name} {{
{target_property_comment}    {target_contract_name} public target;

    constructor() {{
        target = new {target_contract_name}();
    }}
{''.join(sequence_functions)}
{''.join(property_proxies)}
}}
"""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file.write_text(
        source,
        encoding="utf-8",
    )

    print(f"Generated Harness: {output_file}")
    print(f"Generated sequence entries: {len(paths)}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate an Echidna Harness from transaction "
            "sequence paths"
        )
    )

    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Original Solidity source file",
    )
    parser.add_argument(
        "--sequences",
        required=True,
        type=Path,
        help="JSON file containing generated paths",
    )
    parser.add_argument(
        "--target-contract",
        required=True,
        help="Original target contract name",
    )
    parser.add_argument(
        "--harness-contract",
        required=True,
        help="Generated Harness contract name",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output Solidity Harness file",
    )
    parser.add_argument(
        "--prefix",
        default="guided",
        help="Generated sequence function prefix",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=1,
        help="Maximum number of paths to generate",
    )
    parser.add_argument(
        "--solidity-pragma",
        help=(
            "Fallback Solidity pragma expression when the "
            "source file has no pragma"
        ),
    )
    parser.add_argument(
        "--property",
        dest="property_function",
        help=(
            "Generate only the proxy and paths for this explicit "
            "echidna_ property."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.top_k < 1:
        raise ValueError("--top-k must be at least 1")

    generate_harness(
        source_file=args.source,
        sequence_json=args.sequences,
        target_contract_name=args.target_contract,
        harness_contract_name=args.harness_contract,
        output_file=args.output,
        function_prefix=args.prefix,
        top_k=args.top_k,
        solidity_pragma=args.solidity_pragma,
        property_function=args.property_function,
    )


if __name__ == "__main__":
    main()
