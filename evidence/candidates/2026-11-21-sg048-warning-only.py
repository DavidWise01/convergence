"""SG048 frozen warning-only change-point challenge.
Python 3 standard library. Put beside the SG047 and SG043 source files in
evidence/candidates/. No later observations used beyond the full240 retrospective
window. Recreates frozen SG048 decisions and detailed individual failures.
"""
import json,math,pathlib,hashlib,importlib.util
ROOT=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('sg047',ROOT/'2026-11-21-sg047-change-location.py')
sg=importlib.util.module_from_spec(s);s.loader.exec_module(s)
SCENARIOS=sg.SCENARIOS
THRESHOLD=.5186019321426611
GLOBAL_Z=2.291027529910169
LOCAL_Z=5.346129511387088
SG046_FULL_Z=2.453084988962486
SG046_LOCAL_Z=5.9182295530936235
def interval(s,se,z):
 lo=s-z*se;hi=s+z*se
 return ('confirmed' if lo>0 or hi<0 else 'rejected' if lo>-.0032 and hi<.0032 else 'unresolved'),lo,hi
def choose(r,policy):
 alarm=r['score']>THRESHOLD
 full=interval(r['full_s'],r['full_se'],GLOBAL_Z)
 cut=interval(r['cut_s'],r['cut_se'],LOCAL_Z)
 if policy=='pooled':return full,'full_retained',alarm,full,cut
 if policy=='sg046':
  if r['old_flag']:
   v=interval(r['local120_s'],r['local120_se'],SG046_LOCAL_Z)
   return v,'local120',alarm,v,cut
  v=interval(r['full_s'],r['full_se'],SG046_FULL_Z)
  return v,'whole240',alarm,v,cut
 if policy=='sg047':return (cut if alarm else full),('cut' if alarm else 'whole240'),alarm,full,cut
 label=full[0]
 if alarm and label!='unresolved' and cut[0] not in ('unresolved',label):
  return ('unresolved',full[1],full[2]),'contradiction',alarm,full,cut
 return full,'full_retained',alarm,full,cut
def evaluate(rows,policy):
 tally=dict(correct=0,FP=0,FN=0,abstain=0,loss=0.,observations=len(rows)*240)
 coverage={};failures=[];challenged=[];alarms=[]
 for r in rows:
  v,reason,alarm,full,cut=choose(r,policy)
  label,lo,hi=v
  ok=lo<=r['truth']<=hi
  kind='abstain' if label=='unresolved' else 'correct' if (label=='confirmed')==r['drift'] else 'FP' if label=='confirmed' else 'FN'
  tally[kind]+=1;tally['loss']+=14.4+{'correct':0,'FP':150,'FN':90,'abstain':18}[kind]
  for g in ('ALL',r['scenario']):
   stat=coverage.setdefault(g,dict(n=0,covered=0,correct=0,wrong=0,unresolved=0))
   stat['n']+=1;stat['covered']+=int(ok)
   stat['correct']+=int(kind=='correct');stat['wrong']+=int(kind in ('FP','FN'));stat['unresolved']+=int(kind=='abstain')
  if kind in ('FP','FN'):failures.append(dict(seed=r['seed'],scenario=r['scenario'],true_slope=r['truth'],decision=label,kind=kind,cp=r['cp'],alarm=alarm,full_s=r['full_s'],full_se=r['full_se'],cut_s=r['cut_s'],cut_se=r['cut_se']))
  if alarm:alarms.append(dict(seed=r['seed'],scenario=r['scenario'],cp=r['cp'],known_onset=r['known_onset']))
  if reason=='contradiction':challenged.append(dict(seed=r['seed'],scenario=r['scenario'],truth=r['drift'],full_label=full[0],cut_label=cut[0],full_interval=full[1:],cut_interval=cut[1:]))
 tally['loss']=round(tally['loss'],2)
 return dict(summary=tally,coverage=coverage,failures=failures,challenged=challenged,alarms=alarms)
def run(start=123000000,count=40):
 rows=sg.dataset(start,count)
 policies={p:evaluate(rows,p) for p in ('pooled','sg046','sg047','sg048')}
 result=dict(id='TD-CROSSDOMAIN-SG048',freeze_commit='08e2667bf076ca7d9eb2e4cb545a705562373d69',
  seed_start=start,streams=len(rows),policies=policies,
  rows_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest())
 if start==123000000 and count==40:
  assert (policies['sg048']['summary']['correct'],len(policies['sg048']['failures']),policies['sg048']['summary']['abstain'],policies['sg048']['summary']['loss'])==(581,39,100,18018.)
  assert len(policies['sg048']['challenged'])==1
 return result
if __name__=='__main__':
 r=run()
 target=ROOT/'sg048-full-holdout.json'
 target.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({p:dict(v['summary'],coverage=v['coverage']['ALL']['covered'],challenges=len(v['challenged'])) for p,v in r['policies'].items()},indent=2))
