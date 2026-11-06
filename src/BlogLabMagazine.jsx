import React, { useEffect, useMemo, useState } from "react";
import {
  RUBRICS, rubricInfo, rubricForArticle, rubricForEvent, rubricHref, articleHref, eventHref,
  dateHref, keyForLjubljana, niceDate, addDays, weekendDates, eventActiveOn,
  eventIsFuture, eventHour, trustedEvent
} from "./bloglab-taxonomy.js";

const MODULES = import.meta.glob("./articles/published/*.json", { eager: true, import: "default" });
const ARTICLES = Object.values(MODULES)
  .filter((a) => a?.status === "published" && a?.id && a?.title)
  .sort((a, b) => new Date(b.updatedAt || b.createdAt || 0) - new Date(a.updatedAt || a.createdAt || 0));
const IMAGES = {
  hero: "/art/painted/hero.jpg",
  kultura: "/art/painted/dediscina.jpg",
  zabava: "/art/painted/gourmet.jpg",
  sport: "/art/painted/kolesarstvo.jpg",
  weekend: "/art/painted/sezonsko.jpg",
  novice: "/art/painted/vodniki.jpg",
  trails: "/art/painted/gore-traili.jpg"
};
const DAYS = ["Pon", "Tor", "Sre", "Čet", "Pet", "Sob", "Ned"];
const DAYS_LONG = ["Petek", "Sobota", "Nedelja"];
const todayKey = () => keyForLjubljana(new Date());

function useEventsFeed() {
  const [feed, setFeed] = useState({ status: "loading", items: [], updatedAt: "" });
  useEffect(() => {
    const controller = new AbortController();
    const load = async () => {
      try {
        const response = await fetch("/events-feed.json", { cache: "no-store", signal: controller.signal });
        if (!response.ok) throw new Error("No event feed");
        const json = await response.json();
        if (!controller.signal.aborted) setFeed({
          status: "ready", items: (Array.isArray(json.items) ? json.items : []).filter(trustedEvent),
          updatedAt: json.updatedAt || ""
        });
      } catch (error) {
        if (!controller.signal.aborted) setFeed((old) => ({ ...old, status: "error" }));
      }
    };
    load();
    return () => controller.abort();
  }, []);
  return feed;
}
function periodFor(item, today) { return eventIsFuture(item, today) ? "aktualno" : "arhiv"; }
function pickEventsForDate(items, key, rubric = null) {
  return items.filter((item) => eventActiveOn(item, key))
    .filter((item) => !rubric || rubricForEvent(item) === rubric)
    .sort((a, b) => Number(keyForLjubljana(a.startAt) !== key) - Number(keyForLjubljana(b.startAt) !== key) || new Date(a.startAt) - new Date(b.startAt));
}
function dateForArticle(item) {
  return keyForLjubljana(item.updatedAt || item.createdAt) || todayKey();
}
function articleImage(item) { return IMAGES[rubricForArticle(item)] || IMAGES.kultura; }
function eventImage(item) { return IMAGES[rubricForEvent(item)] || IMAGES.kultura; }

function PageHeader({ active = "", q = "" }) {
  const [searchOpen, setSearchOpen] = useState(Boolean(q));
  return (
    <header className="mag-header">
      <div className="mag-header-inner">
        <a className="mag-brand" href="/" aria-label="BlogLab – naslovnica">Blog Lab<span>.</span></a>
        <nav aria-label="Glavna navigacija" className="mag-nav">
          {RUBRICS.map((rubric) => <a key={rubric.slug} className={active === rubric.slug ? "active" : ""} aria-current={active === rubric.slug ? "page" : undefined} href={rubricHref(rubric.slug)}>{rubric.name}</a>)}
        </nav>
        <button className="mag-search-trigger" type="button" aria-expanded={searchOpen} aria-controls="mag-search" onClick={() => setSearchOpen((v) => !v)} aria-label={searchOpen ? "Zapri iskanje" : "Odpri iskanje"}>⌕</button>
      </div>
      {searchOpen && <form id="mag-search" className="mag-search-form" action="/" method="get" role="search">
        <label htmlFor="mag-query">Išči po objavah in dogodkih</label>
        <input id="mag-query" name="iskanje" type="search" defaultValue={q} placeholder="Vnesi naslov, kraj ali temo..." required minLength="2" />
        <button type="submit">Poišči ↗</button>
      </form>}
    </header>
  );
}
function PageFooter() {
  return <footer className="mag-footer"><div className="mag-wide">
    <a className="mag-footer-logo" href="/">Blog Lab.</a><p>Dogodki, kultura, zabava, šport in zgodbe za vsak dan.</p>
    <a href={rubricHref("novice")}>Vse objave ↗</a><a href="/?view=archive">Klasični portal ↗</a>
  </div></footer>;
}
function PaintedBanner({ eyebrow, title, desc, image, compact = false, children }) {
  return <section className={"mag-painted-banner" + (compact ? " compact" : "")} style={{ backgroundImage: "linear-gradient(90deg,rgba(19,38,30,.90),rgba(21,40,31,.70) 46%,rgba(21,40,31,.13)),url(" + image + ")" }}>
    <div className="mag-wide"><span className="mag-overline">{eyebrow}</span><h1>{title}</h1><p>{desc}</p>{children}</div>
  </section>;
}
function Breadcrumbs({ items }) {
  return <nav className="mag-breadcrumb" aria-label="Pot po spletišču"><a href="/">Naslovnica</a>{items.map((item, i) => <React.Fragment key={i}><span aria-hidden="true">/</span>{item.href ? <a href={item.href}>{item.label}</a> : <span aria-current="page">{item.label}</span>}</React.Fragment>)}</nav>;
}
function SectionHeading({ kicker, title, href, link, caption }) {
  return <div className="mag-section-head"><div><span className="mag-overline">{kicker}</span><h2>{title}</h2>{caption && <p>{caption}</p>}</div>{href && <a href={href} className="mag-text-link">{link || "Več ↗"}</a>}</div>;
}
function EventTile({ item, day }) {
  const image = eventImage(item);
  return <a href={eventHref(item)} className="mag-event-tile">
    <span className="mag-image" style={{ backgroundImage: "url(" + image + ")" }} aria-hidden="true" />
    <span className="mag-tile-body">
      <span className="mag-overline">{rubricInfo(rubricForEvent(item)).name} / {eventHour(item, day || keyForLjubljana(item.startAt))}</span>
      <strong>{item.title}</strong><small>{item.place || item.source || "Slovenija"}</small>
      <span className="mag-card-link">Podrobnosti dogodka ↗</span>
    </span>
  </a>;
}
function ArticleTile({ item }) {
  const rub = rubricForArticle(item);
  return <a className="mag-article-tile" href={articleHref(item)}>
    <span className="mag-image" style={{ backgroundImage: "url(" + articleImage(item) + ")" }} aria-hidden="true" />
    <span className="mag-tile-body"><span className="mag-overline">{rubricInfo(rub).name} / {niceDate(dateForArticle(item), { day: "numeric", month: "short", year: "numeric" })}</span>
      <strong>{item.title}</strong><small>{item.excerpt || "Preberi zgodbo na BlogLab."}</small><span className="mag-card-link">Preberi članek ↗</span></span>
  </a>;
}
function Calendar({ events, today }) {
  const [shownMonth, setShownMonth] = useState(today.slice(0, 7));
  const firstKey = shownMonth + "-01";
  const first = new Date(firstKey + "T12:00:00Z");
  const daysInMonth = new Date(Date.UTC(first.getUTCFullYear(), first.getUTCMonth() + 1, 0)).getUTCDate();
  const pad = (first.getUTCDay() + 6) % 7;
  const boxes = Array.from({ length: Math.ceil((pad + daysInMonth) / 7) * 7 }, (_, idx) => {
    const day = idx - pad + 1;
    return day > 0 && day <= daysInMonth ? shownMonth + "-" + String(day).padStart(2, "0") : "";
  });
  function shiftMonth(n) {
    const m = new Date(first.getTime());
    m.setUTCMonth(m.getUTCMonth() + n);
    setShownMonth(m.toISOString().slice(0, 7));
  }
  const shownEvents = pickEventsForDate(events, today).slice(0, 3);
  return <section className="mag-calendar-panel" aria-labelledby="mag-cal-title">
    <SectionHeading kicker="NAČRTUJ DAN" title="Koledar dogodkov" href={dateHref(today)} link="Vsi dogodki ↗" />
    <div className="mag-calendar-sheet">
      <div className="mag-cal-top"><button type="button" onClick={() => shiftMonth(-1)} aria-label="Prejšnji mesec">‹</button><strong>{niceDate(firstKey, { month: "long", year: "numeric" })}</strong><button type="button" onClick={() => shiftMonth(1)} aria-label="Naslednji mesec">›</button></div>
      <div className="mag-calendar-days">{DAYS.map((day) => <span key={day}>{day}</span>)}</div>
      <div className="mag-calendar-days dates">{boxes.map((key, idx) => key ? <a key={key} href={dateHref(key)} className={key === today ? "today" : ""} aria-label={niceDate(key) + ", " + events.filter((e) => eventActiveOn(e, key)).length + " dogodkov"}>
        {Number(key.slice(-2))}{events.some((e) => eventActiveOn(e, key)) && <i aria-hidden="true" />}</a> : <span key={"blank" + idx} />)}</div>
      <div className="mag-cal-agenda"><h3>Danes na koledarju</h3>
        {shownEvents.length ? shownEvents.map((event) => <a key={event.id} href={eventHref(event)}><span>{eventHour(event, today)}</span><strong>{event.title}</strong><span aria-hidden="true">↗</span></a>) : <p>Za danes ni potrjenih dogodkov. Izberi drug datum.</p>}
      </div>
    </div>
  </section>;
}
function FeaturedCulture({ article }) {
  return <section className="mag-culture-feature" aria-label="Kultura in uredniški izbor">
    <SectionHeading kicker="V OSPREDJU" title="Kultura." href={rubricHref("kultura")} link="Vse iz kulture ↗" />
    <a href={article ? articleHref(article) : rubricHref("kultura")} className="mag-feature-big">
      <span className="mag-image" style={{ backgroundImage: "url(" + IMAGES.kultura + ")" }} aria-hidden="true" />
      <span><span className="mag-overline">ZGODBA / KULTURA</span><strong>{article?.title || "Odkrij kulturne zgodbe in dogodke"}</strong><small>{article?.excerpt || "Razstave, kulturna dediščina in dogodki, ki jih je vredno poznati."}</small><em>Preberi več ↗</em></span>
    </a>
  </section>;
}
function WeekendCompact({ events, today }) {
  const days = weekendDates(today);
  return <section className="mag-weekend-compact" aria-labelledby="mag-weekend-heading">
    <div className="mag-mini-head"><span className="mag-overline">PETEK / SOBOTA / NEDELJA</span><a href={rubricHref("weekend")}>Vsi vikendi ↗</a></div>
    <h2 id="mag-weekend-heading">Weekend.</h2>
    <div className="mag-mini-weekend-grid">{days.map((key, idx) => {
      const found = pickEventsForDate(events, key);
      return <a href={dateHref(key)} key={key} className="mag-mini-day">
        <strong>{DAYS_LONG[idx]}</strong><span>{niceDate(key, { day: "numeric", month: "short" })}</span>
        <small>{found.length ? found[0].title : "Oglej si koledar"}</small><em>Odkrij ↗</em>
      </a>;
    })}</div>
  </section>;
}
function SecondaryFeature({ rubric, item }) {
  const data = rubricInfo(rubric);
  return <section className="mag-secondary-feature">
    <div className="mag-section-head"><div><span className="mag-overline">IZBRANO IZ RUBRIKE</span><h2>{data.name}.</h2></div><a href={rubricHref(rubric)} className="mag-text-link">Vse objave ↗</a></div>
    <a className="mag-feature-small" href={item ? articleHref(item) : rubricHref(rubric)}>
      <span className="mag-image" style={{ backgroundImage: "url(" + data.image + ")" }} aria-hidden="true" />
      <span><strong>{item?.title || data.description}</strong><small>{item?.excerpt || data.description}</small><em>Odpri zgodbo ↗</em></span>
    </a>
  </section>;
}
function Home({ events, feedStatus, today }) {
  const active = events.filter((e) => eventIsFuture(e, today));
  const todayItems = pickEventsForDate(active, today);
  const frontItems = (todayItems.length ? todayItems : active.sort((a, b) => new Date(a.startAt) - new Date(b.startAt))).slice(0, 7);
  const spotlight = Object.fromEntries(["kultura", "zabava", "sport"].map((rubric) => [rubric, ARTICLES.find((a) => rubricForArticle(a) === rubric)]));
  return <>
    <PaintedBanner eyebrow="BLOG LAB / KULTURA / ZABAVA / ŠPORT / WEEKEND" title={<>Ujemi danes. <em>Doživi več.</em></>} desc="Dogodki, zanimive zgodbe in ideje za prosti čas — odkrij, kaj se dogaja, in poišči svojo naslednjo izkušnjo." image={IMAGES.hero}>
      <a className="mag-hero-cta" href={dateHref(today)}>Razišči današnje dogodke ↗</a>
    </PaintedBanner>
    <div className="mag-wide mag-home-body">
      <section className="mag-today" id="today">
        <SectionHeading kicker="AKTUALNI DOGODKI / SLOVENIJA" title={todayItems.length ? "Danes se dogaja." : "Prihajajoči dogodki."} caption={niceDate(today, { weekday: "long", day: "numeric", month: "long", year: "numeric" })} href={dateHref(today)} link="Odpri koledar ↗" />
        {frontItems.length ? <div className="mag-today-rail">{frontItems.map((item) => <EventTile key={item.id} item={item} day={eventActiveOn(item, today) ? today : keyForLjubljana(item.startAt)} />)}</div> :
          <p className="mag-empty">{feedStatus === "loading" ? "Nalagam aktualne dogodke ..." : feedStatus === "error" ? "Vir dogodkov trenutno ni dosegljiv." : "Trenutno ni potrjenih dogodkov."}</p>}
      </section>
      <div className="mag-composition">
        <Calendar events={events} today={today} />
        <div className="mag-culture-weekend"><FeaturedCulture article={spotlight.kultura} /><WeekendCompact events={events} today={today} /></div>
      </div>
      <div className="mag-side-stories">
        <SecondaryFeature rubric="zabava" item={spotlight.zabava} />
        <SecondaryFeature rubric="sport" item={spotlight.sport} />
      </div>
      <section className="mag-latest">
        <SectionHeading kicker="NOVE ZGODBE / ARHIV" title="Blog in novice." caption="Objavljeni članki so dostopni v svoji rubriki in kot samostojne strani." href={rubricHref("novice")} link="Vse novice ↗" />
        <div className="mag-article-grid">{ARTICLES.slice(0, 4).map((item) => <ArticleTile key={item.id} item={item} />)}</div>
      </section>
    </div>
  </>;
}
function PeriodNav({ rubric, period }) {
  return <nav className="mag-tabs" aria-label="Obdobje dogodkov">
    {[["vse", "Vse"], ["aktualno", "Aktualni dogodki"], ["arhiv", "Pretekli dogodki"]].map(([key, label]) =>
      <a key={key} href={rubricHref(rubric, key)} aria-current={key === period ? "page" : undefined} className={period === key ? "active" : ""}>{label}</a>)}
  </nav>;
}
function EventsList({ items, today, title }) {
  return <section className="mag-list-group">
    <h2>{title} <span>({items.length})</span></h2>
    {items.length ? <div className="mag-entries">{items.map((event) => <a key={event.id} className="mag-entry" href={eventHref(event)}>
      <span className="mag-entry-image" style={{ backgroundImage: "url(" + eventImage(event) + ")" }} aria-hidden="true" />
      <span className="mag-entry-body"><span className="mag-overline">{rubricInfo(rubricForEvent(event)).name} · {niceDate(keyForLjubljana(event.startAt))}</span><strong>{event.title}</strong>
        <small>{event.place || event.source || "Slovenija"} · {eventHour(event, keyForLjubljana(event.startAt))} · {periodFor(event, today) === "aktualno" ? "Aktualno" : "Preteklo"}</small></span><span className="mag-entry-arrow">↗</span>
    </a>)}</div> : <p className="mag-empty">Za ta izbor trenutno ni objavljenih potrjenih dogodkov.</p>}
  </section>;
}
function ArticleList({ items, title }) {
  return <section className="mag-list-group"><h2>{title} <span>({items.length})</span></h2>
    {items.length ? <div className="mag-article-grid">{items.map((article) => <ArticleTile key={article.id} item={article} />)}</div> : <p className="mag-empty">V tej rubriki trenutno ni objavljenih člankov.</p>}
  </section>;
}
function RubricPage({ rubric, period, events, today }) {
  const data = rubricInfo(rubric);
  if (rubric === "novice") return <NewsPage />;
  if (rubric === "weekend") return <WeekendPage events={events} today={today} period={period} />;
  const relatedArticles = ARTICLES.filter((a) => rubricForArticle(a) === rubric);
  const selectedEvents = events.filter((e) => rubricForEvent(e) === rubric)
    .filter((e) => period === "vse" || periodFor(e, today) === period)
    .sort((a, b) => (Number(eventIsFuture(b, today)) - Number(eventIsFuture(a, today))) || new Date(b.startAt) - new Date(a.startAt));
  return <>
    <PaintedBanner eyebrow="BLOG LAB / RUBRIKA" title={data.name + "."} desc={data.description} image={data.image} compact />
    <div className="mag-wide mag-interior">
      <Breadcrumbs items={[{ label: data.name }]} />
      <div className="mag-stats"><span>{relatedArticles.length} objavljenih člankov</span><span>{events.filter((e) => rubricForEvent(e) === rubric).length} potrjenih dogodkov</span></div>
      <ArticleList items={relatedArticles} title={"Zgodbe: " + data.name} />
      <PeriodNav rubric={rubric} period={period} />
      <EventsList items={selectedEvents} title={period === "aktualno" ? "Prihajajoči dogodki" : period === "arhiv" ? "Pretekli dogodki" : "Vsi dogodki iz rubrike"} today={today} />
    </div>
  </>;
}
function NewsPage() {
  const params = new URLSearchParams(window.location.search);
  const chosen = params.get("vrsta") || "vse";
  const valid = ["vse", "kultura", "zabava", "sport"].includes(chosen) ? chosen : "vse";
  const shown = ARTICLES.filter((article) => valid === "vse" || rubricForArticle(article) === valid);
  return <>
    <PaintedBanner eyebrow="BLOG LAB / VSE OBJAVE" title="Blog in novice." desc="Zgodbe, novice, kultura, zabava in šport. Vse doslej objavljeno na enem mestu." image={IMAGES.novice} compact />
    <div className="mag-wide mag-interior"><Breadcrumbs items={[{ label: "Blog / Novice" }]} />
      <nav className="mag-tabs" aria-label="Filtri člankov">{[["vse", "Vse objave"], ...RUBRICS.filter((r) => ["kultura", "zabava", "sport"].includes(r.slug)).map((r) => [r.slug, r.name])].map(([key, label]) =>
        <a key={key} className={valid === key ? "active" : ""} aria-current={key === valid ? "page" : undefined} href={"/?rubrika=novice" + (key !== "vse" ? "&vrsta=" + key : "")}>{label}</a>)}</nav>
      <ArticleList items={shown} title="Vse objavljene zgodbe" />
    </div>
  </>;
}
function WeekendPage({ events, today, period }) {
  const days = weekendDates(today);
  const active = days.map((key, i) => ({ day: DAYS_LONG[i], key, items: pickEventsForDate(events, key) }));
  const past = events.filter((event) => !eventIsFuture(event, today) && [5, 6, 0].includes(new Date((keyForLjubljana(event.startAt) || "2000-01-01") + "T12:00:00Z").getUTCDay()))
    .sort((a, b) => new Date(b.startAt) - new Date(a.startAt)).slice(0, 40);
  return <>
    <PaintedBanner eyebrow="BLOG LAB / IDEJE ZA PROSTI ČAS" title="Weekend." desc="Dogodki za petek, soboto in nedeljo ter arhiv preteklih vikendov." image={IMAGES.weekend} compact />
    <div className="mag-wide mag-interior"><Breadcrumbs items={[{ label: "Weekend" }]} />
      <div className="mag-tabs"><a href={rubricHref("weekend", "aktualno")} className={period !== "arhiv" ? "active" : ""}>Ta konec tedna</a><a href={rubricHref("weekend", "arhiv")} className={period === "arhiv" ? "active" : ""}>Pretekli vikendi</a></div>
      {period === "arhiv" ? <EventsList items={past} today={today} title="Arhiv vikend dogodkov" /> :
        <div className="mag-weekend-archive-grid">{active.map(({ day, key, items }, idx) =>
          <section key={key} className="mag-weekend-day">
            <a href={dateHref(key)} className="mag-weekend-day-head" style={{ backgroundImage: "linear-gradient(90deg,rgba(29,51,37,.8),rgba(29,51,37,.2)),url(" + [IMAGES.weekend, IMAGES.kultura, IMAGES.trails][idx] + ")" }}>
              <span>{niceDate(key)}</span><strong>{day}</strong><small>Vsi dogodki na ta dan ↗</small>
            </a>
            <div>{items.length ? items.map((item) => <a href={eventHref(item)} key={item.id}>{item.title}<small>{eventHour(item, key)} · {item.place || item.source}</small></a>) : <p>Za ta dan trenutno ni potrjenih dogodkov.</p>}</div>
          </section>
        )}</div>}
      <div className="mag-info-link"><a href={rubricHref("kultura")}>Odkrij tudi kulturo ↗</a><a href={rubricHref("zabava")}>Zabava ↗</a><a href={rubricHref("sport")}>Šport in narava ↗</a></div>
    </div>
  </>;
}
function DatePage({ keyDate, events, today, category }) {
  const validDate = /^\d{4}-\d{2}-\d{2}$/.test(keyDate) && !Number.isNaN(new Date(keyDate + "T12:00:00Z").getTime());
  const date = validDate ? keyDate : today;
  const validCategory = ["vse", "kultura", "zabava", "sport"].includes(category) ? category : "vse";
  const items = pickEventsForDate(events, date, validCategory === "vse" ? null : validCategory);
  return <>
    <PaintedBanner eyebrow="BLOG LAB / KOLEDAR" title="Dogodki po datumu." desc={"Izbrani datum: " + niceDate(date, { weekday: "long", day: "numeric", month: "long", year: "numeric" }) + ". Dogodke preveri pri organizatorju."} image={IMAGES.hero} compact />
    <div className="mag-wide mag-interior"><Breadcrumbs items={[{ label: "Dogodki: " + niceDate(date) }]} />
      <div className="mag-calendar-actions"><a href={dateHref(addDays(date, -1))}>← Prejšnji dan</a><a href={dateHref(today)}>Danes</a><a href={dateHref(addDays(date, 1))}>Naslednji dan →</a></div>
      <nav className="mag-tabs" aria-label="Kategorije dogodkov">{[["vse", "Vsi"],["kultura","Kultura"],["zabava","Zabava"],["sport","Šport"]].map(([rub, label]) =>
        <a key={rub} href={dateHref(date) + (rub === "vse" ? "" : "&vrsta=" + rub)} className={rub === validCategory ? "active" : ""}>{label}</a>)}</nav>
      <EventsList items={items} title={"Dogodki: " + niceDate(date)} today={today} />
    </div>
  </>;
}
function EventDetail({ id, events, today, status }) {
  const item = events.find((e) => e.id === id);
  if (!item) return status === "loading" ? <LoadingPage /> : <NotFound title="Dogodek ni na voljo." />;
  const data = rubricInfo(rubricForEvent(item));
  const officialUrl = typeof item.ticketUrl === "string" && /^https:\/\//.test(item.ticketUrl) ? item.ticketUrl : item.url;
  return <>
    <PaintedBanner eyebrow={"BLOG LAB / " + data.name.toUpperCase()} title={item.title} desc={item.place || item.source || "Slovenija"} image={data.image} compact />
    <div className="mag-wide mag-interior mag-detail"><Breadcrumbs items={[{ href: rubricHref(data.slug), label: data.name }, { label: item.title }]} />
      <div className="mag-article-layout">
        <article><span className="mag-overline">{eventIsFuture(item, today) ? "Aktualni dogodek" : "Pretekli dogodek"} · {item.type || data.name}</span>
          <h2>O dogodku</h2><p>{item.description || "Več informacij je na voljo pri organizatorju."}</p>
          <a className="mag-primary-link" href={officialUrl} target="_blank" rel="noopener noreferrer">Odpri uradne informacije ↗</a>
        </article>
        <aside className="mag-facts"><h3>Informacije</h3><dl><dt>Začetek</dt><dd>{niceDate(keyForLjubljana(item.startAt))} · {eventHour(item)}</dd>
          <dt>Konec</dt><dd>{item.endAt ? niceDate(keyForLjubljana(item.endAt)) : "Preveri pri organizatorju"}</dd>
          <dt>Lokacija</dt><dd>{item.place || "Preveri pri organizatorju"}</dd>
          <dt>Vir</dt><dd>{item.source || "Organizator"}</dd></dl>
          <a href={rubricHref(data.slug)}>Nazaj na {data.name.toLowerCase()} ↗</a></aside>
      </div>
    </div>
  </>;
}
function ArticleDetail({ id }) {
  const item = ARTICLES.find((article) => article.id === id);
  if (!item) return <NotFound title="Članek ni na voljo." />;
  const data = rubricInfo(rubricForArticle(item));
  const blocks = String(item.content || item.excerpt || "").split(/\n\s*\n/).filter(Boolean);
  return <>
    <PaintedBanner eyebrow={"BLOG LAB / " + data.name.toUpperCase()} title={item.title} desc={item.excerpt || data.description} image={data.image} compact />
    <div className="mag-wide mag-interior mag-detail"><Breadcrumbs items={[{ href: rubricHref(data.slug), label: data.name }, { label: item.title }]} />
      <div className="mag-article-layout">
        <article className="mag-reading"><span className="mag-overline">OBJAVLJENO · {niceDate(dateForArticle(item))} · {data.name}</span>
          {blocks.map((block, i) => {
            const text = block.replace(/\*\*/g, "").replace(/\[([^\]]+)\]\(https?:\/\/[^)]+\)/g, "$1");
            if (/^#{2,4}\s/.test(block)) return <h2 key={i}>{text.replace(/^#+\s*/, "")}</h2>;
            return <p key={i}>{text}</p>;
          })}
          {!!item.sources?.length && <div className="mag-sources"><h2>Viri in dodatno branje</h2>
            {item.sources.filter((src) => /^https:\/\//.test(src.url || "")).map((src, i) => <a href={src.url} target="_blank" rel="noopener noreferrer" key={i}>{src.label || "Izvirni vir"} ↗</a>)}</div>}
        </article>
        <aside className="mag-facts"><h3>Več iz rubrike</h3>
          {ARTICLES.filter((a) => a.id !== item.id && rubricForArticle(a) === data.slug).slice(0, 5).map((a) => <a href={articleHref(a)} key={a.id}>{a.title} ↗</a>)}
          <a href={rubricHref(data.slug)} className="mag-back-category">Vsi članki: {data.name} →</a>
        </aside>
      </div>
    </div>
  </>;
}
function SearchPage({ query, events, today }) {
  const q = query.trim().toLocaleLowerCase("sl");
  const articles = ARTICLES.filter((a) => [a.title, a.excerpt, a.category].filter(Boolean).join(" ").toLocaleLowerCase("sl").includes(q));
  const foundEvents = events.filter((e) => [e.title, e.place, e.type, e.description].filter(Boolean).join(" ").toLocaleLowerCase("sl").includes(q));
  return <>
    <PaintedBanner eyebrow="BLOG LAB / ISKANJE" title="Rezultati iskanja." desc={"Poizvedba: " + query} image={IMAGES.novice} compact />
    <div className="mag-wide mag-interior"><Breadcrumbs items={[{ label: "Iskanje" }]} />
      <ArticleList items={articles} title="Najdeni članki" />
      <EventsList items={foundEvents} today={today} title="Najdeni dogodki" />
    </div>
  </>;
}
function LoadingPage() { return <div className="mag-wide mag-interior"><p className="mag-empty">Pridobivam podatke o dogodku ...</p></div>; }
function NotFound({ title }) { return <div className="mag-wide mag-interior"><h1>{title}</h1><p>Vsebina morda ni več na voljo.</p><a href="/" className="mag-primary-link">Nazaj na naslovnico ↗</a></div>; }

export default function BlogLabMagazine() {
  const params = new URLSearchParams(window.location.search);
  const today = useMemo(todayKey, []);
  const feed = useEventsFeed();
  const articleId = params.get("clanek");
  const eventId = params.get("dogodek");
  const dateKey = params.get("dogodki");
  const search = params.get("iskanje");
  const rubric = params.get("rubrika");
  const period = ["vse", "aktualno", "arhiv"].includes(params.get("obdobje")) ? params.get("obdobje") : "vse";
  const active = articleId ? rubricForArticle(ARTICLES.find((a) => a.id === articleId)) :
    eventId ? rubricForEvent(feed.items.find((e) => e.id === eventId)) : rubric;

  let content = <Home events={feed.items} feedStatus={feed.status} today={today} />;
  if (rubric) content = RUBRICS.some((r) => r.slug === rubric) ? <RubricPage rubric={rubric} period={period} events={feed.items} today={today} /> : <NotFound title="Rubrika ne obstaja." />;
  if (dateKey) content = <DatePage keyDate={dateKey} events={feed.items} today={today} category={params.get("vrsta")} />;
  if (search !== null) content = search.trim().length > 1 ? <SearchPage query={search} events={feed.items} today={today} /> : <NotFound title="Vnesi vsaj dve črki za iskanje." />;
  if (eventId) content = <EventDetail id={eventId} events={feed.items} today={today} status={feed.status} />;
  if (articleId) content = <ArticleDetail id={articleId} />;

  return <div className="tourism-site bloglab-redesign bloglab-magazine">
    <PageHeader active={active} q={search || ""} />
    <main id="main">{content}</main>
    <PageFooter />
  </div>;
}
