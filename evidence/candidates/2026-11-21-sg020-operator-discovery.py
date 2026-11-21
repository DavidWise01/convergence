"""SG-020: dictionary-free reconstruction of unknown rational operators.
Python 3, standard library. Exact arithmetic; seed fixes data.
"""
from fractions import Fraction as Q
from random import Random
import json
n=7
def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def mv(A,x):return tuple(dot(row,x) for row in A)
def tr(A):return tuple(zip(*A))
def mm(A,B):return tuple(tuple(dot(row,col) for col in tr(B)) for row in A)
def ident():return tuple(tuple(Q(i==j) for j in range(n)) for i in range(n))
def echelon(A,b=None):
 m=[list(map(Q,row))+([] if b is None else [Q(b[i])]) for i,row in enumerate(A)]
 r=0
 for j in range(n):
  k=next((k for k in range(r,len(m)) if m[k][j]),None)
  if k is None:continue
  m[r],m[k]=m[k],m[r];z=m[r][j];m[r]=[x/z for x in m[r]]
  for k in range(len(m)):
   if k!=r:
    z=m[k][j];m[k]=[x-z*y for x,y in zip(m[k],m[r])]
  r+=1
  if r==len(m):break
 return (r,m)
def rank(A):return echelon(A)[0]
def learn(samples):
 X=tuple(tuple(samples[j][0][i] for j in range(n)) for i in range(n))
 Y=tuple(tuple(samples[j][1][i] for j in range(n)) for i in range(n))
 if rank(X)<n:raise ValueError('underidentified')
 XT=tr(X)
 return tuple(tuple(echelon(XT,Y[i])[1][j][-1] for j in range(n)) for i in range(n))
def fp(A):
 I=ident();one=(Q(1),)*n
 L=tuple(tuple(A[i][j]-I[i][j] for j in range(n)) for i in range(n))
 R=tr(L);rot=tuple(tuple(Q(i==(j+1)%n) for j in range(n)) for i in range(n))
 return dict(mass=mv(tr(A),one)==one,constant=mv(A,one)==one,
             left_fixed=n-rank(R),right_fixed=n-rank(L),
             rotation=mm(A,rot)==mm(rot,A),invertible=rank(A)==n)
def systems():
 A=tuple(tuple(Q(1,2)*(i==j)+Q(1,3)*(i==(j+1)%n)+Q(1,6)*(i==(j-1)%n)
       for j in range(n)) for i in range(n))
 B=tuple(tuple(Q([2,1,3,1,5,2,1][i],[1,2,2,3,4,5,7][i]) if i==j else Q(0)
       for j in range(n)) for i in range(n))
 C=[[Q(0) for j in range(n)] for i in range(n)]
 for j in range(n):
  w=Q(j+1,j+4);C[j][j]=1-w;C[(j+1)%n][j]=w
 return {'A':A,'B':B,'C':tuple(tuple(row) for row in C)}
def run():
 rng=Random(20261121);out=[];checks=0;truth=systems()
 for name,A in truth.items():
  while True:
   x=[tuple(Q(rng.randint(-4,4)) for j in range(n)) for i in range(n)]
   if rank(tr(x))==n:break
  M=learn([(v,mv(A,v)) for v in x])
  assert M==A;checks+=1
  assert fp(M)==fp(A);checks+=1
  for k in range(20):
   v=tuple(Q(rng.randint(-12,12),rng.randint(1,9)) for j in range(n))
   assert mv(M,v)==mv(A,v);checks+=1
  for k in range(4):
   v=tuple(Q(rng.randint(-7,7)) for j in range(n))
   assert mv(M,mv(M,v))==mv(A,mv(A,v));checks+=1
  out.append(dict(system=name,invariants=fp(M),heldout=20,two_step=4))
 basis=[tuple(Q(i==j) for i in range(n)) for j in range(n)]
 A=truth['A'];C=tuple(tuple(A[i][j]+(Q(5) if (i,j)==(0,6) else Q(0)) for j in range(n)) for i in range(n))
 assert A!=C;checks+=1
 for v in basis[:6]:
  assert mv(A,v)==mv(C,v);checks+=1
 assert mv(A,basis[6])!=mv(C,basis[6]);checks+=1
 try:learn([(v,mv(A,v)) for v in basis[:6]+basis[:1]])
 except ValueError:checks+=1
 else:raise AssertionError('expected rank-deficiency')
 assert fp(truth['A'])['mass'] and fp(truth['A'])['rotation'];checks+=1
 assert not fp(truth['B'])['mass'] and not fp(truth['B'])['rotation'];checks+=1
 assert fp(truth['C'])['mass'] and not fp(truth['C'])['rotation'];checks+=1
 assert checks==90
 return dict(checks=checks,results=out,negative_control='Six basis probes cannot distinguish A from A+5e0e6^T')
if __name__=='__main__':print(json.dumps(run(),indent=2))
