// Run: node boundary/test_provenance.cjs
'use strict';
const assert=require('node:assert/strict');
const {classify,STATES}=require('./provenance.js');
const cases=[
 {name:'no source',packet:{},state:'UNKNOWN',share:false},
 {name:'unverified reported owner',packet:{claimed_origin:'A'},state:'UNKNOWN',share:false},
 {name:'explicit blockade no readable steps',packet:{access_block_verified:true},state:'INACCESSIBLE',share:false},
 {name:'a verified step but incomplete history',packet:{verified_steps:true},state:'PARTIAL',share:false},
 {name:'known root with missing link',packet:{origin_authenticated:true,chain_complete:false},state:'PARTIAL',share:false},
 {name:'some verified steps plus denied access',packet:{verified_steps:true,access_block_verified:true},state:'PARTIAL',share:false},
 {name:'claimed completeness without origin',packet:{chain_complete:true,verified_steps:true},state:'PARTIAL',share:false},
 {name:'verified complete individual history',packet:{origin_authenticated:true,verified_steps:true,chain_complete:true},state:'KNOWN',share:false},
 {name:'verified complete history with witness agreement',packet:{origin_authenticated:true,verified_steps:true,chain_complete:true,witness_agreement_verified:true},state:'KNOWN',share:true},
 {name:'many duplicate links are not roots',packet:{same_hash_count:1000},state:'UNKNOWN',share:false},
 {name:'false is not verified',packet:{access_block_verified:false},state:'UNKNOWN',share:false},
 {name:'string true is not evidence',packet:{origin_authenticated:'true',verified_steps:'true',chain_complete:'true'},state:'UNKNOWN',share:false}
];
for(const c of cases){
 const actual=classify(c.packet);
 assert.equal(actual.state,c.state,c.name);
 assert.equal(actual.shared_checkpoint_eligible,c.share,c.name+' / checkpoint');
 assert.equal(actual.claim_of_copying,false,c.name+' / copying');
 assert.equal(actual.claim_of_influence,false,c.name+' / influence');
 assert.ok(STATES.includes(actual.state));
}
assert.throws(()=>classify(null),TypeError);
assert.throws(()=>classify([]),TypeError);
console.log('PASS '+(cases.length+2)+' provenance invariants.');
