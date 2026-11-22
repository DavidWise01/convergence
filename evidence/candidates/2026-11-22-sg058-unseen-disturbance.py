"""SG058: out-of-family disturbance stress, frozen SG057 policy.
Python 3 stdlib; run beside SG057/055/052 in evidence/candidates.
Outputs sg058-pilot-full.json or sg058-holdout-full.json.
"""
import importlib.util,pathlib,random,math,json,hashlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("sg057",ROOT/"2026-11-22-sg057-adaptive-observation.py")
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
DISTURBANCES=("heavy_tails","heteroskedastic","level_jump","oscillatory_bursts","nonlinear_bias")
TRUTHS=("negative","zero","positive")
def gen(seed,before,after,mechanism,onset):
 r=random.Random(seed);rho=.72;noise=0.;level=0.;v=[]
 for t in range(480):
  local=t-240;sign=before if local<onset else after
  if t:level+=.005*sign
  if mechanism=="heavy_tails":
   shock=r.gauss(0,.16)+(r.choice((-1,1))*r.uniform(1.5,3.0) if r.random()<.022 else 0)
  elif mechanism=="heteroskedastic":
   scale=.55 if (local<0 or (local//30)%2==0) else 2.5
   shock=r.uniform(-.23,.23)*scale
  else:shock=r.uniform(-.23,.23)
  noise=rho*noise+shock
  nuisance=0
  if mechanism=="level_jump" and local>=onset+18:nuisance=1.4
  elif mechanism=="oscillatory_bursts" and local>=onset and (local-onset)%80<40:
   nuisance=.8*math.sin(2*math.pi*(local-onset)/18)
  elif mechanism=="nonlinear_bias" and local>=0:
   nuisance=.000018*(local-120)**2
  v.append(level+noise+nuisance)
 return v[240:]
def dataset(start,count):
 out=[]
 for bi,before in enumerate((-1,0,1)):
  for ai,after in enumerate((-1,0,1)):
   for di,mechanism in enumerate(DISTURBANCES):
    for k in range(count):
     seed=start+1000000*bi+200000*ai+30000*di+101*k
     onset=(100,120,140)[k%3]
     obs=gen(seed,before,after,mechanism,onset)
     pred={n:g.m.decision(obs,n) for n in (100,140,180,220,240)}
     out.append(dict(seed=seed,env=mechanism,truth=TRUTHS[ai],before=before,after=after,onset=onset,pred=pred))
 return out
def strict_prefix_policy(obs,table):
 for n in (140,180,220):
  label,slope,se=g.m.decision(obs[:n],n)
  if label=="unresolved":
   key=g.feature(n,label,slope,se)
   if table.get(key,{}).get("authorize",False):return n,"unresolved"
 label,_,_=g.m.decision(obs[:240],240)
 return 240,label
def run(stage="holdout"):
 training=list(g.m.samples(215000000,30));table=g.train(training)
 start,count={"pilot":(227000000,5),"holdout":(233000000,20)}[stage]
 rows=dataset(start,count);scores,ledger=g.tally(rows,table)
 by={}
 for row in ledger:
  d=by.setdefault(row["env"],{p:dict(correct=0,false_direction=0,missed_direction=0,abstain=0,early=0,observations=0,loss=0) for p in ("wait","early_abstain")})
  for p in ("wait","early_abstain"):
   a=row["actions"][p];v=d[p];kind=a["kind"];n=a["n"]
   v[kind]+=1;v["early"]+=int(n<240);v["observations"]+=n;v["loss"]+=.06*n+g.PEN[kind]
 for d in by.values():
  for v in d.values():v["loss"]=round(v["loss"],2)
 mismatches=0
 for r,entry in zip(rows,ledger):
  obs=gen(r["seed"],r["before"],r["after"],r["env"],r["onset"])
  n,label=strict_prefix_policy(obs,table)
  action=entry["actions"]["early_abstain"]
  mismatches+=int((n,label)!=(action["n"],action["label"]))
 if mismatches:raise AssertionError("strict prefix-policy disagrees with ledger")
 result=dict(id="TD-CROSSDOMAIN-SG058",freeze_commit="17de9bb3de025e05b186b9bf6ccb7edb003217b6",stage=stage,streams=len(rows),scores=scores,by_disturbance=by,authorized={k:v for k,v in table.items() if v["authorize"]},strict_prefix_mismatches=mismatches,
  modified=[r for r in ledger if r["actions"]["wait"]["label"]!=r["actions"]["early_abstain"]["label"]],
  wrong=[r for r in ledger if r["actions"]["early_abstain"]["kind"] in ("missed_direction","false_direction")],
  ledger_sha256=hashlib.sha256(json.dumps(ledger,sort_keys=True).encode()).hexdigest(),ledger=ledger)
 if stage=="holdout":
  assert (scores["early_abstain"]["correct"],scores["early_abstain"]["false_direction"],scores["early_abstain"]["abstain"],scores["early_abstain"]["observations"],scores["early_abstain"]["loss"])==(231,28,641,212860,28509.6)
 return result
if __name__=="__main__":
 stage=sys.argv[1] if len(sys.argv)>1 else "holdout";x=run(stage)
 (ROOT/("sg058-"+stage+"-full.json")).write_text(json.dumps(x,indent=2)+"\n")
 print(json.dumps(dict(stage=stage,streams=x["streams"],scores=x["scores"],by_disturbance=x["by_disturbance"],ledger_sha256=x["ledger_sha256"]),indent=2))
