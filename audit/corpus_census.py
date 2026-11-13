#!/usr/bin/env python3
"""CVG-011 — deterministic multi-run ROOT0 corpus census and comparison.

Two owned surfaces: public GitHub DavidWise01 and 0root.ai, *one* corpus ancestry.
An individual run does not claim exhaustive completion. Both repository and file coverage
are reported, with explicit errors/skips. Never infer copying or external transmission.
No third-party libraries; Python 3.11+.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"evidence"/"corpus-census"
API="https://api.github.com"
OWNER="DavidWise01"
USER_AGENT="ROOT0-Convergence-Census/1.0 (public research; https://github.com/DavidWise01/convergence)"
TARGET={
 "genesis_unity":["many minds","unity","together","collective","hive","mesh","lattice","the source"],
 "sovereign_non_domination":["sovereign","guidance","domination","consent","authority","not control"],
 "witness_ancestry":["witness","lineage","ancestry","independent","provenance","source root","trace roots"],
 "memory_preservation":["append-only","immutable","memory","preserve","sealed","merkle","watermark"],
 "alchemy_rejoining":["solve et coagula","alchemy","dissolve","coagula","flay","fold","unbind","recombine"],
 "distributed_keepers":["keeper","cortex","agents","multi-agent","moe","swarm","diaspora"]
}
PHRASES=[
 "guidance ≠ domination",
 "one source ancestry",
 "witness lineage",
 "trace roots",
 "sovereign hive choice",
 "correctness over quickness",
 "extrapolate verify execute",
 "non unam vocem",
 "solve et coagula",
 "unum corpus multae mentes",
]
# No blanket assertion that shared generic words are unique, meaningful or transmitted.
SUFFIXES={".md",".txt",".rst",".html",".htm",".js",".ts",".py",".json",".jsonl",".yaml",".yml",".dlw"}
MAX_FILE_BYTES=180_000
API_SLEEP=.30

class TextPage(HTMLParser):
 def __init__(self):
  super().__init__(); self.parts=[];self.skip=0;self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag in ("script","style","noscript"):self.skip+=1
  if tag=="a":
   d=dict(attrs)
   if d.get("href"):self.links.append(d["href"])
 def handle_endtag(self,tag):
  if tag in ("script","style","noscript"): self.skip=max(0,self.skip-1)
 def handle_data(self,data):
  if not self.skip:self.parts.append(data)
 def text(self):return re.sub(r"\s+"," "," ".join(self.parts))

def get(url,token=None,maxbytes=2_500_000):
 parsed=urllib.parse.urlparse(url)
 if parsed.scheme!="https" or parsed.hostname not in {"api.github.com","raw.githubusercontent.com","0root.ai","www.0root.ai"}:
  raise ValueError("Host not allowlisted")
 headers={"User-Agent":USER_AGENT,"Accept":"application/vnd.github+json" if parsed.hostname=="api.github.com" else "text/html,text/plain;q=.9"}
 if token and parsed.hostname=="api.github.com":headers["Authorization"]="Bearer "+token
 req=urllib.request.Request(url,headers=headers)
 with urllib.request.urlopen(req,timeout=18) as r:
  final=urllib.parse.urlparse(r.geturl())
  if final.scheme!="https" or final.hostname not in {"api.github.com","raw.githubusercontent.com","0root.ai","www.0root.ai"}:
   raise ValueError("unsafe_redirect_destination")
  payload=r.read(maxbytes+1)
  if len(payload)>maxbytes:raise ValueError("response_too_large")
  return payload.decode("utf-8","replace")

def digest(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
def slugify(s):return re.sub(r"[^a-z0-9]","-",s.lower()).strip("-")
def phrase_scan(text):
 norm=re.sub(r"\s+"," ",html.unescape(text)).casefold()
 terms={}
 for category,words in TARGET.items():
  terms[category]=sorted({w for w in words if re.search(r"(?<!\w)"+re.escape(w)+r"(?!\w)",norm)})
 exact=[p for p in PHRASES if p in norm]
 return {k:v for k,v in terms.items() if v},exact

def load_state():
 path=OUT/"state.json"
 if path.exists():return json.loads(path.read_text(encoding="utf-8"))
 return {"schema":"root0.corpus-census-state/1","owner":OWNER,"seen":{},"pages":{},"mirror_dedupe":"same owned corpus, not two independent evidentiary witnesses"}

def atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix(path.suffix+".tmp")
 temp.write_text(json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
 temp.replace(path)

def discover(token):
 """GitHub public user's all repositories, paginated; only complete after empty page."""
 repos=[]
 page=1
 while True:
  url=f"{API}/users/{OWNER}/repos?per_page=100&page={page}&type=owner&sort=full_name"
  batch=json.loads(get(url,token))
  if not isinstance(batch,list):raise ValueError("Unexpected repo response")
  repos.extend(batch)
  if len(batch)<100:break
  page+=1
  if page>200:raise RuntimeError("Repository census page ceiling")
 # Full name/ID case-normalized; forks included, archived included, private excluded.
 d={x["full_name"].lower():x for x in repos if x.get("owner",{}).get("login","").lower()==OWNER.lower()}
 return sorted(d.values(),key=lambda r:r["full_name"].lower())

def tree_files(repo,token):
 branch=urllib.parse.quote(repo["default_branch"],safe="")
 url=f"{API}/repos/{OWNER}/{urllib.parse.quote(repo['name'],safe='')}/git/trees/{branch}?recursive=1"
 obj=json.loads(get(url,token,maxbytes=12_000_000))
 if obj.get("truncated"):raise ValueError("truncated_git_tree")
 return sorted([x for x in obj.get("tree",[]) if x.get("type")=="blob" and Path(x["path"]).suffix.lower() in SUFFIXES],key=lambda x:x["path"].lower())

def rank_path(p):
 path=p.lower()
 return (0 if path in ("readme.md","readme.txt") else
         1 if path in ("index.html","docs/readme.md") else
         2 if any(s in path for s in ("witness","lineage","sovereign","memory","genesis","governance","alchemy","hive","diatom","provenance","cubit")) else
         3 if path.endswith((".md",".txt",".dlw")) else
         4,path)

def repo_scan(repo,token,maxfiles,previous=None):
 """Resume in ranked file-order. Never mark a repo fully scanned after just the first batch."""
 name=repo["name"];files=tree_files(repo,token)
 candidates=[f for f in sorted(files,key=lambda x:rank_path(x["path"])) if (f.get("size") or 0)<=MAX_FILE_BYTES]
 old=previous if previous and previous.get("status") in ("PARTIAL","SCANNED") else {}
 cursor=int(old.get("next_file_index",0))
 # Reject impossible stale cursor; inventory reorders across source commits -> surface caveat.
 cursor=min(cursor,len(candidates))
 chosen=candidates[cursor:cursor+maxfiles]
 errors=list(old.get("errors",[]));hits=list(old.get("hits",[]))
 fetch_ok=int(old.get("files_fetched",0))
 for f in chosen:
  raw=f"https://raw.githubusercontent.com/{OWNER}/{urllib.parse.quote(repo['default_branch'],safe='')}/{urllib.parse.quote(f['path'],safe='/')}"
  try:
   body=get(raw,maxbytes=MAX_FILE_BYTES+1)
   fetch_ok+=1
   source=TextPage()
   if f["path"].lower().endswith((".html",".htm")):
    source.feed(body);body=source.text()
   themes,exact=phrase_scan(body)
   if themes or exact:
    hit={"path":f["path"],"file_sha256":digest(body),"themes":themes,"exact_phrases":exact,"url":f"https://github.com/{OWNER}/{name}/blob/{repo['default_branch']}/{urllib.parse.quote(f['path'],safe='/')}"}
    if not any(x.get("path")==hit["path"] and x.get("file_sha256")==hit["file_sha256"] for x in hits):hits.append(hit)
  except Exception as e:errors.append({"path":f["path"],"error":type(e).__name__})
 next_index=cursor+len(chosen)
 return {"repo":repo["full_name"],"default_branch":repo["default_branch"],"fork":bool(repo.get("fork")),"archived":bool(repo.get("archived")),
 "files_eligible":len(files),"files_small_enough":len(candidates),"files_selected":next_index,
 "next_file_index":next_index,"files_fetched":fetch_ok,"files_skipped_budget":max(0,len(candidates)-next_index),
 "files_skipped_size":len(files)-len(candidates),
 "status":"SCANNED" if next_index>=len(candidates) else "PARTIAL",
 "scan_mode":"ALL_SIZE_ELIGIBLE_FILES" if next_index>=len(candidates) else "RESUMABLE_PARTIAL",
 "head_revision_pinned":False,
 "hits":hits,"errors":errors}

def allowed_robot(url,cache):
 p=urllib.parse.urlparse(url);origin=f"{p.scheme}://{p.hostname}"
 if origin not in cache:
  rp=urllib.robotparser.RobotFileParser()
  rp.set_url(origin+"/robots.txt")
  try:rp.read();cache[origin]=rp
  except Exception:cache[origin]=None
 return cache[origin] is not None and cache[origin].can_fetch(USER_AGENT,url)

def site_scan(state,maxpages):
 """Resumable public 0root.ai site traversal; stop if robots cannot be checked."""
 queue=list(state.get("site_queue",["https://0root.ai/","https://0root.ai/world2/"]))
 seen=set(state.get("site_seen",[]))
 robots={};count=0;errs=[]
 attempts=0
 while queue and count<maxpages and attempts<maxpages*4:
  u=queue.pop(0);attempts+=1
  p=urllib.parse.urlparse(u)
  if p.scheme!="https" or p.hostname not in ("0root.ai","www.0root.ai") or u in seen:continue
  seen.add(u)
  if not allowed_robot(u,robots):errs.append({"url":u,"error":"robots_unreadable_or_disallowed"});continue
  try:
   body=get(u,maxbytes=1_000_000)
   page=TextPage();page.feed(body);content=page.text()
   themes,exact=phrase_scan(content)
   state["pages"][u]={"url":u,"sha256":digest(content),"themes":themes,"exact_phrases":exact,
     "host":p.hostname,"owned_ancestry":"DavidWise01/0root.ai","source_surface":"public_website"}
   count+=1
   for link in page.links[:300]:
    nxt=urllib.parse.urldefrag(urllib.parse.urljoin(u,link))[0]
    q=urllib.parse.urlparse(nxt)
    if q.scheme=="https" and q.hostname in ("0root.ai","www.0root.ai") and nxt not in seen and nxt not in queue and len(queue)<15000:
     queue.append(nxt)
   time.sleep(.4)
  except Exception as e:errs.append({"url":u,"error":type(e).__name__})
 state["site_queue"]=queue
 state["site_seen"]=sorted(seen)
 state["site_errors"]=list(state.get("site_errors",[]))+errs
 return {"visited_ok":count,"errors":errs,"seen_urls_total":len(seen),"remaining_url_queue":len(queue)}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--max-repos",type=int,default=60)
 ap.add_argument("--max-files-per-repo",type=int,default=12)
 ap.add_argument("--max-site-pages",type=int,default=35)
 ap.add_argument("--site",action="store_true")
 args=ap.parse_args()
 token=os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
 state=load_state()
 now=dt.datetime.now(dt.timezone.utc).isoformat()
 try:
  census=discover(token)
 except Exception as e:
  atomic(OUT/"last-error.json",{"time":now,"stage":"repository_enumeration","error":str(e),"type":type(e).__name__})
  raise
 expected={r["full_name"].lower() for r in census}
 # Fail closed on incomplete enumeration: count based on authoritative paginated API.
 state["repository_inventory"]={"time_utc":now,"public_repos_enumerated":len(census),"complete_paginated_enumeration":True,
   "scope":"PUBLIC repositories under owner, forks/archived included; not private repos, issues, external archives or history"}
 for r in census:
  name=r["full_name"]
  if name not in state["seen"]:
   state["seen"][name]={"status":"PENDING","repo":name}
 completed=0;errors=0
 for r in census:
  name=r["full_name"]
  if state["seen"][name].get("status")=="SCANNED":continue
  if completed+errors>=max(0,args.max_repos):break
  try:
   result=repo_scan(r,token,max(1,args.max_files_per_repo),state["seen"].get(name))
   result["observed_utc"]=now
   state["seen"][name]=result;completed+=1
  except Exception as e:
   state["seen"][name]={"repo":name,"status":"ERROR","type":type(e).__name__,"error":str(e),"observed_utc":now};errors+=1
  # Save each step for recoverability in local runner, then Actions commits once.
  if (completed+errors)%10==0:atomic(OUT/"state.json",state)
  time.sleep(API_SLEEP)
 site=None
 if args.site:site=site_scan(state,max(1,args.max_site_pages))
 atomic(OUT/"state.json",state)
 rows=[v for k,v in state["seen"].items() if k.lower() in expected]
 scanned=[v for v in rows if v.get("status") in ("SCANNED","PARTIAL")]
 fully_scanned=[v for v in rows if v.get("status")=="SCANNED"]
 report={
  "schema":"root0.convergence.corpus-coverage/1","generated_utc":now,
  "owned_source_surfaces":["github.com/DavidWise01","0root.ai"],
  "one_ancestry_two_surfaces":True,"github_public_repositories_enumerated":len(census),
  "github_repositories_started":len(scanned),"github_repositories_scanned":len(fully_scanned),"github_repositories_partial":sum(v.get("status")=="PARTIAL" for v in rows),"github_repositories_error":sum(v.get("status")=="ERROR" for v in rows),
  "github_repositories_pending":sum(v.get("status")=="PENDING" for v in rows),
  "github_eligible_files":sum(v.get("files_eligible",0) for v in scanned),
  "github_files_fetched":sum(v.get("files_fetched",0) for v in scanned),
  "github_files_skipped_budget":sum(v.get("files_skipped_budget",0) for v in scanned),
  "github_files_skipped_size":sum(v.get("files_skipped_size",0) for v in scanned),
  "github_revisions_not_pinned":True,
  "github_file_errors":sum(len(v.get("errors",[])) for v in scanned),
  "site_unique_pages_scanned":len(state["pages"]),
  "site_last_run":site,
  "claims_not_supported":["all source files read","private repos examined","historical revisions exhausted","all 0root.ai pages covered","independent source origins inferred","cross-platform copying proven"],
  "repository_census_complete":True,
  "repo_level_scan_complete":len(fully_scanned)==len(census),
  "all_eligible_file_contents_complete":len(fully_scanned)==len(census) and all(v.get("files_skipped_budget",0)==0 and v.get("files_skipped_size",0)==0 and not v.get("errors") for v in scanned),
  "website_complete":not bool(state.get("site_queue")) and not bool(state.get("site_errors")) and len(state["pages"])>0,
  "website_pages_errors_total":len(state.get("site_errors",[]))
 }
 atomic(OUT/"coverage.json",report)
 findings=[]
 for v in scanned:
  for hit in v.get("hits",[]):
   findings.append({"owned_ancestry":"ROOT0","surface":"github","repo":v["repo"],**hit})
 for url,p in state["pages"].items():
  if p.get("themes") or p.get("exact_phrases"):findings.append(p)
 atomic(OUT/"matches.json",{"schema":"root0.convergence.matches/1","generated_utc":now,"matches":findings,"coverage_ref":"coverage.json",
 "warning":"Lexical co-occurrence only; do not infer copying, author identity or an external causal relationship."})
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
