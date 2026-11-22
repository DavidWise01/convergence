"""SG066 frozen late-transition veto, evaluated on fresh synthetic holdout.

Only the observed prefix enters the controller. The only new action is abstain
if the last 50 observations oppose the 240-point decision by >1 standard error.
Original SG057 early-abstention logic and historical source remain immutable.
"""
import hashlib,importlib.util,json,os,pathlib,sys,tempfile,time
import sg062_compat as compat
BASE=pathlib.Path(__file__).resolve().parent
FREEZE="7a7c2be34054a03c1a590e20613bb31fa9ab9d5c"
def hash_record(x):
 return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
class Gate:
 def __init__(self,v):
  self.__v=tuple(v);self.released=0;self.denials=0
 def release(self,n):
  if n<self.released or n>len(self.__v):raise ValueError("invalid monotone release")
  self.released=n
 def read(self,n):
  if n<0 or n>self.released:
   self.denials+=1;raise PermissionError("future observations unavailable")
  return list(self.__v[:n])
def controller(observed,policy,table,g,details=False):
 # It receives only observations already released by Gate.
 for n in (140,180,220):
  g_early=policy(n)
  if g_early is None:continue
  label,slope,se=g.m.decision(g_early,n)
  if label=="unresolved" and table.get(g.feature(n,label,slope,se),{}).get("authorize",False):
   return (n,"unresolved","SG057_early_abstain")
 final_prefix=policy(240)
 label,slope,se=g.m.decision(final_prefix,240)
 if details and label in ("negative","positive"):
  recent,se50=g.m.b.hac(final_prefix[-50:])
  signed=recent if label=="positive" else -recent
  if signed < -se50:
   return (240,"unresolved","last50_opposite_1SE")
 return (240,label,"SG057_final")
def evaluate(stage="holdout"):
 compat.install_aliases();sg=compat.load(59);g=sg.g
 training=list(g.m.samples(215000000,30));table=g.train(training)
 start,count={"pilot":(247000000,5),"holdout":(251000000,20)}[stage]
 names=("SG057_frozen","SG066_veto")
 scores={p:{k:0 for k in ("correct","false_direction","missed_direction","abstain","observations","early","loss")} for p in names}
 by_onset={};by_mix={};ledger=[];denials=0;mutations=0;violations=[];vetoed=[]
 for bi,bef in enumerate((-1,0,1)):
  for ai,aft in enumerate((-1,0,1)):
   for mi,mix in enumerate(sg.MIXES):
    for k in range(count):
     onset=sg.ONSETS[k%4];seed=start+1000000*bi+200000*ai+30000*mi+101*k
     v=sg.gen(seed,bef,aft,mix,onset);gate=Gate(v)
     def prefix(n):
      gate.release(n)
      if n<240:
       try:gate.read(n+1)
       except PermissionError:pass
       else:violations.append(dict(seed=seed,n=n,kind="future_read_allowed"))
      return gate.read(n)
     # Compare baseline and experimental policy using the same fresh monotone Gate.
     base=controller(v,prefix,table,g,False)
     # release stays at 240: create independent Gate to enforce exact checkpoints.
     gate2=Gate(v)
     def prefix2(n):
      gate2.release(n)
      if n<240:
       try:gate2.read(n+1)
       except PermissionError:pass
       else:violations.append(dict(seed=seed,n=n,kind="future_read_allowed"))
      return gate2.read(n)
     novel=controller(v,prefix2,table,g,True)
     denials+=gate.denials+gate2.denials
     truth=("negative","zero","positive")[ai]
     decisions={}
     for p,(n,lab,why) in zip(names,(base,novel)):
      kind=g.m.kind(lab,truth)
      a=dict(n=n,label=lab,kind=kind,reason=why)
      decisions[p]=a;z=scores[p];z[kind]+=1;z["observations"]+=n;z["early"]+=int(n<240);z["loss"]+=.06*n+g.PEN[kind]
      for group,key in ((by_onset,onset),(by_mix,mix)):
       bucket=group.setdefault(str(key),{x:{q:0 for q in ("correct","false_direction","missed_direction","abstain","observations","loss")} for x in names})
       bb=bucket[p];bb[kind]+=1;bb["observations"]+=n;bb["loss"]+=.06*n+g.PEN[kind]
     row=dict(seed=seed,truth=truth,mix=mix,onset=onset,actions=decisions)
     ledger.append(row)
     if novel[2]=="last50_opposite_1SE":vetoed.append(row)
     if novel[0]<240:
      for sign in (-1,1):
       v2=v[:novel[0]]+[v[novel[0]-1]+sign*10*(i+1) for i in range(240-novel[0])]
       def only_prefix(n):return v2[:n]
       if controller(v2,only_prefix,table,g,True)!=novel:violations.append(dict(seed=seed,kind="future_mutation"))
       mutations+=1
 for z in scores.values():z["loss"]=round(z["loss"],2)
 for group in (by_onset,by_mix):
  for entries in group.values():
   for z in entries.values():z["loss"]=round(z["loss"],2)
 result=dict(id="TD-CROSSDOMAIN-SG066",freeze_commit=FREEZE,stage=stage,seed_start=start,n=len(ledger),
  summary=scores,by_onset=by_onset,by_mixture=by_mix,vetoed=vetoed,
  wrong=[r for r in ledger if r["actions"]["SG066_veto"]["kind"] in ("missed_direction","false_direction")],
  gate=dict(denied_future_reads=denials,suffix_modifications=mutations,violations=violations),
  ledger_sha256=hash_record(ledger),ledger=ledger)
 if len(ledger)!=(180 if stage=="pilot" else 720):raise AssertionError("unexpected seed count")
 if violations:raise AssertionError("prefix leak")
 return result
if __name__=="__main__":
 stage=sys.argv[1] if len(sys.argv)>1 else "holdout"
 report=evaluate(stage);folder=pathlib.Path(os.environ.get("SG066_REPORT_DIR",tempfile.gettempdir()))
 folder.mkdir(parents=True,exist_ok=True)
 filename=folder/("sg066-"+stage+"-full.json")
 filename.write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(dict(stage=stage,n=report["n"],summary=report["summary"],by_onset=report["by_onset"],
  vetoes=len(report["vetoed"]),wrong=len(report["wrong"]),gate=report["gate"],ledger_sha256=report["ledger_sha256"],report=str(filename)),indent=2))
