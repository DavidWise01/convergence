"""SG043 reproducible 90% HAC interval coverage and split calibration, Python stdlib."""
import random,math,statistics as st,json,hashlib
SCENARIOS=('reference','correlation_switch','laplace_tail','subtle_drift','fast_oscillation','late_correlation_switch','late_oscillation','variable_period','colored_control')
def stream(seed,scenario,drift):
 r=random.Random(seed);z=0.;phase=0.;out=[]
 for t in range(480):
  rho=.94 if ((scenario in ('correlation_switch','colored_control') and t>=240) or (scenario=='late_correlation_switch' and t>=300)) else .72
  if scenario=='laplace_tail':
   u=r.random()-.5;eps=-.115*math.copysign(math.log1p(-2*abs(u)),u)
  else:eps=r.uniform(-.23,.23)
  z=rho*z+eps
  slope=.0027 if scenario=='subtle_drift' else .005
  spike=7 if t in (42,173) else -7 if t in (87,211) else 0
  osc=0.
  if scenario=='variable_period' and t>=240:
   phase+=2*math.pi/(42+16*(t-240)/240);osc=.55*math.sin(phase)
  elif scenario=='fast_oscillation' and t>=240:osc=.55*math.sin(2*math.pi*(t-240)/60)
  elif scenario=='late_oscillation' and t>=300:osc=.55*math.sin(2*math.pi*(t-300)/60)
  out.append((slope*t if drift else 0.)+3*(t>=120)+z+spike+osc)
 return out[240:]
def trend_hac(v,lag=3):
 y=[st.median(v[i:i+10]) for i in range(0,len(v),10)]
 n=len(y);x=[i-(n-1)/2 for i in range(n)];xx=sum(i*i for i in x)
 beta=sum(a*b for a,b in zip(x,y))/xx;mu=sum(y)/n
 e=[b-mu-beta*a for a,b in zip(x,y)]
 num=sum((x[i]*e[i])**2 for i in range(n))
 for h in range(1,min(lag,n-1)+1):num+=2*(1-h/(lag+1))*sum(x[i]*e[i]*x[i-h]*e[i-h] for i in range(h,n))
 return beta/10,math.sqrt(max(0,num))/xx/10
def observations(start,count):
 rows=[]
 for j,s in enumerate(SCENARIOS):
  for drift in (False,True):
   for k in range(count):
    seed=start+200000*j+10000*int(drift)+101*k
    slope,se=trend_hac(stream(seed,s,drift))
    truth=(.0027 if s=='subtle_drift' else .005) if drift else 0.
    rows.append(dict(seed=seed,scenario=s,drift=drift,truth=truth,slope=slope,se=se,ratio=abs(slope-truth)/max(se,1.e-12)))
 return rows
def coverage(rows,z):
 results={}
 for s in ('ALL',)+SCENARIOS:
  group=rows if s=='ALL' else [r for r in rows if r['scenario']==s]
  hits=sum(r['ratio']<=z for r in group);n=len(group)
  results[s]=dict(n=n,covered=hits,coverage=round(hits/n,5),mean_width=round(sum(2*z*r['se'] for r in group)/n,7),misses=n-hits)
 return results
def cost(rows,z):
 d=dict(correct=0,FP=0,FN=0,abstain=0,loss=0.,observations=len(rows)*240)
 for r in rows:
  lo=r['slope']-z*r['se'];hi=r['slope']+z*r['se']
  label='confirmed' if lo>0 or hi<0 else 'rejected' if lo>-.0032 and hi<.0032 else 'unresolved'
  kind='abstain' if label=='unresolved' else 'correct' if (label=='confirmed')==r['drift'] else 'FP' if label=='confirmed' else 'FN'
  d[kind]+=1;d['loss']+=14.4+{'correct':0,'FP':150,'FN':90,'abstain':18}[kind]
 d['loss']=round(d['loss'],2)
 return d
def run():
 cal=observations(81000000,20);ordered=sorted(r['ratio'] for r in cal)
 rank=min(len(cal),math.ceil((len(cal)+1)*.90));z=ordered[rank-1]
 test=observations(87000000,40)
 result={'id':'TD-CROSSDOMAIN-SG043','freeze_commit':'ae8c8e22218fbd62e97cd9be327c9e3393cca820','calibration_n':len(cal),'calibration_rank':rank,'calibrated_z':z,'holdout_n':len(test),
  'coverage_original':coverage(test,1.645),'coverage_corrected':coverage(test,z),'decision_original':cost(test,1.645),'decision_corrected':cost(test,z),
  'miscoverage_seeds':[{'seed':r['seed'],'scenario':r['scenario'],'drift':r['drift'],'truth':r['truth'],'estimate':round(r['slope'],8),'se':round(r['se'],8),'ratio':round(r['ratio'],5)} for r in test if r['ratio']>z],
  'holdout_sha256':hashlib.sha256(json.dumps(test,sort_keys=True).encode()).hexdigest()}
 assert (result['coverage_corrected']['ALL']['covered'],len(result['miscoverage_seeds']))==(636,84)
 assert result['decision_corrected']['loss']==18426.
 return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
