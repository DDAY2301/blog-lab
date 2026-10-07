from __future__ import annotations
import json, re, urllib.request
from datetime import datetime, timedelta
from html import unescape
from pathlib import Path
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"public"/"events-feed.json"
TZ=ZoneInfo("Europe/Ljubljana")
SOURCES=[
 {"name":"Visit Ljubljana","url":"https://www.visitljubljana.com/sl/obiskovalci/prireditve","type":"Dogodek","place":"Ljubljana"},
 {"name":"Kino Šiška","url":"https://www.kinosiska.si/?post_type=events","type":"Kultura","place":"Kino Šiška · Ljubljana"},
 {"name":"Gala Hala","url":"https://www.galahala.com/","type":"Koncert · Metelkova","place":"Gala Hala · AKC Metelkova"},
 {"name":"Klub K4","url":"https://www.klub-k4.si/","type":"Club","place":"Klub K4 · Ljubljana"},
 {"name":"Cirkus Klub","url":"https://cirkusklub.si/dogodki/","type":"Club","place":"Cirkus Klub · Ljubljana"},
]
MONTHS_SL={"januarja":1,"februarja":2,"marca":3,"aprila":4,"maja":5,"junija":6,"julija":7,"avgusta":8,"septembra":9,"oktobra":10,"novembra":11,"decembra":12}
MONTHS_EN={"JAN":1,"FEB":2,"MAR":3,"APR":4,"MAY":5,"JUN":6,"JUL":7,"AUG":8,"SEP":9,"OCT":10,"NOV":11,"DEC":12}

def clean(v):
    return " ".join(re.sub(r"<[^>]+>"," ",unescape(str(v or ""))).split()).strip()

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"BlogLabEvents/2.0 (+https://bloglab.eu/)","Accept":"text/html,application/xhtml+xml;q=0.9,*/*;q=0.5","Accept-Language":"sl,en;q=0.8"})
    with urllib.request.urlopen(req,timeout=22) as response:
        return response.read(2_500_000).decode("utf-8",errors="replace")

def local_iso(raw):
    raw=clean(raw)
    if not raw:return ""
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}",raw):
            return datetime.fromisoformat(raw+"T09:00:00").replace(tzinfo=TZ).isoformat()
        dt=datetime.fromisoformat(raw.replace("Z","+00:00"))
        if dt.tzinfo is None:dt=dt.replace(tzinfo=TZ)
        return dt.astimezone(TZ).isoformat()
    except Exception:return ""

def location_text(loc):
    if isinstance(loc,str):return clean(loc)
    if not isinstance(loc,dict):return ""
    name=clean(loc.get("name","")); addr=loc.get("address")
    if isinstance(addr,str):address=clean(addr)
    elif isinstance(addr,dict):address=clean(", ".join(str(addr.get(k,"") or "") for k in ("streetAddress","addressLocality") if addr.get(k)))
    else:address=""
    return " · ".join(x for x in (name,address) if x)

def iter_jsonld(v):
    if isinstance(v,list):
        for x in v:yield from iter_jsonld(x)
        return
    if not isinstance(v,dict):return
    if v.get("@graph"):yield from iter_jsonld(v["@graph"])
    typ=v.get("@type"); types=typ if isinstance(typ,list) else [typ]
    if any(str(t).lower()=="event" for t in types if t):yield v
    for k,x in v.items():
        if k!="@graph" and isinstance(x,(dict,list)):yield from iter_jsonld(x)

def jsonld_events(html,source):
    out=[]
    for block in re.findall(r'(?is)<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',html):
        try:payload=json.loads(unescape(block).strip())
        except Exception:continue
        for obj in iter_jsonld(payload):
            title=clean(obj.get("name","")); start=local_iso(obj.get("startDate",""))
            if not title or not start:continue
            url=clean(obj.get("url","")) or source["url"]
            if url.startswith("/"):url=urljoin(source["url"],url)
            out.append({"title":title[:220],"url":url,"source":source["name"],"type":source["type"],"place":location_text(obj.get("location")) or source["place"],"startAt":start,"endAt":local_iso(obj.get("endDate",""))})
    return out

def plain_text(html):
    return clean(re.sub(r"(?is)<(?:script|style|svg|noscript)[^>]*>.*?</(?:script|style|svg|noscript)>"," ",html))

def parse_k4(text,source):
    out=[]; now=datetime.now(TZ)
    pat=re.compile(r"(?i)(\d{1,2})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(.{3,150}?)\s+(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?\s*(?:•\s*)?(?:Vinyl Only Night\s*•\s*)?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?\s*•\s*Klub K4\s*•\s*(\d{1,2}:\d{2})")
    for day,mon,title,hm in pat.findall(text):
        month=MONTHS_EN.get(mon.upper()); year=now.year+(1 if month and month<now.month-6 else 0)
        if not month:continue
        h,m=map(int,hm.split(":")); dt=datetime(year,month,int(day),h,m,tzinfo=TZ)
        out.append({"title":clean(title),"url":source["url"],"source":source["name"],"type":"Club · elektronika","place":source["place"],"startAt":dt.isoformat(),"endAt":""})
    return out

def parse_gala(text,source):
    out=[]; pat=re.compile(r"(?i)(?:ponedeljek|torek|sreda|četrtek|petek|sobota|nedelja),\s*(\d{1,2})\.\s*(januarja|februarja|marca|aprila|maja|junija|julija|avgusta|septembra|oktobra|novembra|decembra)\s*(\d{4})\s*:\s*(.{3,180}?)\s*\((\d{1,2}:\d{2})\)")
    for day,mon,year,title,hm in pat.findall(text):
        month=MONTHS_SL.get(mon.lower())
        if not month:continue
        h,m=map(int,hm.split(":")); dt=datetime(int(year),month,int(day),h,m,tzinfo=TZ)
        out.append({"title":clean(title),"url":source["url"],"source":source["name"],"type":source["type"],"place":source["place"],"startAt":dt.isoformat(),"endAt":""})
    return out

def event_key(item):
    title=re.sub(r"\W+","",clean(item.get("title","")).lower())
    try:day=datetime.fromisoformat(item.get("startAt","")).astimezone(TZ).date().isoformat()
    except Exception:day=item.get("startAt","")[:10]
    return f"{title[:90]}|{day}"

def valid_future(item):
    try:
        start=datetime.fromisoformat(item.get("startAt","")); end=datetime.fromisoformat(item.get("endAt","") or item.get("startAt",""))
        if start.tzinfo is None:start=start.replace(tzinfo=TZ)
        if end.tzinfo is None:end=end.replace(tzinfo=TZ)
        now=datetime.now(TZ)
        return end.astimezone(TZ)>=now-timedelta(hours=12) and start.astimezone(TZ)<=now+timedelta(days=45)
    except Exception:return False

def main():
    existing=[]
    try:existing=json.loads(OUT.read_text(encoding="utf-8")).get("items",[])
    except Exception:pass
    discovered=[]; checked=[]; failed=[]
    for source in SOURCES:
        try:
            html=fetch(source["url"]); text=plain_text(html); found=jsonld_events(html,source)
            if source["name"]=="Klub K4":found+=parse_k4(text,source)
            if source["name"]=="Gala Hala":found+=parse_gala(text,source)
            discovered+=found; checked.append(source["name"])
        except Exception as exc:failed.append(f"{source['name']}: {type(exc).__name__}")
    merged={}
    for item in existing:
        if isinstance(item,dict) and valid_future(item):merged[event_key(item)]=item
    for item in discovered:
        if valid_future(item):merged[event_key(item)]=item
    items=sorted(merged.values(),key=lambda x:x.get("startAt",""))[:30]
    for i,item in enumerate(items):
        if not item.get("id"):item["id"]=f"event-{i+1:02d}-"+re.sub(r"[^a-z0-9]+","-",item.get("title","").lower()).strip("-")[:60]
    status="fresh" if checked and not failed else ("partial" if checked else "stale")
    payload={"updatedAt":datetime.now(TZ).isoformat(timespec="seconds"),"status":status,"sourcesChecked":checked,"sourcesFailed":failed,"items":items}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"EVENTS_FEED_UPDATED items={len(items)} checked={len(checked)} failed={len(failed)}")
    return 0
if __name__=="__main__":raise SystemExit(main())
