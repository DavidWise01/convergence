"""SG027: uncertainty-aware step/drift classification, frozen synthetic holdout."""
import random,statistics,json
N=240
KINDS=('steady','impulses','drift','step','step_drift','colored_steady','colored_step_drift','negative_drift_step')
def stream(kind,seed):
 r=random.Random(seed);z=0.;out=[]
 rho=.72 if 'colored' in kind else .35
 slope=(-.005 if kind=='negative_drift_step' else .005 if kind in ('drift','step_drift','colored_step_drift') else 0.)
 level=3. if kind in ('step','step_drift','colored_step_drift') else (-3. if kind=='negative_drift_step' else 0.)
 for t in range(N):
  z=rho*z+r.uniform(-.23,.23)
  impulse=(7. if t in (42,173) else -7. if t in (87,211) else 0.) if kind in ('impulses','step_drift','colored_step_drift','negative_drift_step') else 0.
  out.append(slope*t+level*(t>=120)+z+impulse)
 return out
def detect(xs,negative=.0018,positive=.0032):
 med=statistics.median
 candidates=[]
 for k in range(30,N-30):
  delta=med(xs[k:k+13])-med(xs[k-13:k])
  if abs(delta)>1.50:candidates.append((abs(delta),k,delta))
 step=max(candidates) if candidates else None
 boundary=step[1] if step else None
 def slope(a,b):
  centers=[i+5 for i in range(a,b-9,10)]
  levels=[med(xs[i-5:i+5]) for i in centers]
  slopes=[(levels[j]-levels[i])/(centers[j]-centers[i]) for i in range(len(centers)) for j in range(i+1,len(centers))]
  return med(slopes)
 if boundary is None:trend=slope(0,N)
 else:trend=med((slope(0,max(60,boundary-10)),slope(min(180,boundary+10),N)))
 magnitude=abs(trend)
 status='rejected' if magnitude<negative else 'confirmed' if magnitude>positive else 'unresolved'
 return {'step_at':boundary,'step_delta':round(step[2],6) if step else None,'slope':round(trend,7),'drift_status':status}
def evaluate(start=900000,count=50):
 cases={};unresolved=[];wrong=[]
 for j,kind in enumerate(KINDS):
  totals={'correct':0,'wrong':0,'unresolved':0,'step_correct':0};examples=[]
  for i in range(count):
   seed=start+173*j+71*i
   out=detect(stream(kind,seed))
   drift_truth=kind in ('drift','step_drift','colored_step_drift','negative_drift_step')
   step_truth=kind in ('step','step_drift','colored_step_drift','negative_drift_step')
   step_good=(out['step_at'] is not None)==step_truth and (not step_truth or abs(out['step_at']-120)<=8)
   totals['step_correct']+=int(step_good)
   status=out['drift_status']
   if status=='unresolved':
    totals['unresolved']+=1
    unresolved.append({'seed':seed,'kind':kind,'trend':out['slope'],'step_at':out['step_at']})
   else:
    ok=((status=='confirmed')==drift_truth) and step_good
    totals['correct']+=int(ok)
    totals['wrong']+=int(not ok)
    if not ok:wrong.append({'seed':seed,'kind':kind,'output':out})
   if i<2:examples.append({'seed':seed,'result':out})
  cases[kind]={**totals,'examples':examples}
 return {'total':count*len(KINDS),'per_kind':cases,'decided_correct':sum(v['correct'] for v in cases.values()),'decided_wrong':len(wrong),'unresolved_count':len(unresolved),'step_loc_correct':sum(v['step_correct'] for v in cases.values()),'unresolved':unresolved,'wrong':wrong}
if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
