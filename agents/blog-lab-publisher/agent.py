from __future__ import annotations
import argparse, hashlib, json, os, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import yaml
BASE = Path(__file__).resolve().parents[2]; HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from services.sources import collect
from services.ai_provider import generate, AIUnavailable
from services.validator import validate
from services.publisher import publish_to_app, slugify
from services.state import load_json, atomic_json
STATE=BASE/"data/agent-state.json"; PROCESSED=BASE/"data/processed-items.json"; STATUS=BASE/"public/data/agent-status.json"; APP=BASE/"src/App.jsx"
def now(): return datetime.now(ZoneInfo("Europe/Ljubljana"))
def enabled(cfg): return cfg.get("enabled", True) and os.getenv("AGENT_ENABLED", "true").lower()=="true"
def status(cfg,state,value,message="",output=None):
    atomic_json(str(STATUS), {"agent":cfg["agent_name"],"status":value,"enabled":enabled(cfg),"last_run":now().isoformat(timespec="seconds"),"last_success":state.get("last_success"),"last_output":output or state.get("last_output"),"next_run":None,"message":message,"posts_today":state.get("posts_today",0),"last_error":state.get("last_error")})
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dry-run",action="store_true"); ap.add_argument("--force",action="store_true"); args=ap.parse_args()
    cfg=yaml.safe_load((HERE/"config.yaml").read_text(encoding="utf-8")); state=load_json(str(STATE),{"consecutive_failures":0,"posts_today":0,"posts_date":None}); processed=load_json(str(PROCESSED),[])
    today=now().date().isoformat()
    if state.get("posts_date")!=today: state["posts_date"],state["posts_today"]=today,0
    if not enabled(cfg): status(cfg,state,"paused","Agent je izklopljen."); print("AGENT_DISABLED"); return 0
    if state["posts_today"]>=int(cfg.get("maximum_outputs_per_day",3)) and not args.force: status(cfg,state,"completed","Dosežena je dnevna omejitev objav."); print("DAILY_LIMIT"); return 0
    status(cfg,state,"collecting","Pridobivanje dovoljenih virov.")
    items=collect(cfg.get("input_sources",[]),int(cfg.get("max_source_items",20))); seen={x.get("hash") for x in processed}; fresh=[x for x in items if x.get("hash") not in seen]
    if not fresh: status(cfg,state,"completed","Ni novih primernih vsebin."); print("NO_NEW_CONTENT"); return 0
    system_prompt=(HERE/"prompts/system.md").read_text(encoding="utf-8"); task_prompt=(HERE/"prompts/task.md").read_text(encoding="utf-8"); status(cfg,state,"generating","Priprava članka.")
    try: article=generate(system_prompt,task_prompt,fresh[:8])
    except AIUnavailable as exc:
        state["last_error"]=str(exc); atomic_json(str(STATE),state); status(cfg,state,"needs_review",str(exc)); print(f"MOCK_OR_AI_UNAVAILABLE: {exc}"); return 0
    article["id"]=slugify(article.get("title",""))+"-"+hashlib.sha1(fresh[0]["url"].encode()).hexdigest()[:8]
    errors=validate(article,int(cfg["min_article_chars"]),int(cfg["max_article_chars"]),set(),{x.get("url") for x in processed if x.get("url")})
    if errors:
        diag=BASE/"logs"/f"failed-{now().strftime('%Y%m%d-%H%M%S')}.json"; diag.parent.mkdir(parents=True,exist_ok=True); diag.write_text(json.dumps({"errors":errors,"article":article},ensure_ascii=False,indent=2),encoding="utf-8")
        state["last_error"]=",".join(errors); state["consecutive_failures"]=state.get("consecutive_failures",0)+1; state["last_failure"]=now().isoformat(timespec="seconds"); atomic_json(str(STATE),state); status(cfg,state,"failed","QA ni uspel."); return 2
    publish_mode=os.getenv("PUBLISH_MODE","automatic").lower()
    if args.dry_run or publish_mode!="automatic":
        draft=BASE/"content/drafts"/f"{article['id']}.json"; draft.parent.mkdir(parents=True,exist_ok=True); draft.write_text(json.dumps(article,ensure_ascii=False,indent=2),encoding="utf-8"); status(cfg,state,"needs_review","Rezultat je shranjen kot osnutek.",str(draft)); print("DRY_RUN_OK"); return 0
    status(cfg,state,"publishing","Objavljanje preverjenega članka."); publish_to_app(str(APP),article,cfg["agent_name"])
    for item in fresh[:8]: processed.append({**item,"processed_at":now().isoformat(timespec="seconds"),"output_id":article["id"]})
    atomic_json(str(PROCESSED),processed[-500:]); state.update({"last_success":now().isoformat(timespec="seconds"),"last_output":article["id"],"last_error":None,"consecutive_failures":0,"posts_date":today,"posts_today":state.get("posts_today",0)+1,"agent_version":"1.0.0"}); atomic_json(str(STATE),state); status(cfg,state,"completed","Članek je pripravljen in čaka na commit.",article["id"]); print(f"PUBLISHED:{article['id']}"); return 0
if __name__=="__main__": raise SystemExit(main())
