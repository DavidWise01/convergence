"""SG046: local post-shift uncertainty audit; Python3 standard library.
Sibling dependency: 2026-11-21-sg043-coverage-audit.py.
Reproduce by invoking python this_file.py, which writes sg046-full-holdout.json.
"""
import json,math,hashlib,statistics,importlib.util,pathlib
P=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("sg043",P/"2026-11-21-sg043-coverage-audit.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
SCENARIOS=m.SCENARIOS
def ar(v):
 n=len(v);mean=sum(v)/n;mid=(n-1)/2
 sl=sum((i-mid)*(x-mean) for i,x in enumerate(v))/sum((i-mid)**2 for i in range(n))
 e=[x-mean-sl*(i-mid) for i,x in enumerate(v)]
 den=sum(x*x for x in e[:-1])
 return sum(x*y for x,y in zip(e[1:],e[:-1]))/den if den else 0,(sum(x*x for x in e)/n)**.5
def changed(v):
 a,sa=ar(v[:120]);b,sb=ar(v[120:])
 return abs(a-b)>.22 or max(sa,sb)/max(min(sa,sb),1e-12)>1.5,a,b
def data(start,count):
 out=[]
 for j,scenario in enumerate(SCENARIOS):
  for drift in (False,True):
   for k in range(count):
    seed=start+200000*j+10000*int(drift)+101*k
    v=m.stream(seed,scenario,drift)
    flag,r1,r2=changed(v)
    whole,whole_se=m.trend_hac(v)
    local,local_se=m.trend_hac(v[120:])
    truth=(.0027 if scenario=="subtle_drift" else .005) if drift else 0.
    out.append(dict(seed=seed,scenario=scenario,drift=drift,truth=truth,flag=flag,rho_early=r1,rho_late=r2,whole_s=whole,whole_se=whole_se,local_s=local,local_se=local_se))
 return out
def q90(rows,mode):
 q=sorted(abs(r[mode+"_s"]-r["truth"])/max(r[mode+"_se"],1e-12) for r in rows)
 return q[min(len(q),math.ceil(.9*(len(q)+1)))-1]
def score(rows,multiplier,select):
 total=dict(correct=0,FP=0,FN=0,abstain=0,loss=0.,observations=len(rows)*240)
 grouped={};misses=[]
 for r in rows:
  mode=select(r);z=multiplier(r)
  estimate=r[mode+"_s"];se=r[mode+"_se"];lo=estimate-z*se;hi=estimate+z*se
  covered=lo<=r["truth"]<=hi
  for group in ("ALL",r["scenario"],"shift_flag" if r["flag"] else "stable_flag"):
   g=grouped.setdefault(group,dict(n=0,covered=0,width=0))
   g["n"]+=1;g["covered"]+=int(covered);g["width"]+=2*z*se
  if not covered:misses.append({k:r[k] for k in ("seed","scenario","drift","truth","flag","rho_early","rho_late")} | dict(estimate=estimate,se=se,interval=[lo,hi],mode=mode))
  label="confirmed" if lo>0 or hi<0 else "rejected" if lo>-.0032 and hi<.0032 else "unresolved"
  outcome="abstain" if label=="unresolved" else "correct" if (label=="confirmed")==r["drift"] else "FP" if label=="confirmed" else "FN"
  total[outcome]+=1;total["loss"]+=14.4+dict(correct=0,FP=150,FN=90,abstain=18)[outcome]
 total["loss"]=round(total["loss"],2)
 for g in grouped.values():
  g["coverage"]=round(g["covered"]/g["n"],5)
  g["mean_width"]=round(g.pop("width")/g["n"],7)
 return dict(total=total,by_group=grouped,misses=misses)
def run(start=107000000,count=40):
 cal=data(103000000,20);zf=q90(cal,"whole");flagged=[r for r in cal if r["flag"]]
 zl=q90(flagged,"local") if len(flagged)>=30 else None
 rows=data(start,count)
 whole=score(rows,lambda r:zf,lambda r:"whole")
 local=score(rows,lambda r:zl if r["flag"] and zl is not None else zf,lambda r:"local" if r["flag"] and zl is not None else "whole")
 result=dict(id="TD-CROSSDOMAIN-SG046",freeze_commit="ad87e204b5c9e3524087651408a0fcd1de0e1c37",calibration=dict(n=len(cal),flagged=len(flagged),whole_z=zf,local_z=zl),holdout_n=len(rows),whole=whole,segment_local=local,sha256=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest())
 if start==107000000 and count==40:
  assert (whole["by_group"]["ALL"]["covered"],local["by_group"]["ALL"]["covered"])==(653,659)
  assert len(local["misses"])==61 and local["total"]["loss"]==18096.
 return result
if __name__=="__main__":
 r=run();(P/"sg046-full-holdout.json").write_text(json.dumps(r,indent=2)+"\n")
 print(json.dumps({k:r[k] for k in ("calibration","holdout_n","sha256")} | dict(whole=r["whole"]["total"],segment_local=r["segment_local"]["total"],misses=len(r["segment_local"]["misses"])),indent=2))
