from collections import Counter
from itertools import product

def run():
    rows=[]; checks=0
    for p in (3,5,7,11,19):
        plane=Counter(x*y%p for x,y in product(range(p),repeat=2))
        dist=Counter({0:1})
        for n in range(1,9):
            dist=Counter({t:sum(dist[s]*plane[(t-s)%p] for s in range(p)) for t in range(p)})
            assert sum(dist.values())==p**(2*n);checks+=1
            assert dist[0]==p**(2*n-1)+(p-1)*p**(n-1);checks+=1
            for t in range(1,p):
                assert dist[t]==p**(2*n-1)-p**(n-1);checks+=1
            if n<=2 and p<=7:
                brute=Counter(sum(a*b for a,b in zip(v[:n],v[n:]))%p for v in product(range(p),repeat=2*n))
                assert brute==dist;checks+=1
            rows.append((p,n,p**(2*n),dist[0],dist[1],dist[0]-dist[1],p+1))
    return checks,rows
if __name__=='__main__':
    checks,rows=run();print('checks',checks)
    for row in rows:print(*row)
