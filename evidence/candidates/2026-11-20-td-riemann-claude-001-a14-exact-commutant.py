"""SG014 exact commutant proof certificate. Python 3 stdlib only."""
from itertools import product
from collections import deque
p=3
G=[(a,b,c,d,1 if (a*d-b*c)%3==1 else -1)
   for a,b,c,d in product(range(3),repeat=4)
   if (a*a+c*c-1)%3==0 and (b*b+d*d-1)%3==0 and (a*b+c*d)%3==0]
def act(g,v):
 a,b,c,d,_=g
 return tuple(z for k in range(0,6,2) for z in
              ((a*v[k]+b*v[k+1])%3,(c*v[k]+d*v[k+1])%3))
rem=set(product(range(3),repeat=6));orbs=[];labels={}
while rem:
 seed=min(rem); signs={};bad=False
 for g in G:
  w=act(g,seed)
  if w in signs and signs[w]!=g[-1]:bad=True
  signs[w]=g[-1]
 rem-=set(signs)
 if not bad:
  idx=len(orbs);orbs.append(signs)
  for v,s in signs.items():labels[v]=(idx,s)
n=len(orbs);assert n==78 and all(len(o)==8 for o in orbs)
reps=[next(v for v,s in o.items() if s==1) for o in orbs]
phases=[tuple((v[2*k]**2+v[2*k+1]**2)%3 for k in range(3))
        for v in reps]
pairs=[(0,1),(1,0),(1,2),(2,1)]
shears=[]
for a,b in pairs:
 mapping=[]
 for v in reps:
  w=list(v);w[2*a]=(w[2*a]+v[2*b])%3
  w[2*a+1]=(w[2*a+1]+v[2*b+1])%3
  mapping.append(labels[tuple(w)])
 assert sorted(i for i,s in mapping)==list(range(n))
 shears.append(mapping)
for k,(a,b) in enumerate(pairs):
 for col,o in enumerate(orbs):
  row,sgn0=shears[k][col]
  for v,sgn in o.items():
   w=list(v);w[2*a]=(w[2*a]+v[2*b])%3
   w[2*a+1]=(w[2*a+1]+v[2*b+1])%3
   assert labels[tuple(w)]==(row,sgn*sgn0)
for o in orbs:
 for k in range(3):
  assert len({(v[2*k]**2+v[2*k+1]**2)%3 for v in o})==1
def commutant_orbits(generators):
 seen=set();survivors=[];killed=0
 for i in range(n):
  for j in range(n):
   if (i,j) in seen:continue
   orbit={(i,j):1};todo=deque([(i,j)]);bad=False
   while todo:
    a,b=todo.popleft();sgn=orbit[(a,b)]
    if phases[a]!=phases[b]:bad=True
    for g in generators:
     aa,sa=g[a];bb,sb=g[b];pair=(aa,bb);value=sgn*sa*sb
     if pair in orbit:
      if orbit[pair]!=value:bad=True
     else:orbit[pair]=value;todo.append(pair)
   seen.update(orbit)
   if bad:killed+=1
   else:survivors.append(orbit)
 assert len(seen)==n*n
 return survivors,killed
complete,killed=commutant_orbits(shears)
partial,_=commutant_orbits(shears[:2])
assert len(complete)==1 and killed==6
assert complete[0]=={(i,i):1 for i in range(n)}
assert len(partial)==15
print('EXACT PASS: dimension=78, coordinates=6084, commutant=1, missing-coupling control=15')
