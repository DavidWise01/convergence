"""SG-009: orthogonal orbit oscillator, numerical cyclotomic check."""
import numpy as np
from itertools import product
from collections import Counter

def construct(p,n):
    U=list(product(range(p),repeat=2*n))
    q=lambda u:sum(u[i]*u[i+n] for i in range(n))%p
    bil=lambda u,v:sum(u[i]*v[i+n]+u[i+n]*v[i] for i in range(n))%p
    group=lambda u:0 if not any(u) else (1 if q(u)==0 else 1+q(u))
    orbits=[[] for _ in range(p+1)]
    for u in U:orbits[group(u)].append(u)
    assert all(orbits)
    reps=[o[0] for o in orbits]
    omega=np.exp(2j*np.pi/p)
    f=np.zeros((p+1,p+1),complex)
    for i,u in enumerate(reps):
        for j,oj in enumerate(orbits):
            hist=Counter(bil(u,v) for v in oj)
            f[i,j]=sum(c*omega**t for t,c in hist.items())/(p**n)
    Q=np.diag([omega**q(u) for u in reps])
    d=p+1
    I=np.eye(d,dtype=complex)
    errF=np.max(np.abs(f@f-I))
    cube=np.linalg.matrix_power(f@Q,3)
    cubeErr=np.max(np.abs(cube-I))
    A=np.vstack([np.kron(f.T,I)-np.kron(I,f),np.kron(Q.T,I)-np.kron(I,Q)])
    sv=np.linalg.svd(A,compute_uv=False)
    dimcomm=int(np.sum(sv<1.e-7))
    fixed=np.zeros(d,dtype=complex)
    fixed[0]=1+p**(n-1)
    fixed[1]=1
    fixed_err=max(np.max(np.abs(f@fixed-fixed)),np.max(np.abs(Q@fixed-fixed)))
    assert fixed_err<1e-8 and errF<1e-8 and cubeErr<1e-8 and dimcomm==2
    return (p,n,p**(2*n),list(map(len,orbits)),dimcomm,float(errF),float(cubeErr),float(fixed_err))

if __name__=='__main__':
    for p,n in [(3,1),(5,1),(7,1),(3,2),(5,2),(3,3)]:
        print(construct(p,n))
