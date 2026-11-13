/* CONVERGENCE PROVENANCE BOUNDARY / 003
   Pure deterministic classifier. No network, no model, no fabricated attestations.
   Does not infer a root from page count, identical content, or a claimed author.
*/
(function(root,factory){
 const engine=factory();
 if(typeof module==='object' && module.exports) module.exports=engine;
 if(root) root.ConvergenceBoundary=engine;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const STATES=Object.freeze(['KNOWN','PARTIAL','INACCESSIBLE','UNKNOWN']);
 const isTrue=x=>x===true;
 function classify(packet){
  if(!packet||typeof packet!=='object'||Array.isArray(packet)) throw TypeError('packet must be an object');
  // Boolean flags require explicit true; absence and false are not interchangeable evidence.
  const complete=isTrue(packet.chain_complete);
  const origin=isTrue(packet.origin_authenticated);
  const steps=isTrue(packet.verified_steps);
  const blocked=isTrue(packet.access_block_verified);
  const witness=isTrue(packet.witness_agreement_verified);
  const flags={origin_authenticated:origin,chain_complete:complete,verified_steps:steps,
   access_block_verified:blocked,witness_agreement_verified:witness};
  const trace=[],notes=[];
  // A complete chain means every link from the specified origin through its observed
  // endpoint has independently checkable evidence. Agreement is necessary when
  // trust is *shared*, but this engine does not fabricate multiple witnesses.
  let state;
  if(origin&&complete&&steps){
   state='KNOWN';trace.push('Authenticated origin + verified steps + complete scoped chain.');
   if(!witness) notes.push('Individual chain is known; independent multi-witness agreement is NOT established.');
  }else if(origin||steps){
   state='PARTIAL';trace.push('At least one origin/step is evidenced, but a complete authenticated chain is not.');
  }else if(blocked){
   state='INACCESSIBLE';trace.push('A specific access obstacle is evidenced; no validated origin or step can be examined.');
  }else{
   state='UNKNOWN';trace.push('No verified origin, verified step, or evidenced access barrier.');
  }
  if(blocked&&state!=='INACCESSIBLE')notes.push('Documented access barrier remains; partial evidence is not erased.');
  if(complete&&!origin)notes.push('A chain marked complete without an authenticated origin is not KNOWN.');
  if(packet.claimed_origin&&!origin)notes.push('A claimed origin is not an authenticated origin.');
  if(packet.same_hash_count>1)notes.push('Repeated matching page fingerprints do not demonstrate independent ancestry.');
  const sharedCheckpoint=state==='KNOWN'&&witness;
  return Object.freeze({state,flags:Object.freeze(flags),trace:Object.freeze(trace),notes:Object.freeze(notes),
   shared_checkpoint_eligible:sharedCheckpoint,
   claim_of_copying:false,claim_of_influence:false});
 }
 return Object.freeze({STATES,classify});
});
