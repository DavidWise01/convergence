"""SG028: frozen followup of SG027 unresolved streams; Python 3 standard library."""
import random,statistics,hashlib,json
from pathlib import Path
SEEDS=(901038,901251,902245,903026)
def generate(seed,drift):
 r=random.Random(seed);z=0.;xs=[]
 for t in range(480):
  z=.72*z+r.uniform(-.23,.23)
  spike=(7. if t in (42,173) else -7. if t in (87,211) else 0.)
  xs.append((.005*t if drift else 0.)+3.*(t>=120)+z+spike)
 return xs
def original(xs):
 med=statistics.median;cs=[]
 for k in range(30,210):
  delta=med(xs[k:k+13])-med(xs[k-13:k])
  if abs(delta)>1.5:cs.append((abs(delta),k,delta))
 k=max(cs)[1] if cs else None
 def slope(a,b):
  centers=[i+5 for i in range(a,b-9,10)]
  levels=[med(xs[i-5:i+5]) for i in centers]
  return med((levels[j]-levels[i])/(centers[j]-centers[i]) for i in range(len(centers)) for j in range(i+1,len(centers)))
 trend=slope(0,240) if k is None else med((slope(0,max(60,k-10)),slope(min(180,k+10),240)))
 return {'decision':'rejected' if abs(trend)<.0018 else 'confirmed' if abs(trend)>.0032 else 'unresolved','slope':round(trend,7),'step_at':k}
def followup(xs):
 levels=[statistics.median(xs[i:i+10]) for i in range(0,240,10)]
 trend=statistics.median((levels[j]-levels[i])/(10*(j-i)) for i in range(24) for j in range(i+1,24))
 return {'decision':'rejected' if abs(trend)<.0018 else 'confirmed' if abs(trend)>.0032 else 'unresolved','slope':round(trend,9)}
def digest(xs):return hashlib.sha256(json.dumps(xs,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def run():
 rows=[];events=[];checks=0
 def event(seed,action,**kw):events.append(dict(seq=len(events)+1,seed=seed,event=action,**kw))
 for seed in SEEDS:
  xs=generate(seed,True);before=original(xs[:240]);after=followup(xs[240:])
  control=followup(generate(seed,False)[240:])
  assert before['decision']=='unresolved';checks+=1
  assert after['decision']=='confirmed';checks+=1
  assert control['decision']=='rejected';checks+=1
  event(seed,'prior_decision',source='SG027',decision='unresolved',original_digest=digest(xs[:240]),original_slope=before['slope'])
  event(seed,'request_new_evidence',start=240,count=240)
  event(seed,'new_observation',start=240,count=240,sha256=digest(xs[240:]))
  event(seed,'followup_decision',decision='confirmed',slope=after['slope'],supersedes_prior=False)
  rows.append({'seed':seed,'original':before,'followup':after,'control':control,'digest':digest(xs[240:])})
 assert len(events)==16;checks+=1
 assert all(e['decision']=='unresolved' for e in events[::4]);checks+=1
 assert all(not e['supersedes_prior'] for e in events[3::4]);checks+=1
 return {'id':'TD-CROSSDOMAIN-SG028','checks':checks,'resolved':4,'control_false_confirmations':0,'extra_samples_per_case':240,'ledger_events':16,'results':rows},events
if __name__=='__main__':
 summary,events=run()
 d=Path(__file__).parent
 (d/'sg028-result.json').write_text(json.dumps(summary,indent=2)+'\n')
 (d/'sg028-events.jsonl').write_text(''.join(json.dumps(e,sort_keys=True)+'\n' for e in events))
 print(json.dumps(summary,indent=2))
