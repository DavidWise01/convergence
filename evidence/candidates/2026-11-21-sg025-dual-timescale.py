"""SG025 dual-timescale adaptive change detection, frozen synthetic holdout."""
import random, statistics, json
KINDS=['steady','spike','drift','step','step_spike']
N=240

def stream(kind,seed):
    r=random.Random(seed);out=[]
    for t in range(N):
        level=(.005*t if kind=='drift' else (3.0 if kind in ('step','step_spike') and t>=120 else 0.0))
        noise=r.uniform(-.26,.26)
        if kind in ('spike','step_spike') and t in (42,87,173,211):
            noise+=(7 if t%2==0 else -7)
        out.append(level+noise)
    return out

def fast(xs):
    ref=statistics.median(xs[:11]);out=[];count=0;direction=0;cool=-999
    for t in range(11,len(xs)):
        recent=statistics.median(xs[t-10:t+1]);delta=recent-ref
        sign=1 if delta>1.15 else -1 if delta < -1.15 else 0
        if sign and sign==direction:count+=1
        elif sign:count=1;direction=sign
        else:count=0;direction=0
        if count>=4 and t-cool>=16:
            abrupt=any(sign*(xs[k]-xs[k-1])>1.5 for k in range(max(1,t-19),t+1))
            out.append((t,'step' if abrupt else 'drift'))
            ref=recent;cool=t;count=0;direction=0
    return out

def slow(xs,lookback=48,shift_threshold=.20,confirm=5):
    streak=0;alarms=[];last=-999
    for t in range(2*lookback-1,len(xs)):
        prior=statistics.median(xs[t-2*lookback+1:t-lookback+1])
        later=statistics.median(xs[t-lookback+1:t+1])
        diff=later-prior
        if abs(diff)>shift_threshold:streak+=1
        else:streak=0
        if streak>=confirm and t-last>20:
            alarms.append((t,'drift'))
            last=t;streak=0
    return alarms

def evaluate(params,seeds):
    results={};fails=[]
    for kind in KINDS:
        good=0;examples=[]
        for seed in seeds[kind]:
            x=stream(kind,seed);f=fast(x);s=slow(x,*params)
            steps=[t for t,k in f if k=='step']
            drifts=[t for t,k in s if k=='drift' and not any(abs(t-v)<=70 for v in steps)]
            if kind in ('steady','spike'):ok=not f and not drifts
            elif kind=='drift':ok=bool(drifts) and not steps
            else:ok=bool([t for t in steps if 120<=t<=145]) and not drifts
            good+=ok
            if not ok:fails.append(dict(kind=kind,seed=seed,fast=f,slow=s,filtered=drifts))
            if len(examples)<2:examples.append(dict(seed=seed,fast=f,slow=s,filtered_drift=drifts))
        results[kind]=dict(passed=good,total=len(seeds[kind]),examples=examples)
    return results,fails

def holdout():
    seeds={k:[510000+53*i+1009*KINDS.index(k) for i in range(30)] for k in KINDS}
    results,fails=evaluate((48,.20,5),seeds)
    assert not fails and sum(v['passed'] for v in results.values())==150
    return dict(total=150,passed=150,results=results,failed=fails,
        freeze='c15f6fc292c8e608f8853a0b6897daccbc7dc16d')
if __name__=='__main__':print(json.dumps(holdout(),indent=2))
