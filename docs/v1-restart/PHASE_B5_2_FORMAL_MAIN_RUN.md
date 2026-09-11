# Phase B5-2 Formal Main Run

Starting branch: develop
Starting commit: 13457133a43c52f0eafdb43cc576735ab6b2a632
Preregistration freeze-stage commit: f71c1a60870c93d26323daeedfbc8e9d4c021e59
Formal implementation baseline: 13457133a43c52f0eafdb43cc576735ab6b2a632
Hash gate: ALL MATCH for 9 artifacts
Formal authorization: B5_MAIN_AUTHORIZED=1 enabled only for the batch shell
Expected runs: 120; seeds exactly 1..10; budget testLimit=100000 timeout=30s workers=1 stopOnFail=false

| Item | Count |
|---|---:|
| Expected | 120 |
| Observed expected dirs | 120 |
| Parsed rows | 120 |
| Derived paper-usable formal | 120 |
| Artifact complete | 120/120 |
| Checksum pass | 120/120 |
| Falsified | 105 |
| Budget exhausted | 15 |
| Compile error | 0 |
| Startup error | 0 |
| Parser error | 0 |
| Unknown error | 0 |
| Incomplete | 0 |

The frozen runner records experiment_class=FORMAL and paper_usable=false in raw
manifests for both smoke and formal directories. Consolidation uses FORMAL plus
artifact, checksum and provenance gates as the formal-equivalent promotion, and
sets paper_usable=true only in derived results. Raw manifests were not edited.

No formal engineering failure occurred. Eight smoke/engineering directories
remain outside the expected registry and are excluded. Frozen/B4 changes=NONE.
New public benchmarks=NONE. Thirty-seed expansion=NO.
Real-source decision=RECOMMENDED_FOR_STRONGER_PACKAGE.
C-venue controlled-package sufficiency=SUFFICIENT; full-package external-validity
sufficiency=PARTIALLY_SUFFICIENT.
Final decision=B5 PASS - GO TO REAL-SOURCE EXTENSION.

Original and Harness execution models differ in transactions, callers, rollback
and calls per wrapper. budget_exhausted is right-censored, not a pass or safety
proof.
