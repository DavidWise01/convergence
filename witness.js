/* CONVERGENCE / ACT V: read-only evidence network.
   A SHA-256 equality is a fingerprint match, NOT verified source ancestry. */
(() => {
'use strict';
const $=id=>document.getElementById(id);
const canvas=$('graph'),ctx=canvas.getContext('2d'),W=980,H=570;
const endpoint='https://raw.githubusercontent.com/DavidWise01/the-convergence-audit/main/crawler/observations.jsonl';
const colors={observation:'#88dfff',group:'#e6be7e'};
let observations=[],nodes=[],edges=[],selected=null,drag=null,dragOffset=[0,0],tick=0;
const safeUrl=s=>{try{const u=new URL(s);return ['http:','https:'].includes(u.protocol)?u.href:null}catch{return null}};
const hash32=s=>{let h=2166136261;for(const c of s){h=Math.imul(h^c.charCodeAt(0),16777619)}return h>>>0};
const rnd=(seed,i)=>(hash32(seed+':'+i)%100000)/100000;
const text=(str,x,y,size=12,color='#c5d6e4',align='left')=>{ctx.fillStyle=color;ctx.font=size+'px monospace';ctx.textAlign=align;ctx.fillText(str,x,y)};
function drawGrid(){
 ctx.fillStyle='#091522';ctx.fillRect(0,0,W,H);
 ctx.lineWidth=.8;ctx.strokeStyle='rgba(103,159,190,.10)';
 for(let x=0;x<W;x+=42){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}
 for(let y=0;y<H;y+=42){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
 const glow=ctx.createRadialGradient(W/2,H/2,10,W/2,H/2,420);
 glow.addColorStop(0,'rgba(79,146,180,.12)');glow.addColorStop(1,'rgba(79,146,180,0)');
 ctx.fillStyle=glow;ctx.fillRect(0,0,W,H)
}
function build(){
 const q=$('filter').value.toLowerCase().trim(),mode=$('group').value;
 const list=observations.filter(r=>(r.matched_phrase+' '+r.host+' '+r.url).toLowerCase().includes(q)).slice(0,75);
 const groups=new Map();nodes=[];edges=[];
 for(const row of list){
  const key=mode==='host'?(row.host||new URL(row.url).hostname):(row.page_sha256||'UNKNOWN_FINGERPRINT');
  if(!groups.has(key))groups.set(key,[]);
  groups.get(key).push(row);
 }
 const keys=[...groups.keys()];
 keys.forEach((key,i)=>{
  const a=(i/Math.max(1,keys.length))*Math.PI*2-Math.PI/2;
  const r=keys.length===1?0:Math.min(195,65+keys.length*11);
  const x=W/2+Math.cos(a)*r,y=H/2+Math.sin(a)*r*.76;
  const root={id:'group:'+key,type:'group',key,x,y,records:groups.get(key),radius:Math.min(24,10+Math.sqrt(groups.get(key).length)*2)};
  nodes.push(root);
  groups.get(key).forEach((row,j)=>{
   const angle=(j/Math.max(1,groups.get(key).length))*Math.PI*2+rnd(row.id||row.url,1)*.35;
   const rad=47+25*rnd(row.url,2);
   const n={id:'page:'+row.id+':'+j,type:'observation',row,x:x+Math.cos(angle)*rad,y:y+Math.sin(angle)*rad,radius:5};
   nodes.push(n);edges.push([root,n])
  });
 });
 $('status').textContent=observations.length?list.length+' / '+observations.length+' SOURCE OBSERVATIONS · '+keys.length+' '+mode.toUpperCase()+' GROUPS':'NO OBSERVATION RECORDS AVAILABLE';
 selected=null;detail(null)
}
function detail(n){
 const element=$('detail');element.replaceChildren();
 const h=document.createElement('strong');
 h.textContent=n?(n.type==='group'?'GROUP INSPECTION':'OBSERVATION INSPECTION'):'SELECT A NODE';
 element.appendChild(h);
 const p=document.createElement('p');
 p.textContent=!n?'Source details appear here when a public record is available.':n.type==='group'?'Cluster key: '+n.key+' · '+n.records.length+' observations. Grouping is not a verified ancestry edge.':'Pattern: '+(n.row.matched_phrase||'—')+' · observed '+(n.row.observed_utc||'—')+' · ancestry '+(n.row.ancestry||'UNKNOWN');
 element.appendChild(p);
 if(n&&n.type==='observation'){
  const a=document.createElement('a');a.textContent='OPEN ORIGINAL SOURCE ↗';
  const url=safeUrl(n.row.url);if(url){a.href=url;a.target='_blank';a.rel='noopener noreferrer'}element.appendChild(a);
  const hash=document.createElement('p');hash.textContent='PAGE SHA-256: '+(n.row.page_sha256||'unavailable');element.appendChild(hash)
 }
}
function frame(){
 tick+=.01;drawGrid();
 if(!nodes.length){
  text('NO SOURCE RECORDS',W/2,270,25,'#b5d2df','center');
  text('The graph populates from the public ledger when available.',W/2,301,13,'#6f92a8','center');
  text('No artificial nodes are generated.',W/2,327,12,'#c7a979','center');
 }
 for(const [a,b] of edges){
  ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);
  ctx.strokeStyle='rgba(135,199,229,.22)';ctx.lineWidth=1;ctx.stroke()
 }
 for(const n of nodes){
  const r=n.radius+(selected===n?3:0),color=colors[n.type];
  ctx.beginPath();ctx.arc(n.x,n.y,r+6,0,Math.PI*2);ctx.fillStyle=color+'17';ctx.fill();
  ctx.beginPath();ctx.arc(n.x,n.y,r,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();
  if(n.type==='group'){
   ctx.beginPath();ctx.arc(n.x,n.y,r+10+2*Math.sin(tick),0,Math.PI*2);ctx.lineWidth=1;
   ctx.strokeStyle='rgba(230,190,126,.32)';ctx.stroke();
   const label=n.key.length>22?n.key.slice(0,20)+'…':n.key;
   text(label,n.x,n.y+r+23,10,'#ddca9c','center')
  }
 }
 requestAnimationFrame(frame)
}
const point=e=>{const rect=canvas.getBoundingClientRect();return [(e.clientX-rect.left)*W/rect.width,(e.clientY-rect.top)*H/rect.height]};
canvas.addEventListener('pointerdown',e=>{
 const [x,y]=point(e);
 let nearest=null,dist=Infinity;
 for(const n of nodes){const d=Math.hypot(x-n.x,y-n.y);if(d<n.radius+12&&d<dist){nearest=n;dist=d}}
 selected=nearest;detail(selected);
 if(nearest){drag=nearest;dragOffset=[nearest.x-x,nearest.y-y];canvas.setPointerCapture(e.pointerId)}
});
canvas.addEventListener('pointermove',e=>{
 if(!drag)return;const [x,y]=point(e);
 drag.x=Math.max(18,Math.min(W-18,x+dragOffset[0]));
 drag.y=Math.max(18,Math.min(H-18,y+dragOffset[1]))
});
canvas.addEventListener('pointerup',()=>{drag=null});
canvas.addEventListener('pointercancel',()=>{drag=null});
async function load(){
 $('status').textContent='CHECKING PUBLIC LEDGER…';nodes=[];edges=[];observations=[];
 try{
  const ctrl=new AbortController();const timer=setTimeout(()=>ctrl.abort(),10000);
  let response;try{response=await fetch(endpoint,{signal:ctrl.signal,cache:'no-store'})}finally{clearTimeout(timer)}
  if(!response.ok)throw Error('HTTP '+response.status);
  const body=await response.text();if(body.length>2500000)throw Error('ledger exceeds view cap');
  const arr=body.trim()?body.trim().split(/\r?\n/).map(l=>JSON.parse(l)):[];
  observations=arr.filter(r=>r&&typeof r.url==='string'&&safeUrl(r.url)&&typeof r.matched_phrase==='string').reverse();
  build();
 }catch(e){$('status').textContent='LEDGER UNAVAILABLE · '+e.message;detail(null)}
}
$('group').addEventListener('change',build);$('filter').addEventListener('input',build);
$('reload').addEventListener('click',load);
frame();load();
})();
