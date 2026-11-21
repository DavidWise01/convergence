"""SG038: two-estimator challenge, SG037 controls; standard-library reproducible experiment."""
import math,random,statistics,json,hashlib,sys
SCENARIOS=('reference','correlation_switch','laplace_tail','subtle_drift','fast_oscillation','late_correlation_switch','late_oscillation')
COUNTS=(3,122,500,273,62); ERRORS=(0,3,19,52,16); BINS=(.45,.60,.75,.90,float('inf')); Z=1.6448536269514722
UPPERS=[(lambda p,n:(p+Z*Z/(2*n)+Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n)))/(1+Z*Z/n))(e/n,n) for e,n in zip(ERRORS,COUNTS)]
def gen(seed,scenario,truth):
 r=random.Random(seed);z=0.;out=[]
 for t in range(480):
  rho=.94 if (scenario=='correlation_switch' and t>=240 or scenario=='late_correlation_switch' and t>=300) else .72
  if scenario=='laplace_tail':
   u=r.random()-.5;eps=-.115*math.copysign(math.log1p(-2*abs(u)),u)
  else:eps=r.uniform(-.23,.23)
  z=rho*z+eps;slope=.0027 if scenario=='subtle_drift' else .005
  spike=7 if t in (42,173) else -7 if t in (87,211) else 0
  oscillating=scenario=='fast_oscillation' and t>=240 or scenario=='late_oscillation' and t>=300
  osc=.55*math.sin(2*math.pi*(t-(300 if scenario=='late_oscillation' else 240))/60) if oscillating else 0
  out.append((slope*t if truth else 0)+3*(t>=120)+z+spike+osc)
 return out
def estimate_rho(pre):
 pairs=[(t,pre[t]) for t in range(110) if abs(pre[t])<1.5]
 if len(pairs)<47:return None
 mt=sum(t for t,v in pairs)/len(pairs);mv=sum(v for t,v in pairs)/len(pairs)
 den=sum((t-mt)**2 for t,v in pairs)
 if not den:return None
 slope=sum((t-mt)*(v-mv) for t,v in pairs)/den;intercept=mv-slope*mt
 res={t:v-intercept-slope*t for t,v in pairs}
 adj=[(res[t-1],res[t]) for t in range(1,110) if t in res and t-1 in res]
 if len(adj)<45:return None
 den=sum(a*a for a,b in adj)
 return sum(a*b for a,b in adj)/den if den else None
def allowed(pre):
 x=estimate_rho(pre);idx=5 if x is None else next(i for i,b in enumerate(BINS) if x<b)
 return idx<5 and COUNTS[idx]>=40 and UPPERS[idx]<.08,idx,x
def theil(v):
 n=len(v)//10; b=[statistics.median(v[10*i:10*(i+1)]) for i in range(n)]
 return statistics.median((b[j]-b[i])/(10*(j-i)) for i in range(n) for j in range(i+1,n))
def classify_slope(s):return 'confirmed' if abs(s)>.0032 else 'rejected' if abs(s)<.0018 else 'unresolved'
def classify(v):
 s=theil(v);return classify_slope(s),s
def alternative(v):
 n=len(v);w=max(20,(n//3)//10*10)
 left=statistics.median(v[:w]);right=statistics.median(v[-w:]);separation=n-w
 return (right-left)/separation
def shifted(v):
 if len(v)<80:return False
 q=v[-80:];mean=sum(q)/80;c=39.5
 slope=sum((i-c)*(x-mean) for i,x in enumerate(q))/sum((i-c)**2 for i in range(80))
 residual=[x-mean-slope*(i-c) for i,x in enumerate(q)]
 den=sum(x*x for x in residual)
 ar=sum(residual[i]*residual[i-1] for i in range(1,80))/den if den else 0
 return ar>.78 or (den/80)**.5>.29
def old_controller(v):
 prior=None;alarm=False;candidate=None;time=None
 for n in range(80,241,20):
  label,s=classify(v[:n]);alarm=alarm or shifted(v[:n]);strong=label!='unresolved' and (abs(s)>.0036 or abs(s)<.0014)
  if alarm:candidate=None
  elif candidate is not None:
   if label!=candidate or not strong:candidate=None
   elif n-time>=20:return n,label,alarm
  if candidate is None and not alarm and n>=120 and strong and label==prior:candidate=label;time=n
  prior=label
 return 240,classify(v)[0],alarm
def new_controller(v,challenge_early=True,challenge_full=True):
 prior=None;alarm=False;candidate=None;time=None;rejected=0
 for n in range(80,241,20):
  label,s=classify(v[:n]);alarm=alarm or shifted(v[:n]);strong=label!='unresolved' and (abs(s)>.0036 or abs(s)<.0014)
  if alarm:candidate=None
  elif candidate is not None:
   if label!=candidate or not strong:candidate=None
   elif n-time>=20:
    other=classify_slope(alternative(v[:n]))
    if not challenge_early or other==label:return n,label,alarm,rejected
    rejected+=1;candidate=None
  if candidate is None and not alarm and n>=120 and strong and label==prior:candidate=label;time=n
  prior=label
 primary=classify(v)[0]
 other=classify_slope(alternative(v))
 if challenge_full and alarm and other!=primary:return 240,'unresolved',alarm,rejected+1
 return 240,primary,alarm,rejected
def outcome(label,truth):
 if label=='unresolved':return 'abstain'
 if (label=='confirmed')==truth:return 'correct'
 return 'FP' if label=='confirmed' else 'FN'
def run(start=31000000,count=10,challenge_early=True,challenge_full=True):
 rows=[]
 for i,scenario in enumerate(SCENARIOS):
  for truth in (False,True):
   for k in range(count):
    seed=start+200000*i+10000*int(truth)+101*k
    v=gen(seed,scenario,truth);ok,b,r=allowed(v[:110]);f=v[240:]
    fixed=(240,classify(f)[0],False);old=old_controller(f) if ok else fixed
    new=new_controller(f,challenge_early,challenge_full) if ok else (*fixed,0)
    choices={}
    for policy,decision in [('fixed',fixed),('sg037',old),('sg038',new)]:
     n,label,alarm=decision[:3];kind=outcome(label,truth)
     choices[policy]={'n':n,'label':label,'alarm':alarm,'outcome':kind,'loss':round(.06*n+{'correct':0,'FP':150,'FN':90,'abstain':18}[kind],2)}
    rows.append({'seed':seed,'scenario':scenario,'truth':truth,'gate':ok,'rho':r,'choices':choices})
 def summarize(selection):
  ans={}
  for group in ['ALL',*SCENARIOS]:
   sub=rows if group=='ALL' else [r for r in rows if r['scenario']==group]
   ans[group]={}
   for policy in ('fixed','sg037','sg038'):
    items=[r['choices'][policy] for r in sub]
    ans[group][policy]={k:sum(v['outcome']==k for v in items) for k in ('correct','FP','FN','abstain')}
    ans[group][policy].update(samples=sum(v['n'] for v in items),loss=round(sum(v['loss'] for v in items),2),early=sum(v['n']<240 for v in items))
  return ans
 failures=[{'seed':r['seed'],'scenario':r['scenario'],'truth':r['truth'],'choice':r['choices']['sg038']} for r in rows if r['choices']['sg038']['outcome'] in ('FP','FN')]
 return {'seed_start':start,'cases':len(rows),'summary':summarize(rows),'failures':failures,'rows_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
if __name__=='__main__':
 args=sys.argv[1:]; start=int(args[0]) if args else 31000000; count=int(args[1]) if len(args)>1 else 10
 print(json.dumps(run(start,count),indent=2))
