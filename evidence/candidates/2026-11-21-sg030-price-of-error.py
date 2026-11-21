"""SG-030 synthetic evidence acquisition cost benchmark. Stdlib only.
Freeze commit: 12e3c4b1e830b28e2e0412714b46737ce19bb3bd.
The 'cost-aware' rule is heuristic, not a proved cost minimizer.
"""
import random, statistics, json, hashlib

COST={'sample':0.06,'FP':150,'FN':90,'abstain':18}
POLICIES=('fixed80','fixed120','fixed160','fixed240','adaptive','cost-aware')

def stream(seed, drift, slope=.005, rho=.72, count=480):
    r=random.Random(seed); z=0.0; out=[]
    for t in range(count):
        z=rho*z+r.uniform(-.23,.23)
        spike=7 if t in (42,173) else -7 if t in (87,211) else 0
        out.append((slope*t if drift else 0)+3*(t>=120)+z+spike)
    return out

def classify(vals):
    bins=[statistics.median(vals[10*i:10*(i+1)]) for i in range(len(vals)//10)]
    slope=statistics.median((bins[j]-bins[i])/(10*(j-i)) for i in range(len(bins)) for j in range(i+1,len(bins)))
    return ('confirmed' if abs(slope)>.0032 else 'rejected' if abs(slope)<.0018 else 'unresolved'),slope

def decide(vals, policy):
    snapshots=[(n,*classify(vals[:n])) for n in range(80,241,40)]
    if policy.startswith('fixed'):
        n=int(policy[5:]); return n,next(l for t,l,_ in snapshots if t==n)
    previous=None
    for n,lab,slope in snapshots:
        if policy=='adaptive' and lab!='unresolved' and lab==previous:
            return n,lab
        if policy=='cost-aware' and n>=120 and lab!='unresolved' and lab==previous and (abs(slope)>.0036 or abs(slope)<.0014):
            return n,lab
        previous=lab
    return 240,'unresolved'

def loss(n,decision,truth):
    cost=n*COST['sample']
    if decision=='unresolved':return cost+COST['abstain'],'abstain'
    if (decision=='confirmed')==truth:return cost,'correct'
    if decision=='confirmed':return cost+COST['FP'],'fp'
    return cost+COST['FN'],'fn'

def evaluate(seed_offset=4200000, trials_per_class=100):
    rows=[];totals={p:{'correct':0,'fp':0,'fn':0,'abstain':0,'observations':0,'loss':0.0} for p in POLICIES}
    checks=0
    for truth in (False,True):
        for k in range(trials_per_class):
            seed=seed_offset+10000*int(truth)+101*k
            generated=stream(seed,truth); new=generated[240:480]
            for p in POLICIES:
                n,decision=decide(new,p)
                c,classification=loss(n,decision,truth)
                assert n in (80,120,160,200,240);checks+=1
                assert decision in ('confirmed','rejected','unresolved');checks+=1
                r=totals[p];r[classification]+=1;r['observations']+=n;r['loss']+=c
                rows.append({'truth':'drift' if truth else 'no_drift','seed':seed,'policy':p,'n':n,'decision':decision,'outcome':classification,'cost':round(c,2)})
    for p,r in totals.items():
        assert sum(r[k] for k in ('correct','fp','fn','abstain'))==2*trials_per_class;checks+=1
        r['loss']=round(r['loss'],4)
    summary={'traces':2*trials_per_class,'policy_traces':len(rows),'checks':checks,'costs':COST,'totals':totals,
             'baseline':'fixed240','seed_recipe':'4200000+10000*int(drift)+101*k, k=0..99',
             'full_row_sha256':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),
             'limitations':['Synthetic known distribution and manually designed candidate policy family',
             'cost-aware is a heuristic; no Bayesian optimality or out-of-family robustness',
             'Paired streams reused across policies; sample count is policy cost per case, not distinct unique observations across policy evaluations']}
    return summary,rows
if __name__=='__main__':
    summary,rows=evaluate()
    print(json.dumps(summary,indent=2))
