"""SG018 preregistered finite graph diffusion test. Python 3 stdlib."""
from fractions import Fraction as F
def mm(a,b):
 n=len(a)
 return [[sum(a[i][k]*b[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
def mv(a,x):return [sum(a[i][j]*x[j] for j in range(len(x))) for i in range(len(x))]
def eye(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def rot(n):return [[F(i==(j+1)%n) for j in range(n)] for i in range(n)]
def cycle(n):return [[F((i==j)+(i==(j+1)%n)+(i==(j-1)%n),3) for j in range(n)] for i in range(n)]
def defect(n):
 w=[[F(0) for _ in range(n)] for _ in range(n)]
 for i in range(n):
  j=(i+1)%n;w[i][j]=w[j][i]=F(2 if i==0 else 1)
 return [[F(i==j)-((sum(w[i]) if i==j else -w[i][j])/5) for j in range(n)] for i in range(n)]
def mass(x):return sum(x)
def variance(x):
 mean=mass(x)/len(x)
 return sum((v-mean)**2 for v in x)
def run():
 checks=0; rows=[]
 for n in [7,11,13]:
  P,R,W=cycle(n),rot(n),defect(n)
  assert mm(P,R)==mm(R,P);checks+=1
  assert mm(W,R)!=mm(R,W);checks+=1
  assert all(sum(P[i][j] for i in range(n))==1 for j in range(n));checks+=n
  assert all(sum(W[i][j] for i in range(n))==1 for j in range(n));checks+=n
  assert mv(P,[F(1)]*n)==[F(1)]*n;checks+=1
  assert mv(W,[F(1)]*n)==[F(1)]*n;checks+=1
  vectors=[[F((i*i+3*i+1)%17-8) for i in range(n)],
           [F((i+1)*(i+2),i+3) for i in range(n)],
           [F(int(i==0)) for i in range(n)]]
  first_after=None
  for vi,v in enumerate(vectors):
   x=v[:]
   for _ in range(8):
    y=mv(P,x)
    assert mass(y)==mass(x);checks+=1
    assert variance(y)<=variance(x);checks+=1
    if variance(x)>0:
     assert variance(y)<variance(x);checks+=1
    x=y
   if vi==0:first_after=variance(x)
   z=mv(R,v)
   assert mass(z)==mass(v) and variance(z)==variance(v);checks+=1
   assert mass([2*t for t in v])!=mass(v) if mass(v)!=0 else True;checks+=1
  assert mass(mv(W,vectors[0]))==mass(vectors[0]);checks+=1
  rows.append({'n':n,'initial_variance':str(variance(vectors[0])),'after8':str(first_after)})
 return checks,rows
if __name__=='__main__':
 checks,rows=run()
 assert checks==311
 print('PASS',checks,'exact rational assertions; results:',rows)
