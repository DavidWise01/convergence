"""SG065: observed-prefix runtime gate and legacy digest normalization.
Read-only GitHub Actions verification; never mutates SG050-SG059 sources.
"""
import hashlib,json,os,pathlib,tempfile,sys,time
import sg062_compat as compat
BASE=pathlib.Path(__file__).resolve().parent
def digest(o,compact=False):
 opts={"sort_keys":True}
 if compact:opts["separators"]=(",",":")
 return hashlib.sha256(json.dumps(o,**opts).encode()).hexdigest()
def readrecord(stem):
 return json.loads((BASE/("2026-11-22-"+stem+".json")).read_text())
class ObservationGate:
 def __init__(self,data):
  self._data=tuple(data);self.released=0;self.denied=0
 def release(self,n):
  if n<self.released or n>len(self._data):raise ValueError("invalid release")
  self.released=n
 def read(self,n):
  if n>self.released or n<0:
   self.denied+=1;raise PermissionError("cannot read unreleased future")
  return list(self._data[:n])
def main():
 start=time.monotonic();compat.install_aliases()
 sg54=compat.load(54);sg59=compat.load(59);sg57=sg59.g
 row054=[];gate_checks=0;violations=[];deny_tests=0
 for bi,before in enumerate(sg54.b.SIGNS):
  for ai,after in enumerate(sg54.b.SIGNS):
   for ei,env in enumerate(sg54.b.NOISE):
    for k in range(40):
     onset=(100,120,140)[k%3];seed=191000000+1000000*bi+200000*ai+30000*ei+101*k
     data=sg54.b.gen(seed,before,after,env,onset);gate=ObservationGate(data)
     trace=[]
     for n in sg54.CHECKPOINTS:
      gate.release(n)
      if n<240:
       try:gate.read(n+1)
       except PermissionError:deny_tests+=1
       else:violations.append(dict(seed=seed,n=n,kind="future_read_allowed"))
      z=sg54.Z*4 if n<240 else sg54.Z
      label,s,se=sg54.classify(gate.read(n),z)
      action="commit_"+label if label!="unresolved" else ("observe" if n<240 else "abstain")
      trace.append(dict(n=n,action=action,label=label,slope=s,se=se,threshold=z))
      if action!="observe":break
     native=sg54.select(data,4)
     normalized=[dict(step,threshold=step["multiplier"]) for step in native]
     for item in normalized:item.pop("multiplier",None)
     if normalized!=trace:violations.append(dict(seed=seed,kind="SG054_stream_replay"))
     final=trace[-1];truth=("negative","zero","positive")[ai]
     full=sg54.classify(data,sg54.Z)[0]
     row054.append(dict(seed=seed,env=env,before=before,after=after,onset=onset,truth=truth,
        baseline=dict(n=240,action="commit_"+full if full!="unresolved" else "abstain",label=full),
        policy_trace=trace,outcome=sg54.b.kind(final["label"],truth)))
     gate_checks+=1
 archive054=readrecord("sg054-hegemonic-policy")["holdout"]["full_records_digest"]
 actual054=digest(row054)
 # Both sources generate the same 720 rows; compare frozen scores and legacy hashes.
 old59=readrecord("sg059-mixture-generalization")["holdout"]["ledger_sha256"]
 native59=sg59.run("holdout")
 rows59=native59["ledger"]
 normalized59=digest(rows59,compact=True)
 table=sg57.train(list(sg57.m.samples(215000000,30)))
 sg059_checked=0;early_mutations=0
 for bi,before in enumerate((-1,0,1)):
  for ai,after in enumerate((-1,0,1)):
   for mi,mix in enumerate(sg59.MIXES):
    for k in range(20):
     onset=sg59.ONSETS[k%4];seed=241000000+1000000*bi+200000*ai+30000*mi+101*k
     data=sg59.gen(seed,before,after,mix,onset)
     gate=ObservationGate(data)
     outcome=None
     for n in (140,180,220,240):
      gate.release(n)
      if n<240:
       try:gate.read(n+1)
       except PermissionError:deny_tests+=1
       else:violations.append(dict(seed=seed,n=n,kind="future_read_allowed"))
      label,s,se=sg57.m.decision(gate.read(n),n)
      if n<240 and label=="unresolved" and table.get(sg57.feature(n,label,s,se),{}).get("authorize",False):
       outcome=(n,"unresolved");break
      if n==240:outcome=(240,label)
     replay=sg59.online(data,table)
     if replay!=outcome:violations.append(dict(seed=seed,kind="SG059_stream_replay"))
     if outcome[0]<240:
      for delta in (-9,9):
       perturbed=data[:outcome[0]]+[data[outcome[0]-1]+delta*(i+1) for i in range(240-outcome[0])]
       if sg59.online(perturbed,table)!=outcome:violations.append(dict(seed=seed,kind="suffix_influence"))
       early_mutations+=1
     sg059_checked+=1
 report=dict(id="TD-CROSSDOMAIN-SG065",github_checkout="exact published SG050-SG059 + additive SG062 loader",
  frozen={"SG054":archive054,"SG059":old59},
  normalized={"SG054":actual054,"SG059":normalized59},
  original_published={"SG059":native59["ledger_sha256"]},
  interpretation={"SG054":"published multiplier key renamed to historical threshold key; numeric fields preserved",
    "SG059":"same 720 rows serialized with compact separators rather than default spacing"},
  counts=dict(sg054_streams=gate_checks,sg059_streams=sg059_checked,forbidden_reads_denied=deny_tests,
    early_suffix_mutations=early_mutations,violations=len(violations)),
  failures=violations[:30],duration_seconds=round(time.monotonic()-start,2))
 report["status"]="PASS" if not violations and actual054==archive054 and normalized59==old59 else "FAIL"
 return report
if __name__=="__main__":
 r=main();folder=pathlib.Path(os.environ.get("SG065_REPORT_DIR",tempfile.gettempdir()))
 folder.mkdir(parents=True,exist_ok=True);target=folder/"sg065-prefix-audit.json"
 target.write_text(json.dumps(r,indent=2)+"\n")
 print(json.dumps(dict(status=r["status"],counts=r["counts"],digests=r["normalized"],
  matches={n:r["normalized"][n]==r["frozen"][n] for n in r["frozen"]},failures=r["failures"],report=str(target)),indent=2))
 sys.exit(0 if r["status"]=="PASS" else 1)
