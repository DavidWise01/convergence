"""SG045: persistence + observable stationarity grouped interval calibration.
Python 3 stdlib; requires sibling SG043 coverage audit in candidates/.
"""
import math,json,hashlib,statistics,importlib.util,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('sg043',ROOT/'2026-11-21-sg043-coverage-audit.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def ar(data):
 n=len(data);center=(n-1)/2;avg=sum(data)/n
 slope=sum((i-center)*(v-avg) for i,v in enumerate(data))/sum((i-center)**2 for i in range(n))
 residual=[v-avg-slope*(i-center) for i,v in enumerate(data)]
 den=sum(v*v for v in residual[:-1])
 rho=sum(a*b for a,b in zip(residual[1:],residual[:-1]))/den if den else 0.
 rms=(sum(v*v for v in residual)/n)**.5
 return rho,rms
def features(data):
 rho,_=ar(data);r1,s1=ar(data[:120]);r2,s2=ar(data[120:])
 shift=abs(r2-r1)>.22 or max(s1,s2)/max(min(s1,s2),1e-12)>1.5
 return ('shift_' if shift else 'stable_')+('high' if rho>=.8 else 'medium' if rho>=.5 else 'low'),rho,r1,r2,shift
def dataset(start,count):
 rows=[]
 for j,scenario in enumerate(m.SCENARIOS):
  for drift in (False,True):
   for k in range(count):
    seed=start+200000*j+10000*int(drift)+101*k
    values=m.stream(seed,scenario,drift);slope,se=m.trend_hac(values)
    truth=(.0027 if scenario=='subtle_drift' else .005) if drift else 0.
    group,rho,r1,r2,shift=features(values)
    rows.append({'seed':seed,'scenario':scenario,'drift':drift,'truth':truth,'slope':slope,'se':se,'ratio':abs(slope-truth)/max(se,1e-12),'group':group,'rho':rho,'rho_early':r1,'rho_late':r2,'shift_flag':shift})
 return rows
def quantile(rows):
 vals=sorted(r['ratio'] for r in rows)
 return vals[min(len(vals),math.ceil((len(vals)+1)*.9))-1]
def audit(rows,zfunc):
 out={'correct':0,'FP':0,'FN':0,'abstain':0,'observations':len(rows)*240,'loss':0.}
 groups={};misses=[]
 for r in rows:
  z=zfunc(r);lo=r['slope']-z*r['se'];hi=r['slope']+z*r['se']
  covered=lo<=r['truth']<=hi
  if not covered:misses.append({k:r[k] for k in ('seed','scenario','drift','truth','slope','se','ratio','group','rho','rho_early','rho_late','shift_flag')})
  for key in ('ALL',r['scenario'],r['group']):
   x=groups.setdefault(key,{'n':0,'covered':0,'width':0.})
   x['n']+=1;x['covered']+=int(covered);x['width']+=2*z*r['se']
  label='confirmed' if lo>0 or hi<0 else 'rejected' if lo>-.0032 and hi<.0032 else 'unresolved'
  category='abstain' if label=='unresolved' else 'correct' if (label=='confirmed')==r['drift'] else 'FP' if label=='confirmed' else 'FN'
  out[category]+=1;out['loss']+=14.4+{'correct':0,'FP':150,'FN':90,'abstain':18}[category]
 for x in groups.values():
  x['coverage']=round(x['covered']/x['n'],5);x['mean_width']=round(x.pop('width')/x['n'],8)
 out['loss']=round(out['loss'],2)
 return {'coverage':groups,'decisions':out,'misses':misses}
def run(start=101000000,count=40):
 calibration=dataset(99000000,20)
 global_z=quantile(calibration)
 groups={}
 for g in sorted(set(x['group'] for x in calibration)):
  subset=[x for x in calibration if x['group']==g]
  groups[g]={'n':len(subset),'z':quantile(subset) if len(subset)>=30 else global_z,'fallback':len(subset)<30}
 hold=dataset(start,count)
 global_result=audit(hold,lambda r:global_z)
 grouped=audit(hold,lambda r:groups.get(r['group'],{'z':global_z})['z'])
 if start==101000000 and count==40:
  assert global_result['coverage']['ALL']['covered']==659
  assert grouped['coverage']['ALL']['covered']==660 and len(grouped['misses'])==60
  assert grouped['decisions']['loss']==16644.
 return {'id':'TD-CROSSDOMAIN-SG045','calibration':{'n':len(calibration),'global_z':global_z,'groups':groups},'holdout_n':len(hold),'global':global_result,'grouped':grouped,'rows_sha256':hashlib.sha256(json.dumps(hold,sort_keys=True).encode()).hexdigest()}
if __name__=='__main__':
 result=run()
 outfile=ROOT/'sg045-full-holdout.json'
 outfile.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'calibration':result['calibration'],'global':result['global']['decisions'],'grouped':result['grouped']['decisions'],'coverage':result['grouped']['coverage'],'miss_count':len(result['grouped']['misses'])},indent=2))
