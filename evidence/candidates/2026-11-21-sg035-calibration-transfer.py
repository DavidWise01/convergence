"""SG035: frozen calibration-transfer stress test; Python 3 standard library."""
import random,statistics,math,json,hashlib
SCENARIOS=('reference','correlation_switch','laplace_tail','subtle_drift','fast_oscillation')
BUDGETS=(.04,.06,.08,.15,.25)
COUNTS=(3,122,500,273,62);ERRORS=(0,3,19,52,16)
Z=1.6448536269514722
def upper(e,n):
 p=e/n;z=Z
 return (p+z*z/(2*n)+z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)
UPPERS=[upper(e,n) for e,n in zip(ERRORS,COUNTS)]
def generate(seed,scenario,truth):
 r=random.Random(seed);z=0.;out=[]
 for t in range(480):
  rho=.94 if scenario=='correlation_switch' and t>=240 else .72
  if scenario=='laplace_tail':
   u=r.random()-.5
   eps=-.115*math.copysign(math.log1p(-2*abs(u)),u)
  else:eps=r.uniform(-.23,.23)
  z=rho*z+eps;slope=.0027 if scenario=='subtle_drift' else .005
  spike=7 if t in (42,173) else -7 if t in (87,211) else 0
  osc=.55*math.sin(2*math.pi*(t-240)/60) if scenario=='fast_oscillation' and t>=240 else 0.
  out.append((slope*t if truth else 0)+3*(t>=120)+z+spike+osc)
 return out
def rho_estimate(pre):
 pairs=[(t,pre[t]) for t in range(110) if abs(pre[t])<1.5]
 if len(pairs)<47:return None
 mt=sum(t for t,v in pairs)/len(pairs);mv=sum(v for t,v in pairs)/len(pairs)
 den=sum((t-mt)**2 for t,v in pairs)
 if not den:return None
 m=sum((t-mt)*(v-mv) for t,v in pairs)/den;b=mv-m*mt
 res={t:v-b-m*t for t,v in pairs}
 adj=[(res[t-1],res[t]) for t in range(1,110) if t in res and t-1 in res]
 if len(adj)<45:return None
 den=sum(a*a for a,b in adj)
 return sum(a*b for a,b in adj)/den if den else None
def classify(v):
 bins=[statistics.median(v[i:i+10]) for i in range(0,len(v),10)]
 s=statistics.median((bins[j]-bins[i])/(10*(j-i)) for i in range(len(bins)) for j in range(i+1,len(bins)))
 return ('confirmed' if abs(s)>.0032 else 'rejected' if abs(s)<.0018 else 'unresolved'),s
def decide(v,policy):
 if policy=='fixed':return 240,classify(v)[0]
 previous=None
 for n in (80,120,160,200,240):
  label,s=classify(v[:n])
  if n>=120 and label!='unresolved' and label==previous and (abs(s)>.0036 or abs(s)<.0014):return n,label
  previous=label
 return 240,'unresolved'
def outcome(label,truth):
 if label=='unresolved':return 'abstain'
 if (label=='confirmed')==truth:return 'correct'
 return 'FP' if label=='confirmed' else 'FN'
def loss(n,kind):return .06*n+{'correct':0,'FP':150,'FN':90,'abstain':18}[kind]
def run():
 rows=[]
 for j,scenario in enumerate(SCENARIOS):
  for truth in (False,True):
   for i in range(40):
    seed=17300000+200000*j+10000*int(truth)+101*i
    v=generate(seed,scenario,truth);rho=rho_estimate(v[:110])
    idx=4 if rho is None or rho>=.9 else (0 if rho<.45 else 1 if rho<.6 else 2 if rho<.75 else 3)
    a=decide(v[240:],'adaptive');f=decide(v[240:],'fixed')
    rows.append({'scenario':scenario,'seed':seed,'truth':truth,'rho':rho,'bin':idx,
      'adaptive':{'n':a[0],'label':a[1],'outcome':outcome(a[1],truth)},
      'fixed':{'n':f[0],'label':f[1],'outcome':outcome(f[1],truth)}})
 results={};failures=[]
 for budget in BUDGETS:
  res={}
  for scenario in SCENARIOS:
   subset=[r for r in rows if r['scenario']==scenario];selected=[]
   for r in subset:
    allowed=COUNTS[r['bin']]>=40 and UPPERS[r['bin']]<budget
    choice='adaptive' if allowed else 'fixed';v=r[choice];selected.append((r,choice,v))
    if v['outcome'] in ('FP','FN'):
     failures.append({'budget':budget,'scenario':scenario,'seed':r['seed'],'truth':r['truth'],'bin':r['bin'],'selected':choice,'error':v['outcome']})
   adapt=[x for x in selected if x[1]=='adaptive']
   decided=sum(x[2]['outcome']!='abstain' for x in adapt)
   s={'n':80,'adaptive_routed':len(adapt),'coverage':len(adapt)/80,
      'correct':sum(x[2]['outcome']=='correct' for x in selected),
      'FP':sum(x[2]['outcome']=='FP' for x in selected),
      'FN':sum(x[2]['outcome']=='FN' for x in selected),
      'abstain':sum(x[2]['outcome']=='abstain' for x in selected),
      'observations':sum(x[2]['n'] for x in selected),
      'loss':round(sum(loss(x[2]['n'],x[2]['outcome']) for x in selected),2),
      'adapt_wrong':sum(x[2]['outcome'] in ('FP','FN') for x in adapt),
      'adapt_decided':decided}
   s['adapt_wrong_rate_given_decided']=round(s['adapt_wrong']/decided,6) if decided else None
   res[scenario]=s
  results[str(budget)]=res
 fixed={scenario:{'n':80,'loss':round(sum(loss(r['fixed']['n'],r['fixed']['outcome']) for r in rows if r['scenario']==scenario),2),
   'wrong':sum(r['fixed']['outcome'] in ('FP','FN') for r in rows if r['scenario']==scenario)} for scenario in SCENARIOS}
 checks=0;assert len(rows)==400;checks+=1
 for budget,rr in results.items():
  for scenario,r in rr.items():
   assert r['correct']+r['FP']+r['FN']+r['abstain']==80;checks+=1
   assert r['adaptive_routed']<=80 and r['observations']<=19200;checks+=1
 return {'id':'TD-CROSSDOMAIN-SG035','calibration_bin_counts':COUNTS,'calibration_bin_errors':ERRORS,
  'calibration_upper_bounds':UPPERS,'budgets':BUDGETS,'scenarios':SCENARIOS,'streams':len(rows),
  'checks':checks,'results':results,'fixed':fixed,'failures':failures,
  'rows_sha256':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()}
if __name__=='__main__':print(json.dumps(run(),indent=2))
