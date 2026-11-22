"""SG059 frozen mixtures and new transition times. Python3 standard library.
Run beside 2026-11-22-sg057-adaptive-observation.py, SG055 and SG052.
python 2026-11-22-sg059-mixture-generalization.py holdout
"""
import importlib.util,pathlib,random,math,json,hashlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("sg057",ROOT/"2026-11-22-sg057-adaptive-observation.py")
g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
MIXES=("tails_jump","variance_oscillation","tails_curvature","jump_variance")
ONSETS=(40,75,165,205)
TRUTHS=("negative","zero","positive")
def gen(seed,before,after,mix,onset):
 r=random.Random(seed);rho=.72;noise=0.;level=0.;series=[]
 for t in range(480):
  local=t-240;direction=before if local<onset else after
  if t:level+=.005*direction
  if mix in ("tails_jump","tails_curvature"):
   shock=r.gauss(0,.16)+(r.choice((-1,1))*r.uniform(1.5,3.) if r.random()<.022 else 0)
  else:
   scale=.55 if (local<0 or (local//30)%2==0) else 2.5
   shock=r.uniform(-.23,.23)*scale
  noise=rho*noise+shock;nuisance=0.
  if mix in ("tails_jump","jump_variance") and local>=onset+18:nuisance+=1.4
  if mix=="variance_oscillation" and local>=onset and (local-onset)%80<40:
   nuisance+=.8*math.sin(2*math.pi*(local-onset)/18)
  if mix=="tails_curvature" and local>=0:nuisance+=.000018*(local-120)**2
  series.append(level+noise+nuisance)
 return series[240:]
def produce(start,count):
 rows=[]
 for bi,before in enumerate((-1,0,1)):
  for ai,after in enumerate((-1,0,1)):
   for mi,mix in enumerate(MIXES):
    for k in range(count):
     seed=start+1000000*bi+200000*ai+30000*mi+101*k
     onset=ONSETS[k%4]
     obs=gen(seed,before,after,mix,onset)
     pred={n:g.m.decision(obs,n) for n in (100,140,180,220,240)}
     rows.append(dict(seed=seed,env=mix,truth=TRUTHS[ai],before=before,after=after,onset=onset,pred=pred))
 return rows
def online(obs,table):
 for n in (140,180,220):
  lab,s,se=g.m.decision(obs[:n],n)
  if lab=="unresolved" and table.get(g.feature(n,lab,s,se),{}).get("authorize",False):
   return n,"unresolved"
 return 240,g.m.decision(obs[:240],240)[0]
def run(stage="holdout"):
 training=list(g.m.samples(215000000,30));table=g.train(training)
 start,count={"pilot":(237000000,5),"holdout":(241000000,20)}[stage]
 rows=produce(start,count);summary,ledger=g.tally(rows,table)
 by={};by_onset={}
 for record,raw in zip(ledger,rows):
  for key,group in ((raw["env"],by),(raw["onset"],by_onset)):
   z=group.setdefault(key,{p:dict(correct=0,missed_direction=0,false_direction=0,abstain=0,observations=0,loss=0.,early=0) for p in ("wait","early_abstain")})
   for p,a in record["actions"].items():
    q=z[p];q[a["kind"]]+=1;q["observations"]+=a["n"];q["loss"]+=.06*a["n"]+g.PEN[a["kind"]];q["early"]+=int(a["n"]<240)
 for group in (by,by_onset):
  for cell in group.values():
   for q in cell.values():q["loss"]=round(q["loss"],2)
 wrong=[x for x in ledger if x["actions"]["early_abstain"]["kind"] in ("missed_direction","false_direction")]
 changes=[x for x in ledger if x["actions"]["early_abstain"]["label"]!=x["actions"]["wait"]["label"]]
 early=[x for x in ledger if x["actions"]["early_abstain"]["n"]<240]
 violations=[];mutations=0
 for raw,record in zip(rows,ledger):
  obs=gen(raw["seed"],raw["before"],raw["after"],raw["env"],raw["onset"])
  observed=online(obs,table);saved=record["actions"]["early_abstain"]
  if observed!=(saved["n"],saved["label"]):violations.append(dict(seed=raw["seed"],kind="online_mismatch"))
  if observed[0]<240:
   for direction in (-1,1):
    edit=obs[:observed[0]]+[obs[observed[0]-1]+direction*8*(i+1) for i in range(240-observed[0])]
    mutations+=1
    if online(edit,table)!=observed:violations.append(dict(seed=raw["seed"],kind="future_leakage",direction=direction))
 assert not violations
 digest=hashlib.sha256(json.dumps(ledger,sort_keys=True).encode()).hexdigest()
 result=dict(id="TD-CROSSDOMAIN-SG059",freeze_commit="bbc36d967e7678db4bee9f92acdd7c6553e793ee",stage=stage,streams=len(rows),summary=summary,by_disturbance=by,by_onset=by_onset,
  authorized={k:v for k,v in table.items() if v["authorize"]},wrong_cases=wrong,changed=changes,early_cases=early,causal_audit=dict(streams=len(rows),mutations=mutations,violations=violations),ledger_sha256=digest,ledger=ledger)
 if stage=="holdout":
  assert (summary["early_abstain"]["correct"],summary["early_abstain"]["false_direction"],summary["early_abstain"]["abstain"],summary["early_abstain"]["observations"],summary["early_abstain"]["loss"])==(137,69,514,169860,29793.6)
 (ROOT/("sg059-"+stage+"-full.json")).write_text(json.dumps(result,indent=2)+"\n")
 return result
if __name__=="__main__":
 result=run(sys.argv[1] if len(sys.argv)>1 else "holdout")
 print(json.dumps(dict(streams=result["streams"],summary=result["summary"],by_disturbance=result["by_disturbance"],by_onset=result["by_onset"],causal_audit=result["causal_audit"],ledger_sha256=result["ledger_sha256"]),indent=2))
