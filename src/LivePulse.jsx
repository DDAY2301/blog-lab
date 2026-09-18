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

export default function LivePulse() {
  const [feed, setFeed] = useState({ items: [], status: "loading", updatedAt: "" });

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const base = import.meta.env.BASE_URL || "/";
        const response = await fetch(`${base}live-feed.json?t=${Date.now()}`, { cache: "no-store" });
        if (!response.ok) throw new Error("feed unavailable");
        const data = await response.json();
        if (active) setFeed(data);
      } catch {
        if (active) setFeed((current) => ({ ...current, status: "unavailable" }));
      }
    };
    load();
    const timer = setInterval(load, 60_000);
    return () => { active = false; clearInterval(timer); };
  }, []);

  const items = useMemo(() => Array.isArray(feed.items) ? feed.items.slice(0, 8) : [], [feed.items]);

  return (
    <aside className="live-pulse" aria-label="Tekoče aktualne novice">
      <div className="live-pulse-head">
        <div>
          <span className="live-dot" />
          <strong>TEKOČE</strong>
        </div>
        <span>30 min</span>
      </div>
      <p className="live-pulse-intro">Kratek pregled aktualnih naslovov, osvežen avtomatsko.</p>
      <div className="live-pulse-list">
        {items.length ? items.map((item, index) => (
          <a href={item.url} target="_blank" rel="noopener noreferrer" className="live-pulse-item" key={`${item.url}-${index}`}>
            <div className="live-pulse-meta">
              <span>{item.source || "Vir"}</span>
              <span>{relativeTime(item.publishedAt)}</span>
            </div>
            <h3>{item.title}</h3>
          </a>
        )) : (
          <div className="live-pulse-empty">Trenutno ni svežih mini objav.</div>
        )}
      </div>
      <div className="live-pulse-foot">
        {feed.updatedAt ? <>Osveženo {relativeTime(feed.updatedAt)}</> : "Samodejno osveževanje"}
        {feed.status === "stale" && <span> · zadnji znani podatki</span>}
      </div>
    </aside>
  );
}
