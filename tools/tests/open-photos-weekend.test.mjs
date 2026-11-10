import test from "node:test";
import assert from "node:assert/strict";
import { PHOTOS, photoForArticle, photoForEvent, photoForRubric } from "../../src/bloglab-open-photos.js";
import { isNightlifeEvent, nightlifeKey, nightlifeForDay } from "../../src/bloglab-nightlife.js";

test("licensed Wikimedia photography requires attribution and provenance", () => {
  for (const photo of Object.values(PHOTOS)) {
    assert.match(photo.src, /^https:\/\/commons\.wikimedia\.org\/wiki\/Special:FilePath\//);
    assert.match(photo.sourceUrl, /^https:\/\/commons\.wikimedia\.org\/wiki\/File:/);
    assert.match(photo.licenseUrl, /^https:\/\/creativecommons\.org\/licenses\/by/);
    assert.ok(photo.author.length > 3);
    assert.ok(photo.note.length > 10);
  }
});
test("photography matches topic; unrelated events do not inherit a fake venue photo", () => {
  assert.equal(photoForArticle({ title:"Daljinske kolesarske poti v Sloveniji" })?.src, PHOTOS.cycling.src);
  assert.equal(photoForArticle({ title:"Vzpon na Triglav" })?.src, PHOTOS.mountains.src);
  assert.equal(photoForArticle({ title:"Na Metelkovi" })?.src, PHOTOS.metelkova.src);
  assert.equal(photoForArticle({ title:"Hrvaška turistična sezona" }), null);
  assert.equal(photoForEvent({ title:"Equinox", place:"SNG Opera Ljubljana" }), null);
  assert.equal(photoForEvent({ title:"Just A Dance", place:"Klub K4 Ljubljana" })?.src, PHOTOS.metropolis.src);
  assert.equal(photoForRubric("weekend")?.src, PHOTOS.metelkova.src);
});
test("weekend slots are verified nightlife only and carry after-midnight events to previous night", () => {
  const friday = {
    id:"friday", status:"confirmed", title:"In Between re|lined x AMOTIK",
    type:"Club · elektronika", place:"Klub K4 Ljubljana",
    startAt:"2026-11-13T23:00:00+01:00", url:"https://www.klub-k4.si/"
  };
  const after = { ...friday,id:"after",title:"Afterparty DJ Set",startAt:"2026-11-14T02:00:00+01:00" };
  const gallery = { ...friday,id:"gallery",title:"Razstava slik",type:"Razstava",startAt:"2026-11-13T20:00:00+01:00" };
  const unconfirmed = { ...friday,id:"unconfirmed",status:"unconfirmed" };
  const saturday = { ...friday,id:"sat",startAt:"2026-11-14T23:00:00+01:00" };
  const sunday = { ...friday,id:"sun",startAt:"2026-11-15T22:00:00+01:00" };
  assert.ok(isNightlifeEvent(friday));
  assert.ok(!isNightlifeEvent(gallery));
  assert.ok(!isNightlifeEvent(unconfirmed));
  assert.equal(nightlifeKey(after), "2026-11-13");
  const results=nightlifeForDay([friday, after, gallery, unconfirmed, saturday, sunday], "2026-11-13");
  assert.deepEqual(results.map(x=>x.id),["friday","after"]);
  assert.deepEqual(nightlifeForDay([friday,saturday,sunday],"2026-11-14").map(x=>x.id),["sat"]);
  assert.deepEqual(nightlifeForDay([friday,saturday,sunday],"2026-11-15").map(x=>x.id),["sun"]);
});
