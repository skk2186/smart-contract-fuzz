# Adaptation Diff Notes: b5-rs-smartbugs-onefunc

## Original archive

The original directory contains the pinned SmartBugs Curated arithmetic source.

## Existing local adaptation

The adapted file is copied from the repository's existing local adapted source. It is not the upstream file.

Recorded adaptation components:

- adds the Echidna property echidna_count_does_not_underflow;
- renames the local contract for the Echidna target;
- makes the run function visibility explicit where the local adaptation does so;
- preserves initialized/count state and the unchecked Solidity 0.4.x arithmetic transition;
- uses the existing local compiler record: source pragma ^0.4.23 and execution pin 0.4.25.

No known counterexample is added to the source. The property follows the declared public vulnerability label but is still a researcher-authored Echidna oracle and must be reviewed before execution. The target skeleton is not injected into fuzzer input.

Adaptation status: EXISTING_LOCAL_ADAPTATION_ARCHIVED_PROPERTY_ADDED.
