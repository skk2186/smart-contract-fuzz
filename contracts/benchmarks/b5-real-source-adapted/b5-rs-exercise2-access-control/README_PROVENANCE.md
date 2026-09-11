# Provenance Packet: b5-rs-exercise2-access-control

Status: ACQUIRED_PINNED_COMMIT

## Source identity

- source name: Building Secure Contracts exercise 2
- repository: crytic/building-secure-contracts
- commit: 2de122e3a6b63bc450a1ec41215f0c44d72fb96b
- source path: program-analysis/echidna/exercises/exercise2/solution.sol; program-analysis/echidna/exercises/exercise2/token.sol
- original retrieval URL: https://raw.githubusercontent.com/crytic/building-secure-contracts/2de122e3a6b63bc450a1ec41215f0c44d72fb96b/program-analysis/echidna/exercises/exercise2/solution.sol
- license retrieval URL: https://raw.githubusercontent.com/crytic/building-secure-contracts/2de122e3a6b63bc450a1ec41215f0c44d72fb96b/LICENSE
- retrieval timestamp: 2026-09-11T11:54:39.3616594+08:00
- license: AGPL-3.0
- local screening reference: contracts/public-benchmarks/
- canonical archived paths:
- original/solution.sol: archived from https://raw.githubusercontent.com/crytic/building-secure-contracts/2de122e3a6b63bc450a1ec41215f0c44d72fb96b/program-analysis/echidna/exercises/exercise2/solution.sol
- original/token.sol: archived from https://raw.githubusercontent.com/crytic/building-secure-contracts/2de122e3a6b63bc450a1ec41215f0c44d72fb96b/program-analysis/echidna/exercises/exercise2/solution.sol
- adapted candidate paths:
- adapted/solution.sol: copied from the pinned original without semantic edits
- adapted/token.sol: copied from the pinned original without semantic edits

## Hash freeze

Original archive hashes:
- original/solution.sol: e52c8081b55f64ed7a562a492714e969026f5e548b2fa99e19213d9f6b59f8fe
- original/token.sol: 87f802a00cb8b4fb991af8d80838fe40a24bd6b6cf1419f89e3505356065738a

Adapted candidate hashes:
- adapted/solution.sol: e52c8081b55f64ed7a562a492714e969026f5e548b2fa99e19213d9f6b59f8fe
- adapted/token.sol: 87f802a00cb8b4fb991af8d80838fe40a24bd6b6cf1419f89e3505356065738a

Archived LICENSE hash: 0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0

The hashes above are duplicated in checksums.tsv. The source archive is the pinned-commit snapshot retrieved in this stage. The adapted files are explicitly separated from the original archive and are not described as upstream files.

## Dependency and property record

- dependency closure: closed by solution.sol -> token.sol; no external import
- contract: TestToken
- declared property: echidna_no_transfer
- source/adaptation gate: no_semantic_change_copy
- semantic gate: conditional_static_gate_replay_required; msg.sender, owner equality and address-keyed mapping
- caller gate: required_same_and_alternating_caller_replay

## Scope

This packet is provenance and adaptation preparation only. It authorizes no B5-4 fuzzing run. Any later execution must use a separately reviewed preregistration, preserve the hashes and retain compile/startup/parser failures.
