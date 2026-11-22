"""SG054 causal, deterministic, single-action checkpoint policy.
Run from evidence/candidates with SG052 sibling file in the same folder.
python 2026-11-22-sg054-hegemonic-policy.py holdout
"""
import importlib.util,json,hashlib,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
sg=ROOT/"2026-11-22-sg052-joint-transition.py"
if not sg.exists():sg=ROOT.parent/"sg052"/"sg052.py"
spec=importlib.util.spec_from_file_location("sg052",sg)
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
CHECKPOINTS=(100,140,180,220,240); Z=4.327111573414373
PENALTY={"correct":0,"missed_direction":90,"false_direction":150,"abstain":18}
def classify(prefix,z):
    s,se=b.hac(prefix[-100:])
    return b.label(s,se,z),s,se
def select(v,early_multiplier=4):
    trace=[]
    for n in CHECKPOINTS:
        z=Z*early_multiplier if n<240 else Z
        label,s,se=classify(v[:n],z)
        action=("commit_"+label) if label!="unresolved" else ("observe" if n<240 else "abstain")
        trace.append(dict(n=n,action=action,label=label,slope=s,se=se,multiplier=z))
        if action!="observe":return trace
    raise AssertionError("unreachable")
def score(trace,truth):
    t=trace[-1];kind=b.kind(t["label"],truth)
    return kind,round(.06*t["n"]+PENALTY[kind],2)
def run(start=191000000,count=40,multiplier=4):
    totals={p:dict(correct=0,missed_direction=0,false_direction=0,abstain=0,loss=0.,observations=0,early_commits=0) for p in ("SG052_final","SG054_policy")}
    groups={};records=[]
    for bi,before in enumerate(b.SIGNS):
      for ai,after in enumerate(b.SIGNS):
        for ei,env in enumerate(b.NOISE):
          for k in range(count):
            onset=(100,120,140)[k%3]
            seed=start+1000000*bi+200000*ai+30000*ei+101*k
            v=b.gen(seed,before,after,env,onset)
            truth=("negative","zero","positive")[ai]
            full,_,_=classify(v,Z)
            baseline=[dict(n=240,action=("commit_"+full if full!="unresolved" else "abstain"),label=full)]
            decision=select(v,multiplier)
            for p,trace in (("SG052_final",baseline),("SG054_policy",decision)):
                kind,loss=score(trace,truth);t=totals[p];t[kind]+=1;t["loss"]+=loss;t["observations"]+=trace[-1]["n"];t["early_commits"]+=int(trace[-1]["n"]<240)
                e=groups.setdefault(env,{}).setdefault(p,dict(correct=0,missed_direction=0,false_direction=0,abstain=0))
                e[kind]+=1
            records.append(dict(seed=seed,env=env,before=before,after=after,onset=onset,truth=truth,baseline=baseline[-1],policy_trace=decision,outcome=score(decision,truth)[0]))
    for t in totals.values():t["loss"]=round(t["loss"],2)
    result=dict(id="TD-CROSSDOMAIN-SG054",freeze_commit="7a61929a1f8a3e053ffd7c02dcfcb4fd1cbe176f",start=start,n=len(records),early_multiplier=multiplier,summary=totals,by_env=groups,records_digest=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest(),failures=[r for r in records if r["outcome"]!="correct"],early_examples=[r for r in records if r["policy_trace"][-1]["n"]<240])
    if start==191000000 and count==40 and multiplier==4:
        assert (totals["SG054_policy"]["correct"],totals["SG054_policy"]["false_direction"],totals["SG054_policy"]["abstain"],totals["SG054_policy"]["observations"])==(437,54,587,257340)
    return result
if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "holdout"
    start,count=(185000000,6) if mode=="pilot" else (191000000,40)
    result=run(start,count,4)
    (ROOT/("sg054-"+mode+"-full.json")).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(dict(summary=result["summary"],records_digest=result["records_digest"]),indent=2))
