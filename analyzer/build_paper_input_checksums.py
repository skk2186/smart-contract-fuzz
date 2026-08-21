#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/paper-data/input-checksums.sha256"
PAPER_MANIFEST = ROOT / "paper-ready/manifest.tsv"
SELF_REFERENTIAL_FREEZE_OUTPUTS = {
    OUTPUT,
    ROOT / "results/paper-data/repository-files.tsv",
    ROOT / "results/paper-data/repository-freeze.json",
}


def manifest_references(path: Path) -> set[Path]:
    with path.open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file, delimiter="\t")
        return {
            ROOT / row[field]
            for row in rows
            for field in ("contract_file", "config_file")
        }


def expand_path(path: Path) -> set[Path]:
    if path.is_file():
        return {path}
    if path.is_dir():
        return {item for item in path.rglob("*") if item.is_file()}
    raise ValueError(f"Missing paper manifest input: {path}")


def paper_manifest_references(path: Path) -> set[Path]:
    references: set[Path] = set()
    with path.open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file, delimiter="\t")
        for row in rows:
            if row["include_in_main"] not in {"yes", "appendix"}:
                continue
            for value in row["source_path"].split(";"):
                target = ROOT / value
                if target in SELF_REFERENTIAL_FREEZE_OUTPUTS:
                    continue
                references.update(expand_path(target))
    return references


def evidence_files() -> list[Path]:
    formal_manifest = ROOT / "results/formal/manifest.tsv"
    b2_manifest = ROOT / "results/formal-b2/manifest.tsv"
    paths = set((ROOT / "results/formal/runs").rglob("*.log"))
    paths.update((ROOT / "results/formal-b2/runs").rglob("*.log"))
    paths.update({formal_manifest, b2_manifest})
    paths.add(ROOT / "results/formal/environment.txt")
    paths.update((ROOT / "results/formal/candidates").rglob("*.json"))
    paths.update(
        {
            ROOT / "results/formal/overhead/metadata.json",
            ROOT / "results/formal/overhead/overhead-detailed.csv",
        }
    )
    paths.update(manifest_references(formal_manifest))
    paths.update(manifest_references(b2_manifest))
    paths.add(PAPER_MANIFEST)
    paths.update(paper_manifest_references(PAPER_MANIFEST))
    missing = sorted(path for path in paths if not path.is_file())
    if missing:
        raise ValueError(f"Missing checksum inputs: {missing}")
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def build() -> None:
    lines = []
    for path in evidence_files():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        relative = path.relative_to(ROOT).as_posix()
        lines.append(f"{digest}  {relative}\n")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(lines), encoding="utf-8")


if __name__ == "__main__":
    build()
    print(f"Saved evidence checksums to {OUTPUT}")
