"""SG042: trend uncertainty via HAC on non-overlapping bin medians.
Frozen parameters are documented in SG042 freeze record. Uses SG041 benchmark as dependency.
"""
import importlib.util,pathlib,math,json,hashlib,sys,statistics
P=pathlib.Path(__file__).with_name('2026-11-21-sg041-surrogate-null.py')
spec=importlib.util.spec_from_file_location('sg041',P)
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
env=getattr(b.b, "b", b.b)

def trend_hac(v,lag=3,z=1.645):
    m=len(v)//10; y=[statistics.median(v[10*i:10*i+10]) for i in range(m)]
    n=len(y); x=[i-(n-1)/2 for i in range(n)]
    xx=sum(t*t for t in x)
    slope_bins=sum(t*yy for t,yy in zip(x,y))/xx
    mean=sum(y)/n
    e=[yy-mean-slope_bins*t for t,yy in zip(x,y)]
    # Sandwich covariance of the OLS numerator with Bartlett weights.
    vnum=sum((x[i]*e[i])**2 for i in range(n))
    for h in range(1,min(lag,n-1)+1):
        vnum+=2*(1-h/(lag+1))*sum(x[i]*e[i]*x[i-h]*e[i-h] for i in range(h,n))
    se=math.sqrt(max(0,vnum))/xx/10
    slope=slope_bins/10
    return slope,se,(slope-z*se,slope+z*se)

def guarded_label(v,original_label,z=1.645,lag=3):
    slope,se,(lo,hi)=trend_hac(v,lag,z)
    if original_label=='unresolved':return 'unresolved',{'slope':slope,'se':se,'lo':lo,'hi':hi,'guard':'prior_unresolved'}
    # A rejection is an equivalence claim: bound slope inside +/- 0.0032.
    # A confirmation requires a sign-consistent confidence interval outside zero.
    accept=(lo>0 or hi<0) if original_label=='confirmed' else (lo>-.0032 and hi<.0032)
    return (original_label if accept else 'unresolved'),{'slope':slope,'se':se,'lo':lo,'hi':hi,'guard':'accepted' if accept else 'held'}

def run(start,count,z=1.645,lag=3):
    rows=[]
    for ix,scenario in enumerate(env.S):
        for truth in (False,True):
            for k in range(count):
                seed=start+200000*ix+10000*int(truth)+101*k
                obs=env.gen(seed,scenario,truth);permit=env.gate(obs[:110]);future=obs[240:]
                baseline=b.ctl(future,seed) if permit else (240,env.label(env.trend(future)),[])
                n,label=baseline[:2]
                revised,diag=guarded_label(future[:n],label,z,lag)
                fixed=(240,env.label(env.trend(future)))
                results={}
                for mode,(samples,out) in [('sg041',(n,label)),('sg042',(n,revised)),('fixed',fixed)]:
                    kind='abstain' if out=='unresolved' else 'correct' if (out=='confirmed')==truth else 'FP' if out=='confirmed' else 'FN'
                    results[mode]={'n':samples,'label':out,'kind':kind,'loss':round(.06*samples+env.COST[kind],2)}
                rows.append({'seed':seed,'scenario':scenario,'truth':truth,'permit':permit,'diagnostic':diag,'results':results})
    summary={}
    for key in ['ALL',*env.S]:
        subset=rows if key=='ALL' else [r for r in rows if r['scenario']==key]
        summary[key]={}
        for policy in ('sg041','sg042','fixed'):
            items=[r['results'][policy] for r in subset]
            summary[key][policy]={**{k:sum(v['kind']==k for v in items) for k in ('correct','FP','FN','abstain')},'samples':sum(v['n'] for v in items),'loss':round(sum(v['loss'] for v in items),2)}
    faults=[{'seed':r['seed'],'scenario':r['scenario'],'truth':r['truth'],'decision':r['results']['sg042'],'diagnostic':r['diagnostic']} for r in rows if r['results']['sg042']['kind'] in ('FP','FN')]
    return {'id':'TD-CROSSDOMAIN-SG042','start':start,'count':count,'z':z,'lag':lag,'summary':summary,'failures':faults,'rows_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
if __name__=='__main__':
    print(json.dumps(run(int(sys.argv[1]) if len(sys.argv)>1 else 67000000,int(sys.argv[2]) if len(sys.argv)>2 else 5),indent=2))
