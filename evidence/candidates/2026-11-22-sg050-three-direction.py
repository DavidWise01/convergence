"""SG050 three-direction synthetic drift holdout. Run: python3 this_file.py"""
import json,math,random,statistics as st,hashlib,sys
SCENARIOS=('reference','correlation_switch','laplace_tail','subtle_drift','fast_oscillation','late_correlation_switch','late_oscillation','variable_period','colored_control')
Z=2.291027529910169; M=.0032
def gen(seed,scenario,d):
 r=random.Random(seed);z=0.;phase=0.;v=[];base=.0027 if scenario=='subtle_drift' else .005
 for t in range(480):
  rho=.94 if (scenario in ('correlation_switch','colored_control') and t>=240) or (scenario=='late_correlation_switch' and t>=300) else .72
  if scenario=='laplace_tail':
   u=r.random()-.5;eps=-.115*math.copysign(math.log1p(-2*abs(u)),u)
  else:eps=r.uniform(-.23,.23)
  z=rho*z+eps;spike=7 if t in (42,173) else -7 if t in (87,211) else 0;osc=0.
  if scenario=='variable_period' and t>=240:
   phase+=2*math.pi/(42+16*(t-240)/240);osc=.55*math.sin(phase)
  elif scenario=='fast_oscillation' and t>=240:osc=.55*math.sin(2*math.pi*(t-240)/60)
  elif scenario=='late_oscillation' and t>=300:osc=.55*math.sin(2*math.pi*(t-300)/60)
  v.append(d*base*t+3*int(t>=120)+z+spike+osc)
 return v[240:],d*base
def hac(v):
 y=[st.median(v[i:i+10]) for i in range(0,len(v),10)];n=len(y);mid=(n-1)/2;x=[i-mid for i in range(n)];xx=sum(a*a for a in x);mu=sum(y)/n
 beta=sum(a*(b-mu) for a,b in zip(x,y))/xx;e=[b-mu-beta*a for a,b in zip(x,y)]
 numer=sum((x[i]*e[i])**2 for i in range(n))
 for lag in range(1,4):numer+=2*(1-lag/4)*sum(x[i]*e[i]*x[i-lag]*e[i-lag] for i in range(lag,n))
 return beta/10,math.sqrt(max(numer,0))/xx/10
def labels(lo,hi):
 new='positive' if lo>0 else 'negative' if hi<0 else 'zero' if lo>-M and hi<M else 'unresolved'
 old='zero' if new=='negative' else new
 return old,new
def outcome(label,truth):
 if label=='unresolved':return 'abstain'
 if label==truth:return 'correct'
 return 'missed_direction' if label=='zero' and truth!='zero' else 'false_direction'
def run(start=139000000,count=40):
 policies=('SG049_positive_only','SG050_three_way');penalty=dict(correct=0,missed_direction=90,false_direction=150,abstain=18)
 totals={p:dict(correct=0,missed_direction=0,false_direction=0,abstain=0,loss=0.,samples=0) for p in policies}
 groups={};fail=[];changes=[];rows=[]
 for j,scenario in enumerate(SCENARIOS):
  for ix,d in enumerate((-1,0,1)):
   truth=('negative','zero','positive')[ix]
   for k in range(count):
    seed=start+200000*j+20000*ix+101*k;v,true_s=gen(seed,scenario,d);s,se=hac(v);lo,hi=s-Z*se,s+Z*se
    old,new=labels(lo,hi);choices=dict(zip(policies,(old,new)))
    item=dict(seed=seed,scenario=scenario,truth=truth,programmed_slope=true_s,estimated_slope=s,standard_error=se,ci=[lo,hi],decisions=choices);rows.append(item)
    for p,label in choices.items():
     kind=outcome(label,truth);totals[p][kind]+=1;totals[p]['samples']+=240;totals[p]['loss']+=14.4+penalty[kind]
     group=groups.setdefault(scenario,{}).setdefault(p,dict(correct=0,missed_direction=0,false_direction=0,abstain=0));group[kind]+=1
     if p==policies[1] and kind!='correct':fail.append(dict(item,category=kind))
    if old!=new:changes.append(dict(item,old_outcome=outcome(old,truth),new_outcome=outcome(new,truth)))
 for p in policies:totals[p]['loss']=round(totals[p]['loss'],2)
 return dict(id='TD-CROSSDOMAIN-SG050',seed_start=start,n=len(rows),count_per_scenario_direction=count,rules=dict(z=Z,effect_margin=M,sampling=240,penalties=penalty),summary=totals,by_scenario=groups,changes=changes,failures=fail,rows_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest())
if __name__=='__main__':
 x=run(int(sys.argv[1]) if len(sys.argv)>1 else 139000000,int(sys.argv[2]) if len(sys.argv)>2 else 40)
 assert x['n']!=1080 or (x['summary']['SG050_three_way']['correct'],x['summary']['SG050_three_way']['false_direction'],x['summary']['SG050_three_way']['abstain'])==(912,57,111)
 print(json.dumps(x,indent=2))
