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
assert.ok(page.includes("mag-culture-weekend"), "Kultura and Weekend must be placed together");
const culture = page.indexOf("<FeaturedCulture article=");
const weekend = page.indexOf("<WeekendCompact events=");
assert.ok(culture >= 0 && weekend > culture, "Weekend must be directly after Kultura");
for (const component of ["RubricPage", "ArticleDetail", "EventDetail", "DatePage", "WeekendPage", "NewsPage", "SearchPage"]) {
 assert.ok(page.includes("function " + component), "Missing deep route: " + component);
}
assert.ok(page.includes("href={rubricHref(rubric.slug)}"), "Header category nav needs real links");
assert.ok(page.includes("href={articleHref(item)}"), "Article cards need a real deep link");
assert.ok(page.includes("href={eventHref(item)}"), "Event cards need a real deep link");
assert.ok(entry.includes("isPublicHome ? <BlogLabMagazine /> : <App />"), "Public magazine and classic editor must be preserved");
assert.ok(css.includes("mag-composition") && css.includes("grid-template-columns"), "Compact editorial layout missing");
assert.ok(css.includes("@media(max-width:640px)"), "Responsive magazine layout missing");
console.log("BlogLab V2: taxonomy, deep links, painting assets and compact layout checks passed");
