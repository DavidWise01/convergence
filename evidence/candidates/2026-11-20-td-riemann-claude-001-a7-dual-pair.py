from itertools import product
from collections import Counter

def run(p):
    U=list(product(range(p),repeat=2)); G=list(product(range(1,p),range(2)))
    def act(g,u):
        a,s=g; x,y=u
        if s:x,y=y,x
        return a*x%p,pow(a,-1,p)*y%p
    def q(u):return u[0]*u[1]%p
    def B(u,v):return (u[0]*v[1]+u[1]*v[0])%p
    checks=0
    for g in G:
        for u in U:
            assert q(act(g,u))==q(u);checks+=1
            for v in U:
                assert B(act(g,u),act(g,v))==B(u,v);checks+=1
    unseen=set(U);orbits=[]
    while unseen:
        u=min(unseen);orb={act(g,u) for g in G};orbits.append(orb);unseen-=orb
    assert len(orbits)==p+1;checks+=1
    assert sorted(map(len,orbits))==[1]+[p-1]*(p-1)+[2*(p-1)];checks+=1
    dims=[]
    for r,s in product(range(2),repeat=2):
        def chi(g):
            a,t=g;return (-1 if r and pow(a,(p-1)//2,p)==p-1 else 1)*(-1 if s and t else 1)
        dim=sum(all(chi(g)==1 for g in G if act(g,min(o))==min(o)) for o in orbits)
        dims.append(dim)
    assert dims==[p+1,1,(p+1)//2,(p+1)//2];checks+=1
    for u in U:
        for v in U:
            a=(u[0]+v[0])%p;b=(u[1]+v[1])%p
            hist=Counter((a*z[1]+b*z[0])%p for z in U)
            assert hist==(Counter({0:p*p}) if a==b==0 else Counter({k:p for k in range(p)}));checks+=1
    return checks,len(orbits),dims
if __name__=='__main__':
    for p in (3,5,7,11):print(p,run(p))
