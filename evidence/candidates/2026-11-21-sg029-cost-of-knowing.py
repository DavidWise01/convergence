"""SG-029: preregistered sequential evidence acquisition (Python stdlib)."""
import random,statistics,hashlib,json
SEEDS=(901038,901251,902245,903026)
def stream(seed,drift):
 r=random.Random(seed);z=0.;out=[]
 for t in range(480):
  z=.72*z+r.uniform(-.23,.23)
  spike=7. if t in (42,173) else -7. if t in (87,211) else 0.
  out.append((.005*t if drift else 0.)+3.*(t>=120)+z+spike)
 return out
def decision(values):
 bins=[statistics.median(values[10*i:10*(i+1)]) for i in range(len(values)//10)]
 slope=statistics.median((bins[j]-bins[i])/(10*(j-i)) for i in range(len(bins)) for j in range(i+1,len(bins)))
 return ('confirmed' if abs(slope)>.0032 else 'rejected' if abs(slope)<.0018 else 'unresolved'),slope
def digest(values):return hashlib.sha256(json.dumps(values,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def run():
 events=[];rows=[];checks=0
 for seed in SEEDS:
  for drift in (True,False):
   kind='drift' if drift else 'control'
   data=stream(seed,drift);batch_data=[];previous=None;history=[]
   def log(event,**kwargs):events.append(dict(seq=len(events)+1,seed=seed,case=kind,event=event,**kwargs))
   log('source_context',original_epoch='0..239',source_digest=digest(data[:240]),prior='SG027 unresolved' if drift else 'SG028 matched control')
   for t in range(240,480,40):
    block=data[t:t+40];batch_data.extend(block)
    log('evidence_batch',from_t=t,to_t=t+39,n=40,sha256=digest(block),cumulative_n=len(batch_data))
    if len(batch_data)<80:
     log('checkpoint',n=len(batch_data),status='insufficient',slope=None)
     continue
    status,s=decision(batch_data)
    history.append(dict(n=len(batch_data),status=status,slope=round(s,10)))
    log('checkpoint',n=len(batch_data),status=status,slope=round(s,10))
    if status!='unresolved' and previous==status:
     log('stopped',n=len(batch_data),status=status,reason='two_consecutive_matching_decisions')
     break
    previous=status
   else:
    status='unresolved';log('stopped',n=len(batch_data),status=status,reason='cap_without_two_decisions')
   truth='confirmed' if drift else 'rejected'
   assert events[-1]['event']=='stopped';checks+=1
   assert len(batch_data)<=240 and len(batch_data)%40==0;checks+=1
   assert status in ('confirmed','rejected','unresolved');checks+=1
   assert sum(e['n'] for e in events if e['event']=='evidence_batch' and e['seed']==seed and e['case']==kind)==len(batch_data);checks+=1
   assert status!='confirmed' or drift
   assert status!='rejected' or not drift
   rows.append(dict(seed=seed,case=kind,decision=status,truth=truth,correct=status==truth,n=len(batch_data),history=history))
 cost=sum(x['n'] for x in rows)
 return dict(id='TD-CROSSDOMAIN-SG029',cases=rows,total_cases=len(rows),correct_decided=sum(x['correct'] for x in rows),wrong_decided=sum(x['decision']!='unresolved' and not x['correct'] for x in rows),unresolved=sum(x['decision']=='unresolved' for x in rows),cost_units=cost,baseline_cost_units=8*240,saved_units=8*240-cost,checks=checks,event_count=len(events),events=events)
if __name__=='__main__':print(json.dumps(run(),indent=2))
