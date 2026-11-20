"""SG-013: full adjacent-slot generator commutant test. Requires numpy/scipy.
Numerical evidence, not an exact irreducibility proof certificate.
Run with OPENBLAS_NUM_THREADS=1 python sg013.py
"""
import itertools
import json
import numpy as np
from scipy.sparse.linalg import LinearOperator, eigsh

def orthogonal(p):
    return [(a,b,c,d,1 if (a*d-b*c)%p==1 else -1)
            for a,b,c,d in itertools.product(range(p),repeat=4)
            if (a*a+c*c-1)%p==0 and (b*b+d*d-1)%p==0 and (a*b+c*d)%p==0]

def moved(g,w,p):
    a,b,c,d,_=g
    return tuple(z for j in range(0,len(w),2)
                 for z in ((a*w[j]+b*w[j+1])%p,(c*w[j]+d*w[j+1])%p))

def make_signed_orbits(p,m):
    G=orthogonal(p)
    remaining=set(itertools.product(range(p),repeat=2*m))
    orbits=[]; labels={}
    while remaining:
        seed=min(remaining); signs={}; bad=False
        for g in G:
            w=moved(g,seed,p)
            if w in signs and signs[w]!=g[-1]:bad=True
            signs[w]=g[-1]
        remaining.difference_update(signs)
        if not bad:
            idx=len(orbits)
            for v,sgn in signs.items():labels[v]=(idx,sgn)
            orbits.append(signs)
    return G,orbits,labels

def operators(p,m,full=True):
    G,orbits,labels=make_signed_orbits(p,m);n=len(orbits)
    invsqrt=np.array([1/np.sqrt(len(o)) for o in orbits])
    zeta=np.exp(2j*np.pi/p); F=[];T=[]
    for slot in range(m):
        M=np.zeros((n,n),complex)
        for col,o in enumerate(orbits):
            for v,sgn in o.items():
                for x,y in itertools.product(range(p),repeat=2):
                    w=list(v);w[2*slot:2*slot+2]=[x,y]
                    item=labels.get(tuple(w))
                    if item is None:continue
                    row,sgn2=item
                    power=(2*(x*v[2*slot]+y*v[2*slot+1]))%p
                    M[row,col]+=sgn*sgn2*invsqrt[col]*invsqrt[row]*zeta**power/p
        assert np.linalg.norm(M.conj().T@M-np.eye(n))<1e-9
        F.append(M)
        T.append(np.diag([zeta**((next(iter(o))[2*slot]**2+
                                    next(iter(o))[2*slot+1]**2)%p) for o in orbits]))
    pairs=[(j,j+1) for j in range(m-1)]+[(j+1,j) for j in range(m-1)]
    if not full:pairs=[(0,1),(1,0)] if m>=2 else []
    shears=[]
    for a,b in pairs:
        M=np.zeros((n,n),complex)
        for col,o in enumerate(orbits):
            for v,sgn in o.items():
                w=list(v)
                w[2*a]=(w[2*a]+v[2*b])%p
                w[2*a+1]=(w[2*a+1]+v[2*b+1])%p
                row,sgn2=labels[tuple(w)]
                M[row,col]+=sgn*sgn2*invsqrt[col]*invsqrt[row]
        assert np.linalg.norm(M.conj().T@M-np.eye(n))<1e-9
        shears.append(M)
    return G,orbits,F+T+shears

def run(p,m,k=10,full=True):
    G,orbits,ops=operators(p,m,full)
    n=len(orbits)
    if n==1:
        return dict(p=p,m=m,rank=1,generators=len(ops),
                    eigenvalues=[0.0],numerical_commutant_dimension=1)
    adj=[u.conj().T for u in ops]
    def mv(v):
        x=v.reshape((n,n));y=np.zeros_like(x)
        for u,uh in zip(ops,adj):
            y+=2*x-u@x@uh-uh@x@u
        return y.ravel()
    L=LinearOperator((n*n,n*n),matvec=mv,dtype=complex)
    eig=np.sort(eigsh(L,k=min(k,n*n-2),which='SM',tol=1e-7,maxiter=800,
                      return_eigenvectors=False).real)
    assert abs(eig[0])<1e-7
    return dict(p=p,m=m,rank=n,generators=len(ops),
                eigenvalues=eig.tolist(),
                numerical_commutant_dimension=int(sum(abs(x)<1e-7 for x in eig)))

if __name__=='__main__':
    for p,m in [(5,1),(3,2),(3,3)]:
        ans=run(p,m)
        assert ans['numerical_commutant_dimension']==1,ans
        print(json.dumps(ans))
    # Negative control: omitting slot-2/3 coupling gives extra null directions.
    bad=run(3,3,full=False)
    assert bad['numerical_commutant_dimension']>1,bad
    print('MISSING_COUPLING_CONTROL',json.dumps(bad))
