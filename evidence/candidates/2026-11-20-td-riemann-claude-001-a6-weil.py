from itertools import product
def compose(a,b,p):
    return tuple((a[j][0],(e+a[j][1])%p) for j,e in b)
def W(a,b,p):
    h=pow(2,-1,p)
    return tuple(((x+a)%p,(b*x+h*a*b)%p) for x in range(p))
def Q(p):
    h=pow(2,-1,p)
    return tuple((x,h*x*x%p) for x in range(p))
def parity(p): return tuple((-x%p,0) for x in range(p))
def run(p):
    checks=0; h=pow(2,-1,p)
    for a,b,c,d in product(range(p),repeat=4):
        target=tuple((j,(e+h*(b*c-a*d))%p) for j,e in W(a+c,b+d,p))
        assert compose(W(a,b,p),W(c,d,p),p)==target; checks+=1
    for a,b in product(range(p),repeat=2):
        assert compose(Q(p),W(a,b,p),p)==compose(W(a,b+a,p),Q(p),p); checks+=1
        for x,y in product(range(p),repeat=2):
            assert (b*y+h*a*b+x*(y+a)-(a*(x+b)-h*a*b+(x+b)*y))%p==0; checks+=1
    assert compose(parity(p),Q(p),p)==compose(Q(p),parity(p),p); checks+=1
    for x,y in product(range(p),repeat=2):
        assert ((-x)*y-x*(-y))%p==0; checks+=1
    for x,y in product(range(p),repeat=2):
        hist=[0]*p
        for z in range(p): hist[(x+y)*z%p]+=1
        assert hist==([p]+[0]*(p-1) if (x+y)%p==0 else [1]*p); checks+=1
    assert h%p != 0; checks+=1
    return checks, (p+1)//2,(p-1)//2
if __name__=='__main__':
    for p in (3,5,7,11,13,17,19): print(p,*run(p))
