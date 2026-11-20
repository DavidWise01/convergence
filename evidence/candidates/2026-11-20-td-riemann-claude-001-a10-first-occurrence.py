"""SG-010: determinant character first occurrence in finite theta rank tower.
Exact integers only. Python 3 standard library.
"""
from itertools import product
from collections import Counter

def determinant(a,p):
 n=len(a); m=[list(row) for row in a]; d=1
 for j in range(n):
  k=next((k for k in range(j,n) if m[k][j]%p),None)
  if k is None:return 0
  if k!=j:m[j],m[k]=m[k],m[j];d=-d
  t=m[j][j]%p;d=d*t%p;z=pow(t,-1,p)
  for k in range(j+1,n):
   c=m[k][j]*z%p
   for l in range(j,n):m[k][l]=(m[k][l]-c*m[j][l])%p
 return d%p

def fixed_dimension(a,p):
 n=len(a);m=[[(a[i][j]-(i==j))%p for j in range(n)] for i in range(n)];rank=0
 for j in range(n):
  q=next((i for i in range(rank,n) if m[i][j]),None)
  if q is None:continue
  m[rank],m[q]=m[q],m[rank];z=pow(m[rank][j],-1,p)
  for i in range(rank+1,n):
   c=m[i][j]*z%p
   for k in range(j,n):m[i][k]=(m[i][k]-c*m[rank][k])%p
  rank+=1
 return n-rank

def orthogonal(n,p):
 vectors=list(product(range(p),repeat=n))
 dot=lambda a,b:sum(x*y for x,y in zip(a,b))%p
 def build(columns):
  j=len(columns)
  if j==n:
   yield tuple(tuple(columns[k][i] for k in range(n)) for i in range(n));return
  for v in vectors:
   if dot(v,v)==1 and all(dot(v,w)==0 for w in columns):
    yield from build(columns+[v])
 return list(build([]))

def run(n,p,depth=4):
 group=orthogonal(n,p)
 counts=Counter((fixed_dimension(g,p),1 if determinant(g,p)==1 else -1) for g in group)
 multiplicity=[]
 for m in range(depth+1):
  numerator=sum(sign*count*p**(m*d) for (d,sign),count in counts.items())
  assert numerator%len(group)==0
  value=numerator//len(group)
  assert value>=0
  multiplicity.append(value)
 assert multiplicity[0]==0
 return dict(N=n,p=p,group_size=len(group),fixed_dimension_character_counts=sorted((d,s,c) for (d,s),c in counts.items()),multiplicity=multiplicity,first_occurrence=next((m for m,a in enumerate(multiplicity) if a>0),None))

if __name__=="__main__":
 expected={(2,3):[0,0,6,78,780],(2,5):[0,1,66,1891,48516],(2,7):[0,0,126,7182,359100],(3,3):[0,0,4,286,9880],(3,5):[0,0,12,6572,976872]}
 for (n,p),values in expected.items():
  out=run(n,p)
  assert out["multiplicity"]==values
  print(out)
