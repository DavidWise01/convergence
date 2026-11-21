"""SG-033 prospective safety gate against early decisions.
Frozen rule: choose adaptive only if pre-decision rho_est < .60.
Python 3 standard library; no future-data leakage in selection.
"""
import random,statistics,json,hashlib
SCENARIOS=(('baseline',.72,.005,False),('weak_drift',.72,.0027,False),('high_correlation',.93,.005,False),('heavy_tailed',.72,.005,True))
COST={'sample':.06,'FP':150,'FN':90,'abstain':18}
def stream(seed,drift,rho,slope,heavy):
 r=random.Random(seed);z=0.;out=[]
 for t in range(480):
  z=rho*z+r.uniform(-.23,.23)
  impulse=7 if t in (42,173) else -7 if t in (87,211) else 0
  if heavy and r.random()<.03:impulse+=r.choice((-2.5,2.5))
  out.append((slope*t if drift else 0.)+3*(t>=120)+z+impulse)
 return out
def estimate_rho(pre):
 pairs=[(t,pre[t]) for t in range(110) if abs(pre[t])<1.5]
 if len(pairs)<47:return None
 mt=sum(t for t,v in pairs)/len(pairs);mv=sum(v for t,v in pairs)/len(pairs)
 denom=sum((t-mt)**2 for t,v in pairs)
 if not denom:return None
 slope=sum((t-mt)*(v-mv) for t,v in pairs)/denom
 intercept=mv-slope*mt
 residual={t:v-intercept-slope*t for t,v in pairs}
 p=[(residual[t-1],residual[t]) for t in range(1,110) if t-1 in residual and t in residual]
 if len(p)<45:return None
 den=sum(a*a for a,b in p)
 return sum(a*b for a,b in p)/den if den else None
def classify(v):
 bins=[statistics.median(v[10*i:10*(i+1)]) for i in range(len(v)//10)]
 s=statistics.median((bins[j]-bins[i])/(10*(j-i)) for i in range(len(bins)) for j in range(i+1,len(bins)))
 return ('confirmed' if abs(s)>.0032 else 'rejected' if abs(s)<.0018 else 'unresolved'),s
def decide(v,policy):
 snapshots=[(n,*classify(v[:n])) for n in range(80,241,40)]
 if policy=='fixed240':return 240,snapshots[-1][1]
 prev=None
 for n,label,s in snapshots:
  if n>=120 and label!='unresolved' and label==prev and (abs(s)>.0036 or abs(s)<.0014):return n,label
  prev=label
 return 240,'unresolved'
def loss(n,label,truth):
 c=n*COST['sample']
 if label=='unresolved':return c+COST['abstain'],'abstain'
 if (label=='confirmed')==truth:return c,'correct'
 return (c+COST['FP'],'FP') if label=='confirmed' else (c+COST['FN'],'FN')
def evaluate(start=10300000,count=50,gate=.60):
 rows=[]
 for ix,(name,rho,slope,heavy) in enumerate(SCENARIOS):
  for truth in (False,True):
   for k in range(count):
    seed=start+100000*ix+10000*int(truth)+101*k
    obs=stream(seed,truth,rho,slope,heavy)
    est=estimate_rho(obs[:110])
    old='fixed240' if est is None or est>=.82 else 'cost-aware'
    chosen='cost-aware' if est is not None and est<gate else 'fixed240'
    scored={}
    for p in ('fixed240','cost-aware'):
     n,label=decide(obs[240:],p);c,o=loss(n,label,truth)
     scored[p]={'n':n,'label':label,'cost':c,'outcome':o}
    rows.append({'scenario':name,'seed':seed,'truth':truth,'rho_est':est,'selected_SG032':old,'selected_gate':chosen,'outcomes':scored})
 sums={}
 for key in ('selected_SG032','selected_gate','fixed240','cost-aware'):
  per={};total={'n':0,'correct':0,'FP':0,'FN':0,'abstain':0,'loss':0,'chosen_adaptive':0}
  for name,*_ in SCENARIOS:
   a=[r for r in rows if r['scenario']==name]
   stat={'n':0,'correct':0,'FP':0,'FN':0,'abstain':0,'loss':0,'chosen_adaptive':0}
   for r in a:
    p=r[key] if key.startswith('selected_') else key
    v=r['outcomes'][p]
    stat[v['outcome']]+=1;stat['n']+=v['n'];stat['loss']+=v['cost'];stat['chosen_adaptive']+=p=='cost-aware'
   for k in stat:total[k]+=stat[k]
   per[name]=stat
  sums[key]={'overall':total,'by_scenario':per}
 result={'id':'TD-CROSSDOMAIN-SG033','parameters':{'gate':gate,'old_gate':.82},'n':len(rows),'summary':sums,
  'rows_digest':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),
  'high_corr_early':[{'seed':r['seed'],'rho_est':r['rho_est']} for r in rows if r['scenario']=='high_correlation' and r['selected_gate']=='cost-aware']}
 if start==10300000 and count==50 and gate==.60:
  assert len(rows)==400
  assert sum(result['summary']['selected_gate']['overall'][k] for k in ('correct','FP','FN','abstain'))==400
  assert result['summary']['selected_gate']['overall']['FP']==2
  assert result['summary']['selected_gate']['overall']['FN']==4
  assert len(result['high_corr_early'])==0
  assert round(result['summary']['selected_gate']['overall']['loss'],2)==7362.0
 return result
if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
