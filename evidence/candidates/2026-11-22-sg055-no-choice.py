"""SG055: deterministic empirical loss ranking across checkpoint actions.
Python 3 stdlib. Place beside SG052 in convergence/evidence/candidates/.
Run: python3 2026-11-22-sg055-no-choice.py
Training, pilot and holdout use disjoint seed ranges.
"""
import json, math, hashlib, pathlib, importlib.util
ROOT=pathlib.Path(__file__).resolve().parent
sg=ROOT/"2026-11-22-sg052-joint-transition.py"
spec=importlib.util.spec_from_file_location('sg052',sg)
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
CP=(100,140,180,220,240);Z=4.327111573414373
PEN={'correct':0,'missed_direction':90,'false_direction':150,'abstain':18}
TRUTH=('negative','zero','positive')
def kind(label,truth):return b.kind(label,truth)
def decision(v,n,z=Z):
 s,se=b.hac(v[max(0,n-100):n]);return b.label(s,se,z),s,se
def feature(n,lab,s,se):
 t=abs(s)/max(se,1e-12)
 return f'{n}:{lab}:{"hi" if t>=5 else "mid" if t>=3 else "low"}'
def samples(start,count):
 for bi,bef in enumerate(b.SIGNS):
  for ai,aft in enumerate(b.SIGNS):
   for ei,env in enumerate(b.NOISE):
    for k in range(count):
     seed=start+1000000*bi+200000*ai+30000*ei+101*k
     onset=(100,120,140)[k%3];v=b.gen(seed,bef,aft,env,onset)
     pred={n:decision(v,n) for n in CP}
     yield dict(seed=seed,truth=TRUTH[ai],env=env,before=bef,after=aft,onset=onset,pred=pred)
def train(rows,min_group=20,buffer=0):
 table={}
 for r in rows:
  end=r['pred'][240][0];waitloss=14.4+PEN[kind(end,r['truth'])]
  for n in CP[:-1]:
   label,s,se=r['pred'][n]
   if label=='unresolved':continue
   key=feature(n,label,s,se)
   g=table.setdefault(key,dict(count=0,commit_loss=0.,wait_loss=0.,commit_errors=0))
   g['count']+=1;g['commit_loss']+=.06*n+PEN[kind(label,r['truth'])]
   g['wait_loss']+=waitloss;g['commit_errors']+=int(kind(label,r['truth'])!='correct')
 for g in table.values():
  g['mean_commit_loss']=g['commit_loss']/g['count']
  g['mean_wait_loss']=g['wait_loss']/g['count']
  risk=(g['commit_errors']+1)/(g['count']+2)
  g['authorize']=g['count']>=min_group and g['mean_commit_loss']+buffer<g['mean_wait_loss'] and risk*90<g['mean_wait_loss']
 return table
def policy(r,table):
 for n in CP[:-1]:
  label,s,se=r['pred'][n]
  if label=='unresolved':continue
  key=feature(n,label,s,se)
  if table.get(key,{}).get('authorize',False):return n,label,key
 return 240,r['pred'][240][0],'deadline'
def summary(rows,table):
 out={p:dict(correct=0,missed_direction=0,false_direction=0,abstain=0,loss=0.,observations=0,early=0) for p in ('SG052_wait','SG054_threshold4','SG055_ranked')}
 records=[]
 for r in rows:
  baseline=(240,r['pred'][240][0],'deadline')
  old=None
  for n in CP[:-1]:
   lab,s,se=r['pred'][n]
   early=b.label(s,se,Z*4)
   if early!='unresolved':old=(n,early,'SG054');break
  sg54=old if old is not None else baseline
  choices={'SG052_wait':baseline,'SG054_threshold4':sg54,'SG055_ranked':policy(r,table)}
  entry=dict(seed=r['seed'],truth=r['truth'],env=r['env'],actions={})
  for p,(n,label,key) in choices.items():
   k=kind(label,r['truth']);o=out[p];o[k]+=1;o['loss']+=.06*n+PEN[k];o['observations']+=n;o['early']+=int(n<240)
   entry['actions'][p]=dict(n=n,label=label,kind=k,key=key)
  records.append(entry)
 for v in out.values():v['loss']=round(v['loss'],2)
 return out,records
def run():
 cal=list(samples(197000000,20));table=train(cal)
 pil=list(samples(199000000,8));pilot,_=summary(pil,table)
 hold=list(samples(203000000,40));scores,records=summary(hold,table)
 result=dict(id='TD-CROSSDOMAIN-SG055',freeze_commit='29ab748a9b80331c6a846586e4bd7de5a257f811',training_n=len(cal),table=table,pilot=pilot,holdout=scores,
  wrong_cases=[r for r in records if r['actions']['SG055_ranked']['kind'] in ('missed_direction','false_direction')],
  early_cases=[r for r in records if r['actions']['SG055_ranked']['n']<240],records_sha256=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest())
 assert scores['SG055_ranked']==dict(correct=460,missed_direction=4,false_direction=52,abstain=564,loss=33667.2,observations=255920,early=164)
 return result
if __name__=='__main__':
 print(json.dumps(run(),indent=2))
