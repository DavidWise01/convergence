"""SG057: frozen adaptive early-abstain policy. Stdlib Python3.
Requires sibling 2026-11-22-sg055-no-choice.py and SG052 in evidence/candidates.
Execute: python3 2026-11-22-sg057-adaptive-observation.py [pilot|holdout].
"""
import importlib.util,pathlib,json,math,hashlib,statistics,sys
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("sg055",ROOT/"2026-11-22-sg055-no-choice.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
if not hasattr(m.b,"kind"):m.b.kind=m.b.outcome
CP=(140,180,220)
PEN=dict(correct=0,missed_direction=90,false_direction=150,abstain=18)
def feature(n,lab,slope,se):
 ratio=abs(slope)/max(se,1e-12)
 band="lt1" if ratio<1 else "lt2" if ratio<2 else "lt4" if ratio<4 else "ge4"
 noise="high" if se>=.002 else "low"
 return f"{n}:{lab}:{band}:{noise}"
def actions(r):
 end=r["pred"][240][0];opts=[]
 for n in CP:
  label,s,se=r["pred"][n]
  if label=="unresolved":opts.append((n,feature(n,label,s,se)))
 return opts,end
def train(rows,min_n=25,sd_factor=1.64):
 groups={}
 for r in rows:
  opts,final=actions(r)
  wait=14.4+PEN[m.kind(final,r["truth"])]
  for n,key in opts:
   diff=wait-(.06*n+18)
   groups.setdefault(key,[]).append(diff)
 table={}
 for key,vals in sorted(groups.items()):
  mean=statistics.mean(vals)
  sd=statistics.stdev(vals) if len(vals)>1 else 1e9
  lower=mean-sd_factor*sd/math.sqrt(len(vals))
  table[key]=dict(n=len(vals),mean_advantage=mean,sd=sd,lower_bound=lower,authorize=len(vals)>=min_n and lower>0)
 return table
def choose(r,table):
 opts,final=actions(r)
 for n,key in opts:
  if table.get(key,{}).get("authorize",False):return n,"unresolved","early_abstain:"+key
 return 240,final,"deadline"
def tally(rows,table):
 totals={p:dict(correct=0,missed_direction=0,false_direction=0,abstain=0,observations=0,loss=0.,early=0) for p in ("wait","early_abstain")}
 ledger=[]
 for r in rows:
  options=dict(wait=(240,r["pred"][240][0],"deadline"),early_abstain=choose(r,table))
  entry=dict(seed=r["seed"],truth=r["truth"],env=r["env"],actions={})
  for p,(n,lab,reason) in options.items():
   k=m.kind(lab,r["truth"]);s=totals[p]
   s[k]+=1;s["observations"]+=n;s["loss"]+=n*.06+PEN[k];s["early"]+=int(n<240)
   entry["actions"][p]=dict(n=n,label=lab,why=reason,kind=k)
  ledger.append(entry)
 for v in totals.values():v["loss"]=round(v["loss"],2)
 return totals,ledger
def run(stage="holdout"):
 training=list(m.samples(215000000,30));table=train(training)
 start,count={"pilot":(219000000,8),"holdout":(223000000,40)}[stage]
 rows=list(m.samples(start,count));summary,ledger=tally(rows,table)
 obj=dict(id="TD-CROSSDOMAIN-SG057",freeze_commit="1ef22e93f5d6021f018be73727c4c1602d28fe84",stage=stage,seed_start=start,n=len(rows),train_n=len(training),table=table,
  authorized={k:v for k,v in table.items() if v["authorize"]},summary=summary,
  changes=[r for r in ledger if r["actions"]["wait"]["label"]!=r["actions"]["early_abstain"]["label"]],
  early_cases=[r for r in ledger if r["actions"]["early_abstain"]["n"]<240],
  wrong_cases=[r for r in ledger if r["actions"]["early_abstain"]["kind"] in ("missed_direction","false_direction")],
  ledger_digest=hashlib.sha256(json.dumps(ledger,sort_keys=True).encode()).hexdigest(),cases=ledger)
 if stage=="holdout":
  assert (summary["early_abstain"]["correct"],summary["early_abstain"]["false_direction"],summary["early_abstain"]["abstain"],summary["early_abstain"]["observations"],summary["early_abstain"]["loss"])==(449,25,606,254780,29944.8)
 return obj
if __name__=="__main__":
 stage=sys.argv[1] if len(sys.argv)>1 else "holdout";x=run(stage)
 (ROOT/("sg057-"+stage+"-full.json")).write_text(json.dumps(x,indent=2)+"\n")
 print(json.dumps(dict(stage=stage,summary=x["summary"],authorized=x["authorized"],ledger_digest=x["ledger_digest"]),indent=2))
