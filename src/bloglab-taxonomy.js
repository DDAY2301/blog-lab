// Public editorial taxonomy. The source category is kept intact in JSON;
// this mapping only determines which portal section displays each story.
export const RUBRICS = [
  { slug: "kultura", name: "Kultura", image: "/art/painted/dediscina.jpg", description: "Razstave, dediščina, gledališče, umetnost in zgodbe ustvarjalcev." },
  { slug: "zabava", name: "Zabava", image: "/art/painted/gourmet.jpg", description: "Koncerti, festivali, kulinarika, druženje in prosti čas." },
  { slug: "sport", name: "Šport", image: "/art/painted/kolesarstvo.jpg", description: "Kolesarstvo, tek, pohodništvo, gore, aktivnosti v naravi in šport." },
  { slug: "weekend", name: "Weekend", image: "/art/painted/sezonsko.jpg", description: "Ideje za petek, soboto in nedeljo ter dogodki za konec tedna." },
  { slug: "novice", name: "Blog / Novice", image: "/art/painted/vodniki.jpg", description: "Vse objavljene zgodbe, vodniki in novice v enem urejenem arhivu." }
];

const sport = /koles|gore|gors|mountain|trail|planin|pohod|hiking|trek|tek\b|tekač|running|maraton|gibanj|rekreacij|outdoor|sport|šport|smuč|sneg|plezan|alpiniz|nogomet|košark|odboj|tenis|plav|kajo|rafting|potap|fitnes|yoga|joga|bicycle|cycling|football|basketball|race|olimp|dirk|poti\s+eurovelo|aktivn.*narav/i;
const culture = /kultur|dedišč|heritage|muzej|museum|galer|razstav|exhibit|literatur|knjiž|umetn|art\b|gledali|theatre|opera|balet|ballet|arhitekt|zgodovin|tradici|grad\b|castle|film|kino|cinema|fotograf|poez|poetry/i;
const entertainment = /zabav|glasb|music|koncert|concert|festival|klub|club|party|komed|comedy|nočn|night|gourmet|kulinar|hrana|food|restavra|okus|kulinarič|tržnic|sezonsk|turist|travel|potovanj|izlet|dogodek|weekend|vikend|oddih|cirkus/i;

export function rubricForArticle(article = {}) {
  const text = [article.category, article.title, article.excerpt].filter(Boolean).join(" ");
  if (sport.test(text)) return "sport";
  if (culture.test(text)) return "kultura";
  if (entertainment.test(text)) return "zabava";
  return "kultura";
}

export function rubricForEvent(item = {}) {
  const type = [item.type, item.title].filter(Boolean).join(" ");
  if (sport.test(type)) return "sport";
  if (culture.test(type)) return "kultura";
  if (entertainment.test(type)) return "zabava";
  return "kultura";
}

export function rubricInfo(slug) {
  return RUBRICS.find((item) => item.slug === slug) || RUBRICS[0];
}
export function articleHref(item) {
  return "/?clanek=" + encodeURIComponent(item.id);
}
export function eventHref(item) {
  return "/?dogodek=" + encodeURIComponent(item.id);
}
export function rubricHref(slug, period = "vse") {
  return "/?rubrika=" + encodeURIComponent(slug) + (period === "vse" ? "" : "&obdobje=" + encodeURIComponent(period));
}
export function dateHref(key) {
  return "/?dogodki=" + encodeURIComponent(key);
}
export function keyForLjubljana(value) {
  // Missing endAt must not become 1970-01-01 (new Date(null) is the Unix epoch).
  if (value === null || value === undefined || value === "") return "";
  const d = new Date(value);
  if (!Number.isFinite(d.getTime())) return "";
  const parts = Object.fromEntries(new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/Ljubljana", year: "numeric", month: "2-digit", day: "2-digit"
  }).formatToParts(d).filter((p) => p.type !== "literal").map((p) => [p.type, p.value]));
  return parts.year + "-" + parts.month + "-" + parts.day;
}
export function addDays(key, count) {
  const d = new Date(key + "T12:00:00Z");
  if (Number.isNaN(d.getTime())) return "";
  d.setUTCDate(d.getUTCDate() + count);
  return d.toISOString().slice(0, 10);
}
export function niceDate(key, opts = { day: "numeric", month: "long", year: "numeric" }) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(key)) return "";
  return new Intl.DateTimeFormat("sl-SI", { timeZone: "UTC", ...opts }).format(new Date(key + "T12:00:00Z"));
}
export function eventActiveOn(item, key) {
  const start = keyForLjubljana(item.startAt);
  if (!start || !key) return false;
  const end = keyForLjubljana(item.endAt) || start;
  return start <= key && key <= end;
}
export function eventIsFuture(item, today) {
  return (keyForLjubljana(item.endAt) || keyForLjubljana(item.startAt)) >= today;
}
export function weekendDates(today) {
  const day = new Date(today + "T12:00:00Z").getUTCDay();
  // On Saturday/Sunday, keep the current weekend; otherwise next Friday.
  const jump = day === 6 ? -1 : day === 0 ? -2 : (5 - day + 7) % 7;
  const friday = addDays(today, jump);
  return [friday, addDays(friday, 1), addDays(friday, 2)];
}
export function eventHour(item, key) {
  if (!item.startAt) return "Po programu";
  if (key && keyForLjubljana(item.startAt) !== key) return "Večdnevni dogodek";
  const date = new Date(item.startAt);
  return Number.isFinite(date.getTime())
    ? new Intl.DateTimeFormat("sl-SI", { timeZone: "Europe/Ljubljana", hour: "2-digit", minute: "2-digit" }).format(date)
    : "Po programu";
}
export function trustedEvent(item) {
  return Boolean(item && item.id && item.title && item.startAt && item.status === "confirmed" &&
    typeof item.url === "string" && /^https:\/\//.test(item.url));
}
