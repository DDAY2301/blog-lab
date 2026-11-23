import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { test } from "node:test";
import { articlePhotoForItem } from "../src/bloglab-article-photos.js";

const dir = new URL("../src/articles/published/", import.meta.url);
const articles = readdirSync(dir).filter(name => name.endsWith(".json"))
  .map(name => JSON.parse(readFileSync(new URL(name, dir), "utf8")))
  .filter(article => article.status === "published");

test("Public article image sources do not repeat across the entire archive", () => {
  const photos = articles.map(item => articlePhotoForItem(item, articles));
  const valid = photos.filter(Boolean);
  assert.ok(valid.length >= articles.length - 4, "Too many articles lost their photos: " + (articles.length - valid.length));
  assert.equal(new Set(valid.map(p => p.src)).size, valid.length, "Repeated article thumbnail URLs");
  assert.equal(new Set(valid.map(p => p.sourceUrl)).size, valid.length, "Repeated licensed source URLs");
  for (const p of valid) {
    assert.match(p.src, /^(https:\/\/|\/media\/articles\/)/);
    assert.match(p.sourceUrl, /^https:\/\//);
    assert.ok(p.author, "Missing photo author");
    assert.ok(p.license, "Missing licence");
  }
});

test("Assignments stay stable under filter/reorder", () => {
  for (const article of articles) {
    assert.equal(
      articlePhotoForItem(article, articles)?.src,
      articlePhotoForItem(article, [...articles].reverse())?.src,
      "Photo changed for " + article.id
    );
  }
});

test("Weather and overseas sports never show their unrelated inherited landscape", () => {
  for (const item of articles.filter(a => /ARSO|nevihte|požarna|India squad|Biketopia/i.test(a.title))) {
    const selected = articlePhotoForItem(item, articles);
    assert.ok(selected, "Missing illustrative image for " + item.id);
    assert.doesNotMatch(selected.src, /Frozen_Lake_Bled|bicycle_expedition/i);
  }
});

test("Croatian tourism stories show two separate Croatian photos", () => {
  const croatia = articles.filter(a => /hrvašk|hrvatsk/i.test(a.title));
  assert.ok(croatia.length >= 2);
  const photos = croatia.map(a => articlePhotoForItem(a, articles));
  assert.ok(photos.every(Boolean));
  assert.equal(new Set(photos.map(p => p.src)).size, photos.length);
  assert.ok(photos.every(p => /Croatia-Coastline|Dubrovnik|croatia|hrvat/i.test(p.src+" "+p.alt+" "+p.sourceUrl)));
});
