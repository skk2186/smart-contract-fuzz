#!/usr/bin/env python3
"""B5 controlled-scenario registry, passive observer, and metric collector."""
from __future__ import annotations
import argparse, csv, json, re
from datetime import datetime
from pathlib import Path

FIELDS = ["run_id","scenario","method","seed","budget","status","property_falsified","budget_exhausted","target_state_reached","target_candidate_rank","top1_hit","top5_hit","dependency_candidate_count","property_candidate_count","candidate_reduction_ratio","required_repeat_count","observed_repeat_count","value_evidence_enabled","repeat_enabled","k","time_to_falsify_seconds","fuzz_seconds","process_wall_seconds","preprocess_seconds","harness_compile_seconds","artifact_complete","checksum_pass"]

def registry(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def paths(path, contract):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    return data.get(contract,{}).get("paths",[])

def candidate_rank(entries, target):
    target=tuple(target)
    for index, entry in enumerate(entries,1):
        if tuple(entry.get("sequence",[])) == target: return index
    return ""

def timestamp(text, pattern):
    match=re.search(r"\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+)\].*"+pattern,text,re.I)
    return datetime.strptime(match.group(1),"%Y-%m-%d %H:%M:%S.%f") if match else None

def status(text, prop, code):
    if re.search(r"Test\s+"+re.escape(prop)+r"\s+falsified|"+re.escape(prop)+r"\s*:\s*(failed|falsified)",text,re.I): return "falsified"
    if re.search(r"compilation failed|ParserError|Could not compile|Source .* not found|Config .* not found",text,re.I): return "startup_error"
    if re.search(r"Test limit reached|testLimit|budget.exhaust|time limit|timed out",text,re.I): return "budget_exhausted"
    return "unknown_error" if code else "incomplete"

def instrument(args):
    source=Path(args.source); output=Path(args.output); text=source.read_text(encoding="utf-8")
    observer="echidna_b5_target_state_observer"
    if args.kind=="original":
        output.write_text(f'// SPDX-License-Identifier: MIT\npragma solidity 0.8.20;\nimport "{source.resolve()}";\ncontract {args.contract}B5OriginalObserver is {args.contract} {{ function {observer}() public view returns (bool) {{ return !{args.getter}(); }} }}\n',encoding="utf-8")
    else:
        pos=text.rfind("}")
        if pos < 0: raise SystemExit("generated harness has no final contract brace")
        text=text[:pos]+f'    function {observer}() public view returns (bool) {{ return !target.{args.getter}(); }}\n'+text[pos:]
        output.write_text(text,encoding="utf-8")

def collect(args):
    spec=registry(args.registry)[args.scenario]
    dep=paths(args.dependency, spec["contract_name"])
    prop=paths(args.property_sequences, spec["contract_name"])
    selected=paths(args.selected_sequences, spec["contract_name"])
    rank=candidate_rank(selected,spec["target_sequence"])
    text=Path(args.raw_log).read_text(encoding="utf-8",errors="ignore")
    state=1 if re.search(r"Test\s+echidna_b5_target_state_observer\s+falsified|echidna_b5_target_state_observer\s*:\s*failed",text,re.I) else 0
    run_status=status(text,spec["property"],args.exit_code)
    start=timestamp(text,r"Running slither on .* Done!")
    failed=timestamp(text,r"Test\s+"+re.escape(spec["property"])+r"\s+falsified")
    end=timestamp(text,r"Test limit reached")
    duration=(failed-start).total_seconds() if failed and start else ""
    fuzz=(end-start).total_seconds() if end and start else duration
    wall=re.search(r"PROCESS_WALL_SECONDS=([0-9.]+)",text)
    repeat=spec["repeat_function"]
    observed=max([entry.get("sequence",[]).count(repeat) for entry in selected],default=0) if repeat else ""
    row=dict.fromkeys(FIELDS,"")
    row.update(run_id=args.run_id,scenario=args.scenario,method=args.method,seed=args.seed,budget="testLimit=100000;timeout=30s",status=run_status,property_falsified=int(run_status=="falsified"),budget_exhausted=int(run_status=="budget_exhausted"),target_state_reached=state,target_candidate_rank=rank,top1_hit=int(rank==1),top5_hit=int(isinstance(rank,int) and rank<=5),dependency_candidate_count=len(dep),property_candidate_count=len(prop),candidate_reduction_ratio=round((len(dep)-len(prop))/len(dep),6) if dep else "",required_repeat_count=spec["required_repeat_count"],observed_repeat_count=observed,value_evidence_enabled=int(args.value_enabled),repeat_enabled=int(args.repeat_enabled),k=args.k,time_to_falsify_seconds=duration,fuzz_seconds=fuzz,process_wall_seconds=wall.group(1) if wall else "",artifact_complete="true",checksum_pass=args.checksum_pass)
    with Path(args.output).open("w",newline="",encoding="utf-8") as f: csv.DictWriter(f,fieldnames=FIELDS,delimiter="\t").writeheader(); csv.DictWriter(f,fieldnames=FIELDS,delimiter="\t").writerow(row)

def expected(args):
    spec=registry(args.registry); methods={"c1":["original","dependency-only","full-k1","full-k5"],"c2":["original","no-repeat","full-k1","full-k5"],"c3":["original","no-value","full-k1","full-k5"]}
    with Path(args.output).open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f,delimiter="\t"); w.writerow(["run_id","scenario","method","seed","budget","expected"])
        for scenario in spec:
            for method in methods[scenario]:
                for seed in range(1,11): w.writerow([f"b5-{scenario}-{method}-s{seed}",scenario,method,seed,"testLimit=100000;timeout=30s","preregistered"])

p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
i=sub.add_parser("instrument"); i.add_argument("--source",required=True); i.add_argument("--output",required=True); i.add_argument("--contract",required=True); i.add_argument("--getter",required=True); i.add_argument("--kind",choices=["original","harness"],required=True)
c=sub.add_parser("collect")
for name in ("registry","scenario","run_id","method","seed","dependency","property_sequences","selected_sequences","raw_log","output"): c.add_argument("--"+name.replace("_","-"),required=True)
c.add_argument("--exit-code",type=int,required=True); c.add_argument("--k",required=True); c.add_argument("--value-enabled",type=int,required=True); c.add_argument("--repeat-enabled",type=int,required=True); c.add_argument("--checksum-pass",default="pass")
e=sub.add_parser("expected"); e.add_argument("--registry",required=True); e.add_argument("--output",required=True)
a=p.parse_args()
if a.cmd=="instrument": instrument(a)
elif a.cmd=="collect": collect(a)
else: expected(a)
