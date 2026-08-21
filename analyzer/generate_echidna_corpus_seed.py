#!/usr/bin/env python3
"""Generate a small Echidna coverage-corpus seed from a concrete call path.

The generated file follows the JSON format emitted by Echidna in
``<corpusDir>/coverage/*.txt``.  This is intentionally a narrow prototype:
zero-argument functions and integer arguments are supported because they cover
the first native multi-transaction regression cases.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable


DEFAULT_TARGET = "0x00a329c0648769A73afAc7F9381E08FB43dBEA72"
DEFAULT_SENDER = "0x0000000000000000000000000000000000010000"
ZERO_WORD = "0x" + "0" * 64

_SIGNATURE_RE = re.compile(r"^\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*\((.*)\)\s*$")
_UINT_RE = re.compile(r"^uint(?:([0-9]+))?$", re.IGNORECASE)
_INT_RE = re.compile(r"^int(?:([0-9]+))?$", re.IGNORECASE)


class SeedSpecError(ValueError):
    """Raised when a seed path cannot be represented by this prototype."""


def split_types(raw: str) -> list[str]:
    """Split a Solidity parameter list while rejecting tuple-like syntax."""

    raw = raw.strip()
    if not raw:
        return []
    # Commas inside tuples would require ABI tuple encoding; fail explicitly
    # instead of silently producing a malformed corpus entry.
    if "(" in raw or ")" in raw or "[" in raw or "]" in raw:
        raise SeedSpecError(f"unsupported parameter type in {raw!r}")
    result = []
    for item in raw.split(","):
        token = item.strip().split()
        if len(token) != 1:
            raise SeedSpecError(
                f"use canonical parameter types without names: {item.strip()!r}"
            )
        result.append(token[0])
    return result


def parse_signature(signature: str) -> tuple[str, list[str]]:
    match = _SIGNATURE_RE.match(signature)
    if not match:
        raise SeedSpecError(
            f"invalid function signature {signature!r}; expected name(type,...)"
        )
    return match.group(1), split_types(match.group(2))


def _uint_contents(type_name: str, value: int) -> dict[str, Any]:
    match = _UINT_RE.fullmatch(type_name)
    if not match:
        raise SeedSpecError(
            f"unsupported argument type {type_name!r}; only uint/uintN is supported"
        )
    bits = int(match.group(1) or "256")
    if bits == 0 or bits > 256 or bits % 8:
        raise SeedSpecError(f"invalid unsigned integer width in {type_name!r}")
    if value < 0 or value >= 2**bits:
        raise SeedSpecError(f"value {value} does not fit {type_name}")
    return {"contents": [bits, str(value)], "tag": "AbiUInt"}


def _int_contents(type_name: str, value: int) -> dict[str, Any]:
    match = _INT_RE.fullmatch(type_name)
    if not match:
        raise SeedSpecError(
            f"unsupported argument type {type_name!r}; only int/intN is supported"
        )
    bits = int(match.group(1) or "256")
    if bits == 0 or bits > 256 or bits % 8:
        raise SeedSpecError(f"invalid signed integer width in {type_name!r}")
    lower = -(2 ** (bits - 1))
    upper = 2 ** (bits - 1) - 1
    if value < lower or value > upper:
        raise SeedSpecError(f"value {value} does not fit {type_name}")
    return {"contents": [bits, str(value)], "tag": "AbiInt"}


def argument_contents(type_name: str, value: int) -> dict[str, Any]:
    if _UINT_RE.fullmatch(type_name):
        return _uint_contents(type_name, value)
    if _INT_RE.fullmatch(type_name):
        return _int_contents(type_name, value)
    raise SeedSpecError(
        f"unsupported argument type {type_name!r}; only integer types are supported"
    )


def build_call(
    signature: str,
    values: Iterable[int],
    *,
    target: str = DEFAULT_TARGET,
    sender: str = DEFAULT_SENDER,
    gas: int = 12_500_000,
) -> dict[str, Any]:
    """Build one Echidna ``SolCall`` object from a Solidity signature."""

    name, types = parse_signature(signature)
    values = list(values)
    if len(values) != len(types):
        raise SeedSpecError(
            f"{signature}: expected {len(types)} argument values, got {len(values)}"
        )
    if gas <= 0:
        raise SeedSpecError("gas must be positive")
    args = [
        argument_contents(type_name, value)
        for type_name, value in zip(types, values)
    ]
    return {
        "call": {"contents": [name, args], "tag": "SolCall"},
        "delay": [ZERO_WORD, ZERO_WORD],
        "dst": target,
        "gas": gas,
        "gasprice": ZERO_WORD,
        "src": sender,
        "value": ZERO_WORD,
    }


def parse_values(raw: str | None) -> list[int]:
    if raw is None or not raw.strip():
        return []
    try:
        return [int(item.strip(), 0) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise SeedSpecError(f"invalid integer value list {raw!r}") from exc


def write_seed(
    output_dir: Path,
    signatures: list[str],
    values: list[int],
    *,
    name: str = "seed-0001.txt",
    target: str = DEFAULT_TARGET,
    sender: str = DEFAULT_SENDER,
    gas: int = 12_500_000,
) -> Path:
    """Write one sequence as a corpus file and return its path."""

    calls = []
    cursor = 0
    for signature in signatures:
        _, types = parse_signature(signature)
        count = len(types)
        calls.append(
            build_call(
                signature,
                values[cursor : cursor + count],
                target=target,
                sender=sender,
                gas=gas,
            )
        )
        cursor += count
    if cursor != len(values):
        raise SeedSpecError(
            f"received {len(values)} values but the path consumes {cursor}"
        )
    if not signatures:
        raise SeedSpecError("at least one function signature is required")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / name
    output_path.write_text(json.dumps(calls, separators=(",", ":")) + "\n")
    return output_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, required=True, help="Echidna corpus directory"
    )
    parser.add_argument(
        "--sequence",
        action="append",
        required=True,
        help="function signature; repeat in execution order, e.g. --sequence deposit()",
    )
    parser.add_argument(
        "--values",
        default="",
        help="comma-separated integer arguments consumed left-to-right",
    )
    parser.add_argument("--name", default="seed-0001.txt")
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--sender", default=DEFAULT_SENDER)
    parser.add_argument("--gas", type=int, default=12_500_000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        output_path = write_seed(
            args.output_dir,
            args.sequence,
            parse_values(args.values),
            name=args.name,
            target=args.target,
            sender=args.sender,
            gas=args.gas,
        )
    except SeedSpecError as exc:
        _parser().error(str(exc))
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
