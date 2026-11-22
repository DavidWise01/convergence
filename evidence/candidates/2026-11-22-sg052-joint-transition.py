"""SG052: simultaneous trend direction and AR1 regime change.
Python3 standard library. No hidden onset or truth passed to classifier.
Run python this_file.py holdout > full-holdout.json.
"""
import math,random,statistics as st,json,hashlib,sys
SIGNS=(-1,0,1); NOISE=('stable_rho72','rho72_to94','rho94_to72')
Z050=2.291027529910169; Z051=2.486294325376533; M=.0032
COST={'correct':0,'missed_direction':90,'false_direction':150,'abstain':18}
def gen(seed,before,after,env,onset):
 r=random.Random(seed);x=0.;level=0.;v=[]
 rb={'stable_rho72':.72,'rho72_to94':.72,'rho94_to72':.94}[env]
 ra={'stable_rho72':.72,'rho72_to94':.94,'rho94_to72':.72}[env]
 for t in range(480):
  local=t-240;d=before if local<onset else after
  if t>0:level+=.005*d
  rho=rb if local<onset else ra
  x=rho*x+r.uniform(-.23,.23)
  v.append(level+x)
 return v[240:]
def hac(v):
 y=[st.median(v[i:i+10]) for i in range(0,len(v),10)]
 n=len(y);mid=(n-1)/2;xs=[i-mid for i in range(n)]
 xx=sum(x*x for x in xs);mu=sum(y)/n
 beta=sum(x*(q-mu) for x,q in zip(xs,y))/xx
 e=[q-mu-beta*x for x,q in zip(xs,y)]
 numer=sum((xs[i]*e[i])**2 for i in range(n))
 for h in range(1,min(3,n-1)+1):
  numer+=2*(1-h/4)*sum(xs[i]*e[i]*xs[i-h]*e[i-h] for i in range(h,n))
 return beta/10,math.sqrt(max(0,numer))/xx/10
def label(beta,se,z):
 lo=beta-z*se;hi=beta+z*se
 if lo>0:return 'positive'
 if hi<0:return 'negative'
 if lo>-M and hi<M:return 'zero'
 return 'unresolved'
def outcome(pred,truth):
 if pred=='unresolved':return 'abstain'
 if pred==truth:return 'correct'
 return 'missed_direction' if pred=='zero' and truth!='zero' else 'false_direction'
def rows(start,count):
 out=[]
 for bi,before in enumerate(SIGNS):
  for ai,after in enumerate(SIGNS):
   for ei,env in enumerate(NOISE):
    for k in range(count):
     onset=(100,120,140)[k%3]
     seed=start+1000000*bi+200000*ai+30000*ei+101*k
     v=gen(seed,before,after,env,onset)
     full,fullse=hac(v);local,localse=hac(v[-100:])
     out.append(dict(seed=seed,before=before,after=after,env=env,onset=onset,full_slope=full,full_se=fullse,local_slope=local,local_se=localse,true_post_slope=after*.005,target=('negative','zero','positive')[ai]))
 return out
def calibrate(data):
 a=sorted(abs(r['local_slope']-r['true_post_slope'])/max(r['local_se'],1e-12) for r in data)
 rank=min(len(a),math.ceil((len(a)+1)*.90))
 return a[rank-1],rank
def evaluate(data,z):
 names=('SG050_full','SG051_full','SG052_trailing100')
 overall={p:dict(correct=0,missed_direction=0,false_direction=0,abstain=0,loss=0.,samples=0,covered=0) for p in names}
 groups={};errors=[];changes=[];ledger=[]
 for r in data:
  preds={'SG050_full':label(r['full_slope'],r['full_se'],Z050),'SG051_full':label(r['full_slope'],r['full_se'],Z051),'SG052_trailing100':label(r['local_slope'],r['local_se'],z)}
  ledger.append(dict(r,predictions=preds))
  for p,pred in preds.items():
   k=outcome(pred,r['target']);s=overall[p];s[k]+=1;s['samples']+=240;s['loss']+=14.4+COST[k]
   beta,se,zp=(r['local_slope'],r['local_se'],z) if p=='SG052_trailing100' else (r['full_slope'],r['full_se'],Z050 if p=='SG050_full' else Z051)
   hit=int(abs(beta-r['true_post_slope'])<=zp*se);s['covered']+=hit
   g=groups.setdefault(r['env'],{}).setdefault(p,dict(correct=0,missed_direction=0,false_direction=0,abstain=0,covered=0))
   g[k]+=1;g['covered']+=hit
   if p=='SG052_trailing100' and k!='correct':errors.append(dict(r,prediction=pred,outcome=k))
  if preds['SG051_full']!=preds['SG052_trailing100']:
   changes.append(dict(seed=r['seed'],before=r['before'],after=r['after'],env=r['env'],onset=r['onset'],old=preds['SG051_full'],new=preds['SG052_trailing100'],old_kind=outcome(preds['SG051_full'],r['target']),new_kind=outcome(preds['SG052_trailing100'],r['target'])))
 for s in overall.values():s['loss']=round(s['loss'],2)
 return dict(summary=overall,by_noise=groups,changes=changes,noncorrect=errors,rows_sha256=hashlib.sha256(json.dumps(ledger,sort_keys=True).encode()).hexdigest())
def run(stage='holdout'):
 cal=rows(157000000,12);z,rank=calibrate(cal)
 start,count=(160000000,6) if stage=='pilot' else (167000000,40)
 out=dict(id='TD-CROSSDOMAIN-SG052',stage=stage,freeze_commit='6e0087420e16c2b622d99848ff6513921a2ec88f',calibration=dict(n=len(cal),rank=rank,z=z),seed_start=start,n=27*count,**evaluate(rows(start,count),z))
 if stage=='holdout':
  assert out['summary']['SG052_trailing100']==dict(correct=458,missed_direction=0,false_direction=45,abstain=577,loss=32688.,samples=259200,covered=967)
 return out
if __name__=='__main__':
 print(json.dumps(run(sys.argv[1] if len(sys.argv)>1 else 'holdout'),indent=2))
