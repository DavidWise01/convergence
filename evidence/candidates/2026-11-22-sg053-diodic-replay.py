"""SG053: strict prefix-only inference and append-only SHA256 hash-chain audit.
Python 3 stdlib. Uses SG052 sibling source in evidence/candidates.
Usage: python 2026-11-22-sg053-diodic-replay.py [seed_start] [count]
"""
import hashlib, importlib.util, json, random, sys, pathlib
BASE=pathlib.Path(__file__).resolve().parent
UPSTREAM=BASE/"2026-11-22-sg052-joint-transition.py"
if not UPSTREAM.exists():UPSTREAM=BASE.parent/"sg052"/"sg052.py"
spec=importlib.util.spec_from_file_location('frozen_sg052',UPSTREAM)
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
CHECKPOINTS=(100,140,180,220,240)
Z=4.327111573414373

def decision(prefix):
    beta,se=b.hac(prefix[-min(100,len(prefix)):])
    return b.label(beta,se,Z)
def future_variants(v,n,seed):
    rng=random.Random(seed*7+n)
    future=v[n:];shuffled=future.copy();rng.shuffle(shuffled)
    return [v[:n]+[x+3*(i+1)/len(future) for i,x in enumerate(future)],
            v[:n]+[x-3*(i+1)/len(future) for i,x in enumerate(future)],v[:n]+shuffled]
def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def digest(o):return hashlib.sha256(canonical(o).encode()).hexdigest()
def audit_one(seed,before,after,env,onset):
    v=b.gen(seed,before,after,env,onset)
    prev='0'*64;ledger=[];errors=[];control_changed=0;control_trials=0;examples=[]
    checkpoints={}
    for n in CHECKPOINTS:
        output=decision(v[:n]);checkpoints[str(n)]=output
        if decision(json.loads(json.dumps(v[:n])))!=output:errors.append(dict(n=n,kind='replay'))
        for variant_id,mutated in enumerate(future_variants(v,n,seed) if n<240 else []):
            if decision(mutated[:n])!=output:errors.append(dict(n=n,kind='future_interference',variant=variant_id))
            old=decision(v);new=decision(mutated)
            control_trials+=1
            if old!=new:
                control_changed+=1
                if len(examples)<2:examples.append(dict(n=n,variant=variant_id,old=old,mutated=new))
        payload=dict(n=n,prefix_digest=digest(v[:n]),decision=output,parent_hash=prev)
        event=dict(payload,hash=digest(payload));ledger.append(event);prev=event['hash']
    prior='0'*64
    for e in ledger:
        payload={k:e[k] for k in ('n','prefix_digest','decision','parent_hash')}
        if e['parent_hash']!=prior or e['hash']!=digest(payload):errors.append(dict(n=e['n'],kind='chain_integrity'))
        prior=e['hash']
    return dict(seed=seed,before=before,after=after,env=env,onset=onset,target=('negative','zero','positive')[b.SIGNS.index(after)],
        predictions=checkpoints,ledger_root=prior,violations=errors,leaky_control_detections=control_changed,leaky_control_trials=control_trials,leaky_examples=examples)
def run(start=179000000,count=40):
    rows=[]
    for bi,before in enumerate(b.SIGNS):
        for ai,after in enumerate(b.SIGNS):
            for ei,env in enumerate(b.NOISE):
                for k in range(count):
                    onset=(100,120,140)[k%3]
                    seed=start+1000000*bi+200000*ai+30000*ei+101*k
                    rows.append(audit_one(seed,before,after,env,onset))
    by={str(n):dict(correct=0,missed_direction=0,false_direction=0,abstain=0) for n in CHECKPOINTS}
    for r in rows:
        for n in CHECKPOINTS:by[str(n)][b.kind(r['predictions'][str(n)],r['target'])]+=1
    summary=dict(id='TD-CROSSDOMAIN-SG053',freeze_commit='b35b8680777df7f6cce4e7a16234f09c86c4feae',
      seed_start=start,streams=len(rows),checkpoints=CHECKPOINTS,check_metrics=by,
      causal_violations=sum(len(r['violations']) for r in rows),
      leaky_comparator_detected=sum(r['leaky_control_detections'] for r in rows),
      leaky_comparator_trials=sum(r['leaky_control_trials'] for r in rows),
      leaky_streams_detected=sum(r['leaky_control_detections']>0 for r in rows),
      ledger_roots_sha256=digest([r['ledger_root'] for r in rows]),
      all_rows_sha256=digest(rows),
      counterexamples=[r for r in rows if r['violations']],
      negative_control_examples=[dict(seed=r['seed'],**r['leaky_examples'][0]) for r in rows if r['leaky_examples']][:15])
    if summary['causal_violations']:raise AssertionError('Causal or append-only violation')
    if start==179000000 and count==40:
        assert summary['leaky_comparator_detected']==7902 and summary['leaky_comparator_trials']==12960
        assert summary['check_metrics']['240']==dict(correct=433,missed_direction=1,false_direction=41,abstain=605)
    return summary,rows
if __name__=='__main__':
    start=int(sys.argv[1]) if len(sys.argv)>1 else 179000000
    count=int(sys.argv[2]) if len(sys.argv)>2 else 40
    summary,rows=run(start,count)
    (BASE/('sg053-'+str(start)+'-audit.json')).write_text(json.dumps(dict(summary=summary,rows=rows),indent=2)+'\n')
    print(json.dumps(summary,indent=2))
