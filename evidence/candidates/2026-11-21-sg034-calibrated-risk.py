"""SG034: preregistered empirical risk-bin safety gate.
Uses SG033's identical signal, environment estimator and decision algorithms.
Pure Python 3 stdlib; run from anywhere, files must be siblings in candidates/.
"""
import importlib.util, pathlib, math, json, hashlib
HERE=pathlib.Path(__file__).resolve().parent
P=HERE/'2026-11-21-sg033-risk-limited-adaptation.py'
spec=importlib.util.spec_from_file_location('sg033',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
BINS=(.45,.60,.75,.90,float('inf'));Z=1.6448536269514722
BUDGET=.08;COST={'sample':.06,'FP':150,'FN':90,'abstain':18}
SCENARIOS=m.SCENARIOS
def classify(label,truth):
 if label=='unresolved':return 'abstain'
 if (label=='confirmed')==truth:return 'correct'
 return 'FP' if label=='confirmed' else 'FN'
def bucket(x):
 if x is None:return len(BINS)
 return next(i for i,b in enumerate(BINS) if x<b)
def wilson_upper(errors,n):
 if n==0:return 1.
 p=errors/n;z=Z
 return min(1.,(p+z*z/(2*n)+z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n))
def cases(start,count):
 for ix,(name,rho,slope,heavy) in enumerate(SCENARIOS):
  for truth in (False,True):
   for k in range(count):
    seed=start+100000*ix+10000*int(truth)+101*k
    obs=m.stream(seed,truth,rho,slope,heavy)
    est=m.estimate_rho(obs[:110])
    fut=obs[240:]
    yield dict(seed=seed,scenario=name,truth=truth,rho=est,bin=bucket(est),
       adaptive=m.decide(fut,'cost-aware'),fixed=m.decide(fut,'fixed240'))
def tally(rows,policy):
 d={'correct':0,'FP':0,'FN':0,'abstain':0,'samples':0,'loss':0.,'early':0,'n':len(rows)}
 for r in rows:
  selected=(r['selected'] if policy=='selected' else policy)
  n,label=r['adaptive'] if selected=='adaptive' else r['fixed']
  status=classify(label,r['truth']);d[status]+=1;d['samples']+=n
  d['early']+=int(selected=='adaptive')
  d['loss']+=COST['sample']*n+(COST.get(status,0) if status!='correct' else 0)
 d['loss']=round(d['loss'],2);return d
def run():
 cal=list(cases(11200000,120));groups={i:{'n':0,'error':0} for i in range(len(BINS)+1)}
 for r in cal:
  g=groups[r['bin']];g['n']+=1;g['error']+=int(classify(r['adaptive'][1],r['truth']) in ('FP','FN'))
 for g in groups.values():
  g['upper95']=wilson_upper(g['error'],g['n'])
  g['eligible']=g['n']>=40 and g['upper95']<BUDGET
 hold=list(cases(15200000,60))
 for r in hold:r['selected']='adaptive' if groups[r['bin']]['eligible'] else 'fixed240'
 overall={p:tally(hold,p) for p in ('selected','adaptive','fixed240')}
 by_scenario={name:{p:tally([r for r in hold if r['scenario']==name],p) for p in overall} for name,*_ in SCENARIOS}
 failures=[]
 for r in hold:
  _,label=r['adaptive'] if r['selected']=='adaptive' else r['fixed']
  status=classify(label,r['truth'])
  if status in ('FP','FN'):
   failures.append(dict(seed=r['seed'],scenario=r['scenario'],truth=r['truth'],rho_est=r['rho'],bin=r['bin'],policy=r['selected'],error_type=status))
 assert len(cal)==960 and len(hold)==480
 assert overall['selected']['correct']==401 and overall['selected']['FP']==7 and overall['selected']['FN']==12
 assert overall['selected']['samples']==89640 and overall['selected']['loss']==8588.4
 assert len(failures)==19
 return dict(id='TD-CROSSDOMAIN-SG034',calibration_bins=groups,calibration_total=len(cal),holdout_total=len(hold),
             overall=overall,by_scenario=by_scenario,errors=failures,
             holdout_sha256=hashlib.sha256(json.dumps(hold,separators=(',',':')).encode()).hexdigest())
if __name__=='__main__':print(json.dumps(run(),indent=2))
