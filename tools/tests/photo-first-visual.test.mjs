import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {
  DISPLAY_PHOTOS, displayPhotoForArticle, displayPhotoForEvent,
  displayPhotoForRubric
} from "../../src/bloglab-display-photos.js";

test("all publicly displayed images use fixed Unsplash CDN URLs and verifiable credits", () => {
  assert.ok(Object.values(DISPLAY_PHOTOS).length >= 8);
  for (const photo of Object.values(DISPLAY_PHOTOS)) {
    assert.match(photo.src, /^https:\/\/images\.unsplash\.com\/photo-\d+-[a-f0-9]+\?/);
    assert.match(photo.sourceUrl, /^https:\/\/unsplash\.com\/photos\//);
    assert.equal(photo.license, "Unsplash License");
    assert.equal(photo.licenseUrl, "https://unsplash.com/license");
    assert.ok(photo.author.length >= 5);
    assert.ok(photo.alt.length >= 8);
    assert.ok(photo.note.toLowerCase().includes("fotografija"));
  }
});

test("every event, article and rubric receives a visual without inventing an event photo", () => {
  for (const item of [
    { title: "Neodvisna gledališka predstava", type: "kultura" },
    { title: "Dirka po Sloveniji", type: "kolesarstvo" },
    { title: "DJ v Klubu K4 Ljubljana", type: "koncert" },
    { title: "Novi predpisi", type: "novice" },
    { title: "Neznana tema", type: "drugo" }
  ]) {
    assert.ok(displayPhotoForEvent(item)?.src);
    assert.ok(displayPhotoForArticle(item)?.src);
  }
  for (const rubric of ["kultura", "zabava", "sport", "weekend", "novice", "unknown"]) {
    assert.ok(displayPhotoForRubric(rubric)?.src);
  }
  assert.equal(displayPhotoForArticle({title:"Kolesarjenje po Golovcu"}),DISPLAY_PHOTOS.cycling);
  assert.equal(displayPhotoForEvent({title:"Zabava in DJ večer"}), DISPLAY_PHOTOS.music);
  assert.equal(displayPhotoForArticle({title:"Pohodniški izlet po Alpah"}), DISPLAY_PHOTOS.hiking);
  assert.equal(displayPhotoForRubric("weekend"), DISPLAY_PHOTOS.nightlife);
});

test("magazine uses photographic Ljubljana hero and never renders missing photo backgrounds", () => {
  const magazine = fs.readFileSync(new URL("../../src/BlogLabMagazine.jsx", import.meta.url), "utf8");
  const css = fs.readFileSync(new URL("../../src/bloglab-real-editorial.css", import.meta.url), "utf8");
  assert.match(magazine, /hero: DISPLAY_PHOTOS\.ljubljana\.src/);
  assert.match(magazine, /const photo = displayPhotoForEvent\(item\)/);
  assert.match(magazine, /const photo = displayPhotoForArticle\(item\)/);
  assert.doesNotMatch(magazine, /backgroundImage: image \? "url\(" \+ image \+ "\)" : "none"/);
  assert.match(css, /background-color:\s*#17352b/);
  assert.match(css, /\.mag-painted-banner h1\s*\{/);
  assert.match(css, /@media \(max-width: 480px\)/);
});
