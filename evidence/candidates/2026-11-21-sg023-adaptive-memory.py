"""SG-023: Exact change detection and adaptive minimum sufficient memory."""
from fractions import Fraction as Q
import json

def solve(a,b):
    if not a:return None
    d=len(a[0]); m=[[Q(v) for v in row]+[Q(b[i])] for i,row in enumerate(a)]
    r=0;p=[]
    for col in range(d):
        j=next((i for i in range(r,len(m)) if m[i][col]),None)
        if j is None:continue
        m[r],m[j]=m[j],m[r];v=m[r][col];m[r]=[w/v for w in m[r]]
        for k in range(len(m)):
            if k!=r:
                v=m[k][col]
                if v:m[k]=[w-v*x for w,x in zip(m[k],m[r])]
        p.append(col);r+=1
    if any(all(v==0 for v in row[:d]) and row[-1]!=0 for row in m):return None
    if len(p)!=d:return None
    return tuple(m[i][-1] for i in range(d))

def fit(segment,d):
    if len(segment)<=d:return None
    return solve([[Q(1)]+[segment[t-i] for i in range(1,d+1)] for t in range(d,len(segment))],segment[d:])

def find(segment):
    for d in range(3):
        coefficients=fit(segment,d)
        if coefficients is not None:return d,coefficients
    return None

def next_value(data, model):
    d,coef=model
    return coef[0]+sum(coef[i]*data[-i] for i in range(1,d+1))

def stream():
    x=[Q(1)]
    for t in range(1,90):
        if t<30:x.append(2*x[-1]+1)
        elif t<60:x.append(x[-1]+x[-2]+1)
        else:x.append(Q(5))
    return x

def run():
    values=stream(); model=find(values[:12]);assert model==(1,(Q(1),Q(2)))
    checks=1; state='active'; active_start=0;quarantine=[]; switches=[];history=[];verified_predictions=0;quarantine_count=0
    for t in range(12,90):
        if state=='active':
            guess=next_value(values[:t],model)
            if guess!=values[t]:
                switches.append(t)
                history.append({'epoch_start':active_start,'epoch_end':t-1,'lag':model[0],'coefficients':list(map(str,model[1])),'first_residual_time':t,'residual':str(values[t]-guess)})
                state='quarantine';quarantine=[values[t]];model=None;quarantine_count+=1
            else:
                verified_predictions+=1;checks+=1
        else:
            quarantine.append(values[t]);quarantine_count+=1
            if len(quarantine)==12:
                found=find(quarantine)
                assert found is not None,(t,quarantine);checks+=1
                active_start=t-11;model=found;state='active'
    assert state=='active'
    history.append({'epoch_start':active_start,'epoch_end':89,'lag':model[0],'coefficients':list(map(str,model[1])),'first_residual_time':None})
    assert switches==[30,60];checks+=1
    assert [r['lag'] for r in history]==[1,2,0];checks+=1
    assert [r['epoch_start'] for r in history]==[0,30,60];checks+=1
    assert quarantine_count==24;checks+=1
    assert verified_predictions==54;checks+=1
    assert fit([Q(5)]*12,2) is None;checks+=1
    assert fit(values[30:42],1) is None;checks+=1
    assert all(values[i]==Q(5) for i in range(60,90));checks+=1
    assert history[0]['epoch_end']<history[1]['epoch_start'] and history[1]['epoch_end']<history[2]['epoch_start'];checks+=1
    return {'checks':checks,'switches':switches,'history':history,'verified_predictions':verified_predictions,'quarantine_observations':quarantine_count,'total_step_checks':78}

if __name__=='__main__':print(json.dumps(run(),indent=2))
