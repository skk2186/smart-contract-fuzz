# Provenance Packet: b5-rs-echidna-flags

Status: ACQUIRED_PINNED_COMMIT

## Source identity

- source name: Echidna flags
- repository: crytic/echidna
- commit: 4454f3a337ed58e89a3be488b8eac03e83cd40f2
- source path: tests/solidity/basic/flags.sol
- original retrieval URL: https://raw.githubusercontent.com/crytic/echidna/4454f3a337ed58e89a3be488b8eac03e83cd40f2/tests/solidity/basic/flags.sol
- license retrieval URL: https://raw.githubusercontent.com/crytic/echidna/4454f3a337ed58e89a3be488b8eac03e83cd40f2/LICENSE
- retrieval timestamp: 2026-09-11T11:54:39.3616594+08:00
- license: AGPL-3.0
- local screening reference: contracts/public-benchmarks/
- canonical archived paths:
- original/flags.sol: archived from https://raw.githubusercontent.com/crytic/echidna/4454f3a337ed58e89a3be488b8eac03e83cd40f2/tests/solidity/basic/flags.sol
- adapted candidate paths:
- adapted/EchidnaFlagsTarget.sol: copied from existing local adaptation

## Hash freeze

Original archive hashes:
- original/flags.sol: 596945d7e23d5329a4cd0d4de4bf12414df0c68b9a6c055c1a14f78f38e15dda

Adapted candidate hashes:
- adapted/EchidnaFlagsTarget.sol: 453562067bbe2a7ef25c0af8ff0b3c0f19415a49fc111198bfc803fae86b59fc

Archived LICENSE hash: 0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0

The hashes above are duplicated in checksums.tsv. The source archive is the pinned-commit snapshot retrieved in this stage. The adapted files are explicitly separated from the original archive and are not described as upstream files.

## Dependency and property record

- dependency closure: self-contained; no imports
- contract: PublicEchidnaFlagsTarget
- declared property: echidna_sometimesfalse
- source/adaptation gate: existing_local_adaptation_archived
- semantic gate: static_gate_pass_replay_pending; target path has no caller/value/time/external dependency signal
- caller gate: not_required_by_declared_target_path; task-level replay still required before execution

## Scope

This packet is provenance and adaptation preparation only. It authorizes no B5-4 fuzzing run. Any later execution must use a separately reviewed preregistration, preserve the hashes and retain compile/startup/parser failures.
