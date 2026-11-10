/**
 * Curated, genuine photography for BlogLab (never AI generated).
 * Wikimedia Commons file pages and licenses were manually reviewed on 2026-11-10.
 * Do not infer a particular event, performer, or date from an illustrative photo.
 * New photos must be matched by subject and carry verifiable license and author.
 */
const commons = (file) =>
  "https://commons.wikimedia.org/wiki/Special:FilePath/" +
  encodeURIComponent(file.replaceAll(" ", "_")) + "?width=1200";
const page = (file) =>
  "https://commons.wikimedia.org/wiki/File:" + encodeURIComponent(file.replaceAll(" ", "_"));

function photo(file, author, license, licenseUrl, subject, note) {
  return Object.freeze({
    src: commons(file),
    sourceUrl: page(file),
    author,
    license,
    licenseUrl,
    alt: subject,
    note: note || "Ilustrativna arhivska fotografija; ne prikazuje nujno opisanega dogodka."
  });
}

export const PHOTOS = Object.freeze({
  metropolis: photo(
    "Ljubljana Night (52002991689).jpg", "Radek Kucharski", "CC BY 2.0",
    "https://creativecommons.org/licenses/by/2.0/",
    "Ljubljana ponoči", "Arhivska fotografija Ljubljane ponoči; ni posnetek posameznega dogodka."
  ),
  metelkova: photo(
    "Metelkova Mesto, Ljubljana - Slovenia (9039267815).jpg",
    "deambulare piano in posti con poca luce", "CC BY 2.0",
    "https://creativecommons.org/licenses/by/2.0/",
    "Metelkova mesto v Ljubljani", "Arhivska fotografija Metelkove; ne prikazuje aktualnega večera."
  ),
  castle: photo(
    "Ljubljana Castle (52931167527).jpg", "George M. Groutas", "CC BY 2.0",
    "https://creativecommons.org/licenses/by/2.0/",
    "Ljubljanski grad", "Fotografija Ljubljanskega gradu; ni posnetek posameznega dogodka."
  ),
  cycling: photo(
    "Commuting by bicycle.jpg", "Petar Milošević", "CC BY-SA 4.0",
    "https://creativecommons.org/licenses/by-sa/4.0/",
    "Kolesarka v Tivolskem podhodu v Ljubljani"
  ),
  mountains: photo(
    "Triglav mountain at sunset.jpg", "Dreamy Pixel", "CC BY 4.0",
    "https://creativecommons.org/licenses/by/4.0/",
    "Triglav v večerni svetlobi"
  )
});

/** No photograph is preferable to a photo of a wrong named town or event. */
export function photoForArticle(item = {}) {
  // Publisher-provided verified Commons images take precedence over the small
  // curated library, provided that the source/credit/license are complete.
  const hero = item.heroImage;
  if (hero && typeof hero === "object" &&
      /^https:\/\/commons\.wikimedia\.org\/wiki\/File:/i.test(hero.sourceUrl || "") &&
      /^https:\/\//.test(hero.url || "") &&
      /CC.?BY|CC0|public domain/i.test(hero.caption || "")) {
    return {
      src: hero.url, sourceUrl: hero.sourceUrl,
      author: hero.caption, license: "", licenseUrl: "",
      alt: hero.alt || item.title || "Fotografija", note: "Foto: navedeni vir Wikimedia Commons."
    };
  }
  const text = [item.category, item.title, item.excerpt].filter(Boolean).join(" ").toLocaleLowerCase("sl");
  if (/metelkov|gala hala|channel zero|gromka|menza pri koritu|jalla jalla|tiffany|monokel/.test(text)) return PHOTOS.metelkova;
  if (/ljubljansk.{0,8}grad|ljubljana castle/.test(text)) return PHOTOS.castle;
  if (/koles|bicikl|cycling|kolo|bicycle/.test(text)) return PHOTOS.cycling;
  if (/triglav|gore|gorsk|planin|pohod|alpe|alpin|mountain|hiking|trail/.test(text)) return PHOTOS.mountains;
  if (/k4|publika|klub|nočn|nightlife|koncert|rave|techno|dj\b|elektronsk|glasba/.test(text) &&
      /ljubljan|metelkov|k4|publika|kultura|zabava|klub/.test(text)) return PHOTOS.metropolis;
  if (/ljubljan/.test(text)) return PHOTOS.metropolis;
  return null;
}

export function photoForEvent(item = {}) {
  const text = [item.title, item.type, item.place, item.source].filter(Boolean).join(" ").toLocaleLowerCase("sl");
  if (/metelkov|gala hala|channel zero|gromka|menza pri koritu|jalla jalla|tiffany|monokel/.test(text)) return PHOTOS.metelkova;
  if (/ljubljansk.{0,8}grad|ljubljana castle/.test(text)) return PHOTOS.castle;
  if (/koles|cycling|bicycle/.test(text)) return PHOTOS.cycling;
  if (/planin|pohod|triglav|trail|mountain/.test(text)) return PHOTOS.mountains;
  if (/ljubljan|k4|publika/.test(text) && /klub|concert|koncert|dj\b|rave|house|techno|glasba|party|music|festiv/.test(text)) return PHOTOS.metropolis;
  return null;
}

export function photoForRubric(rubric) {
  return ({
    kultura: PHOTOS.castle,
    zabava: PHOTOS.metropolis,
    sport: PHOTOS.cycling,
    weekend: PHOTOS.metelkova,
    novice: PHOTOS.metropolis
  })[rubric] || PHOTOS.metropolis;
}
