#!/usr/bin/env python3

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from abstract_interpreter import simulate_path


VIOLATION_PRIORITY = {
    "MUST_VIOLATE": 3,
    "MAY_VIOLATE": 2,
    "UNKNOWN": 1,
    "CANNOT_VIOLATE": 0,
}


def choose_property(
    model: dict[str, Any],
    requested: str | None,
) -> str:
    properties = model.get("properties", {})

    if requested is not None:
        if requested not in properties:
            raise ValueError(
                f"Property {requested!r} not found. "
                f"Available properties: {sorted(properties)}"
            )

        return requested

    if len(properties) != 1:
        raise ValueError(
            "Multiple properties were found. "
            "Specify one with --property."
        )

    return next(iter(properties))


def load_candidate_container(
    data: dict[str, Any],
    contract_name: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Support the two candidate JSON layouts currently used:

    1. {
         "ContractName": {
           "paths": [...]
         }
       }

    2. {
         "contract": "ContractName",
         "paths": [...]
       }
    """
    contract_data = data.get(contract_name)

    if (
        isinstance(contract_data, dict)
        and isinstance(contract_data.get("paths"), list)
    ):
        return contract_data, contract_data["paths"]

    if isinstance(data.get("paths"), list):
        return data, data["paths"]

    raise ValueError(
        f"Could not find candidate paths for "
        f"contract {contract_name!r}"
    )


def integer_field(
    path: dict[str, Any],
    names: tuple[str, ...],
    default: int = 0,
) -> int:
    """
    Read the first available numeric field.

    Different V1 generators may use slightly different field names.
    """
    for name in names:
        value = path.get(name)

        if isinstance(value, bool):
            continue

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                continue

    return default


def property_score_of(
    path: dict[str, Any],
) -> int:
    return integer_field(
        path,
        (
            "property_score",
            "score",
            "value_score",
        ),
        0,
    )


def matches_of(
    path: dict[str, Any],
) -> int:
    return integer_field(
        path,
        (
            "value_matches",
            "matches",
            "match_count",
            "require_matches",
        ),
        0,
    )


def conflicts_of(
    path: dict[str, Any],
) -> int:
    return integer_field(
        path,
        (
            "value_conflicts",
            "conflicts",
            "conflict_count",
            "require_conflicts",
        ),
        0,
    )


def repeat_count(
    sequence: list[str],
) -> int:
    """
    Count function visits beyond the first occurrence.

    Examples:
        [a, b, c]       -> 0
        [a, a, b]       -> 1
        [a, a, a, b]    -> 2
        [a, b, a, b]    -> 2
    """
    return len(sequence) - len(set(sequence))


def annotate_path(
    path: dict[str, Any],
    model: dict[str, Any],
    property_name: str,
    original_rank: int,
) -> dict[str, Any]:
    sequence = path.get("sequence")

    if not (
        isinstance(sequence, list)
        and all(
            isinstance(function_name, str)
            for function_name in sequence
        )
    ):
        raise ValueError(
            f"Invalid sequence at original rank "
            f"{original_rank}: {sequence!r}"
        )

    interpretation = simulate_path(
        model,
        property_name,
        sequence,
    )

    annotated = copy.deepcopy(path)

    annotated["original_rank"] = original_rank
    annotated["property"] = property_name

    annotated["violation_truth"] = (
        interpretation["violation_truth"]
    )

    annotated["violation_class"] = (
        interpretation["violation_class"]
    )

    annotated["violation_priority"] = (
        VIOLATION_PRIORITY[
            interpretation["violation_class"]
        ]
    )

    annotated["path_length"] = len(sequence)
    annotated["repeat_count"] = repeat_count(sequence)

    annotated["terminal_state"] = (
        interpretation["final_state"]
    )

    annotated["interpretation_trace"] = (
        interpretation["trace"]
    )

    annotated["missing_functions"] = (
        interpretation["missing_functions"]
    )

    annotated["dominated_repeat"] = 0
    annotated["dominated_by_sequence"] = None

    return annotated


def base_semantic_key(
    path: dict[str, Any],
) -> tuple[int, int, int, int, int, int]:
    """
    Ranking evidence used for choosing the best non-repeated
    alternative during repeat-dominance analysis.
    """
    return (
        -VIOLATION_PRIORITY[
            path["violation_class"]
        ],
        conflicts_of(path),
        -matches_of(path),
        -property_score_of(path),
        len(path["sequence"]),
        int(path["original_rank"]),
    )


def can_dominate_repeated_path(
    candidate: dict[str, Any],
    repeated_path: dict[str, Any],
) -> bool:
    """
    Determine whether a non-repeated path is a reasonable substitute
    for a repeated path.

    A candidate can dominate only when:

    1. it contains no repeated function;
    2. it is no longer than the repeated path;
    3. both paths end at the same target function;
    4. both paths have the same abstract terminal state;
    5. its violation classification is no worse;
    6. it has no more require conflicts;
    7. it has no fewer require matches.

    Property score is deliberately not required to be no worse,
    because repeated visits can artificially increase dependency
    and property scores.
    """
    candidate_sequence = candidate["sequence"]
    repeated_sequence = repeated_path["sequence"]

    if repeat_count(candidate_sequence) != 0:
        return False

    if repeat_count(repeated_sequence) == 0:
        return False

    if not candidate_sequence or not repeated_sequence:
        return False

    # A useful setup call can replace a repeated target call without
    # reducing the total path length.  For example, ``init -> run`` is
    # preferable to ``run -> run`` even though both paths contain two
    # calls.  Requiring a *strictly* shorter candidate leaves that kind
    # of artificial repetition unpenalized.
    if len(candidate_sequence) > len(repeated_sequence):
        return False

    if candidate_sequence[-1] != repeated_sequence[-1]:
        return False

    # A repeated visit is not redundant when it changes the abstract
    # terminal state.  This guard is intentionally conservative: without
    # proving state-effect equivalence, a shorter path must not suppress a
    # repeated path that may be required to satisfy a later guard (for
    # example depositCount == 2 in RepeatedCallExample).
    if candidate.get("terminal_state") != repeated_path.get(
        "terminal_state"
    ):
        return False

    candidate_priority = VIOLATION_PRIORITY[
        candidate["violation_class"]
    ]

    repeated_priority = VIOLATION_PRIORITY[
        repeated_path["violation_class"]
    ]

    if candidate_priority < repeated_priority:
        return False

    if conflicts_of(candidate) > conflicts_of(
        repeated_path
    ):
        return False

    if matches_of(candidate) < matches_of(
        repeated_path
    ):
        return False

    return True


def mark_dominated_repeat_paths(
    paths: list[dict[str, Any]],
) -> None:
    """
    Locally penalize unnecessary repeated paths.

    This does not globally prioritize short paths. A long path without
    redundant repetition keeps its original semantic and value-ranking
    evidence, which preserves cases such as BranchValue.

    A repeated path is penalized only when a no-longer non-repeated path
    reaches the same final function with no worse violation and require
    evidence.
    """
    non_repeated_paths = [
        path
        for path in paths
        if repeat_count(path["sequence"]) == 0
    ]

    for repeated_path in paths:
        if repeat_count(
            repeated_path["sequence"]
        ) == 0:
            continue

        dominating_candidates = [
            candidate
            for candidate in non_repeated_paths
            if can_dominate_repeated_path(
                candidate,
                repeated_path,
            )
        ]

        if not dominating_candidates:
            continue

        dominating_candidates.sort(
            key=base_semantic_key
        )

        best_candidate = dominating_candidates[0]

        repeated_path["dominated_repeat"] = 1
        repeated_path["dominated_by_sequence"] = (
            copy.deepcopy(
                best_candidate["sequence"]
            )
        )


def ranking_key(
    path: dict[str, Any],
) -> tuple[
    int,
    int,
    int,
    int,
    int,
    int,
    int,
    int,
]:
    """
    Final V2 lexicographic ranking.

    Priority:

    1. violation ability;
    2. fewer require conflicts;
    3. more require matches;
    4. non-dominated repetition;
    5. higher property/value evidence;
    6. shorter path;
    7. fewer repeated visits;
    8. original rank.

    Path length is intentionally placed after semantic, feasibility,
    repeat-dominance and property evidence. This prevents incomplete
    short paths from displacing valid longer paths such as BranchValue.
    """
    sequence = path["sequence"]

    return (
        -VIOLATION_PRIORITY[
            path["violation_class"]
        ],
        conflicts_of(path),
        -matches_of(path),
        int(
            path.get(
                "dominated_repeat",
                0,
            )
        ),
        -property_score_of(path),
        len(sequence),
        repeat_count(sequence),
        int(path["original_rank"]),
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rerank transaction paths according to "
            "their ability to violate an Echidna property."
        )
    )

    parser.add_argument(
        "candidates",
        type=Path,
        help="V1 candidate-path JSON",
    )

    parser.add_argument(
        "predicate_model",
        type=Path,
        help=(
            "JSON generated by "
            "extract_property_predicate.py"
        ),
    )

    parser.add_argument(
        "--contract",
        required=True,
    )

    parser.add_argument(
        "--property",
    )

    parser.add_argument(
        "--output",
        type=Path,
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    candidate_data = json.loads(
        arguments.candidates.read_text(
            encoding="utf-8"
        )
    )

    predicate_model = json.loads(
        arguments.predicate_model.read_text(
            encoding="utf-8"
        )
    )

    model_contract = predicate_model.get(
        "contract"
    )

    if model_contract != arguments.contract:
        raise ValueError(
            "Contract mismatch: "
            f"predicate model contains "
            f"{model_contract!r}, but "
            f"{arguments.contract!r} was requested."
        )

    property_name = choose_property(
        predicate_model,
        arguments.property,
    )

    property_data = predicate_model[
        "properties"
    ][property_name]

    if not property_data.get(
        "supported",
        False,
    ):
        raise ValueError(
            f"Property {property_name!r} is not "
            "supported by the V2 predicate extractor."
        )

    _, candidate_paths = load_candidate_container(
        candidate_data,
        arguments.contract,
    )

    annotated_paths = [
        annotate_path(
            path,
            predicate_model,
            property_name,
            original_rank,
        )
        for original_rank, path in enumerate(
            candidate_paths,
            start=1,
        )
    ]

    mark_dominated_repeat_paths(
        annotated_paths
    )

    ranked_paths = sorted(
        annotated_paths,
        key=ranking_key,
    )

    for v2_rank, path in enumerate(
        ranked_paths,
        start=1,
    ):
        path["v2_rank"] = v2_rank
        path["v2_ranking_key"] = list(
            ranking_key(path)
        )

    output_data = copy.deepcopy(
        candidate_data
    )

    output_container, _ = (
        load_candidate_container(
            output_data,
            arguments.contract,
        )
    )

    output_container["paths"] = ranked_paths

    output_container["v2_property"] = (
        property_name
    )

    output_container[
        "v2_ranking_policy"
    ] = [
        "violation_class_desc",
        "require_conflicts_asc",
        "require_matches_desc",
        "dominated_repeat_asc",
        "property_score_desc",
        "path_length_asc",
        "repeat_count_asc",
        "original_rank_asc",
    ]

    output_data["schema_version_v2"] = "2.0"
    output_data["method_version"] = (
        "Full-v2.0-core-1C-repeat-dominance"
    )

    serialized = json.dumps(
        output_data,
        ensure_ascii=False,
        indent=2,
    )

    if arguments.output:
        arguments.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        arguments.output.write_text(
            serialized + "\n",
            encoding="utf-8",
            newline="\n",
        )
    else:
        sys.stdout.write(
            serialized + "\n"
        )


if __name__ == "__main__":
    main()
