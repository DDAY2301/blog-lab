import { readFileSync, existsSync } from "node:fs";
import assert from "node:assert/strict";
import { join } from "node:path";

const root = process.cwd();
const read = (file) => readFileSync(join(root, file), "utf8");
const home = read("src/BlogLabHome.jsx");
const style = read("src/bloglab-home-v1.css");
const entry = read("src/main.jsx");
const events = JSON.parse(read("public/events-feed.json"));
const published = read("src/BlogLabHome.jsx").includes('import.meta.glob("./articles/published/*.json"');

for (const id of ["today","calendar","stories","weekend","blog"]) {
  assert.ok(home.includes('id="' + id + '"'), "Missing homepage section: " + id);
}
for (const asset of ["hero","dediscina","gourmet","kolesarstvo","sezonsko","gore-traili","vodniki"]) {
  assert.ok(existsSync(join(root, "public/art/painted/" + asset + ".jpg")), "Missing existing oil painting: " + asset);
}
for (const word of ["Kultura", "Zabava", "Šport", "Weekend", "Koledar dogodkov", "Blog in novice"]) {
  assert.ok(home.includes(word), "Missing editorial topic " + word);
}
assert.ok(home.includes('fetch("/events-feed.json"'), "Events feed must power event cards");
assert.ok(published, "Published articles must be sourced from the existing editorial store");
assert.ok(Array.isArray(events.items) && events.items.length, "Event feed empty");
assert.ok(home.includes('status === "confirmed"'), "Event cards should not surface unconfirmed entries");
assert.ok(entry.includes('isPublicHome ? <BlogLabHome /> : <App />'), "Original app must stay available");
assert.ok(style.includes("painted/hero.jpg"), "Original painterly hero must remain");
assert.ok(style.includes("@media(max-width:580px)"), "Mobile layout must be present");
console.log("BlogLab homepage A+C contract passed. Existing art and content sources preserved.");
