# B5-4 Decision

Decision: GO_TO_B5_5_FORMAL_REAL_SOURCE_EXECUTION

## Gate outcome

The four supported candidates have pinned source packets, archived licenses, matching original/adapted SHA-256 records, documented dependency closure and resolved property status. The SmartBugs label-to-property review is complete.

Compiler/preflight results:
- Echidna flags: PASS under solc 0.8.20.
- Echidna multi: PASS under solc 0.8.20.
- SmartBugs multifunc: PASS under solc 0.4.25 using the legacy-compatible solc CLI.
- SmartBugs onefunc: PASS under solc 0.4.25 using the legacy-compatible solc CLI.

The earlier 0.4.x error was caused by an unsupported --base-path option, not by the adapted source. The corrected gate-only retry used fresh non-overwriting run ids. Deterministic replay remains PREPARED_NOT_EXECUTED, and no formal fuzzing or formal result TSV was created.

## Scope decisions

The supported future registry contains exactly 120 rows. The conditional appendix plan contains 30 rows and excludes exercise2 from the supported pool. Exercise2 remains conditional because caller replay has not been executed.

The minimum gate conditions for future B5-5 formal authorization are satisfied subject to researcher review and the separately frozen preregistration. B5-4 does not change B5-Min, B4 or frozen evidence. Future real-source results must remain separately labeled adapted real-source evidence. Budget exhaustion remains right-censored; Original and Harness are not claimed semantically equivalent.

