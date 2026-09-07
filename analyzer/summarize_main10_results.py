#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, subprocess, sys
from collections import Counter, OrderedDict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=Path("work/v1-restart/b4-public-supported-10seed-main")
BENCH={"PUB01":"echidna-flags","PUB02":"echidna-multi","PUB03":"smartbugs-multifunc","PUB04":"smartbugs-onefunc"}
METHODS={"original","full-k1","full-k5"}
ARTIFACTS=("manifest.tsv","command.txt","environment.txt","raw","parsed","summary","status","status/status.env","status/checksums.sha256","parsed/smoke.csv","summary/smoke.csv")

def read_tsv(p):
    with p.open(newline="",encoding="utf-8") as f: return list(csv.DictReader(f,delimiter="\t"))
def read_env(p):
    d={}
    if p.is_file():
        for line in p.read_text(encoding="utf-8",errors="replace").splitlines():
            if "=" in line:
                k,v=line.split("=",1); d[k]=v
    return d
def rel(p):
    try: return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError: return p.as_posix()
def checksum(p):
    if not p.is_file(): return "missing"
    r=subprocess.run(["sha256sum","-c",str(p)],cwd=ROOT,capture_output=True,text=True,check=False)
    return "pass" if r.returncode==0 else "fail"
def parsed(p):
    if not p.is_file(): return "missing"
    with p.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
    s={r.get("status","").strip() for r in rows if r.get("status","").strip()}
    return next(iter(s)) if len(s)==1 else ("missing" if not rows else "mixed")
def mname(v):
    return {"original":"Original","full-k1":"Full-K1","full-k5":"Full-K5"}.get(v.lower(),v)

def prereg_errors(rows):
    e=[]
    if len(rows)!=120: e.append("expected run count is %d, not 120"%len(rows))
    ids=[r.get("run_id","") for r in rows]
    e += ["duplicate run_id: "+x for x,n in Counter(ids).items() if n>1]
    for r in rows:
        run=r["run_id"]; m=r["method"].lower(); bid=r["benchmark_id"]
        try: seed=int(r["seed"])
        except ValueError: seed=-1
        if bid not in BENCH: e.append(run+": benchmark outside PUB01-PUB04")
        if r["benchmark_name"]!=BENCH.get(bid): e.append(run+": benchmark name mismatch")
        if m not in METHODS: e.append(run+": method outside preregistered set")
        if seed not in range(1,11): e.append(run+": seed outside 1-10")
        if r["status"]!="preregistered": e.append(run+": status is not preregistered")
        if r["output_dir"].rstrip("/")!=(OUT/run).as_posix(): e.append(run+": output outside B4 root")
        want="configs/public-c1-original.yaml" if m=="original" else "configs/public-c1-harness.yaml"
        if r["config_path"]!=want: e.append(run+": config does not match method")
    return e

def audit(r):
    d=ROOT/r["output_dir"]; missing=[x for x in ARTIFACTS if not (d/x).exists()]
    logs=sorted((d/"raw").glob("seed-*.log"))
    if not logs: missing.append("raw/seed-*.log")
    e=read_env(d/"status/status.env"); status=e.get("STATUS","missing")
    ps=parsed(d/"parsed/smoke.csv"); match="yes" if status==ps else "no"; cs=checksum(d/"status/checksums.sha256")
    notes=[]
    if missing: notes.append("missing: "+",".join(missing))
    if match=="no": notes.append("parser/status mismatch")
    if cs!="pass": notes.append("checksum_"+cs)
    if status=="budget_exhausted": notes.append("no observed counterexample within the declared budget")
    if r["method"].lower()!="original": notes.append("Harness wrapper execution model; not equivalent to Original")
    inc=bool(missing) or status=="incomplete"; raw=logs[0] if logs else d/"raw/seed-*.log"
    return {"run_id":r["run_id"],"benchmark_id":r["benchmark_id"],"benchmark_name":r["benchmark_name"],"method":mname(r["method"]),"seed":r["seed"],"status":status,"run_completed":e.get("RUN_COMPLETED","0"),"exit_code":e.get("EXIT_CODE",""),"parser_status":ps,"status_match":match,"checksum_status":cs,"raw_log_path":rel(raw),"parsed_path":rel(d/"parsed/smoke.csv"),"summary_path":rel(d/"summary/smoke.csv"),"command_path":rel(d/"command.txt"),"environment_path":rel(d/"environment.txt"),"notes":"; ".join(notes),"audit_incomplete":"yes" if inc else "no"}

def groups(rows):
    gs=OrderedDict()
    for r in rows: gs.setdefault((r["benchmark_id"],r["benchmark_name"],r["method"]),[]).append(r)
    out=[]
    for (bid,bname,m),g in gs.items():
        c=Counter(x["status"] for x in g); mm=sum(x["status_match"]=="no" for x in g); cf=sum(x["checksum_status"]!="pass" for x in g); inc=sum(x["audit_incomplete"]=="yes" or x["status"]=="incomplete" for x in g); block=bool(mm or cf or inc or c["startup_error"] or c["unknown_error"]); notes=[]
        if c["budget_exhausted"]: notes.append("budget_exhausted means no observed counterexample within the declared budget")
        if m!="Original": notes.append("Harness wrapper caveat; no Original equivalence or Total calls speedup claim")
        if block: notes.append("BLOCKING")
        out.append({"benchmark_id":bid,"benchmark_name":bname,"method":m,"runs":str(len(g)),"falsified":str(c["falsified"]),"budget_exhausted":str(c["budget_exhausted"]),"startup_error":str(c["startup_error"]),"unknown_error":str(c["unknown_error"]),"incomplete":str(inc),"parser_status_mismatch":str(mm),"checksum_pass":str(len(g)-cf),"checksum_fail":str(cf),"falsification_rate":"%.6f"%(c["falsified"]/len(g)),"main_table_usable":"no" if block else "conditional","notes":"; ".join(notes)})
    return out

def write_tsv(p,fields,rows):
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def markdown(rows,gs,errors):
    c=Counter(r["status"] for r in rows); cp=sum(r["checksum_status"]=="pass" for r in rows); mm=sum(r["status_match"]=="no" for r in rows); inc=sum(r["audit_incomplete"]=="yes" or r["status"]=="incomplete" for r in rows); block=bool(errors or cp!=len(rows) or mm or inc)
    s=["# B4 V1 Public Supported 10-Seed Main Results","","## Overall result","", "- Expected and audited runs: %d / 120."%len(rows),"- Status counts: falsified=%d; budget_exhausted=%d; startup_error=%d; unknown_error=%d; incomplete=%d."%(c["falsified"],c["budget_exhausted"],c["startup_error"],c["unknown_error"],inc),"- Checksum: %d/%d passed."%(cp,len(rows)),"- Parser/status mismatches: %d."%mm,"- Main-table eligibility: %s."%("no" if block else "conditional"),"","budget_exhausted means no observed counterexample within the declared budget. It is not a property pass or contract-safety result.","","## By benchmark and method","","| benchmark | method | runs | falsified | budget_exhausted | falsification rate | usable |","|---|---|---:|---:|---:|---:|---|"]
    s += ["| %s | %s | %s | %s | %s | %s | %s |"%(r["benchmark_name"],r["method"],r["runs"],r["falsified"],r["budget_exhausted"],r["falsification_rate"],r["main_table_usable"]) for r in gs]
    s += ["","## Audit exceptions",""]; ex=[r for r in rows if r["notes"] and (r["status"]!="falsified" or "mismatch" in r["notes"] or "checksum" in r["notes"] or "missing" in r["notes"])]
    s += ["- BLOCKING: "+x for x in errors]+["- %s: %s"%(r["run_id"],r["notes"]) for r in ex]
    if not errors and not ex: s.append("- No artifact, checksum, parser/status, startup, unknown, or incomplete exceptions observed.")
    s += ["","## Interpretation limits","",
          "- Harness falsified means a counterexample under the generated wrapper execution model; it does not establish semantic equivalence with Original independent multi-transaction execution.",
          "- Original and Harness Total calls are not used to claim speedup or equal work.",
          "- These are descriptive results for the four preregistered supported public benchmarks, not broad superiority over Echidna, SMARTIAN, MuFuzz, or IR-Fuzz.",
          "- exercise2-access-control and PUB06/PUB07/PUB08 are not included.","","## Next step","",
          "The tables may enter C-stage paper result organization only after manual review of run-level evidence and semantic caveats. Broader benchmarks or conditional replay are separate experiments.",""]
    return "\n".join(s)

def main():
    ap=argparse.ArgumentParser(description=__doc__); g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--check-only",action="store_true",help="audit without writing paper-ready files"); g.add_argument("--write",action="store_true",help="audit and write paper-ready result files"); a=ap.parse_args()
    expected=read_tsv(ROOT/"paper-ready/v1/main10_expected_runs.tsv"); errors=prereg_errors(expected); rows=[audit(r) for r in expected]; gs=groups(rows); b4=ROOT/OUT; actual={p.name for p in b4.glob("b4-*") if p.is_dir()} if b4.is_dir() else set(); extra=sorted(actual-{r["run_id"] for r in expected})
    if extra: errors.append("unexpected b4 run directories: "+", ".join(extra))
    mm=sum(r["status_match"]=="no" for r in rows); cf=sum(r["checksum_status"]!="pass" for r in rows); inc=sum(r["audit_incomplete"]=="yes" or r["status"]=="incomplete" for r in rows); block=bool(errors or mm or cf or inc)
    print("expected_runs=%d\naudit_errors=%d\nchecksum_fail=%d\nparser_status_mismatch=%d\nincomplete=%d\nblocking=%s"%(len(rows),len(errors),cf,mm,inc,"yes" if block else "no"))
    for x in errors: print("ERROR: "+x,file=sys.stderr)
    if a.write:
        d=ROOT/"paper-ready/v1"; write_tsv(d/"main10_results_by_run.tsv",["run_id","benchmark_id","benchmark_name","method","seed","status","run_completed","exit_code","parser_status","status_match","checksum_status","raw_log_path","parsed_path","summary_path","command_path","environment_path","notes"],rows); write_tsv(d/"main10_results_summary.tsv",["benchmark_id","benchmark_name","method","runs","falsified","budget_exhausted","startup_error","unknown_error","incomplete","parser_status_mismatch","checksum_pass","checksum_fail","falsification_rate","main_table_usable","notes"],gs); (d/"main10_results_summary.md").write_text(markdown(rows,gs,errors),encoding="utf-8"); print("wrote=paper-ready/v1/main10_results_by_run.tsv"); print("wrote=paper-ready/v1/main10_results_summary.tsv"); print("wrote=paper-ready/v1/main10_results_summary.md")
    return 1 if block else 0
if __name__=="__main__": raise SystemExit(main())
