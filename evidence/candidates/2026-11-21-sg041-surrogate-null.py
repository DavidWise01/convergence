"""SG041: correlation-aware AR(1) surrogate max-peak test, Python stdlib.
Run from repository evidence/candidates/; SG040 and its dependencies are siblings.
Surrogates are generated strictly from acquired prefixes, seeded independently
from truth labels and future observations.
"""
import importlib.util,pathlib,math,random,hashlib,json,statistics as st,sys,functools
BASE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("sg040_repo",BASE/"2026-11-21-sg040-spectral-discovery.py")
root=importlib.util.module_from_spec(spec);spec.loader.exec_module(root)
class Adapter:pass
b=Adapter()
b.S=root.SCENARIOS;b.PERIODS=root.PERIODS;b.COST={'correct':0,'FP':150,'FN':90,'abstain':18}
b.gen=root.gen
b.gate=lambda pre:root.old.b.allowed(pre)[0]
b.trend=root.old.b.theil
b.label=root.old.b.classify_slope
b.alt=root.old.b.alternative
b.alarm=root.old.b.shifted
b.controller=lambda v,mode,threshold:(*root.new_controller(v,threshold),[])
def detrend(q):
 n=len(q);mean=sum(q)/n;c=(n-1)/2
 sl=sum((i-c)*(x-mean) for i,x in enumerate(q))/sum((i-c)**2 for i in range(n))
 return [x-mean-sl*(i-c) for i,x in enumerate(q)]
@functools.lru_cache(maxsize=None)
def basis(n):
 return [(p,[math.cos(2*math.pi*i/p) for i in range(n)],[math.sin(2*math.pi*i/p) for i in range(n)]) for p in b.PERIODS]
def peak_residual(r):
 n=len(r);den=sum(x*x for x in r)
 if not den:return 0.,None,0.
 powers=[]
 for p,cs,ss in basis(n):
  c=sum(x*y for x,y in zip(r,cs));s=sum(x*y for x,y in zip(r,ss))
  powers.append((2*(c*c+s*s)/(n*den),p))
 best=max(powers);other=max((v for v,p in powers if abs(p-best[1])>=20),default=0.)
 return best[0],best[1],other
def peak_test(v,seed,nsur=31):
 if len(v)<100:return dict(p=1.,power=0.,period=None,rho=None,nsur=nsur)
 r=detrend(v[-min(len(v),160):]);n=len(r)
 observed,period,_=peak_residual(r)
 den=sum(r[i-1]**2 for i in range(1,n))
 rho=max(-.97,min(.97,sum(r[i]*r[i-1] for i in range(1,n))/den)) if den else 0.
 variance=sum(x*x for x in r)/n
 sigma=math.sqrt(max(0.,variance*(1-rho*rho)))
 rng=random.Random(seed);exceeds=0
 for j in range(nsur):
  z=rng.gauss(0,math.sqrt(variance));null=[z]
  for k in range(1,n):
   z=rho*z+rng.gauss(0,sigma);null.append(z)
  val,_,_=peak_residual(detrend(null))
  exceeds+=val>=observed
 return dict(p=(1+exceeds)/(nsur+1),power=observed,period=period,rho=rho,nsur=nsur,exceeds=exceeds)
def controller(v,seed,alpha=.0625,nsur=31):
 prev=None;shift=False;candidate=None;time=None;checks=[]
 for n in range(80,241,20):
  slope=b.trend(v[:n]);a=b.label(slope)
  strong=a!='unresolved' and (abs(slope)>.0036 or abs(slope)<.0014)
  shift=shift or b.alarm(v[:n])
  if shift:candidate=None
  elif candidate is not None:
   if a!=candidate or not strong:candidate=None
   elif n-time>=20:
    other=b.label(b.alt(v[:n]))
    if a==other:return n,a,checks
    stat=peak_test(v[:n],seed*1009+n,nsur)
    checks.append(dict(n=n,reason='disagreement',**stat))
    if stat['p']<=alpha:return n,a,checks
    candidate=None
  if candidate is None and not shift and n>=120 and strong and a==prev:candidate=a;time=n
  prev=a
 a=b.label(b.trend(v))
 if shift:
  other=b.label(b.alt(v))
  if a!=other:
   stat=peak_test(v,seed*1009+240,nsur)
   checks.append(dict(n=240,reason='alarmed-final-disagreement',**stat))
   if stat['p']>alpha:return 240,'unresolved',checks
 return 240,a,checks
def run(start=61000000,count=20,alpha=.0625,nsur=31):
 rows=[]
 for ix,scenario in enumerate(b.S):
  for truth in (False,True):
   for k in range(count):
    seed=start+200000*ix+10000*int(truth)+101*k
    x=b.gen(seed,scenario,truth);permit=b.gate(x[:110]);future=x[240:]
    old=b.controller(future,'sg040',.45) if permit else (240,b.label(b.trend(future)),0,[])
    new=controller(future,seed,alpha,nsur) if permit else (240,b.label(b.trend(future)),[])
    fixed=(240,b.label(b.trend(future)))
    choices={}
    for mode,val in (('sg040',old),('sg041',new),('fixed',fixed)):
     n,a=val[:2]
     status='abstain' if a=='unresolved' else 'correct' if (a=='confirmed')==truth else 'FP' if a=='confirmed' else 'FN'
     choices[mode]=dict(n=n,label=a,outcome=status,cost=round(.06*n+b.COST[status],2))
    rows.append(dict(seed=seed,scenario=scenario,truth=truth,gate=permit,choices=choices,diagnostics=new[2]))
 results={}
 for scenario in ('ALL',)+b.S:
  group=rows if scenario=='ALL' else [r for r in rows if r['scenario']==scenario]
  results[scenario]={}
  for mode in ('sg040','sg041','fixed'):
   vals=[r['choices'][mode] for r in group]
   results[scenario][mode]={**{c:sum(v['outcome']==c for v in vals) for c in ('correct','FP','FN','abstain')},
      'samples':sum(v['n'] for v in vals),'loss':round(sum(v['cost'] for v in vals),2),'early':sum(v['n']<240 for v in vals)}
 failures=[{k:r[k] for k in ('scenario','seed','truth','gate')}|dict(outcome=r['choices']['sg041'],diagnostics=r['diagnostics']) for r in rows if r['choices']['sg041']['outcome'] in ('FP','FN')]
 ans=dict(id='TD-CROSSDOMAIN-SG041',start=start,count=count,alpha=alpha,surrogates=nsur,results=results,failures=failures,
  diagnostic_count=sum(len(r['diagnostics']) for r in rows),
  approved_count=sum(sum(c['p']<=alpha for c in r['diagnostics']) for r in rows),
  rows_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest())
 if start==61000000 and count==20 and alpha==.0625 and nsur==31:
  assert ans['results']['ALL']['sg041']=={'correct':312,'FP':4,'FN':4,'abstain':40,'samples':79340,'loss':6440.4,'early':82}
  assert len(failures)==8
 return ans
if __name__=='__main__':
 out=run(int(sys.argv[1]) if len(sys.argv)>1 else 61000000,int(sys.argv[2]) if len(sys.argv)>2 else 20)
 print(json.dumps(out,indent=2))
