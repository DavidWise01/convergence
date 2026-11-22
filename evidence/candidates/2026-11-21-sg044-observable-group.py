"""SG044 observable-group interval calibration. Python 3 stdlib.
Requires sibling SG043 executable in evidence/candidates/.
"""
import math,json,hashlib,statistics as st,importlib.util,pathlib
p=pathlib.Path(__file__).with_name("2026-11-21-sg043-coverage-audit.py")
spec=importlib.util.spec_from_file_location("sg043",p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
EDGES=(.5,.8);MIN_GROUP=30
def classify_group(v):
 n=len(v);mu=sum(v)/n;mid=(n-1)/2
 slope=sum((i-mid)*(q-mu) for i,q in enumerate(v))/sum((i-mid)**2 for i in range(n))
 r=[q-mu-slope*(i-mid) for i,q in enumerate(v)]
 den=sum(r[i-1]**2 for i in range(1,n))
 rho=sum(r[i]*r[i-1] for i in range(1,n))/den if den else 0
 return ('low' if rho<.5 else 'medium' if rho<.8 else 'high'),rho
def dataset(start,count):
 rows=[]
 for j,scenario in enumerate(m.SCENARIOS):
  for drift in (False,True):
   for k in range(count):
    seed=start+200000*j+10000*int(drift)+101*k
    v=m.stream(seed,scenario,drift)
    slope,se=m.trend_hac(v)
    true=(.0027 if scenario=='subtle_drift' else .005) if drift else 0.
    group,rho=classify_group(v)
    rows.append(dict(seed=seed,scenario=scenario,drift=drift,truth=true,slope=slope,se=se,group=group,rho=rho,ratio=abs(slope-true)/max(se,1e-12)))
 return rows
def q90(rows):
 data=sorted(r['ratio'] for r in rows)
 return data[min(len(data),math.ceil((len(data)+1)*.9))-1]
def evaluate(rows,zfun):
 groups=('ALL',)+m.SCENARIOS+('observable_low','observable_medium','observable_high')
 out={};bad=[];dec=dict(correct=0,FP=0,FN=0,abstain=0,loss=0.,observations=len(rows)*240)
 for group in groups:
  subset=rows if group=='ALL' else [r for r in rows if r['group']==group[11:]] if group.startswith('observable_') else [r for r in rows if r['scenario']==group]
  n=len(subset);hit=sum(r['ratio']<=zfun(r) for r in subset)
  out[group]=dict(n=n,covered=hit,coverage=round(hit/n,5) if n else None,mean_width=round(sum(2*zfun(r)*r['se'] for r in subset)/n,7) if n else None)
 for r in rows:
  z=zfun(r);lo=r['slope']-z*r['se'];hi=r['slope']+z*r['se']
  if not lo<=r['truth']<=hi:bad.append({k:r[k] for k in ('seed','scenario','drift','truth','slope','se','group','rho')})
  label='confirmed' if lo>0 or hi<0 else 'rejected' if lo>-.0032 and hi<.0032 else 'unresolved'
  kind='abstain' if label=='unresolved' else 'correct' if (label=='confirmed')==r['drift'] else 'FP' if label=='confirmed' else 'FN'
  dec[kind]+=1;dec['loss']+=14.4+{'correct':0,'FP':150,'FN':90,'abstain':18}[kind]
 dec['loss']=round(dec['loss'],2)
 return dict(coverage=out,decision=dec,misses=bad)
def run():
 cal=dataset(91000000,20);global_z=q90(cal)
 members={g:[r for r in cal if r['group']==g] for g in ('low','medium','high')}
 groups={g:dict(n=len(v),z=q90(v) if len(v)>=MIN_GROUP else global_z,fallback=len(v)<MIN_GROUP) for g,v in members.items()}
 hold=dataset(97000000,40)
 res={'id':'TD-CROSSDOMAIN-SG044','calibration':dict(n=len(cal),global_z=global_z,groups=groups),
      'holdout_n':len(hold),'global':evaluate(hold,lambda r:global_z),'grouped':evaluate(hold,lambda r:groups[r['group']]['z']),
      'rows_sha256':hashlib.sha256(json.dumps(hold,sort_keys=True).encode()).hexdigest()}
 assert (res['global']['coverage']['ALL']['covered'],res['grouped']['coverage']['ALL']['covered'])==(626,633)
 assert len(res['grouped']['misses'])==87
 return res
if __name__=='__main__':print(json.dumps(run(),indent=2))
