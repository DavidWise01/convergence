"""SG064 canonical source and complete ledger SHA256 reconciliation.

Runs on exact GitHub checkout using additive SG062 compatibility loader.
Reads immutable evidence JSON from repository; does not edit source/evidence.
Usage: python evidence/candidates/sg064_provenance.py
Writes audit JSON to SG064_REPORT_DIR (default /tmp), exits nonzero on mismatch.
"""
import hashlib,json,os,pathlib,sys,tempfile,time,traceback
import sg062_compat as compat
BASE=pathlib.Path(__file__).resolve().parent
def record(stem):return json.loads((BASE/("2026-11-22-"+stem+".json")).read_text(encoding="utf-8"))
def audit():
 started=time.time()
 parent=record("sg063-canonical-replay")
 names={50:"sg050-three-direction",51:"sg051-directional-uncertainty",52:"sg052-joint-transition",
 53:"sg053-diodic-replay",54:"sg054-hegemonic-policy",55:"sg055-no-choice",56:"sg056-loss-sensitivity",
 57:"sg057-adaptive-observation",58:"sg058-unseen-disturbance",59:"sg059-mixture-generalization"}
 expected={}
 for n,name in names.items():
  archive=record(name);h=archive["holdout"]
  if n in (50,51,52):expected[n]={"rows_sha256":h["rows_sha256"]}
  elif n==53:expected[n]={"all_rows_sha256":h["all_rows_sha256"],"ledger_roots_sha256":h["ledger_roots_sha256"]}
  elif n==54:expected[n]={"full_records_digest":h["full_records_digest"]}
  elif n==55:expected[n]={"records_sha256":h["records_sha256"]}
  elif n==56:expected[n]={"stream_ledger_sha256":h["stream_ledger_sha256"],"grid_sha256":h["grid_sha256"]}
  else:expected[n]={"ledger_sha256":h["ledger_sha256"]}
 out=dict(id="TD-CROSSDOMAIN-SG064",checkout_source="canonical GitHub repository",source_checks=[],digest_checks=[],
  expected_records={str(n):f"2026-11-22-{name}.json" for n,name in names.items()},
  hash_function="sha256, exact historic published computation; no reformatting",historical_source_files_modified=False)
 for n in names:
  p=compat.source(n)
  observed=compat.sha(p)
  wanted=parent["source_sha256"]["SG"+str(n).zfill(3)]
  out["source_checks"].append(dict(id="SG"+str(n).zfill(3),file=p.name,expected=wanted,actual=observed,status="PASS" if observed==wanted else "FAIL"))
 compat.install_aliases()
 for n in names:
  try:
   m=compat.load(n)
   if n==50:observed={"rows_sha256":m.run()["rows_sha256"]}
   elif n==51:observed={"rows_sha256":m.run()["holdout"]["rows_sha256"]}
   elif n==52:observed={"rows_sha256":m.run("holdout")["rows_sha256"]}
   elif n==53:
    summary,_=m.run(179000000,40)
    observed={"all_rows_sha256":summary["all_rows_sha256"],"ledger_roots_sha256":summary["ledger_roots_sha256"]}
   elif n==54:observed={"full_records_digest":m.run(191000000,40,4)["records_digest"]}
   elif n==55:observed={"records_sha256":m.run()["records_sha256"]}
   elif n==56:observed=m.run()["hashes"]
   elif n==57:observed={"ledger_sha256":m.run("holdout")["ledger_digest"]}
   elif n==58:observed={"ledger_sha256":m.run("holdout")["ledger_sha256"]}
   else:observed={"ledger_sha256":m.run("holdout")["ledger_sha256"]}
   for key,wanted in expected[n].items():
    actual=observed.get(key)
    out["digest_checks"].append(dict(id="SG"+str(n).zfill(3),field=key,expected=wanted,actual=actual,status="PASS" if actual==wanted else "FAIL"))
  except Exception as exc:
   for key,wanted in expected[n].items():
    out["digest_checks"].append(dict(id="SG"+str(n).zfill(3),field=key,expected=wanted,status="ERROR",error=repr(exc),trace=traceback.format_exc()[-1500:]))
 out["source_pass"]=sum(c["status"]=="PASS" for c in out["source_checks"])
 out["digest_pass"]=sum(c["status"]=="PASS" for c in out["digest_checks"])
 out["source_total"]=len(out["source_checks"]);out["digest_total"]=len(out["digest_checks"])
 out["status"]="PASS" if out["source_pass"]==out["source_total"] and out["digest_pass"]==out["digest_total"] else "FAILED_WITH_PRESERVED_COUNTEREXAMPLES"
 out["duration_seconds"]=round(time.time()-started,2)
 return out
if __name__=="__main__":
 result=audit()
 folder=pathlib.Path(os.environ.get("SG064_REPORT_DIR",tempfile.gettempdir()));folder.mkdir(parents=True,exist_ok=True)
 destination=folder/"sg064-provenance.json"
 destination.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(dict(status=result["status"],source_pass=result["source_pass"],source_total=result["source_total"],
  digest_pass=result["digest_pass"],digest_total=result["digest_total"],failures=[x for x in result["source_checks"]+result["digest_checks"] if x["status"]!="PASS"],report=str(destination)),indent=2))
 sys.exit(0 if result["status"]=="PASS" else 1)
