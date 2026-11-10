/**
 * BlogLab's photo-first public UI uses a hand-curated set of actual Unsplash photos.
 * Individual entries are editorial illustrations only, never photos of a listed event.
 * Sources were checked as free (not Unsplash+) on 2026-11-10.
 * Permanent Pixabay CDN hotlinking is prohibited; use locally hosted Pixabay files only.
 */
const U = (id, slug, author, alt, note, width = 1280) => Object.freeze({
  src: `https://images.unsplash.com/${id}?auto=format&fit=crop&w=${width}&q=82`,
  sourceUrl: `https://unsplash.com/photos/${slug}`,
  author,
  license: "Unsplash License",
  licenseUrl: "https://unsplash.com/license",
  alt,
  note: note || "Arhivska oziroma ilustrativna fotografija; ne prikazuje nujno opisanega dogodka."
});

export const DISPLAY_PHOTOS = Object.freeze({
  ljubljana: U("photo-1612174987768-a7c9411ce30b", "aerial-view-of-city-buildings-during-daytime-tQkSI8izWtE", "detait", "Ljubljana, pogled iz zraka na staro mestno jedro", "Fotografija Ljubljane, ne konkretnega dogodka.", 1920),
  river: U("photo-1643413458645-54744c7bccf2", "a-building-sitting-next-to-a-body-of-water-SVEN1hUfECE", "Matevž Krajnik", "Ljubljanica in staro mestno jedro Ljubljane"),
  castle: U("photo-1773658088032-87e28148ea1b", "ljubljana-castle-overlooks-a-city-with-autumn-trees-wwKLeuAmwtM", "ALEKO KEZEVADZE", "Ljubljanski grad in mestna panorama"),
  nightlife: U("photo-1686605894626-3f13b282d3b5", "two-people-standing-in-front-of-a-fountain-at-night-vxzqv57hNyc", "Miguel Alcântara", "Ljubljana ponoči, urbana ulična scena"),
  cafe: U("photo-1686605895479-4fe62587d804", "a-restaurant-at-night-with-lights-on-the-windows-zSCbmDeDPTA", "Miguel Alcântara", "Nočna gostinska ulica v Ljubljani"),
  music: U("photo-1778011390422-a4d4bd8936a7", "crowd-with-hands-up-at-a-bright-concert-stage-z0R4XB25ozI", "Jonathan Ikemura", "Koncertno občinstvo, generična ilustrativna fotografija", "Generična koncertna fotografija, ki ni posnetek opisanega dogodka."),
  cycling: U("photo-1669372701525-06dde0779ba6", "a-person-riding-a-bike-on-a-trail-in-the-woods-BsiX9Ap30mY", "Tadeja Pavšič", "Gorsko kolesarjenje na Golovcu v Ljubljani"),
  hiking: U("photo-1666083543472-bc2aabc51eda", "a-person-hiking-on-a-trail-in-front-of-a-large-rock-lkHdZYgxTNE", "Tadeja Pavšič", "Pohodništvo na Slemenovi špici"),
  bled: U("photo-1639775739665-30a8cff5b004", "a-small-island-in-the-middle-of-a-lake-surrounded-by-mountains-sBOE2ghrlBc", "Simon Hermans", "Blejsko jezero in otok")
});

function keywords(item) {
  return [item?.title, item?.excerpt, item?.description, item?.category, item?.type, item?.place, item?.source]
    .filter(Boolean).join(" ").toLocaleLowerCase("sl");
}

export function displayPhotoForArticle(item = {}) {
  const text = keywords(item);
  if (/koles|bicycle|cycling|bicikl|gorsko kolo|bike/.test(text)) return DISPLAY_PHOTOS.cycling;
  if (/pohod|planin|triglav|alp|gorsk|narav|hiking|mountain|trail|hrib/.test(text)) return DISPLAY_PHOTOS.hiking;
  if (/bled|jezer|bohinj/.test(text)) return DISPLAY_PHOTOS.bled;
  if (/klub|glasb|koncert|dj\b|rave|techno|party|festival|nastop/.test(text)) return DISPLAY_PHOTOS.music;
  if (/gostin|restavracij|kulinar|hrana|pijač|vinar|kuhinj/.test(text)) return DISPLAY_PHOTOS.cafe;
  if (/nočn|nightlife|zabav|metelkov|k4\b/.test(text)) return DISPLAY_PHOTOS.nightlife;
  if (/grad|muzej|dedišč|razstav|zgodovin|arhitektur|kultur/.test(text)) return DISPLAY_PHOTOS.castle;
  if (/ljubljan|reka|mest|urban/.test(text)) return DISPLAY_PHOTOS.river;
  // A real, neutral Slovenian landscape with explicit illustrative credit avoids grey placeholders.
  return DISPLAY_PHOTOS.ljubljana;
}
export function displayPhotoForEvent(item = {}) {
  const text = keywords(item);
  if (/koles|bike|cycling|bicikl/.test(text)) return DISPLAY_PHOTOS.cycling;
  if (/pohod|planin|triglav|alp|gor|narav|hiking|mountain/.test(text)) return DISPLAY_PHOTOS.hiking;
  if (/glasb|koncert|dj\b|rave|techno|party|festival|nastop|glasba|rock|live music/.test(text)) return DISPLAY_PHOTOS.music;
  if (/metelkov|klub k4|nightlife|nočn|diskot|klub/.test(text)) return DISPLAY_PHOTOS.nightlife;
  if (/gostin|kulinar|hrana|vino|pijač|degustacij/.test(text)) return DISPLAY_PHOTOS.cafe;
  if (/gledališč|muzej|razstav|kultur|arhitektur|knjižn/.test(text)) return DISPLAY_PHOTOS.castle;
  return DISPLAY_PHOTOS.river;
}
export function displayPhotoForRubric(rubric = "") {
  return ({
    kultura: DISPLAY_PHOTOS.castle,
    zabava: DISPLAY_PHOTOS.music,
    sport: DISPLAY_PHOTOS.cycling,
    weekend: DISPLAY_PHOTOS.nightlife,
    novice: DISPLAY_PHOTOS.river
  })[rubric] || DISPLAY_PHOTOS.ljubljana;
}
