#!/usr/bin/env python3

import argparse
import csv
import hashlib
import math
import platform
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = [
    "echidna-flags",
    "echidna-multi",
    "exercise2-access-control",
    "smartbugs-multifunc",
    "smartbugs-onefunc",
]
METHODS = ["original", "full-k1", "full-k5"]
VALID_STATUSES = {"falsified", "budget_exhausted", "passed"}
ALL_STATUSES = VALID_STATUSES | {"startup_error", "incomplete"}
EXPECTED_STATUS_COUNTS = {
    "falsified": 413,
    "budget_exhausted": 37,
    "passed": 0,
    "startup_error": 0,
    "incomplete": 0,
}
EXPECTED_METHOD_TOTALS = {
    "original": (144, 150),
    "full-k1": (120, 150),
    "full-k5": (149, 150),
}
PAIRWISE_COMPARISONS = [
    ("full-k1", "original", "Primary"),
    ("full-k5", "original", "Primary"),
    ("full-k1", "full-k5", "Exploratory"),
]
Z_95 = 1.959963984540054


@dataclass(frozen=True)
class Run:
    benchmark: str
    method: str
    seed: int
    status: str
    total_calls: int
    fuzz_seconds: float
    process_wall_seconds: float

    @property
    def event(self) -> int:
        return event_from_status(self.status)


@dataclass(frozen=True)
class KMPoint:
    time: float
    at_risk: int
    events: int
    censored: int
    survival_probability: float


def wilson_interval(
    successes: int,
    runs: int,
    z: float = Z_95,
) -> tuple[float, float]:
    if runs <= 0:
        raise ValueError("Wilson interval requires runs > 0")
    if successes < 0 or successes > runs:
        raise ValueError("Wilson successes must be between 0 and runs")

    proportion = successes / runs
    z_squared = z * z
    denominator = 1.0 + z_squared / runs
    center = (
        proportion + z_squared / (2.0 * runs)
    ) / denominator
    half_width = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / runs
            + z_squared / (4.0 * runs * runs)
        )
        / denominator
    )
    return max(0.0, center - half_width), min(
        1.0,
        center + half_width,
    )


def fisher_exact_two_sided(
    a: int,
    b: int,
    c: int,
    d: int,
) -> float:
    values = (a, b, c, d)
    if any(not isinstance(value, int) for value in values):
        raise ValueError("Fisher table counts must be integers")
    if any(value < 0 for value in values):
        raise ValueError("Fisher table counts must be non-negative")

    row_one = a + b
    row_two = c + d
    column_one = a + c
    total = row_one + row_two
    if total == 0:
        raise ValueError("Fisher table must contain observations")

    denominator = math.comb(total, column_one)

    def probability(x: int) -> float:
        return (
            math.comb(row_one, x)
            * math.comb(row_two, column_one - x)
            / denominator
        )

    minimum = max(0, column_one - row_two)
    maximum = min(row_one, column_one)
    observed_probability = probability(a)
    tolerance = observed_probability * 1e-12 + 1e-15
    probabilities = [
        probability(x)
        for x in range(minimum, maximum + 1)
        if probability(x) <= observed_probability + tolerance
    ]
    return min(1.0, math.fsum(probabilities))


def mcnemar_exact_two_sided(
    a_only_success: int,
    b_only_success: int,
) -> float:
    if (
        not isinstance(a_only_success, int)
        or not isinstance(b_only_success, int)
    ):
        raise ValueError("McNemar discordant counts must be integers")
    if a_only_success < 0 or b_only_success < 0:
        raise ValueError(
            "McNemar discordant counts must be non-negative"
        )

    discordant = a_only_success + b_only_success
    if discordant == 0:
        return 1.0

    tail = min(a_only_success, b_only_success)
    one_sided = math.fsum(
        math.comb(discordant, value)
        for value in range(tail + 1)
    ) / (2**discordant)
    return min(1.0, 2.0 * one_sided)


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    if not p_values:
        return []
    if any(
        not math.isfinite(value) or value < 0.0 or value > 1.0
        for value in p_values
    ):
        raise ValueError("Holm p-values must be finite and in [0, 1]")

    count = len(p_values)
    ordered = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [0.0] * count
    running_maximum = 0.0

    for rank, (original_index, value) in enumerate(ordered):
        candidate = min(1.0, (count - rank) * value)
        running_maximum = max(running_maximum, candidate)
        adjusted[original_index] = running_maximum

    return adjusted


def _validate_survival_observations(
    observations: Sequence[tuple[float, int]],
) -> None:
    if not observations:
        raise ValueError("Survival analysis requires non-empty input")

    for duration, event in observations:
        if duration is None:
            raise ValueError("Survival duration is missing")
        if (
            not isinstance(duration, (int, float))
            or not math.isfinite(float(duration))
            or float(duration) <= 0.0
        ):
            raise ValueError(
                "Survival duration must be a positive finite number"
            )
        if event not in (0, 1):
            raise ValueError("Survival event must be 0 or 1")


def kaplan_meier(
    observations: Sequence[tuple[float, int]],
) -> list[KMPoint]:
    _validate_survival_observations(observations)
    by_time: dict[float, list[int]] = defaultdict(lambda: [0, 0])

    for duration, event in observations:
        bucket = by_time[float(duration)]
        if event == 1:
            bucket[0] += 1
        else:
            bucket[1] += 1

    at_risk = len(observations)
    survival = 1.0
    points = [KMPoint(0.0, at_risk, 0, 0, survival)]

    for duration in sorted(by_time):
        events, censored = by_time[duration]
        if events:
            survival *= 1.0 - events / at_risk
        points.append(
            KMPoint(
                time=duration,
                at_risk=at_risk,
                events=events,
                censored=censored,
                survival_probability=survival,
            )
        )
        at_risk -= events + censored

    return points


def logrank_two_sided(
    group_a: Sequence[tuple[float, int]],
    group_b: Sequence[tuple[float, int]],
) -> tuple[float, float]:
    _validate_survival_observations(group_a)
    _validate_survival_observations(group_b)
    event_times = sorted(
        {
            float(duration)
            for duration, event in [*group_a, *group_b]
            if event == 1
        }
    )
    observed_minus_expected = 0.0
    variance = 0.0

    for event_time in event_times:
        at_risk_a = sum(
            duration >= event_time for duration, _ in group_a
        )
        at_risk_b = sum(
            duration >= event_time for duration, _ in group_b
        )
        events_a = sum(
            duration == event_time and event == 1
            for duration, event in group_a
        )
        events_b = sum(
            duration == event_time and event == 1
            for duration, event in group_b
        )
        at_risk = at_risk_a + at_risk_b
        events = events_a + events_b

        if at_risk == 0 or events == 0:
            continue

        expected_a = events * at_risk_a / at_risk
        observed_minus_expected += events_a - expected_a

        if at_risk > 1:
            variance += (
                at_risk_a
                * at_risk_b
                * events
                * (at_risk - events)
                / (at_risk * at_risk * (at_risk - 1))
            )

    if variance <= 0.0:
        return 0.0, 1.0

    chi_square = observed_minus_expected**2 / variance
    p_value = math.erfc(math.sqrt(chi_square / 2.0))
    return chi_square, min(1.0, max(0.0, p_value))


def event_from_status(status: str) -> int:
    if status == "falsified":
        return 1
    if status in {"budget_exhausted", "passed"}:
        return 0
    raise ValueError(
        f"Status {status!r} is invalid for time-to-falsification"
    )


def _required_text(row: dict[str, str], field: str, context: str) -> str:
    value = row.get(field, "").strip()
    if not value:
        raise ValueError(f"{context}: missing {field}")
    return value


def _required_int(
    row: dict[str, str],
    field: str,
    context: str,
) -> int:
    value = _required_text(row, field, context)
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(
            f"{context}: invalid integer {field}={value!r}"
        ) from error


def _required_float(
    row: dict[str, str],
    field: str,
    context: str,
    *,
    positive: bool,
) -> float:
    value = _required_text(row, field, context)
    try:
        parsed = float(value)
    except ValueError as error:
        raise ValueError(
            f"{context}: invalid number {field}={value!r}"
        ) from error
    if not math.isfinite(parsed):
        raise ValueError(f"{context}: {field} must be finite")
    if positive and parsed <= 0.0:
        raise ValueError(f"{context}: {field} must be positive")
    return parsed


def load_and_validate_runs(input_dir: Path) -> list[Run]:
    paths = sorted(input_dir.glob("*.csv"))
    expected_names = {f"{benchmark}.csv" for benchmark in BENCHMARKS}
    actual_names = {path.name for path in paths}
    if actual_names != expected_names:
        raise ValueError(
            "Parsed input files do not match the five C-1 benchmarks: "
            f"expected={sorted(expected_names)}, actual={sorted(actual_names)}"
        )

    runs = []
    group_seeds: dict[tuple[str, str], set[int]] = defaultdict(set)
    group_counts: Counter[tuple[str, str]] = Counter()
    status_counts: Counter[str] = Counter()

    for path in paths:
        benchmark = path.stem
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            required_fields = {
                "method",
                "status",
                "total_calls",
                "seed",
                "fuzz_seconds",
                "process_wall_seconds",
            }
            if not reader.fieldnames or not required_fields.issubset(
                reader.fieldnames
            ):
                raise ValueError(
                    f"{path}: missing required CSV columns"
                )

            for line_number, row in enumerate(reader, start=2):
                context = f"{path}:{line_number}"
                method = _required_text(row, "method", context)
                if method not in METHODS:
                    raise ValueError(
                        f"{context}: illegal method {method!r}"
                    )
                status = _required_text(row, "status", context)
                if status not in ALL_STATUSES:
                    raise ValueError(
                        f"{context}: illegal status {status!r}"
                    )
                seed = _required_int(row, "seed", context)
                total_calls = _required_int(row, "total_calls", context)
                if total_calls < 0:
                    raise ValueError(
                        f"{context}: total_calls must be non-negative"
                    )
                fuzz_seconds = _required_float(
                    row,
                    "fuzz_seconds",
                    context,
                    positive=True,
                )
                process_wall_seconds = _required_float(
                    row,
                    "process_wall_seconds",
                    context,
                    positive=True,
                )

                group = (benchmark, method)
                if seed in group_seeds[group]:
                    raise ValueError(
                        f"{context}: duplicate seed {seed} in {group}"
                    )
                group_seeds[group].add(seed)
                group_counts[group] += 1
                status_counts[status] += 1
                runs.append(
                    Run(
                        benchmark=benchmark,
                        method=method,
                        seed=seed,
                        status=status,
                        total_calls=total_calls,
                        fuzz_seconds=fuzz_seconds,
                        process_wall_seconds=process_wall_seconds,
                    )
                )

    expected_groups = {
        (benchmark, method)
        for benchmark in BENCHMARKS
        for method in METHODS
    }
    if set(group_counts) != expected_groups:
        raise ValueError(
            f"Expected 15 C-1 groups, found {len(group_counts)}"
        )
    if len(runs) != 450:
        raise ValueError(f"Expected 450 parsed rows, found {len(runs)}")

    expected_seeds = set(range(1, 31))
    for group in sorted(expected_groups):
        if group_counts[group] != 30:
            raise ValueError(
                f"{group}: expected 30 rows, found {group_counts[group]}"
            )
        if group_seeds[group] != expected_seeds:
            raise ValueError(
                f"{group}: seed set must be exactly 1..30"
            )

    observed_status_counts = {
        status: status_counts.get(status, 0)
        for status in EXPECTED_STATUS_COUNTS
    }
    if observed_status_counts != EXPECTED_STATUS_COUNTS:
        raise ValueError(
            "C-1 status totals do not match the audited inputs: "
            f"expected={EXPECTED_STATUS_COUNTS}, "
            f"actual={observed_status_counts}"
        )

    return runs


def _group_runs(
    runs: Iterable[Run],
) -> dict[tuple[str, str], list[Run]]:
    grouped: dict[tuple[str, str], list[Run]] = defaultdict(list)
    for run in runs:
        grouped[(run.benchmark, run.method)].append(run)
    for values in grouped.values():
        values.sort(key=lambda run: run.seed)
    return grouped


def validate_group_summary(path: Path, runs: Sequence[Run]) -> None:
    grouped = _group_runs(runs)
    observed = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "benchmark",
            "method",
            "total_logs",
            "valid_runs",
            "falsified_runs",
            "budget_exhausted_runs",
            "passed_runs",
            "startup_error_runs",
            "incomplete_runs",
            "success_rate",
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path}: missing required summary columns")
        for line_number, row in enumerate(reader, start=2):
            context = f"{path}:{line_number}"
            key = (
                _required_text(row, "benchmark", context),
                _required_text(row, "method", context),
            )
            if key in observed:
                raise ValueError(f"{context}: duplicate summary group {key}")
            observed[key] = row

    if set(observed) != set(grouped):
        raise ValueError("Group summary does not contain the same 15 groups")

    for key, group in grouped.items():
        row = observed[key]
        counts = Counter(run.status for run in group)
        expected = {
            "total_logs": len(group),
            "valid_runs": sum(
                counts[status] for status in VALID_STATUSES
            ),
            "falsified_runs": counts["falsified"],
            "budget_exhausted_runs": counts["budget_exhausted"],
            "passed_runs": counts["passed"],
            "startup_error_runs": counts["startup_error"],
            "incomplete_runs": counts["incomplete"],
        }
        for field, expected_value in expected.items():
            actual_value = _required_int(row, field, f"summary {key}")
            if actual_value != expected_value:
                raise ValueError(
                    f"summary {key}: {field}={actual_value}, "
                    f"expected {expected_value}"
                )
        expected_rate = counts["falsified"] / expected["valid_runs"]
        actual_rate = _required_float(
            row,
            "success_rate",
            f"summary {key}",
            positive=False,
        )
        if not math.isclose(
            actual_rate,
            expected_rate,
            rel_tol=0.0,
            abs_tol=5e-5,
        ):
            raise ValueError(
                f"summary {key}: inconsistent success_rate"
            )


def load_and_validate_preflight(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "benchmark",
            "expected_minimal_path",
            "expected_minimal_path_rank",
            "exact_minimal_path_in_k1",
            "exact_minimal_path_in_k5",
            "any_known_triggering_path_in_k1",
            "any_known_triggering_path_in_k5",
            "top1_sequence",
            "path_count",
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path}: missing required preflight columns")
        rows = {}
        for line_number, row in enumerate(reader, start=2):
            benchmark = _required_text(
                row,
                "benchmark",
                f"{path}:{line_number}",
            )
            if benchmark in rows:
                raise ValueError(
                    f"{path}:{line_number}: duplicate benchmark"
                )
            rows[benchmark] = row

    if set(rows) != set(BENCHMARKS):
        raise ValueError("Path preflight must contain the five C-1 benchmarks")

    required_claims = {
        "exercise2-access-control": {
            "expected_minimal_path_rank": "2",
            "exact_minimal_path_in_k1": "0",
            "exact_minimal_path_in_k5": "1",
            "any_known_triggering_path_in_k1": "0",
            "any_known_triggering_path_in_k5": "1",
        },
        "smartbugs-multifunc": {
            "expected_minimal_path_rank": "3",
            "exact_minimal_path_in_k1": "0",
            "any_known_triggering_path_in_k1": "1",
            "any_known_triggering_path_in_k5": "1",
        },
    }
    for benchmark, claims in required_claims.items():
        for field, expected in claims.items():
            if rows[benchmark][field].strip() != expected:
                raise ValueError(
                    f"Preflight claim mismatch: {benchmark} {field}"
                )
    return rows


def validate_semantics(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    required_terms = [
        "falsified",
        "budget_exhausted",
        "valid_runs",
        "success_rate",
        "Total calls",
        "seqLen=4",
        "seqLen=1",
        "any_known_triggering_path",
    ]
    missing = [term for term in required_terms if term not in text]
    if missing:
        raise ValueError(
            f"{path}: missing required semantic terms {missing}"
        )


def success_rate_rows(
    grouped: dict[tuple[str, str], list[Run]],
) -> list[dict[str, object]]:
    rows = []
    for benchmark in BENCHMARKS:
        for method in METHODS:
            group = grouped[(benchmark, method)]
            falsified = sum(run.event for run in group)
            budget = sum(
                run.status == "budget_exhausted" for run in group
            )
            lower, upper = wilson_interval(falsified, len(group))
            rows.append(
                {
                    "benchmark": benchmark,
                    "method": method,
                    "runs": len(group),
                    "falsified": falsified,
                    "budget_exhausted": budget,
                    "success_rate": falsified / len(group),
                    "wilson_95_lower": lower,
                    "wilson_95_upper": upper,
                }
            )
    return rows


def success_pairwise_rows(
    grouped: dict[tuple[str, str], list[Run]],
) -> list[dict[str, object]]:
    rows = []
    for benchmark in BENCHMARKS:
        for method_a, method_b, family in PAIRWISE_COMPARISONS:
            group_a = grouped[(benchmark, method_a)]
            group_b = grouped[(benchmark, method_b)]
            by_seed_a = {run.seed: run for run in group_a}
            by_seed_b = {run.seed: run for run in group_b}
            success_a = sum(run.event for run in group_a)
            success_b = sum(run.event for run in group_b)
            a_only = sum(
                by_seed_a[seed].event == 1
                and by_seed_b[seed].event == 0
                for seed in sorted(by_seed_a)
            )
            b_only = sum(
                by_seed_a[seed].event == 0
                and by_seed_b[seed].event == 1
                for seed in sorted(by_seed_a)
            )
            rows.append(
                {
                    "benchmark": benchmark,
                    "comparison": f"{method_a} vs {method_b}",
                    "method_a_success": success_a,
                    "method_a_not_falsified": len(group_a) - success_a,
                    "method_b_success": success_b,
                    "method_b_not_falsified": len(group_b) - success_b,
                    "success_rate_difference": (
                        success_a / len(group_a)
                        - success_b / len(group_b)
                    ),
                    "fisher_two_sided_p": fisher_exact_two_sided(
                        success_a,
                        len(group_a) - success_a,
                        success_b,
                        len(group_b) - success_b,
                    ),
                    "paired_a_only_success": a_only,
                    "paired_b_only_success": b_only,
                    "mcnemar_exact_two_sided_p": (
                        mcnemar_exact_two_sided(a_only, b_only)
                    ),
                    "comparison_family": family,
                    "holm_adjusted_p": None,
                    "interpretation_scope": (
                        "Paired exact McNemar is the family-adjusted "
                        "analysis; Fisher is an unpaired sensitivity "
                        "analysis. Equal seed labels do not ensure equal "
                        "random trajectories across different ABIs."
                    ),
                }
            )

    for family in ("Primary", "Exploratory"):
        family_indices = [
            index
            for index, row in enumerate(rows)
            if row["comparison_family"] == family
        ]
        adjusted = holm_adjust(
            [
                float(rows[index]["mcnemar_exact_two_sided_p"])
                for index in family_indices
            ]
        )
        for index, adjusted_p in zip(family_indices, adjusted):
            rows[index]["holm_adjusted_p"] = adjusted_p
    return rows


def km_and_time_summary_rows(
    grouped: dict[tuple[str, str], list[Run]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    curve_rows = []
    summary_rows = []
    for benchmark in BENCHMARKS:
        for method in METHODS:
            group = grouped[(benchmark, method)]
            observations = [
                (run.fuzz_seconds, run.event) for run in group
            ]
            points = kaplan_meier(observations)
            for point in points:
                curve_rows.append(
                    {
                        "benchmark": benchmark,
                        "method": method,
                        "time": point.time,
                        "at_risk": point.at_risk,
                        "events": point.events,
                        "censored": point.censored,
                        "survival_probability": (
                            point.survival_probability
                        ),
                    }
                )

            median_time = next(
                (
                    point.time
                    for point in points
                    if point.survival_probability <= 0.5
                ),
                None,
            )
            successful_durations = [
                run.fuzz_seconds for run in group if run.event == 1
            ]
            events = len(successful_durations)
            summary_rows.append(
                {
                    "benchmark": benchmark,
                    "method": method,
                    "runs": len(group),
                    "events": events,
                    "censored": len(group) - events,
                    "median_time_to_falsification": median_time,
                    "median_reached": int(median_time is not None),
                    "descriptive_successful_median": (
                        statistics.median(successful_durations)
                        if successful_durations
                        else None
                    ),
                    "maximum_observed_duration": max(
                        run.fuzz_seconds for run in group
                    ),
                }
            )
    return curve_rows, summary_rows


def logrank_pairwise_rows(
    grouped: dict[tuple[str, str], list[Run]],
) -> list[dict[str, object]]:
    rows = []
    for benchmark in BENCHMARKS:
        for method_a, method_b, family in PAIRWISE_COMPARISONS:
            group_a = grouped[(benchmark, method_a)]
            group_b = grouped[(benchmark, method_b)]
            observations_a = [
                (run.fuzz_seconds, run.event) for run in group_a
            ]
            observations_b = [
                (run.fuzz_seconds, run.event) for run in group_b
            ]
            chi_square, p_value = logrank_two_sided(
                observations_a,
                observations_b,
            )
            events_a = sum(run.event for run in group_a)
            events_b = sum(run.event for run in group_b)
            rows.append(
                {
                    "benchmark": benchmark,
                    "comparison": f"{method_a} vs {method_b}",
                    "method_a_runs": len(group_a),
                    "method_a_events": events_a,
                    "method_a_censored": len(group_a) - events_a,
                    "method_b_runs": len(group_b),
                    "method_b_events": events_b,
                    "method_b_censored": len(group_b) - events_b,
                    "logrank_chi_square": chi_square,
                    "logrank_two_sided_p": p_value,
                    "comparison_family": family,
                    "holm_adjusted_p": None,
                    "interpretation_scope": (
                        "fuzz_seconds is an operational time metric under "
                        "a testLimit-led budget; it is not equal target-level "
                        "work across Original and Harness."
                    ),
                }
            )

    for family in ("Primary", "Exploratory"):
        family_indices = [
            index
            for index, row in enumerate(rows)
            if row["comparison_family"] == family
        ]
        adjusted = holm_adjust(
            [
                float(rows[index]["logrank_two_sided_p"])
                for index in family_indices
            ]
        )
        for index, adjusted_p in zip(family_indices, adjusted):
            rows[index]["holm_adjusted_p"] = adjusted_p
    return rows


def overall_descriptive_rows(
    grouped: dict[tuple[str, str], list[Run]],
) -> list[dict[str, object]]:
    rows = []
    for method in METHODS:
        method_groups = [
            grouped[(benchmark, method)] for benchmark in BENCHMARKS
        ]
        all_runs = [run for group in method_groups for run in group]
        total_falsified = sum(run.event for run in all_runs)
        expected_falsified, expected_total = EXPECTED_METHOD_TOTALS[method]
        if (
            total_falsified != expected_falsified
            or len(all_runs) != expected_total
        ):
            raise ValueError(
                f"{method}: expected {expected_falsified}/{expected_total}, "
                f"found {total_falsified}/{len(all_runs)}"
            )
        rates = [
            sum(run.event for run in group) / len(group)
            for group in method_groups
        ]
        rows.append(
            {
                "method": method,
                "total_runs": len(all_runs),
                "total_falsified": total_falsified,
                "total_budget_exhausted": sum(
                    run.status == "budget_exhausted" for run in all_runs
                ),
                "pooled_descriptive_rate": (
                    total_falsified / len(all_runs)
                ),
                "macro_average_success_rate": statistics.mean(rates),
                "benchmarks_with_30_of_30": sum(
                    sum(run.event for run in group) == 30
                    for group in method_groups
                ),
                "benchmarks_with_any_budget_exhaustion": sum(
                    any(
                        run.status == "budget_exhausted"
                        for run in group
                    )
                    for group in method_groups
                ),
                "interpretation_scope": (
                    "Descriptive across five heterogeneous benchmarks; "
                    "not a pooled inferential claim."
                ),
            }
        )
    return rows


def _csv_value(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, float):
        return format(value, ".15g")
    return value


def write_csv(path: Path, rows: Sequence[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty output {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(
            {
                field: _csv_value(value)
                for field, value in row.items()
            }
            for row in rows
        )


def _markdown_float(value: object, digits: int = 4) -> str:
    if value is None:
        return "未达到"
    return f"{float(value):.{digits}g}"


def build_report(
    success_rows: Sequence[dict[str, object]],
    pairwise_rows: Sequence[dict[str, object]],
    time_rows: Sequence[dict[str, object]],
    logrank_rows: Sequence[dict[str, object]],
    overall_rows: Sequence[dict[str, object]],
    preflight: dict[str, dict[str, str]],
) -> str:
    lines = [
        "# C-1 公开基准统计报告",
        "",
        "## 1. 数据与实验单位",
        "",
        "本报告基于 5 个公开基准、3 种方法、每组 30 个相同 seed，共 450 次有效运行。统计事件定义为 `status=falsified`；`budget_exhausted` 是右删失，表示在当前 `testLimit` 预算内未发现反例，不表示性质通过或合约安全。实验单位是单个 benchmark/method/seed 运行。",
        "",
        "## 2. 成功率与 95% Wilson 区间",
        "",
        "| 基准 | 方法 | falsified/runs | 成功率 | Wilson 95% CI |",
        "|---|---|---:|---:|---:|",
    ]
    for row in success_rows:
        lines.append(
            "| {benchmark} | {method} | {falsified}/{runs} | "
            "{rate:.4f} | [{lower:.4f}, {upper:.4f}] |".format(
                benchmark=row["benchmark"],
                method=row["method"],
                falsified=row["falsified"],
                runs=row["runs"],
                rate=float(row["success_rate"]),
                lower=float(row["wilson_95_lower"]),
                upper=float(row["wilson_95_upper"]),
            )
        )

    lines.extend(
        [
            "",
            "## 3. 每基准的方法比较",
            "",
            "配对 exact McNemar 利用相同 seed 标签，是主要比较；Fisher 精确检验作为不使用配对关系的敏感性分析。不同 ABI 和动作空间下，同一 seed 不保证形成相同随机轨迹，因此配对强度不应被夸大。Primary family 预先包含 Full-K1/Original 与 Full-K5/Original 的 10 项比较；Exploratory family 包含 K1/K5 的 5 项比较，分别执行 Holm 校正。",
            "",
            "| 基准 | 比较 | 成功率差 | Fisher p | McNemar p | Holm p | family |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in pairwise_rows:
        lines.append(
            "| {benchmark} | {comparison} | {difference:.4f} | "
            "{fisher:.4g} | {mcnemar:.4g} | {holm:.4g} | {family} |".format(
                benchmark=row["benchmark"],
                comparison=row["comparison"],
                difference=float(row["success_rate_difference"]),
                fisher=float(row["fisher_two_sided_p"]),
                mcnemar=float(row["mcnemar_exact_two_sided_p"]),
                holm=float(row["holm_adjusted_p"]),
                family=row["comparison_family"],
            )
        )

    time_lookup = {
        (str(row["benchmark"]), str(row["method"])): row
        for row in time_rows
    }
    lines.extend(
        [
            "",
            "## 4. 右删失、Kaplan–Meier 与 log-rank",
            "",
            "`duration=fuzz_seconds`；只有 falsified 是事件，budget_exhausted/passed 均为右删失。所有 37 个预算耗尽样本都保留在风险集中，没有只比较成功样本平均时间。实验主要截止机制是 `testLimit`，并非各组统一的固定墙钟截止；因此 fuzz_seconds 是本实验的操作性时间到反例指标。",
            "",
            "| 基准 | 方法 | events/censored | KM 中位时间 | 成功样本描述性中位数 | 最大观察时间 |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for benchmark in BENCHMARKS:
        for method in METHODS:
            row = time_lookup[(benchmark, method)]
            lines.append(
                "| {benchmark} | {method} | {events}/{censored} | "
                "{median} | {successful} | {maximum} |".format(
                    benchmark=benchmark,
                    method=method,
                    events=row["events"],
                    censored=row["censored"],
                    median=_markdown_float(
                        row["median_time_to_falsification"]
                    ),
                    successful=_markdown_float(
                        row["descriptive_successful_median"]
                    ),
                    maximum=_markdown_float(
                        row["maximum_observed_duration"]
                    ),
                )
            )

    lines.extend(
        [
            "",
            "log-rank 同样按 Primary/Exploratory family 分别 Holm 校正：",
            "",
            "| 基准 | 比较 | log-rank χ² | 未校正 p | Holm p | family |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in logrank_rows:
        lines.append(
            "| {benchmark} | {comparison} | {chi:.4g} | {p:.4g} | "
            "{holm:.4g} | {family} |".format(
                benchmark=row["benchmark"],
                comparison=row["comparison"],
                chi=float(row["logrank_chi_square"]),
                p=float(row["logrank_two_sided_p"]),
                holm=float(row["holm_adjusted_p"]),
                family=row["comparison_family"],
            )
        )

    exercise = preflight["exercise2-access-control"]
    smartbugs = preflight["smartbugs-multifunc"]
    lines.extend(
        [
            "",
            "## 5. Top-K 敏感性",
            "",
            f"- exercise2-access-control 的有效最短路径 `Owner() -> resume()` 排名为 {exercise['expected_minimal_path_rank']}。它不在 K1、在 K5；因此观察到 Full-K1 0/30、Full-K5 30/30。Top-1 的 `Owner() -> pause()` 不是已确认有效触发路径。",
            f"- smartbugs-multifunc 的最短路径 `init() -> run(uint256)` 排名为 {smartbugs['expected_minimal_path_rank']}，不在 K1；但 K1 包含另一条经原始反例确认的有效路径 `init() -> run(uint256) -> run(uint256)`，所以 K1 仍为 30/30。",
            "- echidna-multi 的 K5 为 29/30，仅 seed 7 在预算内未发现反例。单个右删失样本不足以断言 K5 系统性差于 K1。",
            "",
            "## 6. 统计结果、效应大小与工程意义",
            "",
            "成功率差是当前 30 个 seed 下的观察效应；检验 p 值描述与相应零假设的不相容程度；工程意义还取决于路径覆盖、动作空间和实际预算。三者不能互相替代。Original 与 Harness 的 ABI、调用者和原子执行边界不同，Harness 一次外层调用还可能封装多个目标调用。时间比较可描述实际工具运行表现，但不能解释为等量底层目标函数工作下的算法效率。",
            "",
            "## 7. 当前证据支持的结论",
            "",
            "- C-1 的 450 次运行中，Full-K5、Original、Full-K1 的描述性成功数分别为 149/150、144/150、120/150。",
            "- exercise2 显示 Top-K 是否包含正确状态方向会实质影响有限预算结果。",
            "- smartbugs-multifunc 显示精确最短路径缺失不等价于不存在其他有效触发路径。",
            "- Kaplan–Meier 与 log-rank 分析保留了所有预算耗尽样本，避免了只分析成功样本造成的选择偏差。",
            "",
            "## 8. 不能支持的结论",
            "",
            "- 五个公开基准不足以支持普遍优越性或对任意智能合约的泛化结论。",
            "- budget_exhausted 不能写成性质通过、漏洞不存在或合约安全。",
            "- 不能由 echidna-multi 的一个 K5 预算耗尽样本断言 K5 系统性更差。",
            "- 不能直接使用 Original 与 Harness 的 `Total calls` 宣称同等底层工作量下加速。",
            "- 描述性 150 次汇总不能替代按基准分层的推断分析。",
            "",
            "## 9. 推荐论文表述",
            "",
            "> 在五个 C-1 公开基准、每组 30 个固定 seed 和 100000 次外层调用预算下，Full-K5、Original 与 Full-K1 分别在 149/150、144/150 与 120/150 次运行中发现反例。按基准报告的 Wilson 区间、配对 exact McNemar 检验以及含右删失的 Kaplan–Meier/log-rank 分析用于刻画该实验范围内的不确定性；这些结果不构成对更广泛合约总体的普遍优越性声明。",
            "",
            "> 未发现反例的运行统一表述为预算耗尽，而非性质通过。由于 Original 与 Harness 的调用语义及每次外层调用包含的目标操作数不同，调用数和 fuzz_seconds 只用于描述实际工具运行表现，不解释为等量底层工作下的算法加速。",
            "",
            "## 10. 统计限制",
            "",
            "- 每个基准每种方法只有 30 次运行，极端比例的 Wilson 区间仍有不可忽略宽度。",
            "- 基准数仅为 5，且性质结构存在明显异质性。",
            "- 相同 seed 标签不保证不同 ABI 下的随机轨迹逐步配对。",
            "- testLimit 是主要预算，而 fuzz_seconds 会受不同执行语义和每次调用成本影响。",
            "- 已知触发路径集合来自当前人工审计，不是完整语义可达性证明。",
            "- 总体汇总仅为描述性，不执行忽略基准异质性的 pooled 显著性检验。",
        ]
    )

    lines.extend(
        [
            "",
            "## 附：总体描述性汇总",
            "",
            "| 方法 | falsified/runs | pooled rate | macro rate | 30/30 基准数 | 有预算耗尽的基准数 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in overall_rows:
        lines.append(
            "| {method} | {falsified}/{runs} | {pooled:.4f} | "
            "{macro:.4f} | {perfect} | {exhaustion} |".format(
                method=row["method"],
                falsified=row["total_falsified"],
                runs=row["total_runs"],
                pooled=float(row["pooled_descriptive_rate"]),
                macro=float(row["macro_average_success_rate"]),
                perfect=row["benchmarks_with_30_of_30"],
                exhaustion=row[
                    "benchmarks_with_any_budget_exhaustion"
                ],
            )
        )
    return "\n".join(lines) + "\n"


def build_readme(input_files: Sequence[Path]) -> str:
    input_list = "\n".join(
        f"- `{path.relative_to(ROOT)}`" for path in input_files
    )
    return f"""# C-1 statistical analysis

## Inputs

{input_list}

The analysis validates exactly five benchmarks, three methods, 30 unique seeds per group, 450 rows, and the audited status totals before creating outputs.

## Outputs

- `success-rate-wilson.csv`: per-group success proportions and 95% Wilson intervals.
- `success-rate-pairwise.csv`: Fisher sensitivity analysis, paired exact McNemar tests, and Holm-adjusted McNemar p-values.
- `km-curves.csv`: Kaplan–Meier product-limit curves including right-censored runs.
- `time-to-falsification-summary.csv`: event/censor counts and KM/descriptive time summaries.
- `logrank-pairwise.csv`: two-sided log-rank tests and family-specific Holm adjustment.
- `overall-descriptive.csv`: descriptive totals only; no pooled significance test.
- `public-c1-statistical-report.md`: Chinese paper-oriented report.
- `input-checksums.sha256`: SHA-256 checksums of the inputs listed above.

## Definitions

- Success is `status=falsified`.
- Wilson intervals use the standard score interval with z={Z_95!r}.
- Fisher p-values sum fixed-margin tables with probability no greater than the observed table.
- Exact two-sided McNemar p-values use the binomial distribution of discordant seed pairs under p=0.5.
- Holm correction is applied separately to the predefined families: Primary has Full-K1 vs Original and Full-K5 vs Original across five benchmarks (10 tests); Exploratory has Full-K1 vs Full-K5 across five benchmarks (5 tests). Success-rate Holm values adjust McNemar p-values. Log-rank p-values are adjusted separately using the same family definitions.
- Kaplan–Meier uses `duration=fuzz_seconds`; only falsified runs are events. `budget_exhausted` and `passed` are right-censored.
- The two-sided log-rank test uses the usual observed-minus-expected statistic with the hypergeometric tie variance.

## Rebuild

```bash
python3 analyzer/analyze_public_c1_statistics.py \\
  --input-dir results/public-benchmarks/c1/parsed \\
  --output-dir results/public-benchmarks/c1/statistics
```

Generated with Python {platform.python_version()} using only the Python standard library; no external statistical dependency is required.

## Interpretation limits

The main experimental budget is `testLimit`, not a uniform wall-clock deadline. `fuzz_seconds` is an operational time-to-falsification measure. `Total calls` counts Echidna outer calls. Original uses `seqLen=4`; Harness uses `seqLen=1`, and one Harness call can bundle multiple target calls. Because their ABI, caller, atomicity, and target-call workload differ, calls and time describe observed tool performance rather than equal target-level algorithmic work. Overall 150-run rates are descriptive across five heterogeneous benchmarks and are not pooled inferential claims.
"""


def write_checksums(path: Path, input_files: Sequence[Path]) -> None:
    lines = []
    for input_path in input_files:
        digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {input_path.relative_to(ROOT)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and analyze existing public C-1 parsed results "
            "without running Echidna."
        )
    )
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    c1_root = input_dir.parent
    summary_path = c1_root / "public-c1-group-summary.csv"
    preflight_path = c1_root / "c1-path-preflight.csv"
    semantics_path = c1_root / "data-semantics.md"
    parsed_paths = sorted(input_dir.glob("*.csv"))
    input_files = [
        *parsed_paths,
        summary_path,
        preflight_path,
        semantics_path,
    ]

    missing = [path for path in input_files if not path.is_file()]
    if missing:
        raise ValueError(f"Missing required input files: {missing}")

    # Complete every input validation before creating the output directory.
    runs = load_and_validate_runs(input_dir)
    validate_group_summary(summary_path, runs)
    preflight = load_and_validate_preflight(preflight_path)
    validate_semantics(semantics_path)
    grouped = _group_runs(runs)

    success = success_rate_rows(grouped)
    success_pairwise = success_pairwise_rows(grouped)
    km_curves, time_summary = km_and_time_summary_rows(grouped)
    logrank = logrank_pairwise_rows(grouped)
    overall = overall_descriptive_rows(grouped)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "success-rate-wilson.csv", success)
    write_csv(
        output_dir / "success-rate-pairwise.csv",
        success_pairwise,
    )
    write_csv(output_dir / "km-curves.csv", km_curves)
    write_csv(
        output_dir / "time-to-falsification-summary.csv",
        time_summary,
    )
    write_csv(output_dir / "logrank-pairwise.csv", logrank)
    write_csv(output_dir / "overall-descriptive.csv", overall)
    report = build_report(
        success,
        success_pairwise,
        time_summary,
        logrank,
        overall,
        preflight,
    )
    (output_dir / "public-c1-statistical-report.md").write_text(
        report,
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(
        build_readme(input_files),
        encoding="utf-8",
    )
    write_checksums(
        output_dir / "input-checksums.sha256",
        input_files,
    )
    print(
        "Validated 450 runs across 15 groups: "
        "falsified=413, budget_exhausted=37, "
        "passed=0, startup_error=0, incomplete=0"
    )
    print(f"Saved statistical outputs to {output_dir}")


if __name__ == "__main__":
    main()
