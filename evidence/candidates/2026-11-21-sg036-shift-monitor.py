"""SG036 online shift monitor, imports frozen SG035 simulator. Python stdlib."""
import importlib.util,pathlib,json,hashlib
P=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("sg035",P/"2026-11-21-sg035-calibration-transfer.py")
b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
def alarm(v):
 if len(v)<80:return False
 q=v[-80:];mean=sum(q)/80;c=39.5
 slope=sum((i-c)*(x-mean) for i,x in enumerate(q))/sum((i-c)**2 for i in range(80))
 r=[x-mean-slope*(i-c) for i,x in enumerate(q)]
 den=sum(x*x for x in r)
 rho=sum(r[i]*r[i-1] for i in range(1,80))/den if den else 0
 return rho>.78 or (den/80)**.5>.29
def monitored(v):
 previous=None;latched=False;alarm_at=None
 for n in (80,120,160,200,240):
  label,slope=b.classify(v[:n])
  if alarm(v[:n]):
   if not latched:alarm_at=n
   latched=True
  if not latched and n>=120 and label!='unresolved' and label==previous and (abs(slope)>.0036 or abs(slope)<.0014):
   return n,label,False,None
  previous=label
 return 240,b.classify(v)[0] if latched else 'unresolved',latched,alarm_at
def run():
 policies=('fixed','old','new')
 template=lambda:dict(correct=0,FP=0,FN=0,abstain=0,observations=0,loss=0.,early=0)
 total={p:template() for p in policies}
 by={s:{p:dict(template(),alarm=0) for p in policies} for s in b.SCENARIOS}
 failures=[];rows=[]
 for j,scenario in enumerate(b.SCENARIOS):
  for truth in (False,True):
   for k in range(40):
    seed=21000000+200000*j+10000*int(truth)+101*k
    v=b.generate(seed,scenario,truth);rho=b.rho_estimate(v[:110])
    idx=4 if rho is None or rho>=.90 else 0 if rho<.45 else 1 if rho<.60 else 2 if rho<.75 else 3
    allowed=b.COUNTS[idx]>=40 and b.UPPERS[idx]<.08
    fixed=(240,b.classify(v[240:])[0],False,None)
    n,label=b.decide(v[240:],'adaptive')
    old=(n,label,False,None) if allowed else fixed
    new=monitored(v[240:]) if allowed else fixed
    rows.append(dict(seed=seed,scenario=scenario,truth=truth,rho=rho,allowed=allowed,old=old,new=new,fixed=fixed))
    for p,choice in (('fixed',fixed),('old',old),('new',new)):
     n,label,latched,at=choice;kind=b.outcome(label,truth)
     cost=.06*n+{'correct':0,'FP':150,'FN':90,'abstain':18}[kind]
     for t in (total[p],by[scenario][p]):
      t[kind]+=1;t['observations']+=n;t['loss']+=cost;t['early']+=int(n<240)
     if p=='new':by[scenario][p]['alarm']+=int(latched)
     if kind in ('FP','FN'):failures.append(dict(seed=seed,scenario=scenario,policy=p,n=n,truth=truth,decision=label,error=kind,alarm_at=at))
 for t in list(total.values())+[v for x in by.values() for v in x.values()]:t['loss']=round(t['loss'],2)
 out={'id':'TD-CROSSDOMAIN-SG036','freeze_commit':'0212570b28935371741f57e8d7b3aa310e12afe2',
  'n':len(rows),'summary':total,'by_scenario':by,'failures':failures,
  'rows_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True,default=str).encode()).hexdigest()}
 assert len(rows)==400 and total['old']['FP']+total['old']['FN']==38
 assert (total['new']['correct'],total['new']['FP'],total['new']['FN'],total['new']['abstain'],total['new']['observations'],total['new']['loss'])==(342,6,4,48,79840,6914.4)
 return out
if __name__=='__main__':print(json.dumps(run(),indent=2))
