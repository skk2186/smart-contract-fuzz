#!/usr/bin/env python3
"""Build C1 paper-ready materials from frozen V1 inputs.

Only the audited paper-ready inputs are read.  The --write mode writes only
under paper-ready/v1/c1/ and never runs an experiment.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "paper-ready" / "v1"
OUT = INPUT / "c1"
SUMMARY = INPUT / "main10_results_summary.tsv"
REGISTRY = INPUT / "public_benchmark_registry.tsv"
EVIDENCE = INPUT / "evidence_index.tsv"

SUMMARY_FIELDS = {
    "benchmark_id", "benchmark_name", "method", "runs", "falsified",
    "budget_exhausted", "startup_error", "unknown_error", "incomplete",
    "parser_status_mismatch", "checksum_pass", "checksum_fail",
    "falsification_rate", "main_table_usable", "notes",
}
REGISTRY_FIELDS = {
    "benchmark_id", "benchmark_name", "source_path", "origin",
    "classification", "property", "target_sequence_or_goal",
    "semantic_risk", "main_table_eligible", "notes",
}
EVIDENCE_FIELDS = {
    "evidence_id", "stage", "source_path", "artifact_type",
    "claim_supported", "claim_limitations", "paper_section", "status",
    "use_in_main_table", "notes",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader)


def check_fields(path: Path, rows: list[dict[str, str]], required: set[str]) -> None:
    if not rows:
        raise ValueError(f"no rows: {path}")
    missing = sorted(required - set(rows[0]))
    if missing:
        raise ValueError(f"{path}: missing fields {', '.join(missing)}")


def number(row: dict[str, str], field: str) -> int:
    try:
        return int(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field}={row.get(field)!r}") from exc


def validate(
    summary: list[dict[str, str]],
    registry: list[dict[str, str]],
    evidence: list[dict[str, str]],
) -> list[str]:
    errors: list[str] = []
    try:
        check_fields(SUMMARY, summary, SUMMARY_FIELDS)
        check_fields(REGISTRY, registry, REGISTRY_FIELDS)
        check_fields(EVIDENCE, evidence, EVIDENCE_FIELDS)
    except ValueError as exc:
        return [str(exc)]

    if len(summary) != 12:
        errors.append(f"summary rows={len(summary)} (expected 12)")
    if len(registry) != 8:
        errors.append(f"registry rows={len(registry)} (expected 8)")
    if {r["benchmark_id"] for r in summary} != {"PUB01", "PUB02", "PUB03", "PUB04"}:
        errors.append("summary is outside the four supported B4 benchmark IDs")
    if {r["method"] for r in summary} != {"Original", "Full-K1", "Full-K5"}:
        errors.append("summary method set differs from Original/Full-K1/Full-K5")
    if any(r["main_table_usable"] != "conditional" for r in summary):
        errors.append("main_table_usable is not conditional for every summary row")
    supported = {r["benchmark_id"] for r in registry if r["classification"] == "supported"}
    conditional = {r["benchmark_id"] for r in registry if r["classification"] == "conditional"}
    excluded = {r["benchmark_id"] for r in registry if r["classification"] == "excluded"}
    if supported != {"PUB01", "PUB02", "PUB03", "PUB04"}:
        errors.append("registry supported scope differs from PUB01-PUB04")
    if conditional != {"PUB05"}:
        errors.append("registry conditional scope differs from PUB05")
    if excluded != {"PUB06", "PUB07", "PUB08"}:
        errors.append("registry excluded scope differs from PUB06-PUB08")

    fields = (
        "runs", "falsified", "budget_exhausted", "startup_error",
        "unknown_error", "incomplete", "parser_status_mismatch",
        "checksum_pass", "checksum_fail",
    )
    totals = Counter()
    for row in summary:
        for field in fields:
            try:
                totals[field] += number(row, field)
            except ValueError as exc:
                errors.append(str(exc))
    expected = {
        "runs": 120, "falsified": 118, "budget_exhausted": 2,
        "startup_error": 0, "unknown_error": 0, "incomplete": 0,
        "parser_status_mismatch": 0, "checksum_pass": 120, "checksum_fail": 0,
    }
    for field, want in expected.items():
        if totals[field] != want:
            errors.append(f"summary total {field}={totals[field]} (expected {want})")

    required_evidence = {
        "E05_PHASE03_FORMAL_MECHANISM", "E06_PHASE04_METHOD_POSITIONING",
        "E07_PHASE05_PUBLIC_PREREGISTRATION", "E10_MATCHED_RANDOM_QUARANTINE",
        "E11_HARNESS_SEMANTIC_BOUNDARY", "E12_PHASE_B1_NATIVE_REPLAY_PREP",
        "E15_PHASE_B2_NATIVE_REPLAY_GATE", "E16_NATIVE_REPLAY_GATE_REGISTRY",
        "E17_PHASE_B3_MAIN10_PREREGISTRATION", "E20_PHASE_B4_MAIN10_RUN",
        "E21_MAIN10_RESULTS_BY_RUN", "E22_MAIN10_RESULTS_SUMMARY",
    }
    missing = sorted(required_evidence - {r["evidence_id"] for r in evidence})
    if missing:
        errors.append("missing evidence IDs: " + ", ".join(missing))
    return errors


def cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(cell(v) for v in row) + " |" for row in rows)
    return "\n".join(lines)


def tsv(headers: list[str], rows: list[list[str]]) -> str:
    return "\n".join(["\t".join(headers), *["\t".join(row) for row in rows]]) + "\n"


def build_rq_map() -> str:
    headers = [
        "rq_id", "rq_title", "evidence_sources", "primary_metrics",
        "supported_claim", "limitations", "paper_section", "ready_for_paper",
    ]
    rows = [
        [
            "RQ1",
            "Can property-directed sequence planning produce intended candidate paths?",
            "E05_PHASE03_FORMAL_MECHANISM;E06_PHASE04_METHOD_POSITIONING",
            "candidate-path retention; Property/Value/Repeat/Top-K behavior on controlled benchmarks",
            "The V1 components address their declared controlled obstacles and produce auditable candidate paths.",
            "Designed small benchmarks; no real-ecosystem generalization or end-to-end speedup.",
            "Method; Mechanism evaluation",
            "yes, scoped",
        ],
        [
            "RQ2",
            "Can the generated Harness execute public property benchmarks reliably under the declared wrapper model?",
            "E07_PHASE05_PUBLIC_PREREGISTRATION;E11_HARNESS_SEMANTIC_BOUNDARY;E20_PHASE_B4_MAIN10_RUN;E21_MAIN10_RESULTS_BY_RUN;E22_MAIN10_RESULTS_SUMMARY",
            "artifact completeness; checksum pass; parser/status agreement; status counts",
            "The four preregistered supported tasks produced a complete and auditable 120-run result set under the declared wrapper model.",
            "B2 was static-only; Harness is not Original-equivalent; completeness does not prove safety.",
            "Experimental setup; Reproducibility; Threats",
            "yes, scoped",
        ],
        [
            "RQ3",
            "How do Original, Full-K1, and Full-K5 compare descriptively on the preregistered supported public tasks?",
            "E17_PHASE_B3_MAIN10_PREREGISTRATION;E18_MAIN10_PREREGISTRY;E20_PHASE_B4_MAIN10_RUN;E22_MAIN10_RESULTS_SUMMARY",
            "runs; falsified; budget_exhausted; observed falsification rate by task and method",
            "The three methods can be compared descriptively on the four supported tasks and seeds 1-10.",
            "No significance or superiority claim; no Total-calls speedup; budget observations are not passes.",
            "Results; Public benchmarks",
            "yes, descriptive",
        ],
        [
            "RQ4",
            "What semantic boundaries limit the interpretation of Harness results?",
            "E11_HARNESS_SEMANTIC_BOUNDARY;E12_PHASE_B1_NATIVE_REPLAY_PREP;E15_PHASE_B2_NATIVE_REPLAY_GATE;E16_NATIVE_REPLAY_GATE_REGISTRY",
            "caller model; transaction atomicity; rollback scope; value/time/external-call dependencies; supported/conditional classification",
            "Harness outcomes must be interpreted under a wrapper model and caller-sensitive tasks must remain conditional.",
            "B2 static_gate_only is not complete native replay; fixed-path consistency is not search-process equivalence.",
            "Threats; Semantic limits",
            "yes, as limitation",
        ],
    ]
    return tsv(headers, rows)


def build_claim_matrix() -> str:
    headers = [
        "claim_id", "claim_text", "evidence_ids", "source_files",
        "support_level", "can_write_in_paper", "must_not_overstate", "notes",
    ]
    rows = [
        ["C01", "V1 is an Echidna property-directed Harness synthesis preprocessing method.", "E06_PHASE04_METHOD_POSITIONING", "docs/v1-restart/PHASE_04_METHOD_CLAIM_AND_PREREGISTRATION.md;paper-ready/00_PROJECT_SUMMARY.md", "strong_within_scope", "yes", "Do not call it a new fuzzer or Echidna-core replacement.", "Method-positioning claim only."],
        ["C02", "Controlled Formal benchmarks can validate the Property/Value/Repeat/Top-K mechanisms.", "E05_PHASE03_FORMAL_MECHANISM;E06_PHASE04_METHOD_POSITIONING", "docs/v1-restart/PHASE_03_CONTROLLED_REGRESSION.md;paper-ready/00_PROJECT_SUMMARY.md", "moderate", "yes", "Limit to designed controlled obstacles; do not infer broad real-contract effectiveness.", "Mechanism evidence, not ecosystem evidence."],
        ["C03", "The B4 supported public tasks completed 120/120 runs with provenance checks passing.", "E20_PHASE_B4_MAIN10_RUN;E21_MAIN10_RESULTS_BY_RUN;E22_MAIN10_RESULTS_SUMMARY", "docs/v1-restart/PHASE_B4_MAIN10_RUN.md;docs/v1-restart/PHASE_B4_CLOSEOUT.md;paper-ready/v1/main10_results_summary.tsv", "strong_within_scope", "yes", "State the four-task, three-method, seeds 1-10 scope and conditional main-table status.", "118 falsified, 2 budget_exhausted; 120/120 checksums."],
        ["C04", "Full-K1 and Full-K5 show observed falsifications on most B4 task groups.", "E20_PHASE_B4_MAIN10_RUN;E22_MAIN10_RESULTS_SUMMARY", "docs/v1-restart/PHASE_B4_MAIN10_RUN.md;paper-ready/v1/main10_results_summary.tsv", "moderate", "yes", "Use descriptive wording; do not claim significance, superiority, safety, or speedup.", "Descriptive observation only."],
        ["C05", "Full-K1/Full-K5 are significantly better than Original.", "E20_PHASE_B4_MAIN10_RUN;E22_MAIN10_RESULTS_SUMMARY", "docs/v1-restart/PHASE_B4_MAIN10_RUN.md;paper-ready/v1/main10_results_summary.tsv", "forbidden", "no", "Do not infer statistical significance or superiority from this scoped 10-seed descriptive table.", "The requested strong claim is not supported."],
        ["C06", "Total calls prove speedup.", "E11_HARNESS_SEMANTIC_BOUNDARY;E17_PHASE_B3_MAIN10_PREREGISTRATION;E20_PHASE_B4_MAIN10_RUN", "docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md;docs/v1-restart/PHASE_B3_MAIN10_PREREGISTRATION.md;docs/v1-restart/PHASE_B4_MAIN10_RUN.md", "forbidden", "no", "Original and Harness count different execution layers; no equal-work comparison.", "Never use Total calls as speedup."],
        ["C07", "Harness and Original are completely equivalent.", "E11_HARNESS_SEMANTIC_BOUNDARY;E15_PHASE_B2_NATIVE_REPLAY_GATE", "docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md;docs/v1-restart/PHASE_B2_NATIVE_REPLAY_GATE.md", "forbidden", "no", "Caller, atomicity, rollback, value and block/environment semantics differ.", "Fixed-path agreement would still be narrow."],
        ["C08", "budget_exhausted represents a passed property.", "E20_PHASE_B4_MAIN10_RUN;E22_MAIN10_RESULTS_SUMMARY", "docs/v1-restart/PHASE_B4_MAIN10_RUN.md;paper-ready/v1/main10_results_summary.md", "forbidden", "no", "It means no observed counterexample within the declared budget.", "Not a pass and not a safety proof."],
        ["C09", "V1 is generally better than SMARTIAN/MuFuzz/IR-Fuzz.", "E06_PHASE04_METHOD_POSITIONING;E20_PHASE_B4_MAIN10_RUN", "paper-ready/00_PROJECT_SUMMARY.md;docs/v1-restart/PHASE_B4_MAIN10_RUN.md", "forbidden", "no", "No broad tool-level comparison is established.", "SMARTIAN evidence is only a narrow separate control; MuFuzz/IR-Fuzz are not compared here."],
        ["C10", "exercise2-access-control can enter the supported pooled result.", "E11_HARNESS_SEMANTIC_BOUNDARY;E15_PHASE_B2_NATIVE_REPLAY_GATE;E16_NATIVE_REPLAY_GATE_REGISTRY", "docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md;docs/v1-restart/PHASE_B2_NATIVE_REPLAY_GATE.md;paper-ready/v1/native_replay_gate.tsv", "forbidden", "no", "Keep it conditional because caller/address-keyed mapping semantics require caller-controlled replay.", "It contributes zero B4 supported-pool runs."],
        ["C11", "matched-random-v1 can support a new paper claim.", "E10_MATCHED_RANDOM_QUARANTINE", "results/matched-random-v1/;docs/v1-restart/PHASE_01_CHECKSUM_AUDIT.md", "forbidden", "no", "Provenance is unresolved and the control is quarantined.", "Do not use or pool it for new claims."],
        ["C12", "The current evidence is sufficient for a narrow CCF-C submission attempt.", "E20_PHASE_B4_MAIN10_RUN;E22_MAIN10_RESULTS_SUMMARY;E11_HARNESS_SEMANTIC_BOUNDARY", "docs/v1-restart/PHASE_B4_CLOSEOUT.md;paper-ready/00_PROJECT_SUMMARY.md;docs/v1-restart/SEMANTIC_BOUNDARY_AUDIT.md", "limited", "yes, with narrow positioning", "Do not present the evidence as broad ecosystem validation or a tool-level SOTA result.", "A submission attempt is a positioning decision, not a result claim."],
    ]
    return tsv(headers, rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate frozen V1 inputs and build C1 paper-ready tables/maps; never runs experiments."
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true", help="validate inputs without writing files")
    modes.add_argument("--write", action="store_true", help="validate and write only paper-ready/v1/c1/")
    args = parser.parse_args()
    try:
        summary = read_tsv(SUMMARY)
        registry = read_tsv(REGISTRY)
        evidence = read_tsv(EVIDENCE)
        errors = validate(summary, registry, evidence)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("c1_input_check=fail")
        return 1
    print("c1_input_check=pass")
    print(f"summary_rows={len(summary)}")
    print(f"registry_rows={len(registry)}")
    print(f"evidence_rows={len(evidence)}")
    print("b4_runs=120")
    print("b4_falsified=118")
    print("b4_budget_exhausted=2")
    print("main_table_usable=conditional")
    if args.check:
        print("write=none")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "evaluation_tables.md").write_text(
        build_evaluation_tables(summary, registry), encoding="utf-8"
    )
    (OUT / "rq_evidence_map.tsv").write_text(build_rq_map(), encoding="utf-8")
    (OUT / "claim_evidence_matrix.tsv").write_text(build_claim_matrix(), encoding="utf-8")
    print("write=paper-ready/v1/c1/evaluation_tables.md")
    print("write=paper-ready/v1/c1/rq_evidence_map.tsv")
    print("write=paper-ready/v1/c1/claim_evidence_matrix.tsv")
    return 0


def build_evaluation_tables(
    summary: list[dict[str, str]], registry: list[dict[str, str]]
) -> str:
    registry_table: list[list[str]] = []
    for row in registry:
        bid = row["benchmark_id"]
        if bid in {"PUB01", "PUB02", "PUB03", "PUB04"}:
            role = "B4 supported pool; conditional main-table use"
        elif bid == "PUB05":
            role = "Conditional appendix only; never pooled"
        else:
            role = "Excluded internal candidate; zero B4 runs"
        registry_table.append([
            bid,
            row["benchmark_name"],
            row["classification"],
            row["property"],
            row["target_sequence_or_goal"],
            row["semantic_risk"],
            role,
        ])

    result_table = [
        [
            row["benchmark_name"],
            row["method"],
            row["runs"],
            row["falsified"],
            row["budget_exhausted"],
            row["falsification_rate"],
            row["main_table_usable"],
        ]
        for row in summary
    ]

    lines = [
        "# Evaluation tables (C1 draft)",
        "",
        "These tables are generated from the frozen V1 registry and B4 summary. They are descriptive paper material; run-level rows belong in an appendix.",
        "",
        "## Table 1. Benchmark registry and semantic classification",
        "",
        md_table(
            ["ID", "Benchmark", "Class", "Property", "Declared path/goal", "Semantic risk", "Paper role"],
            registry_table,
        ),
        "",
        "Only PUB01-PUB04 enter the B4 supported pool. PUB05 (exercise2-access-control) remains conditional because of caller identity and address-keyed state; PUB06-PUB08 are excluded internal candidates and contribute no runs. B2 static_gate_pass is a static applicability gate, not a native replay result.",
        "",
        "## Table 2. B4 10-seed descriptive results by benchmark and method",
        "",
        md_table(
            ["Benchmark", "Method", "Runs", "Falsified", "Budget exhausted", "Falsification rate", "Main-table usable"],
            result_table,
        ),
        "",
        "Across the 120 preregistered runs, 118 were classified as falsified and 2 as budget_exhausted; no run was classified as startup_error, unknown_error, or incomplete. budget_exhausted means that no counterexample was observed within the declared budget. It is not a property pass and not a contract-safety result. The two observations are b4-echidna-multi-original-s1 and b4-echidna-multi-full-k5-s7.",
        "",
        "All rows retain main_table_usable=conditional. The rates are observed descriptive rates for four preregistered supported public tasks and seeds 1-10; they do not establish statistical superiority, semantic equivalence, or ecosystem-wide generalization.",
        "",
        "## Table 3. Status and provenance completeness",
        "",
        md_table(
            ["Audit item", "Observed result", "Interpretation"],
            [
                ["Expected B4 runs", "120 / 120", "All preregistered benchmark x method x seed rows are represented."],
                ["Complete artifact sets", "120 / 120", "Manifest, command, environment, raw, parsed, summary, status and checksum artifacts are retained."],
                ["Checksum verification", "120 / 120 pass", "No checksum failure in the derived audit."],
                ["Parser/status mismatch", "0", "No promotion-blocking reconciliation mismatch observed."],
                ["startup_error / unknown_error / incomplete", "0 / 0 / 0", "No run fell into these failure classes."],
                ["Seeds and scope", "1-10; 4 tasks x 3 methods", "No seed 11-30, conditional PUB05, or excluded PUB06-PUB08 was included."],
                ["Main-table flag", "conditional", "Manual review and semantic caveats remain required; this is not yes."],
            ],
        ),
        "",
        "Run-level provenance and raw logs should be placed in an appendix or reproducibility package rather than in the main result table.",
        "",
        "## Table 4. Allowed and disallowed claims",
        "",
        md_table(
            ["Claim family", "Paper wording", "Boundary"],
            [
                ["Allowed", "V1 is an external property-directed Harness-synthesis preprocessing method for Echidna.", "Do not describe it as a new Echidna replacement or general-purpose fuzzer."],
                ["Allowed", "Controlled Formal benchmarks provide evidence for the Property/Value/Repeat/Top-K mechanisms.", "Designed mechanism tests, not a representative ecosystem sample."],
                ["Allowed", "The four preregistered supported tasks yielded a complete, auditable 120-run descriptive comparison.", "Report 118 falsified and 2 budget_exhausted with the stated budget interpretation."],
                ["Allowed", "Full-K1 and Full-K5 produced observed falsifications on most supported task groups.", "Descriptive only; do not convert this into significant superiority or speedup."],
                ["Disallowed", "Full-K1/Full-K5 are significantly better than Original.", "Not supported by this scoped 10-seed descriptive table."],
                ["Disallowed", "Total calls demonstrate speedup.", "Original and Harness count different execution layers."],
                ["Disallowed", "Harness and Original are fully equivalent.", "Caller, transaction atomicity, rollback and environment semantics differ."],
                ["Disallowed", "budget_exhausted means the property passed or the contract is safe.", "It only means no observed counterexample within budget."],
                ["Disallowed", "V1 is generally better than Echidna, SMARTIAN, MuFuzz or IR-Fuzz.", "No tool-level comparison is established here."],
                ["Disallowed", "PUB05, matched-random-v1, or PUB06-PUB08 can be pooled into this result.", "They remain conditional, quarantined, or excluded."],
            ],
        ),
        "",
        "## Table 5. Threats and mitigations",
        "",
        md_table(
            ["Threat", "Risk to interpretation", "Mitigation in this evaluation"],
            [
                ["Small public sample", "Four supported public tasks cannot represent the real-contract ecosystem.", "Report task-level descriptive results; prioritize more public benchmarks for strengthening."],
                ["Conditional access-control task", "Caller/address mapping semantics can change the observed path.", "Keep exercise2-access-control outside the supported pool; require caller-controlled replay for an appendix."],
                ["Static semantic gate", "B2 static_gate_pass could be mistaken for native replay.", "Label B2 static_gate_only; retain task-level replay as a gate for future promotion."],
                ["Wrapper execution model", "Harness and Original differ in caller, transaction and rollback boundaries.", "Report Harness results under the wrapper model and avoid equivalence claims."],
                ["Work metric mismatch", "Total calls can count different layers across methods.", "Do not use Total calls as a speedup measure."],
                ["Legacy control provenance", "matched-random-v1 has unresolved provenance.", "Keep it quarantined and do not use it for new claims."],
                ["External baseline scope", "No tool-level SMARTIAN/MuFuzz/IR-Fuzz comparison is available.", "State the baseline limitation and make only the narrow method-positioning claim."],
            ],
        ),
        "",
        "## Caption drafts",
        "",
        "**Table 1.** Public benchmark registry and semantic classification used to define the supported pool. Only PUB01-PUB04 enter the B4 descriptive comparison; PUB05 is conditional and PUB06-PUB08 are excluded.",
        "",
        "**Table 2.** Descriptive outcomes for the preregistered four-task, three-method, 10-seed comparison. Falsified denotes an observed counterexample under the declared execution model; budget_exhausted denotes no observed counterexample within budget and is not a pass or safety proof.",
        "",
        "**Table 3.** Completeness and provenance audit for the 120 expected B4 runs. The main-table flag remains conditional because artifact completeness does not remove the Harness/Original semantic boundary.",
        "",
        "**Table 4.** Claim boundary for the V1 evaluation. Allowed statements are phase- and scope-limited; disallowed statements require evidence not present in this dataset.",
        "",
        "**Table 5.** Threats to validity and the controls or reporting constraints used to limit over-interpretation.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
