/* Production art-book integrity check; requires npm run art:generate first. */
import { readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const names = ["hero", "kolesarstvo", "dediscina", "sezonsko", "gore-traili", "gourmet", "vodniki"];
for (const name of names) {
  const file = join("public", "art", "generated", name + ".svg");
  const svg = readFileSync(file, "utf8");
  const bytes = statSync(file).size;
  if (bytes < 20000 || bytes > 400000) throw new Error("Invalid art size: " + file + " (" + bytes + ")");
  if (!svg.startsWith("<svg") || !svg.trimEnd().endsWith("</svg>")) throw new Error("Invalid SVG: " + file);
  if (!svg.includes("<title>") || !svg.includes("feTurbulence")) throw new Error("Missing painting or accessible title: " + file);
  console.log("ART_OK", name, bytes);
}
const css = readFileSync("src/painterly-atelier-v5.css", "utf8");
const app = readFileSync("src/App.jsx", "utf8");
for (const selector of [".paint-hero-folio", ".paint-story-paper", ".paint-stories-more", ".paint-rubric-index"]) {
  if (!css.includes(selector)) throw new Error("Missing painterly style: " + selector);
}
if (!app.includes("aria-expanded={showAllStories}")) throw new Error("Missing accessible story expansion");
if (!app.includes("setShowAllStories(false)")) throw new Error("Story expansion does not reset on category change");
if (!app.includes("<LivePulse />")) throw new Error("Real live event feed missing");
console.log("ATELIER_V5_VALID");

const galleryV6Css = readFileSync("src/painterly-photo-v6.css", "utf8");
if (!/\.tourism-site\s*>\s*\.site-header\s+nav\s*\{[^}]*display\s*:\s*flex\s*;/m.test(galleryV6Css)) {
  throw new Error("Mobile rubric navigation is hidden: V6 must explicitly restore display:flex");
}
console.log("MOBILE_NAV_V6_VALID");
