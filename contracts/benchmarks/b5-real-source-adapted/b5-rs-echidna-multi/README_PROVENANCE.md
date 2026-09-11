# Provenance Packet: b5-rs-echidna-multi

Status: ACQUIRED_PINNED_COMMIT

## Source identity

- source name: Echidna multi-step example
- repository: crytic/echidna
- commit: 4454f3a337ed58e89a3be488b8eac03e83cd40f2
- source path: tests/solidity/coverage/multi.sol
- original retrieval URL: https://raw.githubusercontent.com/crytic/echidna/4454f3a337ed58e89a3be488b8eac03e83cd40f2/tests/solidity/coverage/multi.sol
- license retrieval URL: https://raw.githubusercontent.com/crytic/echidna/4454f3a337ed58e89a3be488b8eac03e83cd40f2/LICENSE
- retrieval timestamp: 2026-09-11T11:54:39.3616594+08:00
- license: AGPL-3.0
- local screening reference: contracts/public-benchmarks/
- canonical archived paths:
- original/multi.sol: archived from https://raw.githubusercontent.com/crytic/echidna/4454f3a337ed58e89a3be488b8eac03e83cd40f2/tests/solidity/coverage/multi.sol
- adapted candidate paths:
- adapted/multi.sol: copied from the pinned original without semantic edits

## Hash freeze

Original archive hashes:
- original/multi.sol: 6571e07a58f9060efb5fa49cb6d06f7cb15664a382c4a2f0de312b9921e2c86a

Adapted candidate hashes:
- adapted/multi.sol: 6571e07a58f9060efb5fa49cb6d06f7cb15664a382c4a2f0de312b9921e2c86a

Archived LICENSE hash: 0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0

The hashes above are duplicated in checksums.tsv. The source archive is the pinned-commit snapshot retrieved in this stage. The adapted files are explicitly separated from the original archive and are not described as upstream files.

## Dependency and property record

- dependency closure: self-contained; no imports
- contract: C
- declared property: echidna_state3
- source/adaptation gate: no_semantic_change_copy
- semantic gate: static_gate_pass_replay_pending; require-gated target path has no caller/value/time/external dependency signal
- caller gate: not_required_by_declared_target_path; task-level replay still required before execution

## Scope

This packet is provenance and adaptation preparation only. It authorizes no B5-4 fuzzing run. Any later execution must use a separately reviewed preregistration, preserve the hashes and retain compile/startup/parser failures.
