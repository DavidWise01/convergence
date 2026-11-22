"""SG062 append-only compatibility shim and reproducibility gate.

Historical SG050-SG059 files are NEVER modified. This runner intercepts only
importlib.util.spec_from_file_location while importing frozen source modules.
It supplies these API aliases after the original module executes:
  SG050.three_way(lo,hi) -> SG050.labels(lo,hi)[1]
  SG052.kind(pred,truth) -> SG052.outcome(pred,truth)
That is sufficient to fix known symbol mismatches, not proof of numeric identity.

Usage from a checked-out GitHub repository:
  python evidence/candidates/sg062_compat.py --smoke
  python evidence/candidates/sg062_compat.py --full
All reports are written outside the source tree to SG062_REPORT_DIR or /tmp.
A nonzero exit indicates any failed check, including mismatched historical metrics.
"""
import argparse,hashlib,importlib.util,json,os,pathlib,sys,tempfile,traceback,time
BASE=pathlib.Path(__file__).resolve().parent
SOURCES={
 50:"sg050-three-direction",51:"sg051-directional-uncertainty",
 52:"sg052-joint-transition",53:"sg053-diodic-replay",
 54:"sg054-hegemonic-policy",55:"sg055-no-choice",
 56:"sg056-loss-sensitivity",57:"sg057-adaptive-observation",
 58:"sg058-unseen-disturbance",59:"sg059-mixture-generalization"}
def source(n):return BASE/("2026-11-22-"+SOURCES[n]+".py")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def install_aliases():
    original=importlib.util.spec_from_file_location
    class AliasLoader:
        def __init__(self,wrapped,n):self.wrapped=wrapped;self.n=n
        def create_module(self,spec):
            if hasattr(self.wrapped,"create_module"):return self.wrapped.create_module(spec)
            return None
        def exec_module(self,module):
            self.wrapped.exec_module(module)
            if self.n==50 and not hasattr(module,"three_way"):
                if not hasattr(module,"labels"):raise RuntimeError("SG050 lacks labels")
                module.three_way=lambda lo,hi:module.labels(lo,hi)[1]
            if self.n==52 and not hasattr(module,"kind"):
                if not hasattr(module,"outcome"):raise RuntimeError("SG052 lacks outcome")
                module.kind=module.outcome
            if self.n==56 and not hasattr(module,"P"):
                module.P=("SG052_wait","SG054_threshold4","SG055_ranked")
    def hooked(name,location,*a,**kw):
        spec=original(name,location,*a,**kw)
        if spec is not None and spec.loader is not None:
            filename=pathlib.Path(str(location)).name
            for n in (50,52,56):
                if filename==source(n).name:
                    spec.loader=AliasLoader(spec.loader,n)
                    break
        return spec
    importlib.util.spec_from_file_location=hooked
def load(n):
    spec=importlib.util.spec_from_file_location("sg062_audit_"+str(n),source(n))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def metrics(payload,keys):
    for key in keys:payload=payload[key]
    return payload
def run(full=False):
    started=time.time()
    out=dict(id="TD-CROSSDOMAIN-SG062",source="exact published repository checkout",mode="full" if full else "smoke",
             historical_source_sha256={},checks=[],aliases=["SG050.three_way via labels()[1]","SG052.kind via outcome()","SG056.P restored as frozen three-policy order"],
             history_changed=False)
    for n in SOURCES:
        p=source(n)
        if not p.exists():out["checks"].append(dict(name=f"SG{n:03d} source",status="FAIL",error="file missing"))
        else:
            compile(p.read_text(encoding="utf8"),str(p),"exec")
            out["historical_source_sha256"][f"SG{n:03d}"]=sha(p)
    install_aliases()
    modules={}
    for n in SOURCES:
        try:
            modules[n]=load(n)
            out["checks"].append(dict(name=f"SG{n:03d} import",status="PASS"))
        except Exception as exc:
            out["checks"].append(dict(name=f"SG{n:03d} import",status="FAIL",error=repr(exc),trace=traceback.format_exc()[-700:]))
    def check(name,fn,expected=None):
        try:
            got=fn()
            ok=(expected is None or got==expected)
            out["checks"].append(dict(name=name,status="PASS" if ok else "FAIL",actual=got,expected=expected))
        except Exception as exc:
            out["checks"].append(dict(name=name,status="FAIL",error=repr(exc),trace=traceback.format_exc()[-1000:]))
    if 50 in modules:check("SG050 quick decision",lambda:modules[50].three_way(-.01,-.001),"negative")
    if 52 in modules:check("SG052 compatibility outcome",lambda:modules[52].kind("positive","negative"),"false_direction")
    if 51 in modules:check("SG051 quick dataset",lambda:len(modules[51].dataset(145000000,1)),27)
    if 52 in modules:check("SG052 quick 27-stream generation",lambda:len(modules[52].rows(167000000,1)),27)
    if 53 in modules:check("SG053 causal 27-stream quick replay",lambda:modules[53].run(179000000,1)[0]["causal_violations"],0)
    if 54 in modules:check("SG054 27-stream action simulation",lambda:modules[54].run(191000000,1)["n"],27)
    if 55 in modules:check("SG055 27-stream sample import",lambda:len(list(modules[55].samples(203000000,1))),27)
    if 57 in modules:check("SG057 trained prefix table",lambda:sorted(k for k,v in modules[57].train(list(modules[55].samples(215000000,30))).items() if v["authorize"]),
        ["220:unresolved:lt1:low","220:unresolved:lt2:low"])
    if 58 in modules:check("SG058 new mechanism sampler",lambda:len(modules[58].dataset(233000000,1)),45)
    if 59 in modules:check("SG059 mixed mechanism sampler",lambda:len(modules[59].produce(241000000,1)),36)
    # Exhaustive full benchmark. Call public functions unchanged and catch frozen asserts.
    if full:
        tests=[
          (50,"SG050 full holdout",lambda:metrics(modules[50].run(),["summary","SG050_three_way","correct"]),912),
          (51,"SG051 full holdout",lambda:metrics(modules[51].run(),["holdout","SG051","summary","correct"]),900),
          (52,"SG052 full holdout",lambda:metrics(modules[52].run("holdout"),["summary","SG052_trailing100","correct"]),458),
          (53,"SG053 full holdout",lambda:modules[53].run(179000000,40)[0]["leaky_comparator_detected"],7902),
          (54,"SG054 full holdout",lambda:modules[54].run(191000000,40,4)["summary"]["SG054_policy"]["loss"],34286.4),
          (55,"SG055 full holdout",lambda:modules[55].run()["holdout"]["SG055_ranked"]["loss"],33667.2),
          (56,"SG056 full holdout",lambda:modules[56].run()["wins"],{"SG052_wait":24,"SG054_threshold4":0,"SG055_ranked":3}),
          (57,"SG057 full holdout",lambda:modules[57].run("holdout")["summary"]["early_abstain"]["loss"],29944.8),
          (58,"SG058 full holdout",lambda:modules[58].run("holdout")["scores"]["early_abstain"]["loss"],28509.6),
          (59,"SG059 full holdout",lambda:modules[59].run("holdout")["summary"]["early_abstain"]["loss"],29793.6)]
        for n,name,fn,expected in tests:
            if n in modules:check(name,fn,expected)
    out["duration_seconds"]=round(time.time()-started,2)
    out["passed"]=sum(x["status"]=="PASS" for x in out["checks"])
    out["failed"]=sum(x["status"]=="FAIL" for x in out["checks"])
    out["status"]="PASS" if out["failed"]==0 else "FAIL_WITH_COUNTEREXAMPLES"
    out["canonical_without_shim_passed"]=False
    return out
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--smoke",action="store_true")
    parser.add_argument("--full",action="store_true")
    options=parser.parse_args()
    report=run(options.full)
    folder=pathlib.Path(os.environ.get("SG062_REPORT_DIR",tempfile.gettempdir()))
    folder.mkdir(parents=True,exist_ok=True)
    target=folder/("sg062-"+("full" if options.full else "smoke")+".json")
    target.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(dict(status=report["status"],passed=report["passed"],failed=report["failed"],report=str(target),failures=[x for x in report["checks"] if x["status"]=="FAIL"]),indent=2))
    sys.exit(0 if report["failed"]==0 else 1)
