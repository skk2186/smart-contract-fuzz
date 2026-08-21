import csv
import itertools
from pathlib import Path


FUNCTIONS = [
    "register",
    "deposit",
    "approve",
    "withdraw",
]

CORRECT_SEQUENCE = (
    "register",
    "deposit",
    "approve",
    "withdraw",
)


def render_call(function_name: str) -> str:
    if function_name == "withdraw":
        return "        target.withdraw(x);"

    return f"        target.{function_name}();"


def render_harness(sequence: tuple[str, ...]) -> str:
    calls = "\n".join(render_call(name) for name in sequence)
    sequence_text = " -> ".join(sequence)

    return f"""// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/NoisyFourStepExample.sol";

contract NoisyFourStepPermutationHarness {{
    NoisyFourStepExample public target;

    constructor() {{
        target = new NoisyFourStepExample();
    }}

    /*
     * 固定关键函数集合，仅改变调用顺序：
     * {sequence_text}
     */
    function permuted_sequence_1(uint256 x) public {{
{calls}
    }}

    function echidna_value_safe() public view returns (bool) {{
        return target.value() <= 100;
    }}
}}
"""


def main() -> None:
    root = Path.home() / "smart-contract-fuzzing"

    output_directory = (
        root
        / "contracts"
        / "harnesses"
        / "permuted"
    )
    output_directory.mkdir(parents=True, exist_ok=True)

    manifest_path = (
        root
        / "results"
        / "noisy-four-step"
        / "permutation-sequences.csv"
    )

    rows = []

    permutations = list(itertools.permutations(FUNCTIONS))

    for index, sequence in enumerate(permutations, start=1):
        filename = (
            f"NoisyFourStepPermutationHarness-{index:02d}.sol"
        )
        output_path = output_directory / filename

        output_path.write_text(
            render_harness(sequence),
            encoding="utf-8",
        )

        rows.append(
            {
                "harness_id": index,
                "sequence": " -> ".join(sequence),
                "is_correct_order": sequence == CORRECT_SEQUENCE,
                "file": str(output_path),
            }
        )

    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with manifest_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "harness_id",
                "sequence",
                "is_correct_order",
                "file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} permutation harnesses")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
