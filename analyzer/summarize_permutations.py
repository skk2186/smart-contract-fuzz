import csv
import re
import sys
from collections import defaultdict
from pathlib import Path


def extract_harness_id(file_path: str) -> int | None:
    match = re.search(
        r"harness-(\d+)/seed-\d+\.log",
        file_path,
    )

    if not match:
        return None

    return int(match.group(1))


def main() -> None:
    if len(sys.argv) != 4:
        print(
            "Usage: python summarize_permutations.py "
            "<permutation-summary.csv> "
            "<manifest.csv> "
            "<output.csv>",
            file=sys.stderr,
        )
        raise SystemExit(1)

    summary_path = Path(sys.argv[1])
    manifest_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    with summary_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        experiment_rows = list(csv.DictReader(file))

    with manifest_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        manifest_rows = list(csv.DictReader(file))

    manifest = {
        int(row["harness_id"]): row
        for row in manifest_rows
    }

    grouped = defaultdict(list)

    for row in experiment_rows:
        harness_id = extract_harness_id(row["file"])

        if harness_id is not None:
            grouped[harness_id].append(row)

    output_rows = []

    for harness_id in sorted(manifest):
        rows = grouped.get(harness_id, [])

        falsified = sum(
            row["status"] == "falsified"
            for row in rows
        )

        output_rows.append(
            {
                "harness_id": harness_id,
                "sequence": manifest[harness_id]["sequence"],
                "is_correct_order": (
                    manifest[harness_id]["is_correct_order"]
                ),
                "runs": len(rows),
                "falsified_runs": falsified,
                "success_rate": (
                    round(falsified / len(rows), 4)
                    if rows
                    else 0
                ),
            }
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
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
                "runs",
                "falsified_runs",
                "success_rate",
            ],
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
