"""SG017: exact rational tests of classical Navier-Stokes scaling.
Not a test of either announced proof or a causal ancestry hypothesis.
"""
from fractions import Fraction as F

def test():
    checks=0
    # Scaling u_lambda(t,x)=lambda*u(lambda^2 t,lambda x),
    # pressure p_lambda=lambda^2*p(lambda^2 t,lambda x).
    # Thus ∂t u, (u·∇)u, ∇p, νΔu all scale lambda^3.
    for lam in [F(1,2),F(2),F(3),F(5,2)]:
        time_factor=lam**2
        spatial_factor=lam
        velocity_factor=lam
        pressure_factor=lam**2
        terms=[velocity_factor*time_factor,velocity_factor**2*spatial_factor,
               pressure_factor*spatial_factor,velocity_factor*spatial_factor**2]
        assert all(x==lam**3 for x in terms);checks+=4
        assert velocity_factor**2/spatial_factor**3==lam**-1;checks+=1
    # A classical discretely self-similar scale lambda=2, decreasing intervals to T.
    # Remain-time quartering, characteristic length half, velocity doubling,
    # integrated kinetic energy halves, assuming suitable rescaled profile.
    for k in range(1,13):
        remaining=F(1,4)**k
        radius=F(1,2)**k
        speed=F(2)**k
        energy=F(1,2)**k
        assert remaining==radius**2;checks+=1
        assert speed*radius==1;checks+=1
        assert energy==speed**2*radius**3;checks+=1
        assert remaining/F(1,4)**(k-1)==F(1,4);checks+=1
    # Null / counterexample: generic independent scaling exponents fail PDE equivalence.
    wrong=F(2);wrong_p=F(2)
    bad=[wrong*F(4),wrong**2*F(2),wrong_p*F(2),wrong*F(4)]
    assert len(set(bad))>1;checks+=1
    return checks
if __name__=='__main__':
    print('PASS',test(),'exact rational assertions; classic NS scaling, no theorem verification')
