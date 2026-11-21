"""SG037: 20-observation checks, mandatory challenge and timing audit.
No future observation used to select a policy. Pure Python standard library.
"""
import random, statistics, math, json, hashlib, sys
SCENARIOS=('reference','correlation_switch','laplace_tail','subtle_drift','fast_oscillation','late_correlation_switch','late_oscillation')
BINS=(.45,.60,.75,.90,float('inf'))
COUNTS=(3,122,500,273,62); ERRORS=(0,3,19,52,16)
Z=1.6448536269514722
UPPERS=tuple((lambda p,n:(p+Z*Z/(2*n)+Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n)))/(1+Z*Z/n))(e/n,n) for e,n in zip(ERRORS,COUNTS))
COST={'sample':.06,'FP':150,'FN':90,'abstain':18}
def gen(seed,scenario,truth):
 r=random.Random(seed);z=0.;out=[]
 for t in range(480):
  rho=.94 if ((scenario=='correlation_switch' and t>=240) or (scenario=='late_correlation_switch' and t>=300)) else .72
  if scenario=='laplace_tail':
   u=r.random()-.5;eps=-.115*math.copysign(math.log1p(-2*abs(u)),u)
  else:eps=r.uniform(-.23,.23)
  z=rho*z+eps;slope=.0027 if scenario=='subtle_drift' else .005
  spike=7 if t in (42,173) else -7 if t in (87,211) else 0
  oscillating=((scenario=='fast_oscillation' and t>=240) or (scenario=='late_oscillation' and t>=300))
  oscillation=.55*math.sin(2*math.pi*(t-(300 if scenario=='late_oscillation' else 240))/60) if oscillating else 0
  out.append((slope*t if truth else 0)+3*(t>=120)+z+spike+oscillation)
 return out
def rho_estimate(pre):
 pairs=[(t,pre[t]) for t in range(110) if abs(pre[t])<1.5]
 if len(pairs)<47:return None
 mt=sum(t for t,v in pairs)/len(pairs);mv=sum(v for t,v in pairs)/len(pairs)
 den=sum((t-mt)**2 for t,v in pairs)
 if not den:return None
 slope=sum((t-mt)*(v-mv) for t,v in pairs)/den;intercept=mv-slope*mt
 residual={t:v-intercept-slope*t for t,v in pairs}
 adj=[(residual[t-1],residual[t]) for t in range(1,110) if t in residual and t-1 in residual]
 if len(adj)<45:return None
 den=sum(a*a for a,b in adj)
 return sum(a*b for a,b in adj)/den if den else None
def allowed(pre):
 x=rho_estimate(pre)
 idx=5 if x is None else next(i for i,b in enumerate(BINS) if x<b)
 return idx<5 and COUNTS[idx]>=40 and UPPERS[idx]<.08,idx,x
def classify(v):
 n=len(v)//10
 bins=[statistics.median(v[10*i:10*(i+1)]) for i in range(n)]
 slope=statistics.median((bins[j]-bins[i])/(10*(j-i)) for i in range(n) for j in range(i+1,n))
 return ('confirmed' if abs(slope)>.0032 else 'rejected' if abs(slope)<.0018 else 'unresolved'),slope
def metric(v,window=80):
 if len(v)<window:return None
 q=v[-window:];mean=sum(q)/window;c=(window-1)/2
 slope=sum((i-c)*(x-mean) for i,x in enumerate(q))/sum((i-c)**2 for i in range(window))
 residual=[x-mean-slope*(i-c) for i,x in enumerate(q)]
 den=sum(x*x for x in residual)
 ar=sum(residual[i]*residual[i-1] for i in range(1,window))/den if den else 0
 rms=(den/window)**.5
 return ar,rms
def old_monitored(v):
 previous=None;latched=False;alarm_at=None
 for n in (80,120,160,200,240):
  label,slope=classify(v[:n]);metrics=metric(v[:n],80)
  if metrics and (metrics[0]>.78 or metrics[1]>.29):
   if not latched:alarm_at=n
   latched=True
  if not latched and n>=120 and label!='unresolved' and label==previous and (abs(slope)>.0036 or abs(slope)<.0014):
   return dict(n=n,label=label,alarm_at=alarm_at,candidate_at=n,prevented=False)
  previous=label
 return dict(n=240,label=classify(v)[0] if latched else 'unresolved',alarm_at=alarm_at,candidate_at=None,prevented=latched)
def new_monitored(v,check_every=20,challenge=20,ar_threshold=.78,rms_threshold=.29):
 previous=None;latched=False;alarm_at=None;candidate=None;candidate_at=None;prevented=False
 for n in range(80,241,check_every):
  label,slope=classify(v[:n]);m=metric(v[:n],80)
  if m and (m[0]>ar_threshold or m[1]>rms_threshold):
   if not latched:alarm_at=n
   latched=True
   if candidate is not None:prevented=True
   candidate=None
  strong=label!='unresolved' and (abs(slope)>.0036 or abs(slope)<.0014)
  if candidate is not None and not latched:
   if label!=candidate or not strong:
    candidate=None;prevented=True
   elif n-candidate_at>=challenge:
    return dict(n=n,label=label,alarm_at=alarm_at,candidate_at=candidate_at,prevented=prevented)
  if candidate is None and not latched and n>=120 and strong and label==previous:
   candidate=label;candidate_at=n
  previous=label
 return dict(n=240,label=classify(v)[0],alarm_at=alarm_at,candidate_at=candidate_at,prevented=prevented)
def label_cost(label,truth,n):
 kind='abstain' if label=='unresolved' else 'correct' if (label=='confirmed')==truth else 'FP' if label=='confirmed' else 'FN'
 return kind,round(n*COST['sample']+{'correct':0,'FP':150,'FN':90,'abstain':18}[kind],2)
def run(seed_start=26000000,per_class=40,check_every=20,challenge=20):
 rows=[]
 for i,scenario in enumerate(SCENARIOS):
  for truth in (False,True):
   for k in range(per_class):
    seed=seed_start+200000*i+10000*int(truth)+101*k
    x=gen(seed,scenario,truth);ok,bin_id,rho=allowed(x[:110]);tail=x[240:]
    fixed=dict(n=240,label=classify(tail)[0],alarm_at=None,candidate_at=None,prevented=False)
    old=old_monitored(tail) if ok else fixed
    new=new_monitored(tail,check_every,challenge) if ok else fixed
    row=dict(seed=seed,scenario=scenario,truth=truth,risk_gate=ok,bin=bin_id,rho=rho,shift_onset=60 if scenario in ('late_correlation_switch','late_oscillation') else 0 if scenario in ('correlation_switch','fast_oscillation') else None,choices={})
    for name,p in (('old',old),('new',new),('fixed',fixed)):
     outcome,cost=label_cost(p['label'],truth,p['n'])
     row['choices'][name]=dict(p,outcome=outcome,cost=cost)
    rows.append(row)
 def sums(sub,policy):
  d={k:0 for k in ('correct','FP','FN','abstain')}
  d.update(samples=0,loss=0,early=0,alarms=0,alarm_before_commit=0,alerts_after_shift=0)
  lags=[]
  for r in sub:
   c=r['choices'][policy];d[c['outcome']]+=1;d['samples']+=c['n'];d['loss']+=c['cost'];d['early']+=c['n']<240;d['alarms']+=c['alarm_at'] is not None
   if r['shift_onset'] is not None and c['alarm_at'] is not None and c['alarm_at']>=r['shift_onset']:
    d['alerts_after_shift']+=1;lags.append(c['alarm_at']-r['shift_onset'])
   d['alarm_before_commit']+=c['alarm_at'] is not None and c['n']==240
  d['loss']=round(d['loss'],2);d['median_alarm_lag']=statistics.median(lags) if lags else None
  return d
 total={p:sums(rows,p) for p in ('old','new','fixed')}
 groups={s:{p:sums([r for r in rows if r['scenario']==s],p) for p in ('old','new','fixed')} for s in SCENARIOS}
 failures=[{k:r[k] for k in ('seed','scenario','truth','risk_gate','shift_onset')} | {'outcome':r['choices']['new']} for r in rows if r['choices']['new']['outcome'] in ('FP','FN')]
 answer=dict(id='TD-CROSSDOMAIN-SG037',config={'check_every':check_every,'challenge':challenge,'ar_threshold':.78,'rms_threshold':.29},n=len(rows),summaries=total,by_scenario=groups,failures=failures,seed_start=seed_start,per_class=per_class,rows_digest=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest())
 if seed_start==26000000 and per_class==40 and check_every==20 and challenge==20:
  assert (total['new']['correct'],total['new']['FP'],total['new']['FN'],total['new']['abstain'])==(487,2,5,66)
  assert (total['new']['samples'],total['new']['loss'])==(121700,9240.)
  assert len(failures)==7
 return answer
if __name__=='__main__':
 start=int(sys.argv[1]) if len(sys.argv)>1 else 26000000
 per=int(sys.argv[2]) if len(sys.argv)>2 else 40
 challenge=int(sys.argv[3]) if len(sys.argv)>3 else 20
 print(json.dumps(run(start,per,challenge=challenge),indent=2))
