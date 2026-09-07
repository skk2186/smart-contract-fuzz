# Phase B3: Main10 Preregistration and Runner Lock

## 1. Purpose and stage boundary

This stage freezes the scope and execution contract for the B4 public
supported 10-seed main run. It is a preregistration and runner-safety stage,
not a fuzzing experiment.

No Echidna fuzzing, 10-seed run, 30-seed run, B4 main10 run, Slither run, or
solc compilation is performed by this stage. The only new run directories are
the two explicitly requested safe checks under the B4 work root. They contain
provenance records showing that fuzzing was skipped.

The research question for B4 is narrow: after the supported public benchmark
scope and execution budget are fixed, does the preregistered Original versus
Full-K1 versus Full-K5 comparison produce a complete, classifiable, and
auditable 120-run result set? B3 itself cannot answer that question.

## 2. B2 decision carried into B3

B2 produced a static semantic gate only. static_gate_pass is not replay_pass,
and no B2 row is a fuzzing result. The four rows below are the only rows
permitted into the B4 supported pool:

- PUB01 echidna-flags
- PUB02 echidna-multi
- PUB03 smartbugs-multifunc
- PUB04 smartbugs-onefunc

PUB05 exercise2-access-control remains conditional. Its msg.sender, owner
equality, and address-keyed mapping require caller-controlled same-caller and
alternating-caller replay before it could be considered for a separate
conditional analysis. It is not part of B4.

PUB06, PUB07, and PUB08 remain excluded internal candidates. They are not
public benchmark additions and are not part of B4. matched-random-v1 is not
an input, baseline, or pooled result source.

## 3. Locked B4 supported scope

| benchmark_id | benchmark_name | classification | gate_status | b4_included | method_set | seed_set | expected_runs | config_path | source_path | property | main_table_role | notes |
|---|---|---|---|---|---|---|---:|---|---|---|---|---|
| PUB01 | echidna-flags | supported | static_gate_pass / static_gate_only | yes | Original; Full-K1; Full-K5 | 1-10 | 30 | Original: configs/public-c1-original.yaml; Harness: configs/public-c1-harness.yaml | contracts/public-benchmarks/adapted/EchidnaFlagsTarget.sol | echidna_sometimesfalse | candidate only after successful B4 summary | set0 -> set1 is traceable; retain wrapper atomicity and Original/Harness semantic caveats. |
| PUB02 | echidna-multi | supported | static_gate_pass / static_gate_only | yes | Original; Full-K1; Full-K5 | 1-10 | 30 | Original: configs/public-c1-original.yaml; Harness: configs/public-c1-harness.yaml | contracts/public-benchmarks/raw/echidna/multi.sol | echidna_state3 | candidate only after successful B4 summary | The require chain is traceable; an Original budget exhaustion is not property passed. |
| PUB03 | smartbugs-multifunc | supported | static_gate_pass / static_gate_only | yes | Original; Full-K1; Full-K5 | 1-10 | 30 | Original: configs/public-c1-original.yaml; Harness: configs/public-c1-harness.yaml | contracts/public-benchmarks/adapted/SmartBugsMultiFuncEchidna.sol | echidna_count_does_not_underflow | candidate only after successful B4 summary | Preserve Solidity 0.4.x unchecked arithmetic and the required repeated run call; this is bounded adapted evidence. |
| PUB04 | smartbugs-onefunc | supported | static_gate_pass / static_gate_only | yes | Original; Full-K1; Full-K5 | 1-10 | 30 | Original: configs/public-c1-original.yaml; Harness: configs/public-c1-harness.yaml | contracts/public-benchmarks/adapted/SmartBugsOneFuncEchidna.sol | echidna_count_does_not_underflow | candidate only after successful B4 summary | Repeated single-function integration evidence is not multi-function ordering evidence. |
| PUB05 | exercise2-access-control | conditional | conditional_replay_required / static_gate_only | no | — | — | 0 | — | contracts/public-benchmarks/raw/exercise2/solution.sol | echidna_no_transfer | conditional appendix only | Caller-controlled replay is still required; never pool with the four supported rows. |
| PUB06 | alternative-path-internal | excluded | excluded | no | — | — | 0 | — | contracts/benchmarks/AlternativePathExample.sol | echidna_value_safe | excluded | Internal toy; no public provenance; do not count in B4. |
| PUB07 | multi-property-internal | excluded | excluded | no | — | — | 0 | — | contracts/benchmarks/MultiPropertyExample.sol | echidna_value_a_safe; echidna_value_b_safe | excluded | Internal toy; no public provenance; do not count in B4. |
| PUB08 | three-step-internal | excluded | excluded | no | — | — | 0 | — | contracts/benchmarks/ThreeStepExample.sol | echidna_value_safe | excluded | Internal early controlled toy; do not count in B4. |

The locked size is 4 benchmarks x 3 methods x 10 seeds = 120 runs. PUB05,
PUB06, PUB07, and PUB08 contribute zero runs to this total.

## 4. Methods, budget, and configuration inheritance

The B4 method set is exactly Original, Full-K1, and Full-K5. The
machine-readable expected-run registry normalizes these names to original,
full-k1, and full-k5 for run IDs and runner arguments.

Both public C-1 configs are inherited unchanged from the Phase 06A pilot:

| field | Original | Full-K1 / Full-K5 | locked interpretation |
|---|---:|---:|---|
| testMode | property | property | same property-mode oracle |
| testLimit | 100000 | 100000 | main budget; never adjusted after seeing results |
| timeout | 30 seconds | 30 seconds | per-run timeout |
| seqLen | 4 | 1 | different execution layers: independent Original transactions versus one Harness wrapper call |
| workers | 1 | 1 | fixed serial worker count |
| stopOnFail | true | true | fixed stop policy |
| coverage | true | true | inherited config field; not a new coverage claim |
| format | text | text | raw log format |
| corpus | none | none | no corpusDir; no corpus-seed or matched-random-v1 input |

The compiler recorded by the existing public preflight remains benchmark
specific: 0.8.20 for PUB01/PUB02 and 0.4.25 for PUB03/PUB04. This is compiler
provenance, not a per-method budget exception. The 0.4.x rows retain their
unchecked arithmetic caveat.

Original and Harness do not have identical transaction semantics. A Harness
seqLen=1 is one outer wrapper call that may contain several target calls;
Original seqLen=4 is Echidna's multi-transaction search. Caller identity,
atomicity, rollback boundary, and the meaning of Total calls therefore remain
explicit limitations. Total calls must not be used to claim speedup.

## 5. Output and provenance lock

Every future B4 run must use the fixed root:

~~~text
work/v1-restart/b4-public-supported-10seed-main/<run_id>/
~~~

The expected-run registry enumerates all 120 exact run IDs. Each completed or
failed run must retain at least:

~~~text
manifest.tsv
command.txt
environment.txt
generated/
raw/
parsed/
summary/
status/
status/checksums.sha256
~~~

The runner refuses existing output directories, symlinked roots, unregistered
run IDs, and output paths under results/, paper-ready/ raw-result paths, or
matched-random-v1/. B4 raw logs are never written to frozen evidence.
main10-preflight and main10-dry-run use a fresh b3-main10-* safe-check ID and
write only safe-check provenance; only main10 execution IDs must match the B4 expected-run registry. They do not write Phase 06A or B2 artifacts.

The existing Phase 06A preflight Harness artifacts remain the input source for
the eventual B4 main10 execution. B3 safe modes validate the preregistration
and output protocol; they do not regenerate those artifacts or compile them.

## 6. Runner guard contract

scripts/run_v1_public_smoke_case.sh now recognizes main10-preflight,
main10-dry-run, and the reserved B4 main10 mode. For all main10 modes it:

1. accepts only echidna-flags, echidna-multi, smartbugs-multifunc, and smartbugs-onefunc;
2. rejects exercise2-access-control as conditional;
3. rejects PUB06/PUB07/PUB08 and matched-random-v1;
4. accepts only seed 1 through 10 and explicitly rejects seed 11 through 30;
5. accepts only Original/Full-K1/Full-K5 (case-normalized for the main10 interface);
6. requires a b3-main10-* safe-check ID in safe modes, and a unique run ID matching main10_expected_runs.tsv in main10 execution mode;
7. fixes output below work/v1-restart/b4-public-supported-10seed-main/;
8. skips all Echidna, Slither, solc, and solc-select invocation in the two safe modes;
9. records manifest, command, environment, raw, parsed, summary, status, and checksums;
10. preserves the existing falsified/failed-marker-first classification order for the eventual main run.

The main10 mode is intentionally not invoked in B3. Its presence is a future
B4 execution interface, not a B3 result.

## 7. Status classification lock

For a future B4 run:

- a falsified or failed marker takes priority over budget markers;
- an exit code of zero without a falsified marker is classified by the existing runner/parser rules;
- budget_exhausted means no observed counterexample within the declared budget;
- budget_exhausted is not property passed and is not contract safe;
- startup_error, unknown_error, and incomplete remain separate;
- a parser/status mismatch blocks promotion to any main result table;
- static_gate_pass is not replay pass;
- Phase 06A pilot output is provenance/pilot evidence, not a B4 main result.

## 8. What B4 may and may not claim

After all 120 preregistered runs complete, raw logs and parser output reconcile,
all status/checksum records pass audit, and a fixed summary is generated, B4
may provide a phase-scoped descriptive comparison for these four supported
benchmarks and three declared methods. The resulting table may be considered
for the public-benchmark results section only after that successful summary and
manual review.

B3 and B4 do not authorize claims that V1 is generally better than Echidna,
SMARTIAN, MuFuzz, or IR-Fuzz; that four tasks represent the real-contract
ecosystem; that Harness and Original are semantically equivalent; that
budget_exhausted is a pass or safety proof; that Total calls implies speedup;
or that a preregistration or pilot is a main result. Conditional exercise2 and
excluded PUB06/PUB07/PUB08 cannot be pooled into the supported main table.

## 9. B4 execution-entry checklist

Before any main10 invocation, the researcher must verify:

1. branch is develop, HEAD is the intended reviewed commit, and WSL Git reports a clean worktree;
2. runner index and filesystem modes are executable (100755 / 755);
3. python3 analyzer/build_main10_preregistration.py --check passes;
4. the two preregistration TSVs have 12 and 120 data rows, respectively;
5. only PUB01-PUB04 occur in those TSVs, with no exercise2, PUB06, PUB07, PUB08, or matched-random entry;
6. the public registry still marks PUB01-PUB04 b3_preregistered and after_b4_success, while PUB05 is conditional and PUB06-PUB08 are excluded;
7. Phase 06A preflight Harness artifacts and B2 static gate records are present and unchanged;
8. bash -n scripts/run_v1_public_smoke_case.sh and git diff --check pass;
9. the intended run ID is present in main10_expected_runs.tsv and its output directory does not already exist;
10. a researcher manually reviews this preregistration, the expected-run list, and the first safe-check artifacts before authorizing B4.

The B4 command template is represented by the runner's recorded command for a
preregistered run, for example:

~~~text
bash scripts/run_v1_public_smoke_case.sh --mode main10 --run-id b4-echidna-flags-original-s1 --benchmark echidna-flags --method Original --seed 1
~~~

That command is not executed during B3.

