#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "results/paper-data/repository-files.tsv"
SUMMARY = ROOT / "results/paper-data/repository-freeze.json"
SELF_OUTPUTS = {INVENTORY, SUMMARY}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as file:
        while block := file.read(1024 * 1024):
            value.update(block)
    return value.hexdigest()


def classify(relative: Path) -> str:
    parts = relative.parts
    text = relative.as_posix()
    if parts and parts[0] == ".tools":
        return "local_toolchain"
    if parts[:2] == ("baselines", "smartian"):
        if ".git" in parts:
            return "external_vcs_metadata"
        return "external_dependency"
    if "__pycache__" in parts or relative.suffix in {".pyc", ".pyo"}:
        return "runtime_cache"
    if parts and parts[0] == "checkpoints":
        return "historical_checkpoint"
    if text.startswith("results/formal/overhead-v2/artifacts/"):
        return "excluded_generated_artifact"
    if text.startswith("contracts/harnesses/formal-overhead/"):
        return "excluded_generated_artifact"
    if parts and parts[0] in {"crytic-export"}:
        return "excluded_generated_artifact"
    return "project_managed"


def command_output(command: list[str], cwd: Path = ROOT) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unavailable"


def build() -> None:
    rows: list[dict[str, str | int]] = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path in SELF_OUTPUTS:
            continue
        relative = path.relative_to(ROOT)
        if relative.parts and relative.parts[0] == ".git":
            continue
        rows.append(
            {
                "path": relative.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": digest(path),
                "scope": classify(relative),
            }
        )

    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    with INVENTORY.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=("path", "bytes", "sha256", "scope"),
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(str(row["scope"]) for row in rows)
    sizes = Counter()
    workspace_digest = hashlib.sha256()
    for row in rows:
        sizes[str(row["scope"])] += int(row["bytes"])
        workspace_digest.update(
            f"{row['sha256']}  {row['path']}\n".encode("utf-8")
        )

    smartian_root = ROOT / "baselines/smartian"
    summary = {
        "freeze_format": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "repository_base_commit": command_output(["git", "rev-parse", "HEAD"]),
        "repository_branch": command_output(["git", "branch", "--show-current"]),
        "inventory": INVENTORY.relative_to(ROOT).as_posix(),
        "inventory_excludes": [
            ".git/ (primary repository metadata)",
            INVENTORY.relative_to(ROOT).as_posix(),
            SUMMARY.relative_to(ROOT).as_posix(),
        ],
        "file_count": len(rows),
        "byte_count": sum(int(row["bytes"]) for row in rows),
        "workspace_digest": workspace_digest.hexdigest(),
        "scope_file_counts": dict(sorted(counts.items())),
        "scope_byte_counts": dict(sorted(sizes.items())),
        "environment": {
            "dotnet_version": command_output(
                [str(ROOT / ".tools/dotnet/dotnet"), "--version"]
            ),
            "smartian_commit": command_output(
                ["git", "rev-parse", "HEAD"], cwd=smartian_root
            ),
            "smartian_submodules": command_output(
                ["git", "submodule", "status"], cwd=smartian_root
            ).splitlines(),
        },
        "notes": [
            "All regular files under the workspace were inventoried except the primary .git metadata and the two self-referential freeze outputs.",
            "Local toolchains, nested repositories, caches, checkpoints, and excluded generated artifacts are recorded but are not part of the paper evidence whitelist.",
            "The Git commit created after this inventory is the authoritative managed-project snapshot.",
        ],
    }
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    build()
    print(f"Saved repository inventory to {INVENTORY}")
    print(f"Saved repository freeze summary to {SUMMARY}")
