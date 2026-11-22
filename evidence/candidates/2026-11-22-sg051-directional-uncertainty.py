"""SG051: frozen directional uncertainty calibration; Python3 standard library.
Execute within convergence/evidence/candidates beside SG050. No external packages.
"""
import json,math,hashlib,importlib.util,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("sg050",ROOT/"2026-11-22-sg050-three-direction.py")
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
TRUTHS=("negative","zero","positive")
PENALTY={"correct":0,"missed_direction":90,"false_direction":150,"abstain":18}
def dataset(start,count):
 rows=[]
 for j,scenario in enumerate(b.SCENARIOS):
  for di,d in enumerate((-1,0,1)):
   for k in range(count):
    seed=start+200000*j+20000*di+101*k
    v,truth_slope=b.gen(seed,scenario,d)
    slope,se=b.hac(v)
    rows.append(dict(seed=seed,scenario=scenario,truth=TRUTHS[di],true_slope=truth_slope,estimate=slope,se=se,ratio=abs(slope-truth_slope)/max(se,1e-12)))
 return rows
def quantile(rows):
 vals=sorted(r["ratio"] for r in rows)
 rank=min(len(vals),math.ceil(.9*(len(vals)+1)))
 return vals[rank-1],rank
def decision(r,z):
 lo=r["estimate"]-z*r["se"];hi=r["estimate"]+z*r["se"]
 label=b.three_way(lo,hi)
 kind=b.outcome(label,r["truth"])
 return dict(label=label,kind=kind,covered=lo<=r["true_slope"]<=hi,interval=[lo,hi],loss=14.4+PENALTY[kind])
def evaluate(rows,z):
 summary=dict(correct=0,missed_direction=0,false_direction=0,abstain=0,covered=0,samples=0,loss=0.)
 group={};failures=[];misses=[]
 for r in rows:
  q=decision(r,z);kind=q["kind"]
  summary[kind]+=1;summary["covered"]+=int(q["covered"]);summary["samples"]+=240;summary["loss"]+=q["loss"]
  for k in (r["scenario"],"truth:"+r["truth"]):
   g=group.setdefault(k,dict(n=0,correct=0,missed_direction=0,false_direction=0,abstain=0,covered=0))
   g["n"]+=1;g[kind]+=1;g["covered"]+=int(q["covered"])
  entry=dict(seed=r["seed"],scenario=r["scenario"],truth=r["truth"],true_slope=r["true_slope"],estimate=r["estimate"],se=r["se"],**q)
  if kind!="correct":failures.append(entry)
  if not q["covered"]:misses.append(entry)
 summary["loss"]=round(summary["loss"],2)
 return dict(summary=summary,group=group,failures=failures,coverage_misses=misses)
def run():
 cal=dataset(145000000,20);z,rank=quantile(cal)
 hold=dataset(151000000,40)
 old=evaluate(hold,b.Z);new=evaluate(hold,z)
 changes=[]
 for r in hold:
  a=decision(r,b.Z);c=decision(r,z)
  if a["label"]!=c["label"]:changes.append(dict(seed=r["seed"],scenario=r["scenario"],truth=r["truth"],old=a["label"],new=c["label"],old_kind=a["kind"],new_kind=c["kind"]))
 out=dict(id="TD-CROSSDOMAIN-SG051",freeze_commit="28bb5b6fc1a41220a5af96f8b6c2ce9b4973b72f",calibration=dict(n=len(cal),rank=rank,z=z,original_covered=evaluate(cal,b.Z)["summary"]["covered"],corrected_covered=evaluate(cal,z)["summary"]["covered"]),holdout=dict(n=len(hold),SG050=old,SG051=new,changes=changes,rows_sha256=hashlib.sha256(json.dumps(hold,sort_keys=True).encode()).hexdigest()))
 assert (out["holdout"]["SG051"]["summary"]["correct"],out["holdout"]["SG051"]["summary"]["false_direction"],out["holdout"]["SG051"]["summary"]["abstain"],out["holdout"]["SG051"]["summary"]["loss"])==(900,37,142,23748.)
 return out
if __name__=="__main__":
 print(json.dumps(run(),indent=2))
