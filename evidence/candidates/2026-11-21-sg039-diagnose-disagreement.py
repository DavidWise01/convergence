"""SG039: reproduce frozen diagnosis-aware controller with SG038's simulator.
Run Python 3 from any directory; requires sibling SG038 executable in same repo.
SG039 holdout: python 2026-11-21-sg039-diagnose-disagreement.py 41000000 40
"""
import importlib.util, pathlib, math, statistics, json, hashlib, sys
p=pathlib.Path(__file__).resolve().with_name('2026-11-21-sg038-dual-estimator.py')
spec=importlib.util.spec_from_file_location('sg038_source',p)
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def periodicity(v):
 n=len(v)
 if n<100:return 0.0
 y=v[-min(n,160):];n=len(y);mean=sum(y)/n;c=(n-1)/2
 m=sum((i-c)*(x-mean) for i,x in enumerate(y))/sum((i-c)**2 for i in range(n))
 r=[x-mean-m*(i-c) for i,x in enumerate(y)]
 a=sum(x*math.cos(2*math.pi*i/60) for i,x in enumerate(r))
 d=sum(x*math.sin(2*math.pi*i/60) for i,x in enumerate(r))
 den=sum(x*x for x in r)
 return 2*(a*a+d*d)/(n*den) if den else 0
def diagnostic(a,c,v,threshold=.35):
 if a==c:return a,'agree'
 if periodicity(v)>=threshold:return a,'oscillation-primary'
 return 'unresolved','unexplained-disagreement'
def controller(v,mode='sg039',threshold=.35):
 prev=None;alarm=False;candidate=None;candidate_at=None;disagreements=[];alarm_at=None
 for n in range(80,241,20):
  a=b.classify_slope(b.theil(v[:n]));s=b.theil(v[:n])
  strong=a!='unresolved' and (abs(s)>.0036 or abs(s)<.0014)
  if b.shifted(v[:n]):
   if not alarm:alarm_at=n
   alarm=True
  if alarm:candidate=None
  elif candidate is not None:
   if a!=candidate or not strong:candidate=None
   elif n-candidate_at>=20:
    if mode=='sg037':return n,a,alarm_at,disagreements
    second=b.classify_slope(b.alternative(v[:n]))
    if mode=='sg038':result=a if a==second else 'unresolved';cause='agree' if a==second else 'unexplained-disagreement'
    else:result,cause=diagnostic(a,second,v[:n],threshold)
    if a!=second:disagreements.append((n,cause,round(periodicity(v[:n]),5)))
    if result==a:return n,a,alarm_at,disagreements
    candidate=None
  if candidate is None and not alarm and n>=120 and strong and a==prev:
   candidate=a;candidate_at=n
  prev=a
 a=b.classify_slope(b.theil(v))
 if mode!='sg037' and alarm:
  second=b.classify_slope(b.alternative(v))
  if mode=='sg038':result=a if a==second else 'unresolved';cause='agree' if a==second else 'unexplained-disagreement'
  else:result,cause=diagnostic(a,second,v,threshold)
  if a!=second:disagreements.append((240,cause,round(periodicity(v),5)))
  return 240,result,alarm_at,disagreements
 return 240,a,alarm_at,disagreements
def run(start=41000000,count=40,threshold=.35):
 rows=[]
 for i,scenario in enumerate(b.SCENARIOS):
  for truth in (False,True):
   for k in range(count):
    seed=start+200000*i+10000*int(truth)+101*k
    x=b.gen(seed,scenario,truth);ok,bin_id,rho=b.allowed(x[:110]);v=x[240:]
    choices={}
    for policy in ('sg037','sg038','sg039','fixed'):
     if policy=='fixed' or not ok:n,label,alarm_at,diagnoses=240,b.classify(v)[0],None,[]
     else:n,label,alarm_at,diagnoses=controller(v,policy,threshold)
     status=b.outcome(label,truth)
     choices[policy]={'n':n,'label':label,'status':status,'cost':round(.06*n+{'correct':0,'FP':150,'FN':90,'abstain':18}[status],2),'alarm_at':alarm_at,'diagnoses':diagnoses}
    rows.append({'scenario':scenario,'seed':seed,'truth':truth,'gate':ok,'rho':rho,'choices':choices})
 groups={}
 for group in ('ALL',)+b.SCENARIOS:
  subset=rows if group=='ALL' else [r for r in rows if r['scenario']==group]
  groups[group]={}
  for policy in ('sg037','sg038','sg039','fixed'):
   choices=[r['choices'][policy] for r in subset]
   stats={kind:sum(v['status']==kind for v in choices) for kind in ('correct','FP','FN','abstain')}
   stats.update(samples=sum(v['n'] for v in choices),loss=round(sum(v['cost'] for v in choices),2),early=sum(v['n']<240 for v in choices),disagreements=sum(len(v['diagnoses']) for v in choices),osc_diagnoses=sum(sum(t[1]=='oscillation-primary' for t in v['diagnoses']) for v in choices))
   groups[group][policy]=stats
 failures=[{'seed':r['seed'],'scenario':r['scenario'],'truth':r['truth'],'decision':r['choices']['sg039']} for r in rows if r['choices']['sg039']['status'] in ('FP','FN')]
 result={'id':'TD-CROSSDOMAIN-SG039','seed_start':start,'streams':len(rows),'threshold':threshold,'totals':groups['ALL'],'by_scenario':{k:v for k,v in groups.items() if k!='ALL'},'failures':failures,'sha256_rows':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
 if start==41000000 and count==40 and threshold==.35:
  assert (result['totals']['sg039']['correct'],result['totals']['sg039']['FP'],result['totals']['sg039']['FN'],result['totals']['sg039']['abstain'])==(481,3,5,71)
  assert result['totals']['sg039']['loss']==9442.8 and len(failures)==8
 return result
if __name__=='__main__':
 start=int(sys.argv[1]) if len(sys.argv)>1 else 41000000
 count=int(sys.argv[2]) if len(sys.argv)>2 else 40
 print(json.dumps(run(start,count),indent=2))
