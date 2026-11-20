"""SG-011: irreducibility test of determinant-isotypic finite oscillator sectors.
Python 3 with NumPy. Numerical SVD tolerance 1e-8.
"""
import itertools
import json
import numpy as np

def orthogonal_two(p):
    out=[]
    for a,b,c,d in itertools.product(range(p),repeat=4):
        if (a*a+c*c)%p!=1 or (b*b+d*d)%p!=1 or (a*b+c*d)%p!=0:
            continue
        det=(a*d-b*c)%p
        assert det in (1,p-1)
        out.append(((a,b),(c,d),1 if det==1 else -1))
    return out

def run(p,m):
    states=list(itertools.product(range(p),repeat=2*m))
    index={v:i for i,v in enumerate(states)}
    D=len(states)
    group=orthogonal_two(p)
    P=np.zeros((D,D),dtype=complex)
    for a,b,sgn in group:
        for j,v in enumerate(states):
            w=[]
            for k in range(m):
                x,y=v[2*k:2*k+2]
                w.extend(((a[0]*x+a[1]*y)%p,(b[0]*x+b[1]*y)%p))
            P[index[tuple(w)],j]+=sgn/len(group)
    assert np.max(np.abs(P@P-P))<1e-11
    vals,vecs=np.linalg.eigh(P)
    B=vecs[:,vals>0.5]
    d=B.shape[1]
    assert d=={(5,1):1,(3,2):6}[(p,m)]

    def fourier(slot):
        M=np.zeros((D,D),dtype=complex)
        for j,v in enumerate(states):
            x,y=v[2*slot:2*slot+2]
            for a,b in itertools.product(range(p),repeat=2):
                w=list(v)
                w[2*slot:2*slot+2]=[a,b]
                M[index[tuple(w)],j]=np.exp(2j*np.pi*(2*(x*a+y*b)%p)/p)/p
        return M

    def phase(slot):
        return np.diag([np.exp(2j*np.pi*((v[2*slot]**2+v[2*slot+1]**2)%p)/p) for v in states])

    operators=[]
    for k in range(m):
        operators.extend([('F'+str(k),fourier(k)),('T'+str(k),phase(k))])
    if m>=2:
        M=np.zeros((D,D),dtype=complex)
        for j,v in enumerate(states):
            w=list(v)
            w[2:4]=[(v[2]+v[0])%p,(v[3]+v[1])%p]
            M[index[tuple(w)],j]=1
        operators.append(('GL_shear',M))

    compressed=[]
    max_leak=0
    max_unitary=0
    for name,M in operators:
        max_leak=max(max_leak,float(np.linalg.norm((np.eye(D)-P)@M@B)))
        C=B.conj().T@M@B
        max_unitary=max(max_unitary,float(np.linalg.norm(C.conj().T@C-np.eye(d))))
        compressed.append((name,C))
    equations=np.vstack([np.kron(C.T,np.eye(d))-np.kron(np.eye(d),C) for _,C in compressed])
    singular=np.linalg.svd(equations,compute_uv=False)
    commutant_dimension=int(np.sum(singular<1e-8))
    gap=float(min((s for s in singular if s>=1e-8),default=0))
    assert max_leak<1e-10 and max_unitary<1e-10 and commutant_dimension==1
    return dict(p=p,m=m,ambient_dimension=D,det_dimension=d,orthogonal_order=len(group),
                commutant_dimension=commutant_dimension,max_leak=max_leak,
                max_unitarity_error=max_unitary,commutant_singular_gap=gap,
                generators=[name for name,_ in compressed])

if __name__=='__main__':
    for p,m in [(5,1),(3,2)]:
        print(json.dumps(run(p,m),indent=2))
