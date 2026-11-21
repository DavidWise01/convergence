"""SG040: spectral period search and negative-control holdout.
Requires sibling SG039 Python file; Python3 standard library only.
Run: python 2026-11-21-sg040-spectral-discovery.py
"""
import importlib.util,pathlib,math,random,hashlib,json,sys
path=pathlib.Path(__file__).resolve().with_name('2026-11-21-sg039-diagnose-disagreement.py')
spec=importlib.util.spec_from_file_location('sg039',path)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
b=old.b
SCENARIOS=tuple(b.SCENARIOS)+('variable_period','colored_control')
COST={'correct':0,'FP':150,'FN':90,'abstain':18}
PERIODS=tuple(range(25,101,5))
def gen(seed,scenario,truth):
 if scenario in b.SCENARIOS:return b.gen(seed,scenario,truth)
 r=random.Random(seed);z=0.;phase=0.;out=[]
 for t in range(480):
  rho=.94 if scenario=='colored_control' and t>=240 else .72
  z=rho*z+r.uniform(-.23,.23)
  slope=.005;spike=7 if t in (42,173) else -7 if t in (87,211) else 0
  oscillation=0.
  if scenario=='variable_period' and t>=240:
   phase+=2*math.pi/(42+16*(t-240)/240)
   oscillation=.55*math.sin(phase)
  out.append((slope*t if truth else 0)+3*(t>=120)+z+spike+oscillation)
 return out
def spectral(v):
 if len(v)<100:return 0.,None,0.
 q=v[-min(len(v),160):];n=len(q);mean=sum(q)/n;c=(n-1)/2
 slope=sum((i-c)*(x-mean) for i,x in enumerate(q))/sum((i-c)**2 for i in range(n))
 res=[x-mean-slope*(i-c) for i,x in enumerate(q)]
 den=sum(x*x for x in res)
 if not den:return 0.,None,0.
 powers=[]
 for period in PERIODS:
  cos=sum(x*math.cos(2*math.pi*i/period) for i,x in enumerate(res))
  sin=sum(x*math.sin(2*math.pi*i/period) for i,x in enumerate(res))
  powers.append((2*(cos*cos+sin*sin)/(n*den),period))
 best=max(powers);other=max((p for p,period in powers if abs(period-best[1])>=20),default=0.)
 return best[0],best[1],other
def new_controller(v,threshold=.45):
 previous=None;alarm=False;candidate=None;candidate_time=None;disagreements=0
 for n in range(80,241,20):
  a,s=b.classify(v[:n]);strong=a!='unresolved' and (abs(s)>.0036 or abs(s)<.0014)
  alarm=alarm or b.shifted(v[:n])
  if alarm:candidate=None
  elif candidate is not None:
   if a!=candidate or not strong:candidate=None
   elif n-candidate_time>=20:
    other=b.classify_slope(b.alternative(v[:n]))
    if a!=other:
     disagreements+=1;power,period,second=spectral(v[:n])
     approved=power>=threshold and power>=1.4*second
    else:approved=True
    if approved:return n,a,disagreements
    candidate=None
  if candidate is None and not alarm and n>=120 and strong and a==previous:
   candidate=a;candidate_time=n
  previous=a
 a=b.classify(v)[0]
 if alarm:
  other=b.classify_slope(b.alternative(v))
  if a!=other:
   disagreements+=1;power,period,second=spectral(v)
   if not(power>=threshold and power>=1.4*second):return 240,'unresolved',disagreements
 return 240,a,disagreements
def run(seed_start=51000000,count=40,threshold=.45):
 rows=[]
 for idx,scenario in enumerate(SCENARIOS):
  for truth in (False,True):
   for k in range(count):
    seed=seed_start+200000*idx+10000*int(truth)+101*k
    observations=gen(seed,scenario,truth);ok,_,_=b.allowed(observations[:110]);future=observations[240:]
    choices={}
    for mode in ('fixed','sg037','sg038','sg039','sg040'):
     if mode=='fixed' or not ok:n,lab,diagnoses=240,b.classify(future)[0],0
     elif mode=='sg040':n,lab,diagnoses=new_controller(future,threshold)
     elif mode=='sg037':
      n,lab,_=b.old_controller(future);diagnoses=0
     elif mode=='sg038':
      n,lab,_,diagnoses=b.new_controller(future)
     else:
      n,lab,_,records=old.controller(future,'sg039');diagnoses=len(records)
     kind=b.outcome(lab,truth)
     choices[mode]={'n':n,'label':lab,'outcome':kind,'cost':round(.06*n+COST[kind],2),'diagnoses':diagnoses}
    rows.append({'seed':seed,'scenario':scenario,'truth':truth,'gate':ok,'choices':choices})
 def score(group,mode):
  items=[r['choices'][mode] for r in group]
  return {**{v:sum(item['outcome']==v for item in items) for v in ('correct','FP','FN','abstain')},
    'samples':sum(x['n'] for x in items),'loss':round(sum(x['cost'] for x in items),2),
    'early':sum(x['n']<240 for x in items)}
 results={s:{m:score(rows if s=='ALL' else [r for r in rows if r['scenario']==s],m) for m in ('fixed','sg037','sg038','sg039','sg040')} for s in ('ALL',)+SCENARIOS}
 failures=[{'seed':r['seed'],'scenario':r['scenario'],'truth':r['truth'],'outcome':r['choices']['sg040']} for r in rows if r['choices']['sg040']['outcome'] in ('FP','FN')]
 return {'id':'TD-CROSSDOMAIN-SG040','streams':len(rows),'results':results,'failures':failures,'rows_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
if __name__=='__main__':
 out=run(int(sys.argv[1]) if len(sys.argv)>1 else 51000000,int(sys.argv[2]) if len(sys.argv)>2 else 40,float(sys.argv[3]) if len(sys.argv)>3 else .45)
 print(json.dumps(out,indent=2))
