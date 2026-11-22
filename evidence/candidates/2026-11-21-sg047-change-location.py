"""SG047: locate within-window changes; frozen calibration, negative controls.
Python 3 standard library. Run from evidence/candidates/.
Depends on sibling 2026-11-21-sg043-coverage-audit.py.
Writes full 720-stream holdout and all counterexamples beside this source.
"""
import math,json,hashlib,statistics as st,importlib.util,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("sg043",ROOT/"2026-11-21-sg043-coverage-audit.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
SCENARIOS=m.SCENARIOS;CANDIDATES=(60,80,100,120,140,160,180)
def ar(v):
 n=len(v);mid=(n-1)/2;avg=sum(v)/n
 b=sum((i-mid)*(x-avg) for i,x in enumerate(v))/sum((i-mid)**2 for i in range(n))
 e=[x-avg-b*(i-mid) for i,x in enumerate(v)]
 den=sum(x*x for x in e[:-1])
 return (sum(x*y for x,y in zip(e[1:],e[:-1]))/den if den else 0),(sum(x*x for x in e)/n)**.5
def prior_flag(v):
 a,sa=ar(v[:120]);b,sb=ar(v[120:])
 return abs(b-a)>.22 or max(sa,sb)/max(min(sa,sb),1e-12)>1.5
def scan(v):
 scores=[]
 for t in CANDIDATES:
  a,sa=ar(v[:t]);b,sb=ar(v[t:])
  diff=abs(b-a);ratio=abs(math.log(max(sb,1e-10)/max(sa,1e-10)))
  scores.append((diff+.35*ratio,t,diff,ratio))
 return max(scores)
def dataset(start,count):
 rows=[]
 for j,scenario in enumerate(SCENARIOS):
  for drift in (False,True):
   for k in range(count):
    seed=start+200000*j+10000*int(drift)+101*k
    v=m.stream(seed,scenario,drift)
    score,cp,dr,rms=scan(v)
    full,fullse=m.trend_hac(v);local,localse=m.trend_hac(v[120:]);cut,cutse=m.trend_hac(v[cp:])
    truth=(.0027 if scenario=="subtle_drift" else .005) if drift else 0.
    onset=60 if scenario in ("late_correlation_switch","late_oscillation") else 0 if scenario in ("correlation_switch","fast_oscillation","variable_period","colored_control") else None
    rows.append(dict(seed=seed,scenario=scenario,drift=drift,truth=truth,known_onset=onset,cp=cp,score=score,delta_rho=dr,log_rms_ratio=rms,old_flag=prior_flag(v),full_s=full,full_se=fullse,local120_s=local,local120_se=localse,cut_s=cut,cut_se=cutse))
 return rows
def quantile(rows,which):
 a=sorted(abs(r[which+"_s"]-r["truth"])/max(r[which+"_se"],1e-12) for r in rows)
 return a[min(len(a)-1,math.ceil((len(a)+1)*.9)-1)]
def evaluate(rows,global_z,local_z,threshold,policy):
 total=dict(correct=0,FP=0,FN=0,abstain=0,observations=len(rows)*240,loss=0.)
 by={};misses=[];alarms=[]
 for r in rows:
  if policy=="pooled":alarm=False;which="full";z=global_z
  elif policy=="SG046":alarm=r["old_flag"];which="local120" if alarm else "full";z=local_z if alarm else global_z
  else:alarm=r["score"]>threshold;which="cut" if alarm else "full";z=local_z if alarm else global_z
  s=r[which+"_s"];se=r[which+"_se"];lo=s-z*se;hi=s+z*se
  hit=lo<=r["truth"]<=hi
  if not hit:misses.append(dict(seed=r["seed"],scenario=r["scenario"],truth=r["truth"],drift=r["drift"],selected=which,cp=r["cp"] if alarm else None,score=r["score"],interval=[lo,hi]))
  if alarm:alarms.append(dict(seed=r["seed"],scenario=r["scenario"],cp=r["cp"],score=r["score"],true_onset=r["known_onset"]))
  for group in ("ALL",r["scenario"],"alarm" if alarm else "no_alarm"):
   g=by.setdefault(group,dict(n=0,covered=0,mean_width=0.,wrong=0))
   g["n"]+=1;g["covered"]+=int(hit);g["mean_width"]+=2*z*se
  label="confirmed" if lo>0 or hi<0 else "rejected" if lo>-.0032 and hi<.0032 else "unresolved"
  kind="abstain" if label=="unresolved" else "correct" if (label=="confirmed")==r["drift"] else "FP" if label=="confirmed" else "FN"
  total[kind]+=1;total["loss"]+=14.4+dict(correct=0,FP=150,FN=90,abstain=18)[kind]
  by[r["scenario"]]["wrong"]+=int(kind in ("FP","FN"))
 total["loss"]=round(total["loss"],2)
 for g in by.values():g["coverage"]=round(g["covered"]/g["n"],6);g["mean_width"]=round(g["mean_width"]/g["n"],7)
 return dict(summary=total,coverage=by,misses=misses,alarms=alarms)
def calibrate():
 r=dataset(111000000,20);negative=sorted(a["score"] for a in r if a["known_onset"]!=60)
 cut=negative[min(len(negative)-1,math.ceil((len(negative)+1)*.95)-1)]
 selected=[a for a in r if a["score"]>cut]
 return dict(n=len(r),negative_n=len(negative),threshold=cut,flagged_n=len(selected),global_z=quantile(r,"full"),local_z=quantile(selected,"cut") if len(selected)>=30 else None,rows_sha256=hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest())
def run(stage="holdout"):
 cal=calibrate()
 start,count=(113000000,10) if stage=="pilot" else (117000000,40)
 rows=dataset(start,count)
 old_z=2.453084988962486;old_local=5.9182295530936235
 policies={"pooled":evaluate(rows,cal["global_z"],cal["local_z"],cal["threshold"],"pooled"),
   "SG046":evaluate(rows,old_z,old_local,cal["threshold"],"SG046"),
   "SG047":evaluate(rows,cal["global_z"],cal["local_z"],cal["threshold"],"SG047")}
 late=[r for r in rows if r["known_onset"]==60];others=[r for r in rows if r["known_onset"]!=60]
 detected=[r for r in late if r["score"]>cal["threshold"]]
 detection=dict(late_n=len(late),late_flagged=len(detected),nonlate_n=len(others),nonlate_flagged=sum(r["score"]>cal["threshold"] for r in others),median_location_error=st.median(abs(r["cp"]-60) for r in detected) if detected else None)
 out=dict(id="TD-CROSSDOMAIN-SG047",freeze_commit="c44cce55f24d07f31b140f2aa4865a088f7cd1e1",stage=stage,n=len(rows),calibration=cal,detection=detection,policies=policies,rows_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest())
 if stage=="holdout":
  assert (policies["SG047"]["coverage"]["ALL"]["covered"],len(policies["SG047"]["misses"]))==(617,103)
  assert policies["SG047"]["summary"]["loss"]==21450.
 (ROOT/("sg047-"+stage+"-full.json")).write_text(json.dumps(out,indent=2)+"\n")
 return out
if __name__=="__main__":
 stage=sys.argv[1] if len(sys.argv)>1 else "holdout"
 x=run(stage)
 print(json.dumps(dict(calibration=x["calibration"],detection=x["detection"],scores={p:v["summary"] for p,v in x["policies"].items()},misses=len(x["policies"]["SG047"]["misses"])),indent=2))
