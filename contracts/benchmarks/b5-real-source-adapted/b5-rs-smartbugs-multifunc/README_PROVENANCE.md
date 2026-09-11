# Provenance Packet: b5-rs-smartbugs-multifunc

Status: ACQUIRED_PINNED_COMMIT

## Source identity

- source name: SmartBugs multi-function arithmetic
- repository: smartbugs/smartbugs-curated
- commit: 230e649123477eff332742a59a1c7cc6dc286cab
- source path: dataset/arithmetic/integer_overflow_multitx_multifunc_feasible.sol
- original retrieval URL: https://raw.githubusercontent.com/smartbugs/smartbugs-curated/230e649123477eff332742a59a1c7cc6dc286cab/dataset/arithmetic/integer_overflow_multitx_multifunc_feasible.sol
- license retrieval URL: https://raw.githubusercontent.com/smartbugs/smartbugs-curated/230e649123477eff332742a59a1c7cc6dc286cab/LICENSE
- retrieval timestamp: 2026-09-11T11:54:39.3616594+08:00
- license: Apache-2.0
- local screening reference: contracts/public-benchmarks/
- canonical archived paths:
- original/integer_overflow_multitx_multifunc_feasible.sol: archived from https://raw.githubusercontent.com/smartbugs/smartbugs-curated/230e649123477eff332742a59a1c7cc6dc286cab/dataset/arithmetic/integer_overflow_multitx_multifunc_feasible.sol
- adapted candidate paths:
- adapted/SmartBugsMultiFuncEchidna.sol: copied from existing local adaptation

## Hash freeze

Original archive hashes:
- original/integer_overflow_multitx_multifunc_feasible.sol: b4751ff85a668932e084d03b08992f62b85f3a62dea2224d7f93eafe5628188f

Adapted candidate hashes:
- adapted/SmartBugsMultiFuncEchidna.sol: 399eef34e64cf5e870cb09b0753cbf09023416837c494e54c56dc5ead36f539c

Archived LICENSE hash: c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4

The hashes above are duplicated in checksums.tsv. The source archive is the pinned-commit snapshot retrieved in this stage. The adapted files are explicitly separated from the original archive and are not described as upstream files.

## Dependency and property record

- dependency closure: self-contained after local flattening; no imports
- contract: SmartBugsMultiFuncEchidna
- declared property: echidna_count_does_not_underflow
- source/adaptation gate: existing_local_adaptation_archived_property_added
- semantic gate: static_gate_pass_replay_pending; Solidity 0.4.x unchecked arithmetic and wrapper atomicity remain explicit risks
- caller gate: not_required_by_declared_target_path; task-level replay and property review still required before execution

## Scope

This packet is provenance and adaptation preparation only. It authorizes no B5-4 fuzzing run. Any later execution must use a separately reviewed preregistration, preserve the hashes and retain compile/startup/parser failures.
