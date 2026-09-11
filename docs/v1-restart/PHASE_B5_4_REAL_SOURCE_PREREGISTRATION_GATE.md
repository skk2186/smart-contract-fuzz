# PHASE B5-4: Real-Source Preregistration + Deterministic Replay/Preflight Gate

Status: COMPLETED_GATE_REVIEW
Decision: GO_TO_B5_5_FORMAL_REAL_SOURCE_EXECUTION

Starting branch: develop
Starting HEAD: 92ab87c9a6e49237fe617556d70b97ac6645a3c4
Expected parent: 364c1dce1c85c8d1ec8d884c99ada25744ae165e
Eight pre-existing dirty files were recorded and left untouched.

Inspected: B5-3R decision, provenance/candidate registries, all real-source packets, exercise2 caller/replay plan, B5-3R closeout, B5 final decision, C-venue review, semantic boundary audit and B5 results summary.

Created: B5-4 preregistration, supported/conditional future-run registries, gate report, SmartBugs review, exercise2 status, claim map, decision file, gate script and compiler-compatible retry gate.

Network/source acquisition: no new external source was downloaded in B5-4; the five B5-3R provenance packets were reused. No source packet was changed.

Future planned formal runs: supported 120; conditional appendix 30. Actual formal runs in this phase: 0. The default dry-run was checked. Gate-only preflight artifacts were created with paper_usable=false. Echidna formal fuzzing: NO. Deterministic replay: PREPARED_NOT_EXECUTED. No B5-Min rerun, 30-seed expansion or formal result TSV.

Compiler gate: Echidna flags and multi passed under solc 0.8.20. SmartBugs multifunc and onefunc passed under solc 0.4.25 using the legacy-compatible solc CLI. The earlier 0.4.x error was only the unsupported --base-path option in the first gate invocation; that artifact remains preserved and is not overwritten.

| Candidate | Hash/license | Property review | Compiler/preflight | Readiness |
|---|---|---|---|---|
| flags | PASS/AGPL archived | upstream confirmed | solc 0.8.20 PASS | ready_for_formal_after_researcher_review |
| multi | PASS/AGPL archived | upstream confirmed | solc 0.8.20 PASS | ready_for_formal_after_researcher_review |
| multifunc | PASS/Apache archived | completed researcher-authored review | solc 0.4.25 PASS | ready_for_formal_after_researcher_review |
| onefunc | PASS/Apache archived | completed researcher-authored review | solc 0.4.25 PASS | ready_for_formal_after_researcher_review |
| exercise2 | packet PASS/AGPL archived | source property identity | caller replay PREPARED_NOT_EXECUTED | conditional appendix only |

B4, B5-2, B5-Min, frozen and matched-random evidence were not modified. Exercise2 is excluded from the supported pool. Adapted sources and SmartBugs researcher-authored properties remain explicitly labeled.

Next: researcher review of the frozen 120-row preregistration and gate report, then separately authorize B5-5 formal execution. Exercise2 requires same-caller and alternating-caller replay if appendix use is desired.

