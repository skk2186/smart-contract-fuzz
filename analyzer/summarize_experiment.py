import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path


VALID_STATUSES = {
    "falsified",
    "passed",
    "budget_exhausted",
}
# A valid run has a conclusive parser status: it either falsified a
# property, exhausted the configured test budget without a counterexample,
# or reported a pass without evidence that the test budget was exhausted.


def numeric_values(rows, column):
    values = []

    for row in rows:
        value = str(row.get(column, "")).strip()

        if not value:
            continue

        values.append(float(value))

    return values


def summarize_rows(rows):
    groups = defaultdict(list)

    for row in rows:
        groups[row["method"]].append(row)

    summaries = []

    for method, method_rows in sorted(groups.items()):
        valid_rows = [
            row
            for row in method_rows
            if row["status"] in VALID_STATUSES
        ]
        startup_error_rows = [
            row
            for row in method_rows
            if row["status"] == "startup_error"
        ]
        falsified_rows = [
            row
            for row in valid_rows
            if row["status"] == "falsified"
        ]
        budget_exhausted_rows = [
            row
            for row in valid_rows
            if row["status"] == "budget_exhausted"
        ]
        passed_rows = [
            row
            for row in valid_rows
            if row["status"] == "passed"
        ]
        incomplete_rows = [
            row
            for row in method_rows
            if row["status"] == "incomplete"
        ]

        calls = numeric_values(
            falsified_rows,
            "total_calls",
        )
        fuzz_times = numeric_values(
            falsified_rows,
            "fuzz_seconds",
        )
        wall_times = numeric_values(
            valid_rows,
            "process_wall_seconds",
        )

        summaries.append(
            {
                "method": method,
                "total_logs": len(method_rows),
                "valid_runs": len(valid_rows),
                "falsified_runs": len(falsified_rows),
                "budget_exhausted_runs": len(
                    budget_exhausted_rows
                ),
                "passed_runs": len(passed_rows),
                "startup_error_runs": len(
                    startup_error_rows
                ),
                "incomplete_runs": len(incomplete_rows),
                "success_rate": (
                    round(
                        len(falsified_rows)
                        / len(valid_rows),
                        4,
                    )
                    if valid_rows
                    else ""
                ),
                "median_calls_successful": (
                    statistics.median(calls)
                    if calls
                    else ""
                ),
                "mean_calls_successful": (
                    round(statistics.mean(calls), 4)
                    if calls
                    else ""
                ),
                "median_fuzz_seconds_successful": (
                    round(statistics.median(fuzz_times), 6)
                    if fuzz_times
                    else ""
                ),
                "median_process_wall_seconds": (
                    round(statistics.median(wall_times), 6)
                    if wall_times
                    else ""
                ),
            }
        )

    return summaries


def write_summaries(summaries, output_path: Path) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "method",
        "total_logs",
        "valid_runs",
        "falsified_runs",
        "budget_exhausted_runs",
        "passed_runs",
        "startup_error_runs",
        "incomplete_runs",
        "success_rate",
        "median_calls_successful",
        "mean_calls_successful",
        "median_fuzz_seconds_successful",
        "median_process_wall_seconds",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(summaries)


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: python summarize_experiment.py "
            "<summary.csv> <group-summary.csv>",
            file=sys.stderr,
        )
        raise SystemExit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    summaries = summarize_rows(rows)
    write_summaries(summaries, output_path)

    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
