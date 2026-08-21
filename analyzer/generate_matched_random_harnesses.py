#!/usr/bin/env python3

"""Generate deduplicated Harnesses from a frozen matched-random schedule."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path


PRAGMA_PATTERN = re.compile(r"pragma\s+solidity\s+([^;]+);")
SIGNATURE_PATTERN = re.compile(r"^([A-Za-z_]\w*)\((.*)\)$")


def sanitize_identifier(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not result:
        raise ValueError("Empty Solidity identifier")
    if result[0].isdigit():
        result = "_" + result
    return result


def pascal_identifier(value: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", value)
    result = "".join(part[:1].upper() + part[1:] for part in parts)
    return sanitize_identifier(result or "Case")


def parameter_declaration(solidity_type: str, name: str) -> str:
    if "mapping" in solidity_type or solidity_type.startswith("function"):
        raise ValueError(f"Unsupported Harness parameter type: {solidity_type}")
    if solidity_type in {"bytes", "string"} or "[" in solidity_type:
        return f"{solidity_type} memory {name}"
    return f"{solidity_type} {name}"


def parse_signature(signature: str) -> tuple[str, list[str]]:
    match = SIGNATURE_PATTERN.fullmatch(signature.strip())
    if match is None:
        raise ValueError(f"Invalid function signature: {signature}")
    function_name = match.group(1)
    type_text = match.group(2).strip()
    if not type_text:
        return function_name, []
    # Current V1 signatures contain scalar and array types, not tuples.
    types = [item.strip() for item in type_text.split(",")]
    if any(not item for item in types):
        raise ValueError(f"Invalid parameter list: {signature}")
    return function_name, types


def source_pragma(source: Path, fallback: str) -> str:
    text = source.read_text(encoding="utf-8", errors="strict")
    match = PRAGMA_PATTERN.search(text)
    return match.group(1).strip() if match else fallback


def relative_import(source: Path, output: Path) -> str:
    value = os.path.relpath(source.resolve(), output.parent.resolve())
    value = value.replace(os.sep, "/")
    return value if value.startswith(".") else "./" + value


def render_sequence(sequence: list[str]) -> tuple[str, list[str]]:
    parameters: list[str] = []
    calls: list[str] = []
    for call_index, signature in enumerate(sequence):
        function_name, types = parse_signature(signature)
        argument_names: list[str] = []
        for parameter_index, solidity_type in enumerate(types):
            name = f"arg_{call_index}_{parameter_index}"
            parameters.append(parameter_declaration(solidity_type, name))
            argument_names.append(name)
        calls.append(
            f"        target.{function_name}({', '.join(argument_names)});"
        )
    return ", ".join(parameters), calls


def render_harness(
    source: Path,
    output: Path,
    compiler: str,
    target_contract: str,
    harness_contract: str,
    sequences: list[list[str]],
    properties: list[str],
) -> str:
    functions: list[str] = []
    for sequence_index, sequence in enumerate(sequences, start=1):
        parameters, calls = render_sequence(sequence)
        comment = " -> ".join(sequence)
        functions.append(
            "\n    /*\n"
            f"     * Frozen matched-random sequence: {comment}\n"
            "     */\n"
            f"    function matched_random_sequence_{sequence_index}({parameters}) public {{\n"
            + "\n".join(calls)
            + "\n    }\n"
        )

    proxies: list[str] = []
    for signature in properties:
        name, types = parse_signature(signature)
        if types:
            raise ValueError(f"Property must have no parameters: {signature}")
        proxies.append(
            "\n"
            f"    function {name}() public returns (bool) {{\n"
            f"        return target.{name}();\n"
            "    }\n"
        )

    return (
        "// SPDX-License-Identifier: MIT\n"
        f"pragma solidity {source_pragma(source, compiler)};\n\n"
        f'import "{relative_import(source, output)}";\n\n'
        f"contract {harness_contract} {{\n"
        f"    {target_contract} public target;\n\n"
        "    constructor() {\n"
        f"        target = new {target_contract}();\n"
        "    }\n"
        + "".join(functions)
        + "".join(proxies)
        + "}\n"
    )


def load_cases(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    cases = {row["benchmark"]: row for row in rows}
    if len(cases) != len(rows):
        raise ValueError("Duplicate benchmark in cases manifest")
    return cases


def load_candidate_data(
    project_root: Path, case: dict[str, str]
) -> tuple[list[list[str]], list[str]]:
    path = project_root / case["sequence_json"]
    data = json.loads(path.read_text(encoding="utf-8"))
    contract_data = data.get(case["target_contract"])
    if contract_data is None:
        raise ValueError(f"Target missing from candidate JSON: {case['benchmark']}")
    paths = [entry["sequence"] for entry in contract_data.get("paths", [])]
    properties = contract_data.get("property_functions", [])
    if not paths or not properties:
        raise ValueError(f"Incomplete candidate JSON: {case['benchmark']}")
    return paths, properties


def selection_hash(sequences: list[list[str]]) -> str:
    canonical = json.dumps(
        sequences, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def generate(
    project_root: Path,
    cases_path: Path,
    schedule_path: Path,
    output_root: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    cases = load_cases(cases_path)
    with schedule_path.open("r", encoding="utf-8", newline="") as handle:
        schedule = list(csv.DictReader(handle))
    if not schedule:
        raise ValueError("Matched-random schedule is empty")

    candidate_cache: dict[str, tuple[list[list[str]], list[str]]] = {}
    harness_rows: dict[tuple[str, str], dict[str, str]] = {}
    execution_rows: list[dict[str, str]] = []

    for row in schedule:
        benchmark = row["benchmark"]
        if benchmark not in cases:
            raise ValueError(f"Schedule benchmark missing from cases: {benchmark}")
        case = cases[benchmark]
        if benchmark not in candidate_cache:
            candidate_cache[benchmark] = load_candidate_data(project_root, case)
        paths, properties = candidate_cache[benchmark]
        indices = [
            int(value) - 1
            for value in row["selected_candidate_indices"].split(";")
        ]
        if any(index < 0 or index >= len(paths) for index in indices):
            raise ValueError(f"Candidate index out of range: {benchmark}")
        sequences = [paths[index] for index in indices]
        if selection_hash(sequences) != row["selection_sha256"]:
            raise ValueError(f"Selection hash mismatch: {benchmark}")

        key_text = "-".join(f"{index + 1:03d}" for index in indices)
        harness_key = (benchmark, key_text)
        if harness_key not in harness_rows:
            harness_contract = (
                "MatchedRandomV1"
                + pascal_identifier(benchmark)
                + "C"
                + "_".join(f"{index + 1:03d}" for index in indices)
                + "Harness"
            )
            output = output_root / benchmark / f"candidate-{key_text}.sol"
            source = project_root / case["source_file"]
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                render_harness(
                    source,
                    output,
                    case["compiler"],
                    case["target_contract"],
                    harness_contract,
                    sequences,
                    properties,
                ),
                encoding="utf-8",
            )
            harness_rows[harness_key] = {
                "cohort": case["cohort"],
                "benchmark": benchmark,
                "selected_candidate_indices": row["selected_candidate_indices"],
                "selected_sequences": row["selected_sequences"],
                "selection_sha256": row["selection_sha256"],
                "harness_file": output.relative_to(project_root).as_posix(),
                "harness_contract": harness_contract,
                "compiler": case["compiler"],
                "harness_config": case["harness_config"],
                "semantic_classification": case["semantic_classification"],
            }

        harness = harness_rows[harness_key]
        execution_rows.append(
            {
                "cohort": case["cohort"],
                "benchmark": benchmark,
                "method": "matched-random-k1",
                "fuzz_seed": row["fuzz_seed"],
                "schedule_seed": row["schedule_seed"],
                "selection_id": row["selection_id"],
                "selected_candidate_indices": row["selected_candidate_indices"],
                "selection_sha256": row["selection_sha256"],
                "harness_file": harness["harness_file"],
                "harness_contract": harness["harness_contract"],
                "compiler": case["compiler"],
                "config_file": case["harness_config"],
                "semantic_classification": case["semantic_classification"],
            }
        )

    return list(harness_rows.values()), execution_rows


def write_csv(path: Path, rows: list[dict[str, str]], delimiter: str = ",") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=tuple(rows[0].keys()), delimiter=delimiter
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--schedule", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--harness-manifest", required=True, type=Path)
    parser.add_argument("--execution-manifest", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    output_root = args.output_root
    if not output_root.is_absolute():
        output_root = project_root / output_root
    harness_rows, execution_rows = generate(
        project_root,
        args.cases,
        args.schedule,
        output_root,
    )
    write_csv(args.harness_manifest, harness_rows)
    write_csv(args.execution_manifest, execution_rows, delimiter="\t")
    print(
        f"Generated unique Harnesses: {len(harness_rows)}; "
        f"execution rows: {len(execution_rows)}"
    )


if __name__ == "__main__":
    main()
