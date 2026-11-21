"""SG-032: prospective noise-environment selection, synthetic stress test.
Frozen threshold 0.82; predecision data t=0..109; score uses t=240..479.
Pure stdlib, deterministic. No retuning on holdout.
"""
import random,statistics,json,hashlib
SCENARIOS=(('baseline',.72,.005,False),('weak_drift',.72,.0027,False),('high_correlation',.93,.005,False),('heavy_tailed',.72,.005,True))
COST={'sample':.06,'FP':150,'FN':90,'abstain':18}
THRESHOLD=.82
def stream(seed,drift,rho,slope,heavy):
 r=random.Random(seed);z=0.;out=[]
 for t in range(480):
  z=rho*z+r.uniform(-.23,.23)
  impulse=7 if t in (42,173) else -7 if t in (87,211) else 0
  if heavy and r.random()<.03:impulse+=r.choice((-2.5,2.5))
  out.append((slope*t if drift else 0.)+3*(t>=120)+z+impulse)
 return out
def estimate_rho(pre):
 pairs=[(t,pre[t]) for t in range(110) if abs(pre[t])<1.5]
 mt=sum(t for t,v in pairs)/len(pairs); mv=sum(v for t,v in pairs)/len(pairs)
 slope=sum((t-mt)*(v-mv) for t,v in pairs)/sum((t-mt)**2 for t,v in pairs)
 intercept=mv-slope*mt
 residual={t:v-intercept-slope*t for t,v in pairs}
 pairs2=[(residual[t-1],residual[t]) for t in range(1,110) if t-1 in residual and t in residual]
 if len(pairs2)<45:return None
 den=sum(a*a for a,b in pairs2)
 return sum(a*b for a,b in pairs2)/den if den else None
def classify(v):
 bins=[statistics.median(v[10*i:10*(i+1)]) for i in range(len(v)//10)]
 slope=statistics.median((bins[j]-bins[i])/(10*(j-i)) for i in range(len(bins)) for j in range(i+1,len(bins)))
 return ('confirmed' if abs(slope)>.0032 else 'rejected' if abs(slope)<.0018 else 'unresolved'),slope
def decide(v,policy):
 snapshots=[(n,*classify(v[:n])) for n in range(80,241,40)]
 if policy=='fixed240':return 240,snapshots[-1][1]
 prev=None
 for n,label,slope in snapshots:
  if n>=120 and label!='unresolved' and label==prev and (abs(slope)>.0036 or abs(slope)<.0014):return n,label
  prev=label
 return 240,'unresolved'
def loss(n,label,truth):
 c=n*COST['sample']
 if label=='unresolved':return c+COST['abstain'],'abstain'
 if (label=='confirmed')==truth:return c,'correct'
 return (c+COST['FP'],'FP') if label=='confirmed' else (c+COST['FN'],'FN')
def evaluate(start=8200000,count=50):
 rows=[];checks=0
 for ix,(name,rho,slope,heavy) in enumerate(SCENARIOS):
  for truth in (False,True):
   for k in range(count):
    seed=start+100000*ix+10000*int(truth)+101*k
    obs=stream(seed,truth,rho,slope,heavy)
    est=estimate_rho(obs[:110])
    selected='fixed240' if est is None or est>=THRESHOLD else 'cost-aware'
    future=obs[240:]
    outcomes={}
    for policy in ('fixed240','cost-aware'):
     n,label=decide(future,policy)
     cost,kind=loss(n,label,truth)
     outcomes[policy]={'n':n,'label':label,'cost':cost,'outcome':kind}
     assert n in (80,120,160,200,240);checks+=1
    assert est is None or -2<=est<=2;checks+=1
    rows.append({'environment':name,'seed':seed,'drift_truth':truth,'rho_estimate':est,'correct_environment':(selected=='fixed240')==(name=='high_correlation'),'selected':selected,'outcomes':outcomes})
 summary={}
 for name,_,_,_ in SCENARIOS:
  group=[r for r in rows if r['environment']==name]
  stats={}
  for policy in ('selected','fixed240','cost-aware'):
   samples=[r['outcomes'][r['selected'] if policy=='selected' else policy] for r in group]
   stats[policy]={'loss':round(sum(s['cost'] for s in samples),2),
                  'samples':sum(s['n'] for s in samples),
                  **{k:sum(s['outcome']==k for s in samples) for k in ('correct','FP','FN','abstain')}}
  summary[name]={'environment_correct':sum(r['correct_environment'] for r in group),'environment_total':len(group),'selected_fixed240':sum(r['selected']=='fixed240' for r in group),'policies':stats}
 totals={p:{k:round(sum(s['policies'][p][k] for s in summary.values()),2) for k in ('loss','samples','correct','FP','FN','abstain')} for p in ('selected','fixed240','cost-aware')}
 misses=[{'environment':r['environment'],'seed':r['seed'],'truth':r['drift_truth'],'rho_estimate':round(r['rho_estimate'],6) if r['rho_estimate'] is not None else None,'policy':r['selected']} for r in rows if not r['correct_environment']]
 assert len(rows)==400 and len(misses)==20 and totals['selected']['loss']==6638.4;checks+=1
 return {'checks':checks,'streams':len(rows),'environment_misses':misses,'by_scenario':summary,'totals':totals,'row_sha256':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()}
if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
