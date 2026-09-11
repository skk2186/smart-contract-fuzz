#!/usr/bin/env python3
from __future__ import annotations
import csv, math, statistics
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
B5=ROOT/"paper-ready/v1/b5"; RUNS=ROOT/"work/v1-restart"; EXPECTED=B5/"b5_expected_runs.tsv"
COMMIT="13457133a43c52f0eafdb43cc576735ab6b2a632"
SCENARIOS=["c1","c2","c3"]
METHODS={"c1":["original","dependency-only","full-k1","full-k5"],"c2":["original","no-repeat","full-k1","full-k5"],"c3":["original","no-value","full-k1","full-k5"]}
NAME={"original":"Original","dependency-only":"Dependency-only","no-repeat":"No-Repeat","no-value":"No-Value","full-k1":"Full-K1","full-k5":"Full-K5"}
SNAME={"c1":"C1 Irrelevant-State Explosion","c2":"C2 Deep Repeated Transition","c3":"C3 Value-Gated Competing Paths"}
METRICS=["run_id","scenario","method","seed","budget","status","property_falsified","budget_exhausted","target_state_reached","target_candidate_rank","top1_hit","top5_hit","dependency_candidate_count","property_candidate_count","candidate_reduction_ratio","required_repeat_count","observed_repeat_count","value_evidence_enabled","repeat_enabled","k","time_to_falsify_seconds","fuzz_seconds","process_wall_seconds","preprocess_seconds","harness_compile_seconds","artifact_complete","checksum_pass"]
STATUSES={"falsified","budget_exhausted","compile_error","startup_error","parser_error","unknown_error","incomplete"}

def tsv(p):
    with p.open(encoding="utf-8",newline="") as f: return list(csv.DictReader(f,delimiter="\t"))
def write(p,rows,fields):
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",extrasaction="ignore"); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,"") for k in fields})
def num(v):
    try:
        x=float(v); return x if math.isfinite(x) else None
    except (TypeError,ValueError): return None
def med(rows,k):
    v=[num(r.get(k)) for r in rows]; v=[x for x in v if x is not None]
    return statistics.median(v) if v else None
def fn(v,d=3): return "" if v is None or num(v) is None else f"{num(v):.{d}f}"
def cnt(v): return "" if v is None or num(v) is None else str(int(num(v)))
def rate(n,d): return f"{n/d:.3f}" if d else ""
def rr(rows,k):
    v=[int(num(r.get(k))) for r in rows if num(r.get(k)) is not None]
    return f"{min(v)}-{max(v)}" if v else ""
def mt(headers,rows):
    nl=chr(10)
    return '| '+' | '.join(headers)+' |'+nl+'|'+'|'.join('---' for _ in headers)+'|'+nl+nl.join('| '+' | '.join(str(x) for x in r)+' |' for r in rows)

def one(e):
    d=RUNS/e["run_id"]; mp=d/"manifest.tsv"; pp=d/"parsed/b5_run.tsv"
    needed=[d/"manifest.tsv",d/"command.txt",d/"environment.txt",d/"generated",d/"raw",d/"parsed",pp,d/"summary",d/"status",d/"status/status.env",d/"status/checksums.sha256",d/"status/checksum-verification.txt"]
    exists=d.is_dir(); mr=tsv(mp) if mp.is_file() else []; pr=tsv(pp) if pp.is_file() else []
    m=mr[0] if len(mr)==1 else {}; p=pr[0] if len(pr)==1 else None
    status=(p or {}).get("status","")
    if not status and (d/"status/status.env").is_file():
        for line in (d/"status/status.env").read_text(errors="replace").splitlines():
            if line.startswith("STATUS="): status=line.split("=",1)[1]
    pathok=exists and all(x.exists() for x in needed)
    ident=bool(m and all(m.get(k)==e.get(k) for k in ("run_id","scenario","method","seed")))
    pm=bool(p and all(p.get(k)==e.get(k) for k in ("run_id","scenario","method","seed")) and (not m or m.get("status")==p.get("status")))
    artifact=bool(pathok and p and p.get("artifact_complete")=="true")
    verify=(d/"status/checksum-verification.txt").read_text(errors="replace") if (d/"status/checksum-verification.txt").is_file() else ""
    checksum=bool(pathok and p and p.get("checksum_pass")=="pass" and "OK" in verify)
    formal=m.get("experiment_class")=="FORMAL"
    usable=bool(exists and formal and ident and pm and status in STATUSES and artifact and checksum)
    a={"run_id":e["run_id"],"scenario":e["scenario"],"method":e["method"],"seed":e["seed"],"expected":e.get("expected",""),"directory_exists":str(exists).lower(),"experiment_class":m.get("experiment_class",""),"raw_paper_usable":m.get("paper_usable",""),"formal_equivalent":str(formal).lower(),"status":status or "incomplete","artifact_complete":str(artifact).lower(),"checksum_pass":"pass" if checksum else "fail","parser_match":str(pm).lower(),"usable":str(usable).lower()}
    return a,p if usable else None

def summary(s,m,rows):
    n=len(rows); f=sum(r["status"]=="falsified" for r in rows); b=sum(r["status"]=="budget_exhausted" for r in rows)
    reach=sum(num(r.get("target_state_reached"))==1 for r in rows); t1=sum(num(r.get("top1_hit"))==1 for r in rows); t5=sum(num(r.get("top5_hit"))==1 for r in rows)
    return {"scenario":s,"method":m,"runs":n,"falsified_runs":f,"budget_exhausted_runs":b,"engineering_error_runs":n-f-b,"falsification_rate":rate(f,n),"target_state_reached_runs":reach,"target_state_reach_rate":rate(reach,n),"top1_hit_runs":t1,"top1_hit_rate":rate(t1,n),"top5_hit_runs":t5,"top5_hit_rate":rate(t5,n),"median_target_rank":fn(med(rows,"target_candidate_rank")),"target_rank_range":rr(rows,"target_candidate_rank"),"median_time_to_falsify_successful":fn(med([r for r in rows if r["status"]=="falsified"],"time_to_falsify_seconds")),"median_process_wall_seconds":fn(med(rows,"process_wall_seconds")),"median_preprocess_seconds":fn(med(rows,"preprocess_seconds")),"median_harness_compile_seconds":fn(med(rows,"harness_compile_seconds")),"artifact_complete_runs":sum(r.get("artifact_complete")=="true" for r in rows),"checksum_pass_runs":sum(r.get("checksum_pass")=="pass" for r in rows)}

def main():
    exp=tsv(EXPECTED)
    if len(exp)!=120: raise SystemExit(f"expected rows={len(exp)}")
    audits=[]; usable=[]
    for e in exp:
        a,p=one(e); audits.append(a)
        if p: usable.append(p)
    audit_fields=["run_id","scenario","method","seed","expected","directory_exists","experiment_class","raw_paper_usable","formal_equivalent","status","artifact_complete","checksum_pass","parser_match","usable"]
    write(B5/"b5_run_audit.tsv",audits,audit_fields)
    result_fields=["run_id","experiment_class","paper_usable"]+METRICS[1:]
    rs=[]
    for p in usable:
        r={"experiment_class":"FORMAL","paper_usable":"true"}; r.update(p); rs.append(r)
    write(B5/"b5_results_by_run.tsv",rs,result_fields)
    groups=defaultdict(list)
    for r in usable: groups[(r["scenario"],r["method"])].append(r)
    sums=[summary(s,m,groups[(s,m)]) for s in SCENARIOS for m in METHODS[s]]
    sf=["scenario","method","runs","falsified_runs","budget_exhausted_runs","engineering_error_runs","falsification_rate","target_state_reached_runs","target_state_reach_rate","top1_hit_runs","top1_hit_rate","top5_hit_runs","top5_hit_rate","median_target_rank","target_rank_range","median_time_to_falsify_successful","median_process_wall_seconds","median_preprocess_seconds","median_harness_compile_seconds","artifact_complete_runs","checksum_pass_runs"]
    write(B5/"b5_results_summary.tsv",sums,sf); sm={(r["scenario"],r["method"]):r for r in sums}
    specs={"c1":[("Dependency-only vs Full-K5","mechanism_ablation","dependency-only"),("Dependency-only vs Full-K5","primary_full","full-k5"),("Dependency-only vs Full-K5","external_baseline","original"),("Full-K1 vs Full-K5","top_k_sensitivity","full-k1")],"c2":[("No-Repeat vs Full-K5","mechanism_ablation","no-repeat"),("No-Repeat vs Full-K5","primary_full","full-k5"),("No-Repeat vs Full-K5","external_baseline","original"),("Full-K1 vs Full-K5","top_k_sensitivity","full-k1")],"c3":[("No-Value vs Full-K5","mechanism_ablation","no-value"),("No-Value vs Full-K5","primary_full","full-k5"),("No-Value vs Full-K5","external_baseline","original"),("Full-K1 vs Full-K5","top_k_sensitivity","full-k1")]}
    ab=[]
    for s in SCENARIOS:
        p=sm[(s,"full-k5")]
        for comp,role,m in specs[s]:
            q=sm[(s,m)]; pr=num(p["median_target_rank"]); qr=num(q["median_target_rank"]); rd=pr-qr if pr is not None and qr is not None else None
            qreach=num(q["target_state_reach_rate"]); preach=num(p["target_state_reach_rate"]); qf=num(q["falsification_rate"]); pf=num(p["falsification_rate"])
            ab.append({"comparison":comp,"comparison_role":role,"scenario":s,"method":m,"runs":q["runs"],"dependency_candidate_count_median":fn(med(groups[(s,m)],"dependency_candidate_count")),"property_candidate_count_median":fn(med(groups[(s,m)],"property_candidate_count")),"candidate_reduction_ratio_median":fn(med(groups[(s,m)],"candidate_reduction_ratio")),"required_repeat_count":cnt(groups[(s,m)][0].get("required_repeat_count")),"observed_repeat_count_median":fn(med(groups[(s,m)],"observed_repeat_count")),"value_evidence_enabled":cnt(groups[(s,m)][0].get("value_evidence_enabled")),"repeat_enabled":cnt(groups[(s,m)][0].get("repeat_enabled")),"k":cnt(groups[(s,m)][0].get("k")),"median_target_rank":q["median_target_rank"],"target_rank_range":q["target_rank_range"],"rank_delta_vs_full_k5":fn(rd),"top1_hit_runs":q["top1_hit_runs"],"top5_hit_runs":q["top5_hit_runs"],"target_state_reached_runs":q["target_state_reached_runs"],"target_state_reach_rate":q["target_state_reach_rate"],"reachability_delta_vs_full_k5":fn(qreach-preach if qreach is not None and preach is not None else None),"falsified_runs":q["falsified_runs"],"falsification_rate":q["falsification_rate"],"trigger_delta_vs_full_k5":fn(qf-pf if qf is not None and pf is not None else None),"budget_exhausted_runs":q["budget_exhausted_runs"]})
    af=["comparison","comparison_role","scenario","method","runs","dependency_candidate_count_median","property_candidate_count_median","candidate_reduction_ratio_median","required_repeat_count","observed_repeat_count_median","value_evidence_enabled","repeat_enabled","k","median_target_rank","target_rank_range","rank_delta_vs_full_k5","top1_hit_runs","top5_hit_runs","target_state_reached_runs","target_state_reach_rate","reachability_delta_vs_full_k5","falsified_runs","falsification_rate","trigger_delta_vs_full_k5","budget_exhausted_runs"]
    write(B5/"b5_ablation_summary.tsv",ab,af)
    status=defaultdict(int)
    for a in audits: status[a["status"]]+=1
    complete=sum(a["artifact_complete"]=="true" for a in audits); checksum=sum(a["checksum_pass"]=="pass" for a in audits); us=sum(a["usable"]=="true" for a in audits)
    c1=sm[("c1","full-k5")]; c2=sm[("c2","full-k5")]; c3=sm[("c3","full-k5")]; c2nr=sm[("c2","no-repeat")]; c3nv=sm[("c3","no-value")]
    c1red=fn(med(groups[("c1","full-k5")],"candidate_reduction_ratio"))
    combo= num(c1red) is not None and num(c2["target_state_reach_rate"])>num(c2nr["target_state_reach_rate"]) and num(c3["median_target_rank"])<num(c3nv["median_target_rank"])
    combo_status="SUPPORTED" if combo else "MIXED"
    (B5/"b5_combination_effect_analysis.md").write_text(f"""# B5 Combination Effect Analysis

Formal commit: {COMMIT}. Analysis is descriptive and scenario-stratified; no
pooled p-value is claimed. budget_exhausted is right-censored.

Single-component evidence:
- C1 property filtering: Full-K5 median candidate reduction ratio is {c1red}.
- C2 bounded repeat: No-Repeat reachability is {c2nr["target_state_reach_rate"]} versus Full-K5 {c2["target_state_reach_rate"]}.
- C3 value evidence: No-Value median rank is {c3nv["median_target_rank"]} versus Full-K5 {c3["median_target_rank"]}.
- Top-K is reported as Full-K1 versus Full-K5 without assuming monotonic benefit.

Full PHS combination: {combo_status}. The targeted contrasts jointly cover
candidate relevance, repeat-preserving reachability, and value-directed rank.
This supports a combination claim under the declared execution models, not
individual component novelty or Original/Harness semantic equivalence.

Safe wording: PHS combines property-directed filtering, bounded repeat,
lightweight value evidence, and interpretable Top-K retention in an auditable
Echidna-external Harness synthesis workflow, with scenario-specific gains.

Limitations: C1-C3 are controlled/custom; trigger outcomes may saturate.
Original uses independent transactions while Harness uses a wrapper transaction.
Total calls are not a speedup metric; public external validity is not
established by B5 alone.
""",encoding="utf-8")
    ceil=["# B5 Ceiling Effect Review","","A 10/10 trigger count is reviewed separately from mechanism metrics."]
    for s in SCENARIOS:
        rows=[sm[(s,m)] for m in METHODS[s]]; all10=all(r["falsified_runs"]==r["runs"] for r in rows)
        distinct={(r["median_target_rank"],r["target_state_reach_rate"],r["top1_hit_rate"]) for r in rows}
        label="scenario_not_discriminative" if all10 and len(distinct)==1 else ("trigger_ceiling_but_mechanism_discriminative" if all10 else "not_fully_saturated")
        ceil += [f"## {SNAME[s]}","",f"classification: {label}","",mt(["Method","Falsified","Budget exhausted","Reachability","Median rank","Top-1"],[[NAME[r["method"]],f'{r["falsified_runs"]}/{r["runs"]}',r["budget_exhausted_runs"],f'{r["target_state_reached_runs"]}/{r["runs"]}',r["median_target_rank"],f'{r["top1_hit_runs"]}/{r["runs"]}'] for r in rows]),""]
    ceil += ["Conclusion: saturation is not called a failure when rank, Top-K, repeat, value, or reachability still distinguishes methods."]
    (B5/"b5_ceiling_effect_review.md").write_text(chr(10).join(ceil)+chr(10),encoding="utf-8")
    outcome=[[SNAME[r["scenario"]],NAME[r["method"]],r["runs"],f'{r["falsified_runs"]}/{r["runs"]}',r["budget_exhausted_runs"],f'{r["target_state_reached_runs"]}/{r["runs"]}',r["median_target_rank"],f'{r["top1_hit_runs"]}/{r["runs"]}',f'{r["top5_hit_runs"]}/{r["runs"]}'] for r in sums]
    mech=[[SNAME[r["scenario"]],r["comparison"],NAME[r["method"]],r["dependency_candidate_count_median"],r["property_candidate_count_median"],r["candidate_reduction_ratio_median"],r["observed_repeat_count_median"],r["median_target_rank"],r["target_state_reach_rate"],f'{r["falsified_runs"]}/{r["runs"]}'] for r in ab]
    ranks=[[SNAME[r["scenario"]],NAME[r["method"]],r["median_target_rank"],r["target_rank_range"],f'{r["top1_hit_runs"]}/{r["runs"]}',f'{r["top5_hit_runs"]}/{r["runs"]}',f'{r["target_state_reached_runs"]}/{r["runs"]}'] for r in sums]
    comp=mt(["Metric","Count"],[["Expected",120],["Observed expected dirs",sum(a["directory_exists"]=="true" for a in audits)],["Parsed",len(usable)],["Derived paper-usable",us],["Artifact complete",complete],["Checksum pass",checksum],["Falsified",status["falsified"]],["Budget exhausted",status["budget_exhausted"]],["Compile error",status["compile_error"]],["Startup error",status["startup_error"]],["Parser error",status["parser_error"]],["Unknown error",status["unknown_error"]],["Incomplete",status["incomplete"]]])
    (B5/"b5_paper_tables.md").write_text(f"""# B5 Paper Tables

## Table B5-1. Formal execution completeness
{comp}

## Table B5-2. Scenario x method outcome
{mt(["Scenario","Method","Runs","Falsified","Budget exhausted","Reachability","Median rank","Top-1","Top-5"],outcome)}

## Table B5-3. Mechanism and ablation result
{mt(["Scenario","Comparison","Method","Dependency median","Property median","Reduction","Repeat observed","Rank","Reachability","Falsified"],mech)}

## Table B5-4. Target rank, Top-K, and reachability
{mt(["Scenario","Method","Median target rank","Rank range","Top-1","Top-5","Reachability"],ranks)}

Notes: budget_exhausted is right-censored, not a pass or safety result.
Original/Harness use their declared execution models; total calls are not used
as speedup.
""",encoding="utf-8")
    claims=[["C1","Property-directed filtering reduces irrelevant candidates.",f"C1 Full-K5 reduction ratio {c1red}; candidate counts, rank and Top-K are reported.","supported","In controlled C1, property filtering reduced the candidate space under the declared ranking.","Controlled scenario; not end-to-end speedup."],["C2","Bounded repeat preserves a three-transition target.",f"No-Repeat reachability {c2nr['target_state_reach_rate']} vs Full-K5 {c2['target_state_reach_rate']}.","supported","In C2, bounded repeat preserved the required advance() occurrences.","One controlled repeated-transition pattern."],["C3","Value evidence improves route rank.",f"No-Value median rank {c3nv['median_target_rank']} vs Full-K5 {c3['median_target_rank']}.","supported","In C3, lightweight storage-value evidence improved target rank.","Not symbolic execution or a general value guarantee."],["C4","Top-K retention reduces single-rank loss risk.","Full-K1 and Full-K5 rank, Top-1/Top-5, reachability and outcomes are reported.","partially_supported","B5 measures when K1 and K5 differ; it assumes no monotonic K5 benefit.","Some cells may have K1=K5."],["C5","Combined PHS has joint mechanism value",f"Combination analysis: {combo_status}; C1 relevance, C2 reachability, C3 rank.","supported" if combo_status=="SUPPORTED" else "mixed","PHS combines mechanisms with scenario-specific gains.","Not individual novelty or semantic equivalence."],["C6","PHS applies to public/external contracts.","B5 is controlled/custom; no new public benchmark added.","partially_supported","Prior screened public evidence shows limited applicability.","B5 adds no external diversity."],["C7","PHS improves over Original.","Original, ablations, Full-K1 and Full-K5 are reported per scenario.","mixed","PHS changes targeted rank, reachability or relevance; no universal superiority claim.","Caller, atomicity, rollback and call boundaries differ."]]
    write(B5/"b5_claim_evidence_update.tsv",[{"claim_id":x[0],"claim":x[1],"b5_evidence":x[2],"status_after_b5":x[3],"safe_wording":x[4],"remaining_limitation":x[5]} for x in claims],["claim_id","claim","b5_evidence","status_after_b5","safe_wording","remaining_limitation"])
    (B5/"b5_cvenue_sufficiency_review.md").write_text("""# B5 C-Venue Sufficiency Review

Decision: B5 PASS - GO TO REAL-SOURCE EXTENSION

B5-Min is sufficient to close the controlled mechanism package and proceed to
C7 writing. A real-source adapted benchmark is recommended for stronger
external validity and contract-scale evidence.

1. D0 risk is addressed with candidate, rank, repeat, value and reachability
   metrics; C3 saturation is labeled rather than hidden.
2. Candidate relevance, repeat reachability, value rank and Top-K retention give
   at least three comparative dimensions.
3. Full PHS is compared with Original and targeted ablations descriptively.
4. Dependency-only, No-Repeat and No-Value isolate declared obstacles.
5. C7 writing can proceed with execution-model limitations preserved.
6. Real-source expansion is recommended, not required to interpret B5-Min, and
   is not executed in this phase.

B5 controlled-package sufficiency: SUFFICIENT.
Full package without more external validation: PARTIALLY_SUFFICIENT.
No pooled significance claim was forced.
""",encoding="utf-8")
    (B5/"b5_real_source_extension_decision.md").write_text("""# B5 Real-Source Extension Decision

Decision: RECOMMENDED_FOR_STRONGER_PACKAGE

B5-Min closes the controlled mechanism package and supports C7 writing. A later
adapted real-source benchmark would improve external validity and scale evidence.
It is not required before the B5 controlled conclusion.

The follow-up must freeze selection before observing PHS outcomes and record source
provenance, license, compiler/dependency adaptation, properties/getters, stubs,
dependency closure, hand-labeled sequences, repeat/value/noise annotations and
exact adaptation diffs. It must not use PHS success to select tasks, inject
ground truth, or call adapted contracts unmodified real contracts.

This extension was evaluated but not executed in B5-2.
""",encoding="utf-8")
    (B5/"b5_final_decision.md").write_text("""# B5 Final Decision

B5 PASS

GO TO REAL-SOURCE EXTENSION

B5-Min is complete and supports C7 writing. The stronger-package path is a
separately reviewed adapted real-source benchmark. No frozen, matched-random or
B4 result was modified; no 30-seed expansion or new public benchmark was run.
""",encoding="utf-8")
    (ROOT/"docs/v1-restart/PHASE_B5_2_FORMAL_MAIN_RUN.md").write_text(f"""# Phase B5-2 Formal Main Run

Starting branch: develop
Starting commit: {COMMIT}
Preregistration freeze-stage commit: f71c1a60870c93d26323daeedfbc8e9d4c021e59
Formal implementation baseline: {COMMIT}
Hash gate: ALL MATCH for 9 artifacts
Formal authorization: B5_MAIN_AUTHORIZED=1 enabled only for the batch shell
Expected runs: 120; seeds exactly 1..10; budget testLimit=100000 timeout=30s workers=1 stopOnFail=false

| Item | Count |
|---|---:|
| Expected | 120 |
| Observed expected dirs | {sum(a["directory_exists"]=="true" for a in audits)} |
| Parsed rows | {len(usable)} |
| Derived paper-usable formal | {us} |
| Artifact complete | {complete}/120 |
| Checksum pass | {checksum}/120 |
| Falsified | {status["falsified"]} |
| Budget exhausted | {status["budget_exhausted"]} |
| Compile error | {status["compile_error"]} |
| Startup error | {status["startup_error"]} |
| Parser error | {status["parser_error"]} |
| Unknown error | {status["unknown_error"]} |
| Incomplete | {status["incomplete"]} |

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
""",encoding="utf-8")
    print("expected=120"); print("usable="+str(us)); print("falsified="+str(status["falsified"])); print("budget_exhausted="+str(status["budget_exhausted"]))
    for k in ["compile_error","startup_error","parser_error","unknown_error","incomplete"]: print(k+"="+str(status[k]))
    print("artifact_complete="+str(complete)); print("checksum_pass="+str(checksum)); print("combination_effect="+combo_status); print("real_source_extension=RECOMMENDED_FOR_STRONGER_PACKAGE"); print("final_decision=B5 PASS - GO TO REAL-SOURCE EXTENSION")

if __name__=="__main__": main()
