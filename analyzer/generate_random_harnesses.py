import csv
import random
from pathlib import Path


FUNCTIONS = [
    ("register", False),
    ("deposit", False),
    ("approve", False),
    ("withdraw", True),
    ("noise1", True),
    ("noise2", False),
    ("noise3", False),
    ("noise4", False),
    ("noise5", True),
    ("noise6", False),
]


def render_call(function_name: str, needs_argument: bool) -> str:
    if needs_argument:
        return f"        target.{function_name}(x);"

    return f"        target.{function_name}();"


def render_harness(sequence: list[tuple[str, bool]]) -> str:
    calls = "\n".join(
        render_call(function_name, needs_argument)
        for function_name, needs_argument in sequence
    )

    sequence_comment = " -> ".join(
        function_name
        for function_name, _ in sequence
    )

    return f"""// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import "../../benchmarks/NoisyFourStepExample.sol";

contract NoisyFourStepRandomHarness {{
    NoisyFourStepExample public target;

    constructor() {{
        target = new NoisyFourStepExample();
    }}

    /*
     * 随机生成的四步函数序列：
     * {sequence_comment}
     */
    function random_sequence_1(uint256 x) public {{
{calls}
    }}

    function echidna_value_safe() public view returns (bool) {{
        return target.value() <= 100;
    }}
}}
"""


def main() -> None:
    project_root = Path.home() / "smart-contract-fuzzing"

    output_directory = (
        project_root
        / "contracts"
        / "harnesses"
        / "random"
    )
    output_directory.mkdir(parents=True, exist_ok=True)

    manifest_path = (
        project_root
        / "results"
        / "noisy-four-step"
        / "random-sequences.csv"
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for experiment_id in range(1, 11):
        generator = random.Random(experiment_id)

        # 选择四个互不重复的函数，并随机确定顺序。
        sequence = generator.sample(FUNCTIONS, 4)

        output_path = (
            output_directory
            / f"NoisyFourStepRandomHarness-{experiment_id}.sol"
        )

        output_path.write_text(
            render_harness(sequence),
            encoding="utf-8",
        )

        rows.append(
            {
                "experiment_id": experiment_id,
                "sequence": " -> ".join(
                    function_name
                    for function_name, _ in sequence
                ),
                "file": str(output_path),
            }
        )

    with manifest_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "experiment_id",
                "sequence",
                "file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("Generated 10 random harnesses")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
