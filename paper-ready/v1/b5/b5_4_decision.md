# B5-4 Decision

Decision: GO_TO_B5_4R_FIX_GATE

Four supported candidates have pinned source packets, archived licenses, SHA-256 records, documented closures and a completed SmartBugs property review. The supported future registry has exactly 120 rows; the separate conditional plan has 30 and excludes exercise2.

Static source, hash, license, property and import checks pass. Deterministic replay is prepared but not executed. Explicit compiler preflight is blocked because solc is unavailable, so B5-5 minimum readiness is not satisfied.

Restore reproducible solc 0.8.20/0.4.25 and rerun the same gate without changing packets or inclusion. Review compile output before B5-5 authorization. Preserve any failure and do not select by PHS outcome.

B5-4 does not change B5-Min, B4 or frozen evidence. C7 writing may continue with the external-validity limitation, but real-source execution is not complete. The four supported tasks may later be separately labeled adapted real-source evidence; exercise2 remains appendix-only after caller/replay review.

