# C5 Final Table Drafts

以下是供论文排版和人工复核使用的表格草稿，不是新的实验结果。数字来自现有 `paper-ready/v1/` 表格、C1 evaluation material、evidence index 和已冻结的语义审计；不读取 `work/` 原始数据，也不展开 120 行 run-level 记录。

## Table 1. Benchmark registry and semantic classification

| ID | Benchmark | Classification | Property | Declared path/goal | Caller / semantic note | Replay / paper role |
|---|---|---|---|---|---|---|
| PUB01 | `echidna-flags` | supported | `echidna_sometimesfalse` | `set0(100*k) -> set1(10*m)` | same caller sufficient; parameter constraints; wrapper atomicity caveat | static gate only; supported B4 pool, main-table flag conditional |
| PUB02 | `echidna-multi` | supported | `echidna_state3` | `f(12) -> g(8) -> h(z)` | same caller sufficient; step `require` chain; wrapper atomicity caveat | static gate only; supported B4 pool, main-table flag conditional |
| PUB03 | `smartbugs-multifunc` | supported | `echidna_count_does_not_underflow` | `init() -> run(a) -> run(b)` | Solidity 0.4.x unchecked arithmetic; repeated run; wrapper atomicity caveat | static gate only; supported B4 pool, main-table flag conditional |
| PUB04 | `smartbugs-onefunc` | supported | `echidna_count_does_not_underflow` | `run(a) -> run(b)` | repeated single-function trigger; wrapper atomicity caveat | static gate only; supported B4 pool, main-table flag conditional |
| PUB05 | `exercise2-access-control` | conditional | `echidna_no_transfer` | `Owner() -> resume()` with caller condition | `msg.sender`, address-keyed mapping and caller alternation; high semantic risk | conditional appendix only; never pooled |
| PUB06 | `alternative-path-internal` | excluded | `echidna_value_safe` | `openRouteA/B -> confirm -> execute(x)` | internal synthetic toy; no public provenance | zero B4 runs |
| PUB07 | `multi-property-internal` | excluded | `echidna_value_a_safe`, `echidna_value_b_safe` | `prepare -> authorize -> execute(x,y)` | internal synthetic toy; two properties; no public provenance | zero B4 runs |
| PUB08 | `three-step-internal` | excluded | `echidna_value_safe` | `register -> deposit -> withdraw(x)` | prior internal pilot material; no public provenance | zero B4 runs |

**Table note.** Only PUB01--PUB04 enter the B4 supported pool. PUB05 remains conditional; PUB06--PUB08 are excluded internal candidates. `static_gate_pass` is not complete native EVM replay.

## Table 2. Controlled mechanism evidence

| Controlled benchmark / aggregate | Mechanism or contrast | Existing observation | Interpretation allowed in paper | Boundary |
|---|---|---|---|---|
| Four primary controlled benchmarks | Dependency -> Property candidate retention | 92 candidate paths -> 31 retained; 61 fewer; 66.30% reduction | Property-related filtering can shrink the inspected candidate set in the designed cases | Candidate-space change is not an end-to-end efficiency result |
| NoisyFourStep | Property filtering | 30 candidates -> 3; target path becomes unique Top-1 | The declared dependency/noise obstacle is observable and filterable | Constructed benchmark; not ecosystem evidence |
| BranchValue | Property-K1 vs Value-K1 / Full-K1 | Property-K1: 0/30; Value-K1: 30/30; Full-K1: 30/30 | Lightweight value direction evidence separates the declared value obstacle | Does not establish complete constraint solving |
| RepeatedCall | No-repeat configuration vs bounded repeat / Full | No-repeat: 0/30; Full method: 30/30 | Bounded repeat can retain the declared repeated-call path | Does not imply unlimited repetition or general public-task effect |
| ResetExample | Reset interference and Top-K ranking | Reset expands tied candidates; value evidence distinguishes the target path in the controlled ranking | Value evidence can help explain Top-K selection under the declared ranking obstacle | Do not call the selected path globally optimal |

**Table note.** These rows are mechanism evidence for small, purpose-built contracts. They do not support ecosystem-level generalization, tool ranking, or efficiency claims.

## Table 3. Public supported 10-seed results

| Benchmark | Method | Runs | Falsified | Budget exhausted | Observed falsification rate | Artifact complete | Checksum pass | Parser/status mismatch | Main-table usable |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `echidna-flags` | Original | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |
| `echidna-flags` | Full-K1 | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |
| `echidna-flags` | Full-K5 | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |
| `echidna-multi` | Original | 10 | 9 | 1 | 0.900000 | 10/10 | 10/10 | 0 | conditional |
| `echidna-multi` | Full-K1 | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |
| `echidna-multi` | Full-K5 | 10 | 9 | 1 | 0.900000 | 10/10 | 10/10 | 0 | conditional |
| `smartbugs-multifunc` | Original | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |
| `smartbugs-multifunc` | Full-K1 | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |
| `smartbugs-multifunc` | Full-K5 | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |
| `smartbugs-onefunc` | Original | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |
| `smartbugs-onefunc` | Full-K1 | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |
| `smartbugs-onefunc` | Full-K5 | 10 | 10 | 0 | 1.000000 | 10/10 | 10/10 | 0 | conditional |

**Table note.** Scope is 4 supported tasks × 3 methods × seeds 1--10 = 120 runs. Overall: 118 falsified and 2 budget exhausted. The two budget-exhausted rows are `echidna-multi/Original/seed 1` and `echidna-multi/Full-K5/seed 7`; this means no counterexample was observed within the declared budget, not that the property passed or the contract is safe. `main_table_usable=conditional` is intentionally unchanged.

## Table 4. Provenance completeness and status audit

| Audit item | Existing result | Paper interpretation |
|---|---:|---|
| Expected / represented B4 runs | 120 / 120 | All preregistered benchmark × method × seed rows are represented |
| Complete artifact sets | 120 / 120 | Manifest, command, environment, raw, parsed, summary, status and checksum artifacts are retained |
| Checksum verification | 120 / 120 pass | No checksum failure in the current derived audit |
| Parser/status mismatch | 0 | No reconciliation mismatch in the summary audit |
| `startup_error` | 0 | No startup error classified |
| `unknown_error` | 0 | No unknown error classified |
| `incomplete` | 0 | No incomplete run classified |
| `falsified` | 118 / 120 | Observed property counterexample under the declared execution model and budget |
| `budget_exhausted` | 2 / 120 | No observed counterexample within budget; not a pass or safety proof |
| Seed scope | 1--10 | No 30-seed result is part of this table |
| Main-table flag | conditional | Manual semantic review remains required; do not change to yes |
| Quarantined legacy control | matched-random-v1 | Provenance unresolved; excluded from new claims and pooled results |

**Table note.** Provenance completeness is an audit property of the result chain. It does not prove contract safety, semantic equivalence, independent reproduction, or tool superiority.

## Table 5. Allowed and forbidden claims

| Claim class | Allowed wording | Forbidden wording / boundary |
|---|---|---|
| Method position | PHS is an external property-directed Harness-synthesis preprocessing layer before Echidna | Do not call it a new complete fuzzer or an Echidna-core replacement |
| Controlled evidence | The designed benchmarks show observable Property/Value/Repeat/Top-K mechanism behavior | Do not generalize the constructed contracts to the ecosystem |
| Public result | The four supported tasks yield a complete, auditable 120-run descriptive comparison | Do not describe four tasks as ecosystem representation |
| Outcome counts | Report 118 falsified and 2 budget exhausted with their declared meanings | Do not call budget exhausted a pass, safety, or absence of vulnerability |
| Candidate reduction | Report candidate-space reduction as a planning observation | Do not turn candidate counts or Total calls into an efficiency or acceleration claim |
| Harness relation | Report caller, atomicity, rollback and context differences between Original and wrapper execution | Do not call the models fully equivalent or interchangeable |
| External tools | Cite SMARTIAN, MuFuzz, IR-Fuzz and others as related directions after verification | Do not claim tool-level superiority without a fair executed comparison |
| Conditional task | Keep `exercise2-access-control` as a separate conditional case | Do not pool it with PUB01--PUB04 |
| Legacy control | Keep matched-random-v1 in quarantine | Do not use it for a new paper claim |

## Table 6. Threats and mitigations

| Threat type | Threat | Existing mitigation | Remaining limitation |
|---|---|---|---|
| Internal validity | Purpose-built controlled benchmarks simplify real interactions | Keep mechanism rows separate and label them controlled evidence | No guarantee that the same signals dominate in other contracts |
| Internal validity | Original and Harness use different call layers and configurations | Record method, seqLen, compiler, budget and wrapper caveats | No equal-work or same-semantics comparison is established |
| Construct validity | `budget_exhausted`, artifact completeness and checksum can be conflated | Define them separately and retain status fields | They still do not measure safety probability |
| Semantic validity | Caller, atomicity, rollback, value, block context, external calls and reentrancy may differ | Figure 3, conditional registry and static-gate caveats | Complete caller-controlled/native replay remains future work |
| External validity | Only four public tasks are in the supported pool | Use task-level descriptive reporting; keep PUB05 conditional | More public tasks and scale diversity are needed |
| Benchmark validity | Adapted SmartBugs tasks use Solidity 0.4.x unchecked arithmetic | Preserve compiler and adaptation notes | Adapted small tasks are not a broad ecosystem sample |
| Reproducibility | Missing or inconsistent provenance could bias the result chain | Keep manifest-to-checksum chain and 120/120 audit fields | Artifact completeness is not independent reproduction |
| Baseline comparison | No complete fair SMARTIAN/MuFuzz/IR-Fuzz comparison | State the limitation and keep Related Work directional | No external tool ranking is supported |
| Legacy evidence | matched-random-v1 provenance is unresolved | Maintain quarantine and exclude from C5 tables | The control cannot be used until separately repaired and re-audited |

## Assembly notes

- Table 1 and Table 6 should be checked against the semantic boundary audit before layout.
- Table 3 should be generated from `main10_results_summary.tsv`; this draft is a paper-facing condensation and deliberately does not list 120 rows.
- Table 4 should remain an audit table, not a safety or performance table.
- Table 5 is a claim-control aid and should not be read as experimental evidence.
