#!/usr/bin/env python3

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ManifestGroup:
    benchmark: str
    method: str
    contract_file: str
    contract_name: str
    config_file: str


def read_manifest(path: Path) -> list[ManifestGroup]:
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file, delimiter="\t"))

    required = {
        "benchmark",
        "method",
        "contract_file",
        "contract_name",
        "config_file",
    }
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"Invalid experiment manifest: {path}")

    groups = [ManifestGroup(**{key: row[key] for key in required}) for row in rows]
    keys = [(group.benchmark, group.method) for group in groups]
    if len(keys) != len(set(keys)):
        raise ValueError(f"Duplicate benchmark/method group in {path}")
    return groups


def validate_manifest_runs(
    manifest_path: Path,
    runs_root: Path,
    *,
    expected_groups: int,
    expected_seeds: int,
    completion_marker: str,
) -> list[ManifestGroup]:
    groups = read_manifest(manifest_path)
    if len(groups) != expected_groups:
        raise ValueError(
            f"Expected {expected_groups} manifest groups, found {len(groups)}"
        )

    expected = list(range(1, expected_seeds + 1))
    manifest_keys = {(group.benchmark, group.method) for group in groups}
    actual_keys = set()

    for group in groups:
        directory = runs_root / group.benchmark / group.method
        if not directory.is_dir():
            raise ValueError(f"Missing run group: {directory}")

        logs = list(directory.glob("seed-*.log"))
        seeds = []
        for path in logs:
            match = re.fullmatch(r"seed-(\d+)\.log", path.name)
            if match:
                seeds.append(int(match.group(1)))
        if sorted(seeds) != expected or len(seeds) != len(set(seeds)):
            raise ValueError(
                f"Expected seed 1-{expected_seeds} exactly once in {directory}; "
                f"found {sorted(seeds)}"
            )

        for seed in expected:
            path = directory / f"seed-{seed}.log"
            text = path.read_text(encoding="utf-8", errors="ignore")
            if completion_marker not in text:
                raise ValueError(f"Missing completion marker in {path}")

            header_seed = re.search(r"(?m)^SEED=(\d+)\s*$", text)
            footer_seed = re.search(r"(?m)^Seed:\s*(\d+)\s*$", text)
            for match in (header_seed, footer_seed):
                if match and int(match.group(1)) != seed:
                    raise ValueError(f"Seed mismatch in {path}")

        actual_keys.add((group.benchmark, group.method))

    for benchmark_directory in runs_root.iterdir():
        if not benchmark_directory.is_dir():
            continue
        for method_directory in benchmark_directory.iterdir():
            if method_directory.is_dir() and list(
                method_directory.glob("seed-*.log")
            ):
                actual_keys.add(
                    (benchmark_directory.name, method_directory.name)
                )

    extras = actual_keys - manifest_keys
    if extras:
        raise ValueError(f"Run groups absent from manifest: {sorted(extras)}")

    return groups
