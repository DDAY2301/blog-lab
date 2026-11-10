import { magazineCardArtwork, LJUBLJANA_PAINTINGS, stableArtworkIndex } from "../src/bloglab-artwork.js";
import { readFileSync, existsSync } from "node:fs";
import assert from "node:assert/strict";
import { join } from "node:path";
import {
 RUBRICS, rubricForArticle, rubricForEvent, rubricHref, articleHref, eventHref,
 dateHref, weekendDates, addDays, eventActiveOn, keyForLjubljana, trustedEvent
} from "../src/bloglab-taxonomy.js";

const root = process.cwd();
const load = (path) => readFileSync(join(root, path), "utf8");
const page = load("src/BlogLabMagazine.jsx");
const entry = load("src/main.jsx");
const css = load("src/bloglab-magazine.css");
const feed = JSON.parse(load("public/events-feed.json"));
const articlePaths = [];
// Representative editorial taxonomy ensures that nature and movement land under Sport.
assert.equal(rubricForArticle({ category: "Kolesarstvo", title: "Eurovelo kolesarske poti" }), "sport");
assert.equal(rubricForArticle({ category: "Gore & traili", title: "Pohodniške poti v Sloveniji" }), "sport");
assert.equal(rubricForArticle({ category: "Dediščina", title: "Razstava v Narodnem muzeju" }), "kultura");
assert.equal(rubricForArticle({ category: "Gourmet", title: "Kulinarika Slovenije" }), "zabava");
assert.equal(rubricForEvent({ type: "Concert · classical", title: "Koncert" }), "zabava");
assert.equal(rubricForEvent({ type: "Exhibition", title: "Razstava" }), "kultura");
assert.equal(rubricForEvent({ type: "Trail race", title: "Pohod" }), "sport");

assert.equal(RUBRICS.length, 5);
for (const slug of ["kultura", "zabava", "sport", "weekend", "novice"]) {
 assert.ok(RUBRICS.some((r) => r.slug === slug), "Missing rubrica " + slug);
 assert.ok(rubricHref(slug).startsWith("/?rubrika="));
}
assert.equal(articleHref({ id: "abc" }), "/?clanek=abc");
assert.equal(eventHref({ id: "xyz" }), "/?dogodek=xyz");
assert.equal(dateHref("2026-11-06"), "/?dogodki=2026-11-06");
assert.deepEqual(weekendDates("2026-11-06"), ["2026-11-06", "2026-11-07", "2026-11-08"]);
assert.deepEqual(weekendDates("2026-11-07"), ["2026-11-06", "2026-11-07", "2026-11-08"]);
assert.deepEqual(weekendDates("2026-11-08"), ["2026-11-06", "2026-11-07", "2026-11-08"]);
assert.equal(addDays("2026-11-06", 2), "2026-11-08");
assert.equal(eventActiveOn({ startAt: "2026-11-06T19:00:00+01:00", endAt: null }, "2026-11-06"), true);
assert.equal(eventActiveOn({ startAt: "2026-11-06T19:00:00+01:00", endAt: null }, "2026-11-07"), false);
assert.ok(feed.items.some(trustedEvent), "No confirmed events in the existing feed");

for (const asset of ["hero", "dediscina", "gourmet", "kolesarstvo", "sezonsko", "gore-traili", "vodniki"]) {
 assert.ok(existsSync(join(root, "public/art/painted/" + asset + ".jpg")), "Original oil painting missing: " + asset);
}
assert.ok(page.includes('import.meta.glob("./articles/published/*.json"'), "All published articles must be indexed");
// The homepage has three equal editorial cards, followed by a separate full-width Weekend.
assert.ok(page.includes('className="mag-rubrics-grid"'), "Missing three-column rubric grid");
assert.ok(page.includes('className="mag-weekend-feature-grid"'), "Missing full-width Weekend cards");
assert.ok(page.includes('["kultura", "zabava", "sport"].map('), "All three categories must be present");
const calendar = page.indexOf('<Calendar events={events} today={today} />');
const rubrics = page.indexOf('<section className="mag-rubrics"');
const weekend = page.indexOf('<WeekendFeature events={events} today={today} />');
const news = page.indexOf('<section className="mag-latest"');
assert.ok(calendar >= 0 && calendar < rubrics && rubrics < weekend && weekend < news,
  "Expected ordering: calendar, Kultura / Zabava / Sport, Weekend, news");
assert.ok(!page.includes("mag-culture-weekend"), "Obsolete interleaved Weekend layout present");
assert.ok(!page.includes("<WeekendCompact"), "Obsolete compact Weekend layout present");
assert.ok(page.includes('className="mag-calendar-month"'), "Calendar month and agenda must be siblings");
assert.ok(page.includes('className="mag-cal-agenda"'), "Missing adjacent daily events agenda");
for (const component of ["RubricPage", "ArticleDetail", "EventDetail", "DatePage", "WeekendPage", "NewsPage", "SearchPage"]) {
 assert.ok(page.includes("function " + component), "Missing deep route: " + component);
}
assert.ok(page.includes("href={rubricHref(rubric.slug)}"), "Header category nav needs real links");
assert.ok(page.includes("href={articleHref(item)}"), "Article cards need a real deep link");
assert.ok(page.includes("href={eventHref(item)}"), "Event cards need a real deep link");
assert.ok(entry.includes("isPublicHome ? <BlogLabMagazine /> : <App />"), "Public magazine and classic editor must be preserved");
assert.ok(css.includes(".mag-rubrics-grid") && css.includes("grid-template-columns:repeat(3"),
  "Three category columns must be explicitly styled");
assert.ok(css.includes(".mag-weekend-feature-grid") && css.includes(".mag-calendar-sheet"),
  "Full-width Weekend and split calendar styles must be present");
assert.ok(css.includes("@media(max-width:640px)"), "Responsive magazine layout missing");

const pathSamples = [
  "ljubljana-grad.png", "ljubljana-tromostovje.png",
  "ljubljana-zmajski-most.png", "ljubljana-ljubljanica.png"
];
assert.equal(LJUBLJANA_PAINTINGS.length, pathSamples.length);
for (const name of pathSamples) {
  const filename = join(root, "public/art/painted", name);
  assert.ok(existsSync(filename), "Missing imported Ljubljana painting: " + name);
  const image = readFileSync(filename);
  assert.equal(image.subarray(1, 4).toString(), "PNG", "Invalid PNG asset " + name);
  assert.ok(image.length > 30000, "Corrupted Ljubljana painting: " + name);
}
const sample = { id: "culture-123", title: "Dogodek" };
assert.equal(magazineCardArtwork(sample, "kultura", "/fallback.jpg"), magazineCardArtwork(sample, "kultura", "/fallback.jpg"));
assert.equal(magazineCardArtwork(sample, "sport", "/art/painted/kolesarstvo.jpg"), "/art/painted/kolesarstvo.jpg");
const seen = new Set(Array.from({length: 100}, (_, i) => stableArtworkIndex("magazine-" + i)));
assert.equal(seen.size, 4, "All four Ljubljana scenes must be reachable from deterministic rotation");
// The painterly assets remain available in the classic view, but public magazine
// has transitioned to licensed documentary photography.
assert.ok(page.includes('from "./bloglab-open-photos.js"'), "Magazine must use verified real photos");
assert.ok(page.includes('from "./bloglab-nightlife.js"'), "Weekend must use confirmed club nights");
assert.ok(page.includes('photoForArticle(item)'), "Article images should match article subject");
assert.ok(page.includes('nightlifeForDay(events, key)'), "Weekend must not list unrelated daytime events");
assert.ok(page.includes('Fotografije, avtorji in licence'), "Accessible photo credits missing");

console.log("BlogLab V2: taxonomy, deep links, painting assets and compact layout checks passed");
