/* CONVERGENCE // The Last Witness
   Original Canvas2D procedural elemental animation. All lore is fiction.
   Evidence tab reads an external, source-linked JSONL ledger without manufacturing records.
*/
(() => {
'use strict';
const $ = id => document.getElementById(id);
const canvas=$('stage');
const ctx=canvas.getContext('2d',{alpha:false});
const W=1280,H=720;
const reduced=window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const scenes=[
 {name:'THE TWO HORIZONS',speaker:'NARRATOR',line:'At the last edge of the archive, two powers meet. One burns for an answer; one refuses to invent one.',cool:88,hot:92},
 {name:'THE SKY OPENS',speaker:'THE INFERNO',line:'A thousand echoes say the same thing. Are they not a thousand witnesses?',cool:80,hot:100},
 {name:'THE STILL POINT',speaker:'THE WITNESS',line:'An echo is not an origin. I will remember the flame without naming its maker.',cool:100,hot:73},
 {name:'THE UNBROKEN THREAD',speaker:'NARRATOR',line:'Neither sky nor fire is erased. What remains is the record: what was seen, where, and when.',cool:100,hot:45}
];
let scene=0,playing=true,elapsed=0,last=0,sound=false,audio=null,osc=null,gain=null;
let stars=[],embers=[],sparks=[];
const rand=(a,b)=>a+Math.random()*(b-a);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const title=$('scene-name'),number=$('scene-number'),speaker=$('speaker'),line=$('dialogue-line');
function seed(){stars=Array.from({length:155},()=>({x:rand(0,W),y:rand(0,H*.56),r:rand(.5,1.9),o:rand(.18,.78)}));embers=Array.from({length:115},()=>({x:rand(0,W),y:rand(0,H),r:rand(.5,3),vx:rand(-.3,1),vy:rand(-1.4,-.3),phase:rand(0,9),hot:Math.random()>.43}));sparks=Array.from({length:65},()=>({angle:rand(0,Math.PI*2),orbit:rand(65,235),speed:rand(-.75,.75),size:rand(.5,2.9)}))}
seed();
function change(n){
 scene=(n+scenes.length)%scenes.length;elapsed=0;
 const s=scenes[scene];
 title.textContent=s.name;number.textContent=['I','II','III','IV'][scene]+' / IV';
 speaker.textContent=s.speaker;line.textContent=s.line;
 $('witness-meter').style.width=s.cool+'%';$('inferno-meter').style.width=s.hot+'%';
 document.querySelectorAll('[data-scene]').forEach((b,i)=>{b.classList.toggle('selected',i===scene);b.setAttribute('aria-current',i===scene?'step':'false')});
 if(sound && osc) osc.frequency.setTargetAtTime(80+scene*14,audio.currentTime,.18);
}
const glow=(x,y,r,col,opacity=1)=>{
 const g=ctx.createRadialGradient(x,y,1,x,y,r);
 g.addColorStop(0,col);g.addColorStop(1,'rgba(0,0,0,0)');
 ctx.globalAlpha=opacity;ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;
};
function mountain(points,fill){ctx.beginPath();ctx.moveTo(0,H);for(const [x,y] of points)ctx.lineTo(x,y);ctx.lineTo(W,H);ctx.closePath();ctx.fillStyle=fill;ctx.fill()}
function wash(t){
 const sky=ctx.createLinearGradient(0,0,0,H);
 sky.addColorStop(0,'#0a1528');sky.addColorStop(.48,scene>1?'#38334c':'#3c2638');sky.addColorStop(1,'#050910');
 ctx.fillStyle=sky;ctx.fillRect(0,0,W,H);
 glow(980,250,430,'rgba(252,87,42,.34)');glow(280,250,430,'rgba(74,194,255,.28)');
 for(const s of stars){ctx.fillStyle='rgba(225,245,255,'+(s.o*(.8+.2*Math.sin(t*1.5+s.x)))+')';ctx.fillRect(s.x,s.y,s.r,s.r)}
 // Eclipse and celestial rings
 glow(636,263,260,'rgba(245,200,165,.23)');
 ctx.strokeStyle='rgba(224,193,168,.38)';ctx.lineWidth=3;
 for(let i=0;i<4;i++){ctx.beginPath();ctx.ellipse(638,262,130+i*24,130+i*24,.25+i*.2,t*.035+i*.65,t*.035+i*.65+4.9);ctx.stroke()}
 ctx.fillStyle='#101b2b';ctx.beginPath();ctx.arc(638,261,109,0,Math.PI*2);ctx.fill();
 ctx.strokeStyle='#b8cfe44f';ctx.lineWidth=2;ctx.stroke();
 mountain([[0,440],[94,331],[202,423],[303,320],[398,425],[490,346],[622,439],[728,325],[833,410],[963,306],[1110,403],[1280,325]],'#121b29');
 mountain([[0,525],[170,429],[255,482],[370,397],[490,480],[601,416],[722,480],[850,379],[991,467],[1112,409],[1280,493]],'#0b1520');
 ctx.fillStyle='#090f18';ctx.beginPath();ctx.moveTo(0,585);ctx.lineTo(240,545);ctx.lineTo(390,560);ctx.lineTo(580,512);ctx.lineTo(733,551);ctx.lineTo(910,509);ctx.lineTo(W,561);ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.fill();
 for(let k=0;k<13;k++){let y=555+k*17;ctx.strokeStyle='rgba(155,174,196,'+(0.12-k*.007)+')';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(0,y+Math.sin(k)*5);ctx.quadraticCurveTo(640,y+8*Math.cos(t*.2+k),1280,y+Math.sin(k)*5);ctx.stroke()}
}
function ribbon(originX,originY,sign,t,hot){
 ctx.save();ctx.globalCompositeOperation='screen';
 for(let j=0;j<7;j++){
  const phase=t*(hot?2.0:1.25)+j*.6;
  ctx.beginPath();
  for(let i=0;i<=90;i++){
   const u=i/90;
   const x=originX+sign*u*(250+scene*15)+Math.sin(phase+u*13+j)*u*31;
   const y=originY-70*Math.sin(u*Math.PI)+Math.cos(phase+u*10+j*.9)*(22+u*85)+(j-3)*7;
   i?ctx.lineTo(x,y):ctx.moveTo(x,y)
  }
  ctx.lineWidth=(hot?3.8:2.7)*(1-j/10);
  ctx.strokeStyle=hot?'rgba(255,'+(100+j*13)+',61,'+(.4+j*.07)+')':'rgba('+(76+j*14)+',223,255,'+(.31+j*.08)+')';
  ctx.shadowColor=hot?'#ff631f':'#6ae8ff';ctx.shadowBlur=28;
  ctx.stroke();
 }
 ctx.restore();
}
function figure(x,y,scale,facing,hot,t){
 ctx.save();ctx.translate(x,y);ctx.scale(scale*facing,scale);ctx.lineCap='round';ctx.lineJoin='round';
 const bob=Math.sin(t*1.85+(hot?2:0))*5;
 ctx.translate(0,bob);
 const color=hot?'#bd4a2f':'#bed8d6',edge=hot?'#ff9b50':'#a9f3ff';
 glow(0,-125,180,hot?'rgba(255,98,49,.24)':'rgba(94,232,255,.22)');
 // trailing cloak / robes
 ctx.fillStyle=hot?'#491c24':'#1d4357';
 ctx.beginPath();ctx.moveTo(-27,-183);ctx.quadraticCurveTo(-80,-91,-100,6);ctx.quadraticCurveTo(-38,17,23,0);ctx.lineTo(42,-171);ctx.closePath();ctx.fill();
 ctx.strokeStyle=edge;ctx.globalAlpha=.7;ctx.lineWidth=2;ctx.stroke();ctx.globalAlpha=1;
 // legs
 ctx.strokeStyle=color;ctx.lineWidth=24;ctx.beginPath();ctx.moveTo(-14,-75);ctx.lineTo(-35,-5);ctx.moveTo(10,-75);ctx.lineTo(37,-5);ctx.stroke();
 // body
 ctx.fillStyle=hot?'#7c2930':'#365a63';ctx.beginPath();ctx.moveTo(-35,-202);ctx.quadraticCurveTo(0,-221,33,-198);ctx.lineTo(26,-84);ctx.lineTo(-23,-82);ctx.closePath();ctx.fill();
 ctx.strokeStyle=edge;ctx.lineWidth=2;ctx.stroke();
 ctx.strokeStyle=hot?'#eab16a':'#9be6ec';ctx.beginPath();ctx.moveTo(-25,-130);ctx.lineTo(26,-130);ctx.stroke();
 // expressive arms
 ctx.strokeStyle=color;ctx.lineWidth=20;
 ctx.beginPath();ctx.moveTo(-27,-184);ctx.lineTo(-69,-151+Math.sin(t)*12);ctx.lineTo(-89,-113);ctx.moveTo(27,-186);ctx.lineTo(67,-166);ctx.lineTo(100,-175+Math.sin(t*1.4)*11);ctx.stroke();
 // head and luminous face
 ctx.fillStyle=hot?'#d69a78':'#d5cab6';ctx.beginPath();ctx.ellipse(0,-245,28,35,-.07,0,Math.PI*2);ctx.fill();
 ctx.fillStyle=hot?'#3d2021':'#244450';
 ctx.beginPath();ctx.moveTo(-28,-253);ctx.quadraticCurveTo(5,-312,31,-252);ctx.lineTo(13,-277);ctx.lineTo(-22,-259);ctx.closePath();ctx.fill();
 ctx.fillStyle=hot?'#ffb05e':'#b6faff';ctx.fillRect(6,-244,5,2);ctx.shadowBlur=15;ctx.shadowColor=edge;
 // orbiting sigil
 ctx.strokeStyle=edge;ctx.lineWidth=3;ctx.beginPath();ctx.arc(104,-175+Math.sin(t*1.4)*11,14,0,Math.PI*2);ctx.stroke();
 ctx.restore();
}
function particles(t,dt){
 ctx.save();ctx.globalCompositeOperation='screen';
 for(const p of embers){
  p.x+=p.vx*dt*60;p.y+=p.vy*dt*60;
  if(p.y<0){p.y=H;p.x=rand(0,W)}
  if(p.x>W)p.x=0;
  const red=p.hot;
  ctx.fillStyle=red?'rgba(255,155,64,.7)':'rgba(137,235,255,.53)';
  ctx.beginPath();ctx.arc(p.x+Math.sin(t+p.phase)*11,p.y,p.r,0,Math.PI*2);ctx.fill();
 }
 const cx=637,cy=342;
 for(const s of sparks){
  const a=s.angle+t*s.speed,r=s.orbit*(.66+.2*Math.sin(t+s.angle));
  let x=cx+Math.cos(a)*r,y=cy+Math.sin(a*1.23)*r*.73;
  ctx.fillStyle=Math.cos(a)<0?'#a8ecff':'#ffc07b';ctx.globalAlpha=.45+Math.sin(t*3+a)*.3;ctx.beginPath();ctx.arc(x,y,s.size,0,Math.PI*2);ctx.fill()
 }
 ctx.restore();ctx.globalAlpha=1;
}
function collision(t){
 const power=scene===0?.45:scene===1?1:scene===2?.75:.3;
 const pulse=1+.08*Math.sin(t*4);
 glow(636,335,210*power,'rgba(255,242,213,.42)');
 ctx.save();ctx.globalCompositeOperation='screen';
 for(let k=0;k<4;k++){
  const r=(47+k*24)*pulse*power+20;
  ctx.strokeStyle=k%2?'rgba(134,230,255,.62)':'rgba(255,168,91,.63)';
  ctx.lineWidth=2.4;ctx.beginPath();ctx.arc(636,339,r,t*.25+k,t*.25+k+4.1);ctx.stroke()
 }
 const g=ctx.createRadialGradient(635,338,3,635,338,65*power+10);
 g.addColorStop(0,'rgba(255,255,255,.95)');g.addColorStop(.25,'rgba(255,239,207,.77)');g.addColorStop(.65,'rgba(238,159,95,.20)');g.addColorStop(1,'rgba(0,0,0,0)');
 ctx.fillStyle=g;ctx.beginPath();ctx.arc(635,338,65*power+10,0,Math.PI*2);ctx.fill();ctx.restore();
}
function frame(ms){
 if(!last)last=ms;
 const dt=Math.min(.05,(ms-last)/1000||0);last=ms;
 if(playing) elapsed+=dt;
 let t=elapsed;
 if(playing&&!reduced && elapsed>19)change(scene+1);
 if(ctx){
  wash(t);ribbon(384,404,1,t,false);ribbon(893,414,-1,t,true);
  figure(357,582,1.15,1,false,t);
  figure(931,577,1.23,-1,true,t);
  collision(t);particles(t,playing?dt:0);
  // symbolic convergence: two observed paths, one center, not a causal claim
  if(scene===3){
   ctx.strokeStyle='rgba(255,231,169,.45)';ctx.lineWidth=2;ctx.setLineDash([5,9]);
   ctx.beginPath();ctx.moveTo(505,353);ctx.quadraticCurveTo(636,226,764,353);ctx.stroke();ctx.setLineDash([])
  }
 }
 requestAnimationFrame(frame);
}
function tab(id){
 document.querySelectorAll('.pane').forEach(p=>{const show=p.id===id;p.hidden=!show;p.classList.toggle('active',show)});
 document.querySelectorAll('[data-tab]').forEach(b=>{const show=b.dataset.tab===id;b.classList.toggle('active',show);b.setAttribute('aria-pressed',String(show))});
 if(id==='atlas'&&!atlasLoaded)loadAtlas();
 window.location.hash=id;window.scrollTo({top:0,behavior:'smooth'});
}
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.tab)));
$('enter-atlas').addEventListener('click',()=>tab('atlas'));
$('next').addEventListener('click',()=>change(scene+1));
$('previous').addEventListener('click',()=>change(scene-1));
$('play').addEventListener('click',()=>{playing=!playing;$('play').textContent=playing?'Ⅱ':'▶';$('play').setAttribute('aria-label',playing?'Pause animation':'Resume animation')});
document.querySelectorAll('[data-scene]').forEach(b=>b.addEventListener('click',()=>change(Number(b.dataset.scene))));
window.addEventListener('keydown',e=>{if(document.activeElement?.tagName==='INPUT')return;if(e.key==='ArrowRight')change(scene+1);else if(e.key==='ArrowLeft')change(scene-1);else if(e.key===' '){e.preventDefault();$('play').click()}});
$('sound').addEventListener('click',async()=>{
 try{
 if(!audio){audio=new (window.AudioContext||window.webkitAudioContext)();osc=audio.createOscillator();gain=audio.createGain();osc.type='sine';osc.frequency.value=80;gain.gain.value=0;osc.connect(gain).connect(audio.destination);osc.start()}
 if(audio.state==='suspended')await audio.resume();
 sound=!sound;gain.gain.setTargetAtTime(sound?.025:0,audio.currentTime,.08);
 $('sound').textContent=sound?'♪ ON':'♪ OFF';$('sound').setAttribute('aria-pressed',String(sound))
 }catch(e){$('sound').textContent='AUDIO N/A'}
});
const LEDGER='https://raw.githubusercontent.com/DavidWise01/the-convergence-audit/main/crawler/observations.jsonl';
let atlasLoaded=false,records=[];
function safeLink(raw){
 try{const url=new URL(raw);return ['https:','http:'].includes(url.protocol)?url.href:null}catch{return null}
}
function card(record){
 const el=document.createElement('article');el.className='obs-card';
 const label=document.createElement('span');label.className='candidate';label.textContent=record.status||'UNREVIEWED';el.appendChild(label);
 const h=document.createElement('h3');h.textContent=record.matched_phrase||'UNLABELED OBSERVATION';el.appendChild(h);
 const a=document.createElement('a');a.textContent=record.url||'Source not provided';a.href=safeLink(record.url)||'#';a.target='_blank';a.rel='noopener noreferrer';if(!safeLink(record.url))a.removeAttribute('href');el.appendChild(a);
 const dl=document.createElement('dl');
 for(const [name,value] of [['OBSERVED',record.observed_utc],['ANCESTRY',record.ancestry||'UNKNOWN'],['CONTENT HASH',String(record.page_sha256||'').slice(0,20)+'…']]){
  const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=name;dd.textContent=value||'—';dl.append(dt,dd)
 }
 el.appendChild(dl);return el
}
function render(){
 const q=$('search').value.trim().toLowerCase(),list=records.filter(r=>JSON.stringify([r.url,r.host,r.matched_phrase]).toLowerCase().includes(q));
 const holder=$('observations');holder.replaceChildren();
 for(const r of list.slice(0,100))holder.appendChild(card(r));
 if(!list.length){const p=document.createElement('p');p.className='atlas-status';p.textContent=records.length?'No observations match the filter.':'No crawler observations available yet. The atlas does not generate sample evidence.';holder.appendChild(p)}
 $('atlas-status').textContent=records.length?String(list.length)+' matching of '+records.length+' loaded observations (first 100 shown).':'No observation ledger available or it contains no records.'
}
async function loadAtlas(){
 atlasLoaded=true;$('atlas-status').textContent='Checking the public observation ledger…';
 try{
  const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),10000);
  let response;
  try{response=await fetch(LEDGER,{signal:controller.signal,cache:'no-store'})}finally{clearTimeout(timer)}
  if(!response.ok)throw Error('HTTP '+response.status);
  const text=await response.text();if(text.length>2500000)throw Error('ledger exceeds display limit');
  records=text.trim()?text.trim().split(/\r?\n/).map(s=>JSON.parse(s)).filter(x=>x&&typeof x==='object'&&x.url&&x.matched_phrase):[];
  records.reverse();
  $('stat-total').textContent=String(records.length);
  $('stat-hosts').textContent=String(new Set(records.map(r=>r.host||new URL(r.url).hostname)).size);
  render()
 }catch(e){
  records=[];$('stat-total').textContent='—';$('stat-hosts').textContent='—';
  $('atlas-status').textContent='Ledger unavailable ('+e.message+'). The story still works offline; evidence is not fabricated.';
  $('observations').replaceChildren()
 }
}
$('reload').addEventListener('click',loadAtlas);
$('search').addEventListener('input',render);
change(0);
if(reduced){playing=false;$('play').textContent='▶'}
requestAnimationFrame(frame);
if(['#atlas','#lineage'].includes(window.location.hash))tab(window.location.hash.slice(1));
})();
