"""SG021: exact rational governing-law discovery. Python 3 stdlib."""
from fractions import Fraction as F
from itertools import product
import json
def solve(rows,outputs):
 n=len(rows[0]);A=[list(map(F,row))+[F(y)] for row,y in zip(rows,outputs)]
 pivots=[];r=0
 for c in range(n):
  k=next((k for k in range(r,len(A)) if A[k][c]),None)
  if k is None:continue
  A[r],A[k]=A[k],A[r];z=A[r][c];A[r]=[v/z for v in A[r]]
  for i in range(len(A)):
   if i!=r:
    z=A[i][c]
    if z:A[i]=[v-z*w for v,w in zip(A[i],A[r])]
  pivots.append(c);r+=1
 if any(all(x==0 for x in row[:n]) and row[n]!=0 for row in A):return None
 if len(pivots)!=n:return None
 return tuple(A[k][-1] for k in range(n))
def fit(xs,ys,kind,a=0,b=0):
 if kind=='poly':
  z=solve([[x**i for i in range(a+1)] for x in xs],ys)
  if z is None:return None
  def pred(x):return sum(z[i]*x**i for i in range(a+1))
 elif kind=='hinge':
  z=solve([[F(1),x,max(F(0),x)] for x in xs],ys)
  if z is None:return None
  def pred(x):return z[0]+z[1]*x+z[2]*max(F(0),x)
 else:
  z=solve([[x**i for i in range(a+1)]+[-y*x**i for i in range(1,b+1)] for x,y in zip(xs,ys)],ys)
  if z is None:return None
  def pred(x):
   den=1+sum(z[a+i]*x**i for i in range(1,b+1))
   return None if den==0 else sum(z[i]*x**i for i in range(a+1))/den
 if any(pred(x)!=y for x,y in zip(xs,ys)):return None
 return (kind,a,b,z,pred)
def discover(xs,ys):
 opts=[]
 for degree in range(3):
  t=fit(xs,ys,'poly',degree)
  if t:opts.append(t)
 t=fit(xs,ys,'hinge')
 if t:opts.append(t)
 for a,b in product(range(3),(1,2)):
  t=fit(xs,ys,'rational',a,b)
  if t:opts.append(t)
 return sorted(opts,key=lambda x:(len(x[3]),{'poly':0,'hinge':1,'rational':2}[x[0]],x[1],x[2]))
def systems():
 return {'A':lambda x:2*x+1,'B':lambda x:x*x-x+2,'C':lambda x:1-x+3*max(F(0),x),'D':lambda x:(x+1)/(x*x+1)}
def run():
 xs=[F(x) for x in range(-5,6)]
 held=[F(k,2) for k in (-11,-9,-7,-5,-3,-1,1,3,5,7,9,11)]+[F(-6),F(6)]
 rows=[];checks=0
 for name,fn in systems().items():
  opts=discover(xs,[fn(x) for x in xs]);assert opts;checks+=1
  kind,a,b,z,pred=opts[0]
  for x in held:assert pred(x)==fn(x);checks+=1
  assert all(pred(x)==fn(x) for x in xs);checks+=1
  rows.append(dict(id=name,family=kind,degree=[a,b],coefficients=list(map(str,z)),heldout=14,valid_candidate_count=len(opts)))
 train=[(F(a),F(b)) for a,b in [(-2,1),(-1,1),(0,1),(1,1),(2,1),(1,0),(1,2),(2,3),(0,0),(3,2)]]
 next_state=lambda prev,cur:2*cur-prev+1
 c=solve([[F(1),cur,prev] for prev,cur in train],[next_state(prev,cur) for prev,cur in train])
 assert c==(F(1),F(2),F(-1));checks+=1
 unseen=[(F(-5),F(2)),(F(9),F(1)),(F(0),F(-4)),(F(5,2),F(1,3)),(F(7),F(7)),(F(-1,2),F(2,3))]
 for prev,cur in unseen:assert c[0]+c[1]*cur+c[2]*prev==next_state(prev,cur);checks+=1
 assert next_state(F(0),F(1))!=next_state(F(1),F(1));checks+=1
 q=systems()['B'];assert q(F(0))==q(F(1))==2;checks+=1
 assert q(F(2))!=2;checks+=1
 assert fit([F(0),F(1)],[F(2),F(2)],'poly',2) is None;checks+=1
 assert checks==75
 return dict(assertions=checks,one_step=rows,recurrence_coefficients=list(map(str,c)),recurrence_heldout=6,controls=['short history is ambiguous','current state alone insufficient'])
if __name__=='__main__':print(json.dumps(run(),indent=2))
