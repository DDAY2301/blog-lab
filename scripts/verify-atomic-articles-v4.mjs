// Atomic V4 fail-closed validation before EVERY production build.
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const app = fs.readFileSync(path.join(root, "src/App.jsx"), "utf8");
const anchor = "const starterArticles = [";
const marker = 'import.meta.glob("./articles/published/*.json"';
if (!app.includes(anchor) || !app.includes(marker)) {
  throw new Error("ATOMIC_V4_NOT_WIRED");
}
if (app.includes("bytes omitted")) throw new Error("LEGACY_ARTICLE_CORRUPTED");
const start = app.indexOf(anchor);
const end = app.indexOf("const emptyDraft", start);
if (end < start) throw new Error("LEGACY_ARTICLE_BOUNDARY_NOT_FOUND");
const legacy = app.slice(start, end);
const ids = [...legacy.matchAll(/^\s*(?:"id"|id):\s*"([^"]+)"/gm)].map(x => x[1]);
const seen = new Set(ids);
if (ids.length < 174 || seen.size !== ids.length) {
  throw new Error("LEGACY_ARTICLE_COUNT_OR_DUPLICATE: " + ids.length + "/" + seen.size);
}
const dir = path.join(root, "src/articles/published");
let atomicCount = 0;
const entries = fs.existsSync(dir) ? fs.readdirSync(dir).filter(x => x.endsWith(".json")) : [];
for (const name of entries) {
  const articleId = name.slice(0, -5);
  if (!/^[a-z0-9][a-z0-9-]{1,119}$/.test(articleId)) {
    throw new Error("INVALID_ATOMIC_FILENAME: " + name);
  }
  const value = JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));
  if (!value || Array.isArray(value) || typeof value !== "object" ||
      value.id !== articleId || !value.title || !value.excerpt ||
      !value.content || !value.category || !Array.isArray(value.sources)) {
    throw new Error("INVALID_ATOMIC_ARTICLE: " + name);
  }
  if (seen.has(articleId)) throw new Error("DUPLICATE_ATOMIC_ID: " + articleId);
  seen.add(articleId);
  atomicCount++;
}
console.log("ATOMIC_V4_VALID legacy=" + ids.length + " atomic=" + atomicCount + " total=" + seen.size);
