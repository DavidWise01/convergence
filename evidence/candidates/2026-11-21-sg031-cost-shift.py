"""SG-031: preregistered cost-shift and unfamiliar-noise holdout. Stdlib only."""
import random,statistics,json,hashlib
POLICIES=('fixed160','fixed240','adaptive','cost-aware')
SCENARIOS=(('baseline',.72,.005,False),('weak_drift',.72,.0027,False),('high_correlation',.93,.005,False),('heavy_tailed',.72,.005,True))
COSTS={'original':{'sample':.06,'FP':150,'FN':90,'abstain':18},'high_false_confirm':{'sample':.06,'FP':600,'FN':90,'abstain':18},'cheap_observe':{'sample':.01,'FP':150,'FN':90,'abstain':18},'expensive_observe':{'sample':.25,'FP':150,'FN':90,'abstain':18}}
def stream(seed,drift,rho,slope,heavy):
 r=random.Random(seed);z=0.;out=[]
 for t in range(480):
  z=rho*z+r.uniform(-.23,.23)
  impulse=7 if t in (42,173) else -7 if t in (87,211) else 0
  if heavy and r.random()<.03:impulse+=r.choice((-2.5,2.5))
  out.append((slope*t if drift else 0.)+3*(t>=120)+z+impulse)
 return out
def classify(v):
 bins=[statistics.median(v[10*i:10*(i+1)]) for i in range(len(v)//10)]
 slope=statistics.median((bins[j]-bins[i])/(10*(j-i)) for i in range(len(bins)) for j in range(i+1,len(bins)))
 return ('confirmed' if abs(slope)>.0032 else 'rejected' if abs(slope)<.0018 else 'unresolved'),slope
def decide(v,policy):
 snapshots=[(n,*classify(v[:n])) for n in range(80,241,40)]
 if policy.startswith('fixed'):
  n=int(policy[5:]);return n,next(l for t,l,s in snapshots if t==n)
 previous=None
 for n,label,slope in snapshots:
  if policy=='adaptive' and label!='unresolved' and label==previous:return n,label
  if policy=='cost-aware' and n>=120 and label!='unresolved' and label==previous and (abs(slope)>.0036 or abs(slope)<.0014):return n,label
  previous=label
 return 240,'unresolved'
def outcome(label,truth):
 if label=='unresolved':return 'abstain'
 if (label=='confirmed')==truth:return 'correct'
 return 'FP' if label=='confirmed' else 'FN'
def run():
 entries=[];checks=0
 for i,(name,rho,slope,heavy) in enumerate(SCENARIOS):
  for truth in (False,True):
   for k in range(40):
    seed=7300000+100000*i+10000*int(truth)+101*k
    v=stream(seed,truth,rho,slope,heavy)[240:]
    for policy in POLICIES:
     n,label=decide(v,policy);oc=outcome(label,truth)
     assert n in (80,120,160,200,240);checks+=1
     assert oc in ('correct','FP','FN','abstain');checks+=1
     entries.append(dict(scenario=name,seed=seed,truth=truth,policy=policy,n=n,decision=label,outcome=oc))
 summaries={}
 for name,_,_,_ in SCENARIOS:
  summaries[name]={}
  for policy in POLICIES:
   sub=[e for e in entries if e['scenario']==name and e['policy']==policy]
   summ={'correct':sum(e['outcome']=='correct' for e in sub),'FP':sum(e['outcome']=='FP' for e in sub),'FN':sum(e['outcome']=='FN' for e in sub),'abstain':sum(e['outcome']=='abstain' for e in sub),'samples':sum(e['n'] for e in sub)}
   assert sum(summ[z] for z in ('correct','FP','FN','abstain'))==80;checks+=1
   summ['loss']={key:round(summ['samples']*c['sample']+summ['FP']*c['FP']+summ['FN']*c['FN']+summ['abstain']*c['abstain'],2) for key,c in COSTS.items()}
   summaries[name][policy]=summ
 rankings={}
 for name in summaries:rankings[name]={c:sorted(POLICIES,key=lambda p:summaries[name][p]['loss'][c]) for c in COSTS}
 return {'id':'TD-CROSSDOMAIN-SG031','checks':checks,'n_streams':320,'n_policy_evaluations':len(entries),'scenarios':summaries,'rankings':rankings,'rows_sha256':hashlib.sha256(json.dumps(entries,separators=(',',':')).encode()).hexdigest()}
if __name__=='__main__':print(json.dumps(run(),indent=2))
