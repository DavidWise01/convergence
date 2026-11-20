"""SG-012 exact tower-extension witness: Python standard library."""
from itertools import product
from fractions import Fraction
def orthogonal(p):
 return [(a,b,c,d,1 if (a*d-b*c)%p==1 else -1)
         for a,b,c,d in product(range(p),repeat=4)
         if (a*a+c*c-1)%p==0 and (b*b+d*d-1)%p==0 and (a*b+c*d)%p==0]
def move(g,w,p):
 a,b,c,d,_=g
 return tuple(z for j in range(0,len(w),2)
              for z in ((a*w[j]+b*w[j+1])%p,(c*w[j]+d*w[j+1])%p))
def orbits(p,m,G):
 remaining=set(product(range(p),repeat=2*m));good=[]
 while remaining:
  seed=min(remaining);signs={};conflict=False
  for g in G:
   w=move(g,seed,p)
   if w in signs and signs[w]!=g[4]: conflict=True
   signs[w]=g[4]
  assert set(signs)<=remaining
  remaining.difference_update(signs)
  if not conflict:good.append(min(signs))
 return good
def character_rank(p,m,G):
 total=0
 for g in G:
  fixed=sum(move(g,w,p)==w for w in product(range(p),repeat=2))
  total+=g[4]*fixed**m
 assert total%len(G)==0
 return total//len(G)
def test(p,m):
 G=orthogonal(p)
 low=orbits(p,m,G); high=orbits(p,m+1,G)
 assert len(low)==character_rank(p,m,G)
 assert len(high)==character_rank(p,m+1,G)
 assert {w+(0,0) for w in low}.issubset(set(high))
 # Fourier on a newly appended zero pair: F delta_0=p^-1 sum_{z in Fp^2}delta_z.
 retained=Fraction(1,p*p); leakage=1-retained
 assert leakage>0 and retained+leakage==1
 return (p,m,len(low),len(high),str(retained),str(leakage))
if __name__=="__main__":
 expected=[(3,2,6,78,"1/9","8/9"),(5,1,1,66,"1/25","24/25"),
           (3,1,0,6,"1/9","8/9"),(5,2,66,1891,"1/25","24/25")]
 for e in expected:
  got=test(e[0],e[1]);assert got==e;print(got)
 print("PASS: four exact tower-extension regression cases")
