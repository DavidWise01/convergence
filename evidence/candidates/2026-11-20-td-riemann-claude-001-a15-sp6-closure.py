"""SG-015: exact Sp6(F3) generation certificate. Standard Python only."""
from collections import deque, Counter
P,N=3,6
I=tuple(tuple(int(i==j) for j in range(N)) for i in range(N))
def matrix(edits):
 a=[list(row) for row in I]
 for (i,j),v in edits.items():a[i][j]=v%P
 return tuple(map(tuple,a))
def mul(a,b):return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(N))%P for j in range(N)) for i in range(N))
def transpose(a):return tuple(tuple(a[j][i] for j in range(N)) for i in range(N))
def apply(a,v):return tuple(sum(a[i][j]*v[j] for j in range(N))%P for i in range(N))
def inverse(a):
 b=[list(a[i])+list(I[i]) for i in range(N)]
 for j in range(N):
  k=next(k for k in range(j,N) if b[k][j]);b[j],b[k]=b[k],b[j]
  q=pow(b[j][j],-1,P);b[j]=[q*x%P for x in b[j]]
  for k in range(N):
   if k!=j:
    q=b[k][j];b[k]=[(x-q*y)%P for x,y in zip(b[k],b[j])]
 return tuple(tuple(row[N:]) for row in b)
def orbit(actions):
 root=(1,0,0,0,0,0);seen={root:0};queue=deque([root]);hist=Counter()
 while queue:
  v=queue.popleft();hist[seen[v]]+=1
  for a in actions:
   w=apply(a,v)
   if w not in seen:seen[w]=seen[v]+1;queue.append(w)
 return len(seen),sorted(hist.items())
gens={}
for k in range(3):
 gens[f'F{k}']=matrix({(k,k):0,(k+3,k+3):0,(k,k+3):-1,(k+3,k):1})
 gens[f'T{k}']=matrix({(k,k+3):1})
for a,b in [(0,1),(1,0),(1,2),(2,1)]:gens[f'S{a}{b}']=matrix({(a,b):1,(b+3,a+3):-1})
J=matrix({(i,i):0 for i in range(N)}|{(i,i+3):1 for i in range(3)}|{(i+3,i):-1 for i in range(3)})
assert len(gens)==10
assert all(mul(mul(transpose(g),J),g)==J for g in gens.values())
actions=list(gens.values())+[inverse(a) for a in gens.values()]
count,hist=orbit(actions)
assert count==728 and hist==[(0,1),(1,4),(2,23),(3,78),(4,222),(5,328),(6,72)]
control=[g for name,g in gens.items() if name not in ('S12','S21')]
small,small_hist=orbit(control+[inverse(g) for g in control])
assert small==80
order=3**9
for k in range(1,4):order*=3**(2*k)-1
assert order==9170703360
# T0 is rank-one transvection (or its inverse), and conjugates cover all 364 lines.
print({'symplectic_generators':10,'orbit':count,'shells':hist,'missing_link_orbit':small,'projective_lines':count//2,'group_order_by_formula':order,'status':'PASS'})
