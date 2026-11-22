"""SG056 frozen 27-cell loss grid. Stdlib Python3; sibling SG055 and SG052 needed.
Run from convergence/evidence/candidates, output full stream ledger JSON.
"""
import json,hashlib,itertools,importlib.util,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("sg055",ROOT/"2026-11-22-sg055-no-choice.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=("SG052_wait","SG054_threshold4","SG055_ranked")
FALSE=(75,150,300);ABSTAIN=(6,18,36);SAMPLE=(.03,.06,.12)
def run():
 training=list(m.samples(197000000,20));table=m.train(training,20,0)
 ledger=[]
 for r in m.samples(211000000,40):
  baseline=(240,r["pred"][240][0],"deadline")
  sg54=baseline
  for n in m.CP[:-1]:
   _,s,se=r["pred"][n]
   lab=m.b.label(s,se,m.Z*4)
   if lab!="unresolved":sg54=(n,lab,"SG054");break
  choices=dict(zip(P,(baseline,sg54,m.policy(r,table))))
  ledger.append(dict(seed=r["seed"],truth=r["truth"],env=r["env"],before=r["before"],after=r["after"],onset=r["onset"],actions={p:dict(n=n,label=lab,kind=m.kind(lab,r["truth"]),key=key) for p,(n,lab,key) in choices.items()}))
 cells=[]
 for error,abstain,sample in itertools.product(FALSE,ABSTAIN,SAMPLE):
  loss={p:0. for p in P}
  penalty=dict(correct=0,missed_direction=90,false_direction=error,abstain=abstain)
  for row in ledger:
   for p,a in row["actions"].items():loss[p]+=sample*a["n"]+penalty[a["kind"]]
  loss={p:round(loss[p],4) for p in P}
  winner=min(P,key=lambda p:(loss[p],P.index(p)))
  cells.append(dict(false_direction_cost=error,abstain_cost=abstain,sample_cost=sample,loss=loss,winner=winner,regret={p:round(loss[p]-loss[winner],4) for p in P}))
 counts={p:dict(correct=0,missed_direction=0,false_direction=0,abstain=0,early=0,observations=0,wrong_seeds=[]) for p in P}
 for r in ledger:
  for p,a in r["actions"].items():
   s=counts[p];s[a["kind"]]+=1;s["early"]+=int(a["n"]<240);s["observations"]+=a["n"]
   if a["kind"] in ("false_direction","missed_direction"):s["wrong_seeds"].append(r["seed"])
 winners={p:sum(c["winner"]==p for c in cells) for p in P}
 center=next(c for c in cells if (c["false_direction_cost"],c["abstain_cost"],c["sample_cost"])==(150,18,.06))
 def sha(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest()
 result=dict(id="TD-CROSSDOMAIN-SG056",freeze_commit="329cb6e6c6ee8448bf7ac04a4f440a3efa53787a",n=len(ledger),training_n=len(training),authorized_groups={k:v for k,v in table.items() if v["authorize"]},center=center,policy_counts=counts,wins=winners,grid=cells,hashes=dict(stream_ledger_sha256=sha(ledger),grid_sha256=sha(cells)),rows=ledger)
 assert len(ledger)==1080 and len(cells)==27 and winners==dict(SG052_wait=24,SG054_threshold4=0,SG055_ranked=3)
 return result
if __name__=="__main__":
 x=run();(ROOT/"sg056-full-holdout.json").write_text(json.dumps(x,indent=2)+"\n")
 print(json.dumps({k:x[k] for k in ("n","center","wins","hashes")},indent=2))
