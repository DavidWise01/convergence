"""SG-024: noisy-regime detection with pilot-informed frozen thresholds.
Standard library only; 150 holdout traces are fresh after GitHub freeze.
"""
import json, random, statistics
N=240;WINDOW=11;THRESHOLD=1.15;PERSIST=4;COOLDOWN=16
KINDS=('steady','spike','drift','step','step_spike')

def series(kind,seed):
    rng=random.Random(seed)
    output=[]
    for t in range(N):
        mean=.005*t if kind=='drift' else (3. if t>=120 and kind in ('step','step_spike') else 0.)
        noise=rng.uniform(-.26,.26)
        if kind in ('spike','step_spike') and t in (42,87,173,211):
            noise+=7 if t%2==0 else -7
        output.append(mean+noise)
    return output

def detector(stream):
    reference=statistics.median(stream[:WINDOW]); events=[]
    consecutive=0;sign=0;last_fire=-999
    for t in range(WINDOW,N):
        recent=statistics.median(stream[t-WINDOW+1:t+1]);residual=recent-reference
        direction=(1 if residual>THRESHOLD else -1 if residual<-THRESHOLD else 0)
        if direction and direction==sign: consecutive+=1
        elif direction: consecutive=1;sign=direction
        else:consecutive=0;sign=0
        if consecutive>=PERSIST and t-last_fire>=COOLDOWN:
            start=max(1,t-19)
            abrupt=any(direction*(stream[k]-stream[k-1])>1.5 for k in range(start,t+1))
            events.append({'at':t,'type':'step' if abrupt else 'drift',
                'old_reference':round(reference,5),'new_reference':round(recent,5),
                'persistent_windows':consecutive})
            reference=recent;last_fire=t;consecutive=0;sign=0
    return events

def run():
    examples={};by_kind={};total_checks=0;all_pass=True;failures=[]
    for kind in KINDS:
        per=[];passed=0
        for i in range(30):
            seed=460000+i*37+KINDS.index(kind)*1009
            events=detector(series(kind,seed))
            steps=[e['at'] for e in events if e['type']=='step']
            drifts=[e['at'] for e in events if e['type']=='drift']
            if kind in ('steady','spike'):valid=not events
            elif kind=='drift':valid=(len(drifts)>=1 and not steps)
            else:valid=(any(120<=t<=145 for t in steps) and not drifts and len(steps)==1)
            total_checks+=1;passed+=int(valid)
            if not valid:failures.append({'kind':kind,'seed':seed,'events':events})
            per.append(events)
        by_kind[kind]={'passes':passed,'trials':30,'first_events':per[0],'events_over_30':sum(len(v) for v in per)}
        examples[kind]=per[0]
    return {'checks':total_checks,'passed':sum(v['passes'] for v in by_kind.values()),'by_kind':by_kind,'failures':failures[:25], 'limits':'150 synthetic traces; labels and model inputs known; fixed threshold learned from earlier pilot'}
if __name__=='__main__': print(json.dumps(run(),indent=2))
