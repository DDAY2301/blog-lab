import React, { useEffect, useMemo, useState } from "react";

const ARTICLE_MODULES = import.meta.glob("./articles/published/*.json", { eager: true, import: "default" });
const PUBLISHED_ARTICLES = Object.values(ARTICLE_MODULES)
  .filter((item) => item && item.status === "published" && item.title && item.id)
  .sort((a, b) => new Date(b.updatedAt || b.createdAt || 0) - new Date(a.updatedAt || a.createdAt || 0));

const ART = {
  hero: "/art/painted/hero.jpg",
  culture: "/art/painted/dediscina.jpg",
  fun: "/art/painted/gourmet.jpg",
  sport: "/art/painted/kolesarstvo.jpg",
  weekend: "/art/painted/sezonsko.jpg",
  trails: "/art/painted/gore-traili.jpg",
  guide: "/art/painted/vodniki.jpg"
};
const CATEGORIES = ["Vse", "Kultura", "Zabava", "Šport"];
const DAY_NAMES = ["Pon", "Tor", "Sre", "Čet", "Pet", "Sob", "Ned"];

function toDateKey(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat("en-GB", {
      timeZone: "Europe/Ljubljana", year: "numeric", month: "2-digit", day: "2-digit"
    }).formatToParts(date).filter((p) => p.type !== "literal").map((p) => [p.type, p.value])
  );
  return parts.year + "-" + parts.month + "-" + parts.day;
}
function shiftKey(key, days) {
  const date = new Date(key + "T12:00:00Z");
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}
function mondayFirstDay(key) {
  const weekday = new Date(key + "T12:00:00Z").getUTCDay();
  return (weekday + 6) % 7;
}
function formatKey(key, options = { day: "numeric", month: "long" }) {
  return new Intl.DateTimeFormat("sl-SI", { timeZone: "UTC", ...options })
    .format(new Date(key + "T12:00:00Z"));
}
function eventCategory(item) {
  const value = [item.type, item.title].filter(Boolean).join(" ").toLowerCase();
  if (/sport|koles|tekmov|tek|maraton|nogomet|košark|hokej|trail|pohod|basket|football|run\b|race/.test(value)) return "Šport";
  if (/zabav|koncert|concert|music|glasb|festival|club|klub|nočn|gourmet|hrana|kulinar|food|comedy|stand.up|party|kino|film/.test(value)) return "Zabava";
  return "Kultura";
}
function articleCategory(article) {
  const value = [article.category, article.title].join(" ").toLowerCase();
  if (/koles|gore|trail|planin|pohod|sport|tekmov/.test(value)) return "Šport";
  if (/gourmet|kulinar|sezons|hrana|turiz|zabav/.test(value)) return "Zabava";
  return "Kultura";
}
function paintingFor(category) {
  if (category === "Šport") return ART.sport;
  if (category === "Zabava") return ART.fun;
  return ART.culture;
}
function eventOnDate(item, key) {
  if (!item.startAt || !key) return false;
  const start = toDateKey(item.startAt);
  const end = item.endAt ? toDateKey(item.endAt) : start;
  return start <= key && (end || start) >= key;
}
function eventOrderFor(key) {
  return (a, b) => {
    const startsTodayA = toDateKey(a.startAt) === key ? 0 : 1;
    const startsTodayB = toDateKey(b.startAt) === key ? 0 : 1;
    if (startsTodayA !== startsTodayB) return startsTodayA - startsTodayB;
    return new Date(a.startAt || 0) - new Date(b.startAt || 0);
  };
}
function eventTime(item, key) {
  if (toDateKey(item.startAt) !== key) return "Večdnevni dogodek";
  return new Intl.DateTimeFormat("sl-SI", { timeZone: "Europe/Ljubljana", hour: "2-digit", minute: "2-digit" }).format(new Date(item.startAt));
}
function validEvent(item) {
  return item && item.title && typeof item.startAt === "string" &&
    typeof item.url === "string" && /^https:\/\//.test(item.url) && item.status === "confirmed";
}

function MagazineHeader({ onCategory, openSearch, searchOpen, query, setQuery }) {
  return (
    <header className="site-header labab-header">
      <div className="labab-nav-inner">
        <a href="/" className="brand labab-brand" aria-label="BlogLab – začetna stran">Blog Lab<span className="labab-dot">.</span></a>
        <nav aria-label="Glavne rubrike">
          <button type="button" onClick={() => onCategory("Kultura")}>Kultura</button>
          <button type="button" onClick={() => onCategory("Zabava")}>Zabava</button>
          <button type="button" onClick={() => onCategory("Šport")}>Šport</button>
          <a href="#weekend">Weekend</a>
          <a href="/?view=archive">Blog / Novice</a>
        </nav>
        <button className="labab-search-toggle" type="button" onClick={openSearch} aria-label={searchOpen ? "Zapri iskanje" : "Odpri iskanje"} aria-expanded={searchOpen}>⌕</button>
      </div>
      {searchOpen && <div className="labab-search-panel"><label htmlFor="labab-search">Poišči dogodek ali članek</label><input id="labab-search" type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Naslov, kraj, rubrika ..." autoFocus /></div>}
    </header>
  );
}

function EventCard({ item, dateKey, index }) {
  const category = eventCategory(item);
  return (
    <a className="labab-event-card" href={item.ticketUrl && /^https:\/\//.test(item.ticketUrl) ? item.ticketUrl : item.url} target="_blank" rel="noopener noreferrer" aria-label={item.title + " – preveri pri organizatorju"}>
      <span className="labab-event-paint" style={{ backgroundImage: "url(" + paintingFor(category) + ")" }} aria-hidden="true" />
      <span className="labab-paint-caption">Oljna ilustracija</span>
      <span className="labab-event-no">0{index + 1} / {category}</span>
      <strong>{item.title}</strong>
      <span className="labab-event-meta">{eventTime(item, dateKey)} · {item.place || item.source || "Slovenija"}</span>
      <span className="labab-event-visit">Podrobnosti ↗</span>
    </a>
  );
}

function EventCalendar({ events, dateKey, setDateKey, category, setCategory, query }) {
  const [offset, setOffset] = useState(0);
  const month = useMemo(() => {
    const date = new Date(dateKey + "T12:00:00Z");
    return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + offset, 1, 12));
  }, [dateKey, offset]);
  const monthKey = month.toISOString().slice(0, 10);
  const days = new Date(Date.UTC(month.getUTCFullYear(), month.getUTCMonth() + 1, 0, 12)).getUTCDate();
  const before = mondayFirstDay(monthKey);
  const squares = Array.from({ length: Math.ceil((before + days) / 7) * 7 }, (_, i) => {
    const day = i - before + 1;
    return day >= 1 && day <= days ? monthKey.slice(0, 8) + String(day).padStart(2, "0") : "";
  });
  const matches = events
    .filter((event) => eventOnDate(event, dateKey))
    .filter((event) => category === "Vse" || eventCategory(event) === category)
    .filter((event) => !query || [event.title, event.type, event.place].join(" ").toLowerCase().includes(query.toLowerCase()))
    .sort(eventOrderFor(dateKey)).slice(0, 5);

  function moveMonth(direction) {
    const next = new Date(Date.UTC(month.getUTCFullYear(), month.getUTCMonth() + direction, 1, 12));
    setDateKey(next.toISOString().slice(0, 10));
    setOffset(0);
  }

  return (
    <section className="labab-calendar-panel" aria-labelledby="labab-calendar-heading" id="calendar">
      <div className="labab-subhead"><div><span className="labab-kicker">VSE NA ENEM MESTU</span><h2 id="labab-calendar-heading">Koledar dogodkov</h2></div><span className="labab-handnote">izberi svoj dan ↘</span></div>
      <div className="labab-calendar-sheet">
        <div className="labab-month">
          <button type="button" onClick={() => moveMonth(-1)} aria-label="Prejšnji mesec">‹</button>
          <strong>{formatKey(monthKey, { month: "long", year: "numeric" })}</strong>
          <button type="button" onClick={() => moveMonth(1)} aria-label="Naslednji mesec">›</button>
        </div>
        <div className="labab-weekdays">{DAY_NAMES.map((d) => <span key={d}>{d}</span>)}</div>
        <div className="labab-calendar-grid">{squares.map((date, i) => {
          const total = date ? events.filter((event) => eventOnDate(event, date)).length : 0;
          return date ? (
            <button key={date} className={date === dateKey ? "selected" : ""} type="button" onClick={() => { setDateKey(date); setOffset(0); }} aria-label={formatKey(date, { day: "numeric", month: "long", year: "numeric" }) + ", " + total + " dogodkov"} aria-pressed={date === dateKey}>
              <span>{Number(date.slice(-2))}</span>{total > 0 && <i aria-hidden="true" />}
            </button>
          ) : <span key={"blank-" + i} className="labab-calendar-empty" />;
        })}</div>
        <div className="labab-filters" aria-label="Filtri dogodkov">{CATEGORIES.map((label) => <button key={label} type="button" className={category === label ? "active" : ""} aria-pressed={category === label} onClick={() => setCategory(label)}>{label}</button>)}</div>
        <div className="labab-selected-day"><strong>{formatKey(dateKey, { weekday: "long", day: "numeric", month: "long" })}</strong><span>{matches.length ? "Izbrani dogodki" : "Za ta izbor ni potrjenih dogodkov"}</span></div>
        <div className="labab-day-list">{matches.map((item) => <a href={item.url} key={item.id || item.url} target="_blank" rel="noopener noreferrer"><span className="labab-day-time">{eventTime(item, dateKey)}</span><span className="labab-day-name">{item.title}<small>{item.place || item.source}</small></span><span aria-hidden="true">↗</span></a>)}</div>
      </div>
    </section>
  );
}

function EditorialFeature({ group, article, onRead, image }) {
  return (
    <article className="labab-feature">
      <div className="labab-feature-art" style={{ backgroundImage: "url(" + image + ")" }} role="img" aria-label={"Oljna ilustracija: " + group} />
      <div className="labab-feature-copy"><span className="labab-kicker">{group} / IZBOR UREDNIŠTVA</span><h3>{article ? article.title : "Nove zgodbe v pripravi"}</h3><p>{article ? article.excerpt : "Spremljaj rubriko – nove zgodbe bodo objavljene tukaj."}</p>{article && <button type="button" onClick={() => onRead(article)}>Preberi zgodbo ↗</button>}</div>
    </article>
  );
}

function ArticleSheet({ article, onClose }) {
  useEffect(() => {
    if (!article) return;
    const handleEscape = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [article, onClose]);
  if (!article) return null;
  const content = String(article.content || article.excerpt || "").split(/\n\n+/).slice(0, 40);
  return <div className="labab-dialog-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
    <section className="labab-article-dialog" role="dialog" aria-modal="true" aria-labelledby="labab-article-title">
      <button type="button" className="labab-dialog-close" onClick={onClose} aria-label="Zapri članek">×</button>
      <span className="labab-kicker">{article.category || "BlogLab"} · {formatKey(toDateKey(article.updatedAt || article.createdAt || new Date()))}</span>
      <h2 id="labab-article-title">{article.title}</h2>
      {content.map((text, i) => <p key={i}>{text.replace(/^#+\s*/gm, "").replace(/\*\*/g, "")}</p>)}
      {!!article.sources?.length && <div className="labab-article-sources"><strong>Viri</strong>{article.sources.filter((s) => /^https:\/\//.test(s.url || "")).map((source, i) => <a key={i} href={source.url} target="_blank" rel="noopener noreferrer">{source.label || "Vir"} ↗</a>)}</div>}
    </section>
  </div>;
}

export default function BlogLabHome() {
  const today = useMemo(() => toDateKey(new Date()), []);
  const [events, setEvents] = useState([]);
  const [feedStatus, setFeedStatus] = useState("loading");
  const [selectedDay, setSelectedDay] = useState(today);
  const [category, setCategory] = useState("Vse");
  const [searchOpen, setSearchOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedArticle, setSelectedArticle] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await fetch("/events-feed.json", { cache: "no-store", signal: controller.signal });
        if (!response.ok) throw new Error("Feed unavailable");
        const data = await response.json();
        setEvents(Array.isArray(data.items) ? data.items.filter(validEvent) : []);
        setFeedStatus("ready");
      } catch (error) {
        if (error.name !== "AbortError") setFeedStatus("error");
      }
    }
    load();
    return () => controller.abort();
  }, []);

  const upcoming = useMemo(() => events.filter((event) => toDateKey(event.endAt || event.startAt) >= today).sort(eventOrderFor(today)), [events, today]);
  const todayEvents = useMemo(() => upcoming.filter((item) => eventOnDate(item, today)).sort(eventOrderFor(today)), [upcoming, today]);
  const chosenEvents = (todayEvents.length ? todayEvents : upcoming)
    .filter((event) => !query || [event.title, event.type, event.place].join(" ").toLowerCase().includes(query.toLowerCase()))
    .slice(0, 7);

  const featured = useMemo(() => ({
    "Kultura": PUBLISHED_ARTICLES.find((item) => articleCategory(item) === "Kultura"),
    "Zabava": PUBLISHED_ARTICLES.find((item) => articleCategory(item) === "Zabava"),
    "Šport": PUBLISHED_ARTICLES.find((item) => articleCategory(item) === "Šport")
  }), []);
  const news = PUBLISHED_ARTICLES.filter((item) => !query || [item.title, item.category].join(" ").toLowerCase().includes(query.toLowerCase())).slice(0, 4);
  const friday = shiftKey(today, (5 - new Date(today + "T12:00:00Z").getUTCDay() + 7) % 7);
  const weekend = ["Petek", "Sobota", "Nedelja"].map((day, i) => {
    const key = shiftKey(friday, i);
    return { day, key, events: upcoming.filter((event) => eventOnDate(event, key)).sort(eventOrderFor(key)).slice(0, 2) };
  });

  const openCategory = (next) => {
    setCategory(next);
    document.getElementById("calendar")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <main className="tourism-site bloglab-redesign">
      <MagazineHeader onCategory={openCategory} openSearch={() => setSearchOpen((value) => !value)} searchOpen={searchOpen} query={query} setQuery={setQuery} />
      <section className="hero paint-hero labab-hero">
        <div className="labab-hero-content">
          <span className="labab-hero-folio">BLOG LAB / KULTURA / ZABAVA / ŠPORT / WEEKEND</span>
          <span className="eyebrow"><span /> NOVA DIGITALNA NASLOVNICA</span>
          <h1>Ujemi danes. <em>Doživi več.</em></h1>
          <p>Dogodki, zgodbe in ideje za prosti čas. Vse pomembno na enem mestu – od kulture in zabave do športa in vikend načrtov.</p>
          <a href="#today" className="primary">Razišči današnje dogodke ↗</a>
        </div>
        <span className="labab-hero-side">Izbrano s pogledom uredništva</span>
      </section>

      <div className="home-content container paint-story-paper labab-home">
        <section id="today" className="labab-today">
          <div className="labab-heading"><div><span className="labab-kicker">DNEVNI PREGLED / LJUBLJANA IN SLOVENIJA</span><h2>{todayEvents.length ? "Danes se dogaja." : "V prihodnjih dneh."}</h2><p>{formatKey(today, { weekday: "long", day: "numeric", month: "long", year: "numeric" })} · preveri podrobnosti pri organizatorju</p></div><a href="#calendar">Vsi dogodki ↗</a></div>
          {chosenEvents.length ? <div className="labab-events-strip" aria-label="Izbor sedmih dogodkov">{chosenEvents.map((item, i) => <EventCard key={item.id || item.url + i} item={item} index={i} dateKey={eventOnDate(item, today) ? today : toDateKey(item.startAt)} />)}</div> : <p className="labab-no-results">{feedStatus === "loading" ? "Preverjam koledar dogodkov ..." : feedStatus === "error" ? "Koledar trenutno ni dosegljiv. Poskusi ponovno pozneje." : "Za ta izbor ni potrjenih dogodkov."}</p>}
        </section>

        <div className="labab-two-columns">
          <EventCalendar events={upcoming} dateKey={selectedDay} setDateKey={setSelectedDay} category={category} setCategory={setCategory} query={query} />
          <section className="labab-editorial" id="stories" aria-labelledby="labab-editorial-title">
            <div className="labab-subhead"><div><span className="labab-kicker">ZGODBE, KI OSTAJAJO</span><h2 id="labab-editorial-title">V ospredju</h2></div><span className="labab-handnote">uredniški izbor ↘</span></div>
            <div className="labab-feature-grid">
              <EditorialFeature group="Kultura" article={featured.Kultura} onRead={setSelectedArticle} image={ART.culture} />
              <EditorialFeature group="Zabava" article={featured.Zabava} onRead={setSelectedArticle} image={ART.fun} />
              <EditorialFeature group="Šport" article={featured.Šport} onRead={setSelectedArticle} image={ART.sport} />
            </div>
          </section>
        </div>

        <section id="weekend" className="labab-weekend" aria-labelledby="labab-weekend-title">
          <div className="labab-heading"><div><span className="labab-kicker">PETEK / SOBOTA / NEDELJA</span><h2 id="labab-weekend-title">Weekend.</h2><p>Kam za konec tedna? Trije dnevi, veliko možnosti.</p></div><a href="#calendar">Celoten koledar ↗</a></div>
          <div className="labab-weekend-grid">{weekend.map(({ day, key, events: items }, i) => (
            <article key={day} className="labab-weekend-card">
              <div className="labab-weekend-paint" style={{ backgroundImage: "url(" + [ART.weekend, ART.guide, ART.trails][i] + ")" }} role="img" aria-label="Oljna ilustracija" />
              <div className="labab-weekend-copy"><span className="labab-kicker">{formatKey(key, { day: "numeric", month: "long" })}</span><h3>{day}</h3>
                {items.length ? items.map((item) => <a key={item.id || item.url} href={item.url} target="_blank" rel="noopener noreferrer">{item.title}<small>{eventTime(item, key)} · {item.place || item.source}</small></a>) : <p>Za ta dan trenutno ni potrjenega dogodka.</p>}
              </div>
            </article>
          ))}</div>
        </section>

        <section id="blog" className="labab-news" aria-labelledby="labab-news-title">
          <div className="labab-heading"><div><span className="labab-kicker">BLOG LAB / ZADNJE OBJAVE</span><h2 id="labab-news-title">Blog in novice.</h2><p>Najnovejše zgodbe, razmisleki in aktualnosti.</p></div><a href="/?view=archive">Celoten arhiv ↗</a></div>
          <div className="labab-news-grid">{news.map((item, i) => (
            <button type="button" className="labab-news-card" key={item.id} onClick={() => setSelectedArticle(item)}>
              <span className="labab-news-image" style={{ backgroundImage: "url(" + [ART.culture, ART.fun, ART.sport, ART.guide][i] + ")" }} />
              <span className="labab-news-category">{item.category || "BlogLab"}</span>
              <strong>{item.title}</strong>
              <span className="labab-news-date">{formatKey(toDateKey(item.updatedAt || item.createdAt || new Date()))} · Preberi ↗</span>
            </button>
          ))}</div>
          {!news.length && <p className="labab-no-results">Za ta iskalni niz ni objavljenih člankov.</p>}
        </section>
      </div>

      <footer className="labab-footer"><div className="container"><strong>Blog Lab.</strong><span>Slovenija skozi dogodke, kulturo, zabavo in šport.</span><a href="/?view=archive">Prejšnja različica / Arhiv ↗</a></div></footer>
      <ArticleSheet article={selectedArticle} onClose={() => setSelectedArticle(null)} />
    </main>
  );
}
