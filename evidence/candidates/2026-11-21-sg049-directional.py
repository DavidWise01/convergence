"""SG049 frozen positive-direction hypothesis classification, Python3 stdlib.
Run beside the SG048/SG047/SG043 sibling repository sources.
python 2026-11-21-sg049-directional.py holdout
"""
import json,hashlib,sys,pathlib,importlib.util
ROOT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('sg048',ROOT/'2026-11-21-sg048-warning-only.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
Z=old.GLOBAL_Z
def directional(s,se):
 lo=s-Z*se;hi=s+Z*se
 if lo>0:return 'confirmed','positive',lo,hi
 if hi<0:return 'rejected','negative',lo,hi
 if lo>-.0032 and hi<.0032:return 'rejected','negligible',lo,hi
 return 'unresolved','ambiguous',lo,hi
def audit(rows):
 sums={p:dict(correct=0,FP=0,FN=0,abstain=0,observations=len(rows)*240,loss=0.) for p in ('sg048','sg049')}
 groups={};failures={p:[] for p in sums};transitions=[]
 for r in rows:
  full,_,alarm,_,cut=old.choose(r,'sg048')
  prior=full[0]
  new,cause,lo,hi=directional(r['full_s'],r['full_se'])
  if alarm and new!='unresolved' and cut[0] not in ('unresolved',new):
   new='unresolved';cause='boundary_conflict'
  outcomes={}
  for policy,label in (('sg048',prior),('sg049',new)):
   category='abstain' if label=='unresolved' else 'correct' if (label=='confirmed')==r['drift'] else 'FP' if label=='confirmed' else 'FN'
   outcomes[policy]=category
   item=sums[policy];item[category]+=1;item['loss']+=14.4+{'correct':0,'FP':150,'FN':90,'abstain':18}[category]
   detail=groups.setdefault(r['scenario'],{p:dict(correct=0,FP=0,FN=0,abstain=0) for p in sums})[policy]
   detail[category]+=1
   if category in ('FP','FN'):
    failures[policy].append(dict(seed=r['seed'],scenario=r['scenario'],truth=r['drift'],slope=r['full_s'],se=r['full_se'],interval=[lo,hi],label=label,cause=cause,kind=category))
  if prior!=new:
   transitions.append(dict(seed=r['seed'],scenario=r['scenario'],truth=r['drift'],prior=prior,new=new,old_outcome=outcomes['sg048'],new_outcome=outcomes['sg049'],cause=cause,interval=[lo,hi]))
 for p in sums:sums[p]['loss']=round(sums[p]['loss'],2)
 return dict(summary=sums,groups=groups,failures=failures,transitions=transitions,rows_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest())
def run(stage='holdout'):
 start,count={'pilot':(125000000,10),'holdout':(129000000,40)}[stage]
 rows=old.sg.dataset(start,count)
 result=dict(id='TD-CROSSDOMAIN-SG049',freeze_commit='cdc8ad8451d71384a27023882c70687c99483de0',stage=stage,seed_start=start,n=len(rows),z=Z,**audit(rows))
 if stage=='holdout':
  assert (result['summary']['sg049']['correct'],result['summary']['sg049']['FP'],result['summary']['sg049']['FN'],result['summary']['sg049']['abstain'],result['summary']['sg049']['loss'])==(587,24,1,108,16002.)
  assert len(result['transitions'])==20
 return result
if __name__=='__main__':
 stage=sys.argv[1] if len(sys.argv)>1 else 'holdout'
 obj=run(stage)
 (ROOT/('sg049-'+stage+'-full.json')).write_text(json.dumps(obj,indent=2)+'\n')
 print(json.dumps({'stage':stage,'summary':obj['summary'],'changes':len(obj['transitions']),'wrong_seeds':[x['seed'] for x in obj['failures']['sg049']]},indent=2))
