"""SG-026 offline two-component identification with robust medians, standard library."""
import random,statistics,json
N=240; KINDS=('steady','impulses','drift','step','step_drift','colored_steady','colored_step_drift','negative_drift_step')
def stream(kind,seed):
 r=random.Random(seed); z=0.;out=[]
 rho=.72 if 'colored' in kind else .35
 drift=(-.005 if kind=='negative_drift_step' else .005 if kind in ('drift','step_drift','colored_step_drift') else 0.)
 step=3. if kind in ('step','step_drift','colored_step_drift') else (-3. if kind=='negative_drift_step' else 0.)
 for t in range(N):
  z=rho*z+r.uniform(-.23,.23)
  impulse=(7. if t in (42,173) else -7. if t in (87,211) else 0.) if kind in ('impulses','step_drift','colored_step_drift','negative_drift_step') else 0.
  out.append(drift*t+step*(t>=120)+z+impulse)
 return out

def detect(x,step_threshold=1.50,drift_threshold=.0027,span=13):
 med=statistics.median; steps=[]
 for k in range(30,N-30):
  left=med(x[k-span:k]);right=med(x[k:k+span]);delta=right-left
  if abs(delta)>step_threshold:steps.append((abs(delta),k,delta))
 if steps:
  amplitude,k,delta=max(steps)
  # delta includes drift over span (~.065); exact position is not guaranteed
  step_index=k
  step_magnitude=delta
 else:step_index=None;step_magnitude=0.
 # Estimate trend from 10-observation bin medians using median pairwise slopes.
 def robust_slope(a,b):
  centers=[i+5 for i in range(a,b-9,10)]
  levels=[med(x[i-5:i+5]) for i in centers]
  diffs=[(levels[j]-levels[i])/(centers[j]-centers[i]) for i in range(len(levels)) for j in range(i+1,len(levels))]
  return med(diffs)
 if step_index is None:
  slope=robust_slope(0,240)
 else:
  slope=med([robust_slope(0,max(60,step_index-10)),robust_slope(min(180,step_index+10),240)])
 return {'step':step_index,'step_magnitude':round(step_magnitude,5),'drift':abs(slope)>drift_threshold,'slope':round(slope,6)}

def evaluate(seed_start=100000, count=30):
 results={};fail=[]
 for idx,kind in enumerate(KINDS):
  hits=0;examples=[]
  for i in range(count):
   seed=seed_start+137*idx+53*i
   result=detect(stream(kind,seed))
   expected_step=kind in ('step','step_drift','colored_step_drift','negative_drift_step')
   expected_drift=kind in ('drift','step_drift','colored_step_drift','negative_drift_step')
   ok=((result['step'] is not None)==expected_step and (not expected_step or abs(result['step']-120)<=8) and result['drift']==expected_drift)
   hits+=ok
   if not ok:fail.append({'kind':kind,'seed':seed,'outcome':result})
   if len(examples)<2:examples.append({'seed':seed,'outcome':result})
  results[kind]={'pass':hits,'total':count,'examples':examples}
 return {'n':len(KINDS)*count,'passed':sum(v['pass'] for v in results.values()),'results':results,'failures':fail}
if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
