"""SG060: read-only audit of the SG050-SG059 published Python chain.

Run from any checked-out convergence repository:
  python evidence/candidates/2026-11-22-sg060-repro-check.py
This report fails when required public symbols are missing. It never patches history.
Optional --temp-smoke creates a temporary COPY with explicitly labeled compatibility
shims for diagnostic imports; a temp-smoke PASS is NOT a canonical runtime PASS.
"""
import ast,hashlib,importlib.util,json,pathlib,shutil,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parent
FILES={
 50:'sg050-three-direction',51:'sg051-directional-uncertainty',
 52:'sg052-joint-transition',53:'sg053-diodic-replay',
 54:'sg054-hegemonic-policy',55:'sg055-no-choice',
 56:'sg056-loss-sensitivity',57:'sg057-adaptive-observation',
 58:'sg058-unseen-disturbance',59:'sg059-mixture-generalization'}
NAME=lambda n:f'2026-11-22-{FILES[n]}.py'
REQUIRED={51:{50:['three_way']},53:{52:['kind']},54:{52:['kind']},55:{52:['kind']}}
def run(temp_smoke=False):
 report=dict(id='TD-CROSSDOMAIN-SG060',source_checks=[],direct_missing_symbols=[],transitive_risks=[],temporary_imports=[],canonical_clean_checkout_executed=False)
 definitions={}
 for n in FILES:
  f=ROOT/NAME(n)
  if not f.exists():
   report['source_checks'].append(dict(version=n,status='MISSING'));definitions[n]=set();continue
  try:
   txt=f.read_text(encoding='utf8');tree=ast.parse(txt);compile(tree,str(f),'exec')
   defs={a.name for a in tree.body if isinstance(a,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}
   defs|={z.id for a in tree.body if isinstance(a,(ast.Assign,ast.AnnAssign)) for t in (a.targets if isinstance(a,ast.Assign) else [a.target]) for z in ast.walk(t) if isinstance(z,ast.Name)}
   definitions[n]=defs
   report['source_checks'].append(dict(version=n,status='SYNTAX_PASS',source_sha256=hashlib.sha256(txt.encode()).hexdigest()))
  except Exception as exc:
   definitions[n]=set();report['source_checks'].append(dict(version=n,status='SYNTAX_FAIL',error=str(exc)))
 for consumer,providers in REQUIRED.items():
  for provider,symbols in providers.items():
   for symbol in symbols:
    if symbol not in definitions[provider]:
     report['direct_missing_symbols'].append(dict(consumer=consumer,provider=provider,symbol=symbol))
 if any(x['symbol']=='kind' for x in report['direct_missing_symbols']):
  report['transitive_risks']=['SG057 calls SG055.kind→SG052.kind','SG058 and SG059 import SG057 and inherit same scoring dependency']
 if temp_smoke:
  with tempfile.TemporaryDirectory(prefix='sg060-temp-') as td:
   tmp=pathlib.Path(td)/'workspace'/'candidates';tmp.mkdir(parents=True)
   for n in FILES:
    if (ROOT/NAME(n)).exists():shutil.copy2(ROOT/NAME(n),tmp/NAME(n))
   for n,suffix in ((50,"\ndef three_way(lo,hi):return labels(lo,hi)[1]\n"),(52,"\nkind=outcome\n")):
    p=tmp/NAME(n)
    if p.exists():p.write_text(p.read_text()+suffix)
   for n in FILES:
    # Temporary legacy folder copies support earlier local-layout imports too.
    sibling=tmp.parent/f'sg{n:03d}';sibling.mkdir(exist_ok=True)
    source=tmp/NAME(n)
    if source.exists():shutil.copy2(source,sibling/f'sg{n:03d}.py')
   for n in FILES:
    p=tmp/NAME(n)
    if not p.exists():continue
    code="import importlib.util,sys;s=importlib.util.spec_from_file_location('audit',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)"
    q=subprocess.run([sys.executable,'-c',code,str(p)],capture_output=True,text=True,timeout=20)
    report['temporary_imports'].append(dict(version=n,status='PASS' if q.returncode==0 else 'FAIL',stderr=q.stderr[-700:]))
 report['summary']=dict(syntax_pass=sum(x['status']=='SYNTAX_PASS' for x in report['source_checks']),missing_direct=len(report['direct_missing_symbols']),temporary_imports_pass=sum(x['status']=='PASS' for x in report['temporary_imports']))
 return report
if __name__=='__main__':
 obj=run('--temp-smoke' in sys.argv)
 print(json.dumps(obj,indent=2))
 sys.exit(int(obj['summary']['syntax_pass']!=10 or obj['summary']['missing_direct']>0 or any(x['status']=='FAIL' for x in obj['temporary_imports'])))
