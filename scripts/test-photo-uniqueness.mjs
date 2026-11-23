import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { eventPhotoForItem, eventPhotoKind, EVENT_PHOTO_BANK } from "../src/bloglab-event-photos.js";

const dir = new URL("../", import.meta.url);
const feed = JSON.parse(readFileSync(new URL("../public/events-feed.json", import.meta.url), "utf8"));
const events = feed.items || [];

test("Every currently published event receives its own non-reused photo", () => {
  const chosen = events.map(item => eventPhotoForItem(item, events));
  const absent = events.filter((_, i) => !chosen[i]).map(item => item.id);
  assert.deepEqual(absent, [], "missing event photos: " + absent.join(", "));
  assert.equal(new Set(chosen.map(photo => photo.src)).size, events.length, "photo reuse across events");
  for (const photo of chosen) {
    assert.match(photo.src, /^https:\/\/images\.unsplash\.com\/photo-/);
    assert.match(photo.sourceUrl, /^https:\/\/unsplash\.com\/photos\//);
    assert.equal(photo.license, "Unsplash License");
    assert.ok(photo.author);
    assert.match(photo.note, /ne prikazuje napovedanega dogodka/);
  }
});

test("Sorting/filtering changes nothing about an event's chosen photo", () => {
  const sorted = [...events].reverse();
  for (const event of events) {
    assert.equal(eventPhotoForItem(event, sorted)?.src, eventPhotoForItem(event, events)?.src);
  }
});

test("Surplus events don't silently recycle photos", () => {
  const additional = Array.from({ length: EVENT_PHOTO_BANK.music.length + 3 }, (_, i) => ({
    id: "test-new-concert-" + i, title: "New concert " + i, type: "Concert"
  }));
  const selections = additional.map(item => eventPhotoForItem(item, additional)).filter(Boolean);
  assert.equal(new Set(selections.map(item => item.src)).size, selections.length);
  assert.ok(selections.length < additional.length);
});

test("Topic buckets classify performances, exhibitions, literature and food correctly", () => {
  assert.equal(eventPhotoKind({ title: "OJAČEVALNICA", type: "Workshop · music" }), "music");
  assert.equal(eventPhotoKind({ title: "COSMOS KOSOVEL", type: "Exhibition · literature" }), "gallery");
  assert.equal(eventPhotoKind({ title: "Doctor Zhivago", type: "Ballet drama" }), "stage");
  assert.equal(eventPhotoKind({ title: "Omakase", type: "Culinary experience" }), "food");
});

test("Both Croatian tourism articles have distinct, geographically relevant photos", () => {
  const paths = [
    "../src/articles/published/hrvaska-turisticna-sezona-bo-podrla-rekorde-slovenska-bo-dobra-24ur-com-148ab55f.json",
    "../src/articles/published/hrvaski-turizem-po-slabem-juniju-navzgor-pomagali-tudi-slovenci-delo-si-3d62ff2d.json"
  ];
  const articles = paths.map(path => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf8")));
  assert.equal(new Set(articles.map(a => a.heroImage.sourceUrl)).size, 2);
  for (const a of articles) {
    assert.match(a.heroImage.sourceUrl, /commons\.wikimedia\.org\/wiki\/File:/);
    assert.match(a.heroImage.alt, /hrvašk|dubrovnik/i);
    assert.doesNotMatch(a.heroImage.sourceUrl, /bled|slovenia/i);
    assert.match(a.heroImage.caption, /CC BY/);
  }
});
