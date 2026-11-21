"""SG-022 exact minimum sufficient autoregressive memory. Python 3 stdlib."""
from fractions import Fraction as F
import json
CASES = [
    ('C0',[5],[],5,0),
    ('C1',[2],[2],1,1),
    ('C2',[0,1],[1,1],1,2),
    ('C3',[0,0,1],[1,1,1],1,3),
    ('C4',[0,0,0,1],[1,1,1,1],1,4),
]

def sequence(init, coeff, constant, length):
    s=list(map(F,init)); d=len(coeff)
    while len(s)<length:
        s.append(F(constant)+sum(F(a)*s[-i] for i,a in enumerate(coeff,1)))
    return s[:length]

def solve_exact(A,b):
    if not A:return None
    n=len(A[0]); mat=[list(map(F,row))+[F(y)] for row,y in zip(A,b)]
    pivot=[];r=0
    for j in range(n):
        row=next((i for i in range(r,len(mat)) if mat[i][j]),None)
        if row is None:continue
        mat[r],mat[row]=mat[row],mat[r]
        z=mat[r][j];mat[r]=[v/z for v in mat[r]]
        for i in range(len(mat)):
            if i!=r:
                z=mat[i][j]
                if z:mat[i]=[v-z*w for v,w in zip(mat[i],mat[r])]
        pivot.append(j);r+=1
    if any(all(v==0 for v in row[:n]) and row[-1]!=0 for row in mat):return None
    if len(pivot)!=n:return None
    return tuple(mat[i][-1] for i in range(n))

def fit_lag(train,d):
    if len(train)<=d:return None
    A=[[F(1)]+[train[t-i] for i in range(1,d+1)] for t in range(d,len(train))]
    y=train[d:]
    return solve_exact(A,y)

def discover(train,max_lag=4):
    for d in range(max_lag+1):
        x=fit_lag(train,d)
        if x is not None:return d,x
    return None

def predict(history,coef,length):
    d=len(coef)-1;hist=list(history)
    for _ in range(length):
        hist.append(coef[0]+sum(coef[i]*hist[-i] for i in range(1,d+1)))
    return hist[-length:]

def run():
    results=[];checks=0
    for name,init,coeff,c,expected in CASES:
        series=sequence(init,coeff,c,40)
        train=series[:28];test=series[28:]
        found=discover(train)
        assert found and found[0]==expected,(name,found);checks+=1
        d,parameters=found
        predicted=predict(train,parameters,12)
        for a,b in zip(predicted,test):assert a==b,(name,a,b);checks+=1
        for k in range(d):assert fit_lag(train,k) is None;checks+=1
        results.append(dict(id=name,lag=d,coefficients=list(map(str,parameters)),holdout=12,passed=True))
    assert discover([F(0),F(1)]) is None;checks+=1
    aliased=sequence([0,1,1,2],[1,1,0,0],0,40)
    alias=discover(aliased[:28]);assert alias and alias[0]==2;checks+=1
    assert predict(aliased[:28],alias[1],12)==aliased[28:];checks+=1
    damaged=sequence([0,1],[1,1],1,40)[:28];damaged[17]+=F(1)
    assert discover(damaged) is None;checks+=1
    assert fit_lag([F(1)]*6,4) is None;checks+=1
    return {'assertions':checks,'results':results,'counterexamples':{'short_unidentified':True,'authored_order4_observable_order2':True,'single_tamper_rejected':True,'constant_high_lag_rank_deficient':True}}
if __name__=='__main__': print(json.dumps(run(),indent=2))
