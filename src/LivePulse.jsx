import { useEffect, useMemo, useState } from "react";

function relativeTime(value) {
  if (!value) return "";
  const ms = Date.now() - new Date(value).getTime();
  if (!Number.isFinite(ms)) return "";
  const minutes = Math.max(0, Math.round(ms / 60000));
  if (minutes < 1) return "zdaj";
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} h`;
  return new Intl.DateTimeFormat("sl-SI", { day: "numeric", month: "short" }).format(new Date(value));
}
function eventDay(value) {
  const date = new Date(value);
  if (!value || !Number.isFinite(date.getTime())) return "";
  return new Intl.DateTimeFormat("sl-SI", { weekday: "short", day: "numeric", month: "short" }).format(date);
}
function eventTime(value) {
  if (!value || !String(value).includes("T")) return "";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "";
  return new Intl.DateTimeFormat("sl-SI", { hour: "2-digit", minute: "2-digit" }).format(date);
}
export default function LivePulse() {
  const [feed, setFeed] = useState({ items: [], status: "loading", updatedAt: "" });
  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const base = import.meta.env.BASE_URL || "/";
        const response = await fetch(`${base}events-feed.json?t=${Date.now()}`, { cache: "no-store" });
        if (!response.ok) throw new Error("events feed unavailable");
        const data = await response.json();
        if (active) setFeed(data);
      } catch {
        if (active) setFeed((current) => ({ ...current, status: "unavailable" }));
      }
    };
    load();
    const timer = setInterval(load, 5 * 60_000);
    return () => { active = false; clearInterval(timer); };
  }, []);
  const items = useMemo(() => (Array.isArray(feed.items) ? [...feed.items] : [])
    .filter((item) => item?.title && item?.url)
    .sort((a,b) => new Date(a.startAt || 0) - new Date(b.startAt || 0))
    .slice(0,12), [feed.items]);
  return (
    <aside id="events-today" className="live-pulse events-pulse" aria-label="Aktualni dogodki v Ljubljani in Sloveniji">
      <div className="live-pulse-head"><div><span className="live-dot" /><strong>DOGODKI</strong></div><span>{items.length ? `${items.length} izbranih` : "dnevno"}</span></div>
      <p className="live-pulse-intro">Kultura, šport, koncerti, festivali in nočno življenje — preverjeno pri organizatorjih in uradnih koledarjih.</p>
      <div className="live-pulse-list">
        {items.length ? items.map((item,index) => (
          <a href={item.url} target="_blank" rel="noopener noreferrer" className="live-pulse-item event-pulse-item" key={item.id || `${item.url}-${index}`}>
            <div className="event-pulse-top"><span className="event-type">{item.type || "Dogodek"}</span><span>{eventDay(item.startAt)}{eventTime(item.startAt) ? ` · ${eventTime(item.startAt)}` : ""}</span></div>
            <h3>{item.title}</h3>
            <div className="event-place">{item.place || item.source || "Slovenija"}</div>
            <div className="live-pulse-meta"><span>{item.source || "Uradni vir"}</span><span>↗</span></div>
          </a>
        )) : <div className="live-pulse-empty">Koledar se trenutno osvežuje. Dogodki se ob naslednji sinhronizaciji znova preverijo pri uradnih virih.</div>}
      </div>
      <div className="live-pulse-ad" data-ad-slot="events-rail" aria-label="Oglasni prostor"><span>OGLAS</span><small>300 × 250 / native</small></div>
      <div className="live-pulse-foot">{feed.updatedAt ? <>Preverjeno {relativeTime(feed.updatedAt)}</> : "Dnevno preverjanje"}{feed.status === "stale" && <span> · zadnji znani podatki</span>}{feed.status === "partial" && <span> · delna osvežitev</span>}</div>
    </aside>
  );
}
