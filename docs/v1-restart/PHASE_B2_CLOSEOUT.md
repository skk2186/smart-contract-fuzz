# Phase B2 Closeout

## Repository baseline

- Branch: `develop`
- HEAD: `2103c0ee8a804de34ccaa2cfe45c228528c2b7d9`
- HEAD message: `docs: preregister V1 public benchmark expansion`
- Initial B2 state after the requested permission restoration: clean.
- The pre-existing mode-only difference on `scripts/run_v1_public_smoke_case.sh` was restored from working-tree `100644` to executable `755`; no content was changed.
- Runner index mode remains `100755`; filesystem mode is `755`.

## Scope audit

- Added B2 runner: `analyzer/run_native_replay_gate.py`.
- Ran the runner in deterministic `static_gate_only` mode.
- Did not run Echidna fuzzing.
- Did not run Slither or solc as part of B2.
- Did not run 10 seeds.
- Did not run 30 seeds.
- Did not modify `results/` or frozen evidence.
- Did not modify `matched-random-v1/`.
- Did not add a benchmark.
- Did not create a branch, commit, or push.
- PUB06/PUB07/PUB08 were not processed and remain excluded/deferred.

## B2 gate summary

| benchmark | gate_status | execution_mode | B3 disposition |
|---|---|---|---|
| `echidna-flags` | `static_gate_pass` | `static_gate_only` | supported B3 preregistration after seed/config lock |
| `echidna-multi` | `static_gate_pass` | `static_gate_only` | supported B3 preregistration; preserve budget_exhausted caveat |
| `smartbugs-multifunc` | `static_gate_pass` | `static_gate_only` | supported B3 preregistration; bounded 0.4.x arithmetic task |
| `smartbugs-onefunc` | `static_gate_pass` | `static_gate_only` | supported B3 preregistration; repeated single-function integration only |
| `exercise2-access-control` | `conditional_replay_required` | `static_gate_only` | conditional B3 track only; caller-controlled replay still required |

No task received `replay_pass`. No task received `needs_manual_review` after the source/config/preflight audit. PUB06/PUB07/PUB08 remain excluded rather than being treated as manual-review public candidates.

## Files

New or updated tracked files are:

- `analyzer/run_native_replay_gate.py`
- `docs/v1-restart/PHASE_B2_NATIVE_REPLAY_GATE.md`
- `docs/v1-restart/PHASE_B2_CLOSEOUT.md`
- `paper-ready/v1/native_replay_gate.tsv`
- `paper-ready/v1/public_benchmark_registry.tsv`
- `paper-ready/v1/evidence_index.tsv`

The generated run directory is `work/v1-restart/b2-native-replay-gate/` and contains the top-level manifest/summary/checksum plus one manifest, gate JSON, notes, command, environment, and checksum set per benchmark.

## B3 decision

B2 permits preparation of B3 preregistration for the four supported static-gate rows. It does not authorize starting a 10-seed main run without first locking the B3 manifest and configuration. The exercise2 row may proceed only as conditional appendix/semantic-boundary work and remains outside supported pooled evidence.

Please inspect the listed diffs and gate artifacts, then perform `git add`, commit, and push to `develop` yourself if they are accepted.
