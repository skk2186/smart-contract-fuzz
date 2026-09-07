# Evaluation tables (C1 draft)

These tables are generated from the frozen V1 registry and B4 summary. They are descriptive paper material; run-level rows belong in an appendix.

## Table 1. Benchmark registry and semantic classification

| ID | Benchmark | Class | Property | Declared path/goal | Semantic risk | Paper role |
|---|---|---|---|---|---|---|
| PUB01 | echidna-flags | supported | echidna_sometimesfalse | set0(100*k) -> set1(10*m) | parameter constraints; wrapper atomicity caveat | B4 supported pool; conditional main-table use |
| PUB02 | echidna-multi | supported | echidna_state3 | f(12) -> g(8) -> h(z) | step require chain; wrapper atomicity caveat | B4 supported pool; conditional main-table use |
| PUB03 | smartbugs-multifunc | supported | echidna_count_does_not_underflow | init() -> run(a) -> run(b), second input targets unchecked underflow | Solidity 0.4.x arithmetic and wrapper atomicity | B4 supported pool; conditional main-table use |
| PUB04 | smartbugs-onefunc | supported | echidna_count_does_not_underflow | run(a) -> run(b), second input targets unchecked underflow | Solidity 0.4.x arithmetic and wrapper atomicity | B4 supported pool; conditional main-table use |
| PUB05 | exercise2-access-control | conditional | echidna_no_transfer | Owner() -> resume() with same caller; compare alternating callers | msg.sender; address-keyed mapping; caller alternation | Conditional appendix only; never pooled |
| PUB06 | alternative-path-internal | excluded | echidna_value_safe | openRouteA/B -> confirm -> execute(x) | internal synthetic toy; stage require; no public provenance | Excluded internal candidate; zero B4 runs |
| PUB07 | multi-property-internal | excluded | echidna_value_a_safe; echidna_value_b_safe | prepare -> authorize -> execute(x,y) | internal synthetic toy; two properties; no public provenance | Excluded internal candidate; zero B4 runs |
| PUB08 | three-step-internal | excluded | echidna_value_safe | register -> deposit -> withdraw(x) | internal synthetic toy; prior pilot material; no public provenance | Excluded internal candidate; zero B4 runs |

Only PUB01-PUB04 enter the B4 supported pool. PUB05 (exercise2-access-control) remains conditional because of caller identity and address-keyed state; PUB06-PUB08 are excluded internal candidates and contribute no runs. B2 static_gate_pass is a static applicability gate, not a native replay result.

## Table 2. B4 10-seed descriptive results by benchmark and method

| Benchmark | Method | Runs | Falsified | Budget exhausted | Falsification rate | Main-table usable |
|---|---|---|---|---|---|---|
| echidna-flags | Original | 10 | 10 | 0 | 1.000000 | conditional |
| echidna-flags | Full-K1 | 10 | 10 | 0 | 1.000000 | conditional |
| echidna-flags | Full-K5 | 10 | 10 | 0 | 1.000000 | conditional |
| echidna-multi | Original | 10 | 9 | 1 | 0.900000 | conditional |
| echidna-multi | Full-K1 | 10 | 10 | 0 | 1.000000 | conditional |
| echidna-multi | Full-K5 | 10 | 9 | 1 | 0.900000 | conditional |
| smartbugs-multifunc | Original | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-multifunc | Full-K1 | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-multifunc | Full-K5 | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-onefunc | Original | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-onefunc | Full-K1 | 10 | 10 | 0 | 1.000000 | conditional |
| smartbugs-onefunc | Full-K5 | 10 | 10 | 0 | 1.000000 | conditional |

Across the 120 preregistered runs, 118 were classified as falsified and 2 as budget_exhausted; no run was classified as startup_error, unknown_error, or incomplete. budget_exhausted means that no counterexample was observed within the declared budget. It is not a property pass and not a contract-safety result. The two observations are b4-echidna-multi-original-s1 and b4-echidna-multi-full-k5-s7.

All rows retain main_table_usable=conditional. The rates are observed descriptive rates for four preregistered supported public tasks and seeds 1-10; they do not establish statistical superiority, semantic equivalence, or ecosystem-wide generalization.

## Table 3. Status and provenance completeness

| Audit item | Observed result | Interpretation |
|---|---|---|
| Expected B4 runs | 120 / 120 | All preregistered benchmark x method x seed rows are represented. |
| Complete artifact sets | 120 / 120 | Manifest, command, environment, raw, parsed, summary, status and checksum artifacts are retained. |
| Checksum verification | 120 / 120 pass | No checksum failure in the derived audit. |
| Parser/status mismatch | 0 | No promotion-blocking reconciliation mismatch observed. |
| startup_error / unknown_error / incomplete | 0 / 0 / 0 | No run fell into these failure classes. |
| Seeds and scope | 1-10; 4 tasks x 3 methods | No seed 11-30, conditional PUB05, or excluded PUB06-PUB08 was included. |
| Main-table flag | conditional | Manual review and semantic caveats remain required; this is not yes. |

Run-level provenance and raw logs should be placed in an appendix or reproducibility package rather than in the main result table.

## Table 4. Allowed and disallowed claims

| Claim family | Paper wording | Boundary |
|---|---|---|
| Allowed | V1 is an external property-directed Harness-synthesis preprocessing method for Echidna. | Do not describe it as a new Echidna replacement or general-purpose fuzzer. |
| Allowed | Controlled Formal benchmarks provide evidence for the Property/Value/Repeat/Top-K mechanisms. | Designed mechanism tests, not a representative ecosystem sample. |
| Allowed | The four preregistered supported tasks yielded a complete, auditable 120-run descriptive comparison. | Report 118 falsified and 2 budget_exhausted with the stated budget interpretation. |
| Allowed | Full-K1 and Full-K5 produced observed falsifications on most supported task groups. | Descriptive only; do not convert this into significant superiority or speedup. |
| Disallowed | Full-K1/Full-K5 are significantly better than Original. | Not supported by this scoped 10-seed descriptive table. |
| Disallowed | Total calls demonstrate speedup. | Original and Harness count different execution layers. |
| Disallowed | Harness and Original are fully equivalent. | Caller, transaction atomicity, rollback and environment semantics differ. |
| Disallowed | budget_exhausted means the property passed or the contract is safe. | It only means no observed counterexample within budget. |
| Disallowed | V1 is generally better than Echidna, SMARTIAN, MuFuzz or IR-Fuzz. | No tool-level comparison is established here. |
| Disallowed | PUB05, matched-random-v1, or PUB06-PUB08 can be pooled into this result. | They remain conditional, quarantined, or excluded. |

## Table 5. Threats and mitigations

| Threat | Risk to interpretation | Mitigation in this evaluation |
|---|---|---|
| Small public sample | Four supported public tasks cannot represent the real-contract ecosystem. | Report task-level descriptive results; prioritize more public benchmarks for strengthening. |
| Conditional access-control task | Caller/address mapping semantics can change the observed path. | Keep exercise2-access-control outside the supported pool; require caller-controlled replay for an appendix. |
| Static semantic gate | B2 static_gate_pass could be mistaken for native replay. | Label B2 static_gate_only; retain task-level replay as a gate for future promotion. |
| Wrapper execution model | Harness and Original differ in caller, transaction and rollback boundaries. | Report Harness results under the wrapper model and avoid equivalence claims. |
| Work metric mismatch | Total calls can count different layers across methods. | Do not use Total calls as a speedup measure. |
| Legacy control provenance | matched-random-v1 has unresolved provenance. | Keep it quarantined and do not use it for new claims. |
| External baseline scope | No tool-level SMARTIAN/MuFuzz/IR-Fuzz comparison is available. | State the baseline limitation and make only the narrow method-positioning claim. |

## Caption drafts

**Table 1.** Public benchmark registry and semantic classification used to define the supported pool. Only PUB01-PUB04 enter the B4 descriptive comparison; PUB05 is conditional and PUB06-PUB08 are excluded.

**Table 2.** Descriptive outcomes for the preregistered four-task, three-method, 10-seed comparison. Falsified denotes an observed counterexample under the declared execution model; budget_exhausted denotes no observed counterexample within budget and is not a pass or safety proof.

**Table 3.** Completeness and provenance audit for the 120 expected B4 runs. The main-table flag remains conditional because artifact completeness does not remove the Harness/Original semantic boundary.

**Table 4.** Claim boundary for the V1 evaluation. Allowed statements are phase- and scope-limited; disallowed statements require evidence not present in this dataset.

**Table 5.** Threats to validity and the controls or reporting constraints used to limit over-interpretation.
