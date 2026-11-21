"""SG-019 blind finite-operator identification, exact arithmetic (stdlib)."""
from fractions import Fraction as F
from itertools import product
import json

def matvec(M,v): return tuple(sum(a*x for a,x in zip(row,v)) for row in M)
def eye(n): return tuple(tuple(F(i==j) for j in range(n)) for i in range(n))
def matrix(n,kind):
    if kind=='identity': return eye(n)
    if kind=='right_shift': return tuple(tuple(F(i==(j+1)%n) for j in range(n)) for i in range(n))
    if kind=='left_shift': return tuple(tuple(F(j==(i+1)%n) for j in range(n)) for i in range(n))
    if kind=='amplify2': return tuple(tuple(F(2*(i==j)) for j in range(n)) for i in range(n))
    if kind=='cycle_diffusion': return tuple(tuple(F((i==j)+(i==(j+1)%n)+(i==(j-1)%n),3) for j in range(n)) for i in range(n))
    if kind=='biased_diffusion': return tuple(tuple(F(i==j,2)+F(i==(j+1)%n,3)+F(i==(j-1)%n,6) for j in range(n)) for i in range(n))
    if kind=='defect_diffusion':
        W=[[F(0) for j in range(n)] for i in range(n)]
        for i in range(n):
            j=(i+1)%n; w=F(2 if i==0 else 1); W[i][j]=W[j][i]=w
        return tuple(tuple(F(i==j)-(sum(W[i]) if i==j else -W[i][j])/5 for j in range(n)) for i in range(n))
    raise ValueError(kind)
KINDS=('identity','right_shift','left_shift','amplify2','cycle_diffusion','biased_diffusion','defect_diffusion')

def fingerprint(M):
    n=len(M); one=tuple([F(1)]*n)
    mass=all(sum(M[i][j] for i in range(n))==1 for j in range(n))
    constant=matvec(M,one)==one
    R=matrix(n,'right_shift')
    equiv=all(sum(M[i][k]*R[k][j] for k in range(n))==sum(R[i][k]*M[k][j] for k in range(n)) for i in range(n) for j in range(n))
    return dict(mass=mass,uniform_fixed=constant,rotation_equivariant=equiv)

def learn(train, models):
    return sorted(name for name,M in models.items() if all(matvec(M,x)==y for x,y in train))

def run():
    n=7; models={name:matrix(n,name) for name in KINDS}
    # Training probes are identical for every hidden candidate; labels hidden from inference.
    probes=[tuple(F(int(j==0)) for j in range(n)),tuple(F(j*j-2*j+3) for j in range(n))]
    heldout=[tuple(F((j*3+5)%11-5) for j in range(n)),tuple(F(j+1,j+2) for j in range(n)),tuple(F(int(j==3)) for j in range(n))]
    results=[];checks=0
    for secret in KINDS:
        truth=models[secret];train=[(v,matvec(truth,v)) for v in probes]
        fit=learn(train,models)
        assert fit==[secret],(secret,fit);checks+=1
        recovered=models[fit[0]]
        for v in heldout:
            assert matvec(recovered,v)==matvec(truth,v);checks+=1
        assert fingerprint(recovered)==fingerprint(truth);checks+=1
        results.append(dict(hidden_id='H'+str(len(results)+1),recovered=fit[0],unique=True,holdout_pass=3,fingerprint=fingerprint(recovered)))
    # Counterexample: uniform probe cannot identify even basic conservative operators.
    uniform=tuple([F(1)]*n)
    candidates=learn([(uniform,uniform)],models)
    assert len(candidates)>1 and 'identity' in candidates and 'cycle_diffusion' in candidates;checks+=1
    # Single impulse identifies all our fixed candidates, but does not prove identifiability of arbitrary operators.
    impulse=probes[0]
    for name,M in models.items():
        fit=learn([(impulse,matvec(M,impulse))],models)
        assert fit==[name];checks+=1
    # Full linear identification requires n basis probes if operator hypothesis set unrestricted.
    E=[tuple(F(int(j==i)) for j in range(n)) for i in range(n)]
    for M in models.values():
        cols=[matvec(M,v) for v in E]
        reconstruct=tuple(tuple(cols[j][i] for j in range(n)) for i in range(n))
        assert reconstruct==M;checks+=1
    return {'n':n,'model_count':len(models),'training_probes':len(probes),'heldout_probes':len(heldout),'results':results,'uniform_ambiguity':candidates,'exact_checks':checks,'generalization_limit':'finite candidate dictionary only; arbitrary operators need basis identification'}

if __name__=='__main__': print(json.dumps(run(),indent=2))
