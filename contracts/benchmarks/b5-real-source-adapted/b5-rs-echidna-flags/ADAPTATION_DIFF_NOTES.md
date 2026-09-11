# Adaptation Diff Notes: b5-rs-echidna-flags

## Original archive

original/flags.sol is the pinned upstream Echidna example.

## Existing local adaptation

adapted/EchidnaFlagsTarget.sol is copied from the repository's existing local adapted source. It is not the upstream file.

Recorded changes relative to the upstream example:

- adds SPDX and an explicit Solidity pragma for the local toolchain;
- renames the contract to PublicEchidnaFlagsTarget;
- uses int256 explicitly for the parameters;
- retains flag0, flag1, set0, set1 and echidna_sometimesfalse;
- omits echidna_alwaystrue and echidna_revert_always because they are unrelated framework self-tests.

The target state transition and declared property are retained. No owner, caller, mapping, arithmetic, require, fallback or external-call behavior is introduced. The known set0 -> set1 sequence is an audit annotation only and is not injected into fuzzer input.

Adaptation status: EXISTING_LOCAL_ADAPTATION_ARCHIVED.
