# License Evidence: b5-rs-exercise2-access-control

## Detected license

- detected license: AGPL-3.0
- repository: crytic/building-secure-contracts
- pinned commit: 2de122e3a6b63bc450a1ec41215f0c44d72fb96b
- evidence source: original/LICENSE archived from https://raw.githubusercontent.com/crytic/building-secure-contracts/2de122e3a6b63bc450a1ec41215f0c44d72fb96b/LICENSE
- archived LICENSE SHA-256: 0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0
- SPDX header evidence: Both archived Solidity files contain SPDX-License-Identifier: AGPL-3.0; repository LICENSE is also archived.
- repository LICENSE archived: YES
- source acquisition status: ACQUIRED_PINNED_COMMIT

## Paper-inclusion assessment

The repository license file and pinned source commit are archived, so the license evidence is sufficient for provenance screening. This does not by itself establish semantic eligibility, property validity or B5-4 execution authorization.

The candidate remains conditional because caller identity, mapping keys and rollback semantics require a separate replay gate.

## Required follow-up

Keep this file with README_PROVENANCE.md, ADAPTATION_DIFF_NOTES.md and checksums.tsv. If any future source or license hash changes, block the candidate and create a new reviewed packet.
