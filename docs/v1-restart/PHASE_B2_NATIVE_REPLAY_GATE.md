# Phase B2: Native Replay / Semantic Gate Audit

## 1. Purpose

B2 audits the five public benchmarks already registered by B1 using fixed-path native replay preparation and a semantic gate. The research question is whether each task has a traceable source, configuration, property, known target sequence, compiler record, and semantic model sufficient to enter B3 preregistration.

This stage is an audit of execution-model applicability. It is not a fuzzing experiment and it does not estimate discovery rate, time-to-finding, coverage, speedup, or superiority over another fuzzer.

## 2. Scope and non-scope

The scope is exactly:

- `echidna-flags`
- `echidna-multi`
- `smartbugs-multifunc`
- `smartbugs-onefunc`
- `exercise2-access-control`

PUB06 `AlternativePath`, PUB07 `MultiProperty`, and PUB08 `ThreeStep` were not processed. They are internal/non-independent candidates and remain excluded/deferred; they are not B3 supported public tasks.

B2 did not modify benchmark source semantics, formal configs, `results/`, frozen evidence, or `matched-random-v1/`. It did not run Echidna fuzzing, 10 seeds, or 30 seeds.

## 3. Method

The new `analyzer/run_native_replay_gate.py` runner:

1. reads the B1 public registry and Phase 05 preregistration;
2. checks the source and both public C-1 config paths;
3. records source/config SHA-256 values and the compiler recorded by the existing preflight manifest;
4. checks the existing B1/Phase 06A preflight status, summary, generated read/write artifacts, full-sequence artifact, and harness artifacts;
5. scans the source closure for caller, address-keyed mapping, value/payable, block/time, external-call, and revert/require signals;
6. writes deterministic manifests, semantic gate JSON/TSV, notes, environment records, and checksums under `work/v1-restart/b2-native-replay-gate/`.

The environment available for this run did not provide `solc` or `echidna-test`. Therefore every output uses `execution_mode=static_gate_only`. No row is labeled `replay_pass`; the static gate does not claim that an EVM replay executed.

## 4. Gate results

| benchmark | classification before B2 | gate_status | execution_mode | main_table_gate | B3 action |
|---|---|---|---|---|---|
| `echidna-flags` | supported | `static_gate_pass` | `static_gate_only` | `yes_after_b3_prereg` | `include_in_b3_supported` |
| `echidna-multi` | supported | `static_gate_pass` | `static_gate_only` | `yes_after_b3_prereg` | `include_in_b3_supported` |
| `smartbugs-multifunc` | supported | `static_gate_pass` | `static_gate_only` | `yes_after_b3_prereg` | `include_in_b3_supported` |
| `smartbugs-onefunc` | supported | `static_gate_pass` | `static_gate_only` | `yes_after_b3_prereg` | `include_in_b3_supported` |
| `exercise2-access-control` | conditional | `conditional_replay_required` | `static_gate_only` | `conditional_only` | `include_in_b3_conditional` |

### Task-level interpretation

- `echidna-flags`: `set0(100*k) -> set1(10*m)` is present in the existing full-sequence artifact. The source has no caller, value, block/time, or external-call dependency in the target path. It can enter B3 supported preregistration, while retaining the wrapper atomicity caveat.
- `echidna-multi`: `f(12) -> g(8) -> h(z)` is present and the require chain is explicit. The existing Original seed-1 `budget_exhausted` remains “no observed counterexample within budget,” not property passed or contract safe.
- `smartbugs-multifunc`: `init() -> run(a) -> run(b)` is present. The repeated `run` is required and the Solidity 0.4.x unchecked arithmetic semantics must remain in the B3 record. This is a bounded adapted arithmetic task, not broad ecosystem evidence.
- `smartbugs-onefunc`: `run(a) -> run(b)` is present. Initialization and triggering are both inside one repeated function, so it is integration/repeated-single-function evidence and not evidence of a multi-function ordering advantage.
- `exercise2-access-control`: `Owner() -> resume()` is present, but the source uses `msg.sender`, owner equality, and an address-keyed mapping in the imported token closure. It requires caller-controlled replay comparing same-caller and alternating-caller schedules and remains outside supported pooled evidence.

## 5. What B2 supports and does not support

B2 supports traceability and a narrow semantic readiness decision for B3. It does not support:

- Original/Harness full semantic equivalence;
- a native replay result or a replay-based property result;
- a claim that a budget-exhausted run passed its property;
- a 10-seed or 30-seed discovery-rate result;
- a speedup claim based on total calls;
- a claim that V1 is better than Echidna, SMARTIAN, MuFuzz, or IR-Fuzz;
- broad real-ecosystem generalization from these five tasks.

The four `static_gate_pass` rows are eligible for B3 supported preregistration, not direct promotion to a formal main table. `exercise2-access-control` is eligible only for a separate conditional B3 track and must not be pooled with the four supported rows.

## 6. Next step

B3 should freeze the supported task list, compiler/configuration records, seeds, budget, timeout, workers, stop-on-fail policy, and success/failure classification before any main run. If native EVM replay becomes available, exercise2 must first receive caller-controlled same-caller and alternating-caller replay; a successful same-caller Harness path alone is insufficient.
