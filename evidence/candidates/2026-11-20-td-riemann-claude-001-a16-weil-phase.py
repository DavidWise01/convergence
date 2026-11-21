"""SG-016. Exact cyclotomic Weil phase test; Python standard library only."""
from fractions import Fraction as Q
from itertools import product
states=list(product(range(3),repeat=2));n=9
Z=(Q(0),Q(0));ONE=(Q(1),Q(0))
def add(x,y):return x[0]+y[0],x[1]+y[1]
def mul(x,y):
 a,b=x;c,d=y
 return a*c-b*d,a*d+b*c-b*d
def zeta(k):return (ONE,(Q(0),Q(1)),(Q(-1),Q(-1)))[k%3]
def total(xs):
 s=Z
 for x in xs:s=add(s,x)
 return s
def times(a,b):return [[total(mul(a[i][k],b[k][j]) for k in range(n)) for j in range(n)] for i in range(n)]
def equal(a,b):return a==b
def diag(vals):return [[vals[i] if i==j else Z for j in range(n)] for i in range(n)]
def ident():return diag([ONE]*n)
def negative(a):return [[(-x,-y) for x,y in row] for row in a]
F=[[tuple(v/3 for v in zeta(2*sum(a*b for a,b in zip(x,y)))) for y in states] for x in states]
T=diag([zeta(sum(t*t for t in x)) for x in states])
I=ident();P=[[ONE if states[i]==tuple(-t%3 for t in states[j]) else Z for j in range(n)] for i in range(n)]
F2=times(F,F);T2=times(T,T);FT=times(F,T)
assert equal(F2,P) and equal(times(F2,F2),I) and equal(times(T2,T),I)
assert equal(times(times(FT,FT),FT),negative(I))
minusFT=negative(FT)
assert equal(times(times(minusFT,minusFT),minusFT),I)
def W(a,b):
 M=[[Z for _ in range(n)] for _ in range(n)]
 for j,x in enumerate(states):
  y=tuple((x[k]+a[k])%3 for k in range(2))
  M[states.index(y)][j]=zeta(sum(a[k]*b[k]+2*b[k]*x[k] for k in range(2)))
 return M
Tinv=T2;Finv=times(F2,F)
for a in states:
 for b in states:
  w=W(a,b);newb=tuple((b[k]+a[k])%3 for k in range(2));newa=tuple(-b[k]%3 for k in range(2))
  assert equal(times(times(T,w),Tinv),W(a,newb))
  assert equal(times(times(F,w),Finv),W(newa,a))
def mm4(a,b):return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(4))%3 for j in range(4)) for i in range(4))
S=((0,0,2,0),(0,0,0,2),(1,0,0,0),(0,1,0,0))
U=((1,0,0,0),(0,1,0,0),(1,0,1,0),(0,1,0,1))
su=mm4(S,U)
assert mm4(mm4(su,su),su)==tuple(tuple(int(i==j) for j in range(4)) for i in range(4))
print("PASS: F^2=P; F^4=T^3=I; (FT)^3=-I; ((-F)T)^3=I; 162 Weyl covariance identities")
