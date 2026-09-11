# PHASE B5-4: Real-Source Preregistration + Deterministic Replay/Preflight Gate

Status: COMPLETED_WITH_PREFLIGHT_BLOCKER
Decision: GO_TO_B5_4R_FIX_GATE

Starting branch: develop
Starting HEAD: 92ab87c9a6e49237fe617556d70b97ac6645a3c4
Expected parent: 364c1dce1c85c8d1ec8d884c99ada25744ae165e
Eight pre-existing dirty files were recorded and left untouched.

Inspected: B5-3R decision, provenance/candidate registries, all packets, exercise2 caller/replay plan, B5-3R closeout, B5 final decision, C-venue review, semantic boundary audit and B5 results summary.

Created: B5-4 preregistration, supported/conditional future-run registries, gate report, SmartBugs review, exercise2 status, claim map, decision file and analyzer/b5_4_real_source_gate.py.

Future planned formal runs: supported 120; conditional appendix 30. Actual formal runs in this phase: 0. Default dry-run was checked. Explicit compile preflight was run for supported candidates only; solc unavailable, recorded as ENVIRONMENT_GATE_BLOCKED. Echidna formal fuzzing: NO. Deterministic replay: prepared_not_executed. No B5-Min rerun, 30-seed expansion or formal result TSV. Gate artifacts, if present, are gate-only and paper_usable=false.

| Candidate | Hash/license | Property review | Gate | Readiness |
|---|---|---|---|---|
| flags | PASS/AGPL archived | upstream confirmed | compiler blocked | blocked_compile_or_dependency |
| multi | PASS/AGPL archived | upstream confirmed | compiler blocked | blocked_compile_or_dependency |
| multifunc | PASS/Apache archived | completed researcher-authored review | compiler blocked | blocked_compile_or_dependency |
| onefunc | PASS/Apache archived | completed researcher-authored review | compiler blocked | blocked_compile_or_dependency |
| exercise2 | packet PASS/AGPL archived | source property identity | caller replay prepared_not_executed | conditional appendix only |

B4, B5-2, B5-Min, frozen and matched-random evidence were not modified. Exercise2 is excluded from the supported pool. Adapted sources and SmartBugs researcher-authored properties are explicitly labeled.

Next: provide reproducible solc, rerun the same gate, review output, then decide on B5-5 authorization. Exercise2 separately needs same-caller and alternating-caller replay for appendix use.

