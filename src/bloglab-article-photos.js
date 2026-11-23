/*
 * Stable article-level image allocation for the public BlogLab magazine.
 * Keep a trustworthy, topic-appropriate article hero unless it is already used
 * by another published story. Replace generic/repeated/wrong-place heroes with
 * a genuinely distinct, credited, illustrative photograph. Never fabricate
 * an event image. If a topic bank runs out, leave the photo empty.
 */
import { displayPhotoForArticle as legacyPhoto, DISPLAY_PHOTOS } from "./bloglab-display-photos.js";
import { EVENT_PHOTO_BANK } from "./bloglab-event-photos.js";

const U = (id, slug, author, alt) => Object.freeze({
  src: `https://images.unsplash.com/${id}?auto=format&fit=crop&w=1280&q=82`,
  sourceUrl: `https://unsplash.com/photos/${slug}`,
  author, license: "Unsplash License", licenseUrl: "https://unsplash.com/license",
  alt, note: "Ilustrativna fotografija: ne prikazuje nujno kraja, datuma ali dogodka v članku."
});

const CYCLING = [
  U("photo-1602107275849-b117c6085652", "man-in-white-shirt-riding-on-black-mountain-bike-during-daytime-7x0u2thW6Gs", "Yury Kirillov", "Gorski kolesar pri Bovcu v Sloveniji"),
  U("photo-1775541028026-161ac7991587", "group-of-cyclists-racing-on-a-paved-road-YIIQ4GDep1M", "Ricardo IV Tamayo", "Skupina cestnih kolesarjev"),
  U("photo-1471506480208-91b3a4cc78be", "person-cycling-on-road-distance-with-mountain-during-daytime-VfUN94cUy4o", "Urban Vintage", "Kolesar na gorski cesti"),
  U("photo-1605050825077-289f85b6cf43", "men-riding-bicycle-on-road-during-daytime-iZJrOqEaPNI", "Munbaik Cycling Clothing", "Cestno kolesarjenje"),
  U("photo-1660888148084-ad2da4d979a7", "a-man-riding-a-bicycle-on-a-road-surrounded-by-trees-dgzaPk5IY58", "Markus Spiske", "Cestni kolesar na vzponu"),
  U("photo-1674642692100-0afe184d4052", "a-man-riding-a-bike-down-a-curvy-road-B-5AVSNmfow", "Alessandro Trovato", "Kolesar na gorskem prelazu"),
  U("photo-1766556578867-4b511ab7de4a", "cyclist-riding-on-a-winding-road-near-mountains-bdVcH9ENxTk", "Frank Rolando Romero", "Kolesar na ovinkasti gorski cesti"),
  U("photo-1760892471867-d50bb945c13d", "mountain-biker-with-bicycle-on-dirt-road-at-sunset-WnjgidvICuE", "Sunil Chandra Sharma", "Gorski kolesar ob sončnem zahodu"),
  U("photo-1615845522846-02f89af04c2e", "man-in-black-jacket-riding-bicycle-on-road-during-daytime-oro0KHgeQ_g", "Jack Delulio", "Cestna kolesarja"),
  U("photo-1695238070098-83d6775247a7", "a-man-riding-a-bike-down-a-road-next-to-a-forest-ypR86XLah9Y", "Krzysztof Kowalik", "Kolesar na gorski cesti"),
  DISPLAY_PHOTOS.cycling
];
const MOUNTAINS = [
  U("photo-1743188913205-c2e42e666856", "a-cabin-nestled-amidst-trees-and-mountains-h3U_zWWsI4U", "Loris Oberländer", "Koča pri Triglavskih jezerih, Julijske Alpe"),
  U("photo-1708552592289-350724a8e695", "a-lone-tree-on-a-grassy-hill-with-mountains-in-the-background-ZdlvjidyjyE", "Tomas Hudolin", "Gorska pokrajina Julijskih Alp"),
  U("photo-1772964161706-ee2b9e44718d", "a-road-leading-through-a-mountain-valley-slDU9sL3dK4", "viktor rejent", "Gorska dolina v Sloveniji"),
  DISPLAY_PHOTOS.hiking,
  DISPLAY_PHOTOS.bled,
  U("photo-1639775739665-30a8cff5b004", "a-small-island-in-the-middle-of-a-lake-surrounded-by-mountains-sBOE2ghrlBc", "Simon Hermans", "Blejsko jezero z gorami")
];
const WEATHER = [
  U("photo-1497163326116-446ff9cbfe51", "thunderstorm-clouds-on-skies-FVDPl2ddsp8", "SHTTEFAN", "Nevihtni oblaki"),
  U("photo-1668813832453-414dc50d2e3a", "a-field-with-lightning-striking-in-the-distance", "Raychel Sanner", "Strela nad pokrajino"),
  U("photo-1728781409032-91c66005e052", "a-black-and-white-photo-of-storm-clouds-DksmPnDDcp8", "Frederick Wallace", "Temni nevihtni oblaki"),
  U("photo-1642947746939-f49ca9096628", "a-lightning-storm-is-seen-over-a-city-at-night-NzxpGa8lAh0", "Ramiro Pianarosa", "Nočna nevihta")
];
const CULTURE = [
  DISPLAY_PHOTOS.castle, DISPLAY_PHOTOS.river, DISPLAY_PHOTOS.ljubljana,
  ...EVENT_PHOTO_BANK.gallery
];
const FOOD = [U("photo-1617307715850-c6965f2aead4", "cooked-food-on-blue-ceramic-plate-6EO9G_cOCi0", "Lottie Griffiths", "Pripravljena hrana na krožniku")];
const CRICKET = U("photo-1730739463889-34c7279277a9", "a-cricket-stadium-filled-with-lots-of-people-UvGtaCC1eVs", "Zoshua Colah", "Kriketni stadion v Indiji");
const TOURISM = [DISPLAY_PHOTOS.ljubljana, DISPLAY_PHOTOS.river, DISPLAY_PHOTOS.castle];

const BAD_SOURCE_HINTS = [
  { source: "frozen_lake_bled", title: /vrem|arso|neviht|turist|požarn|plohe/i },
  { source: "tustanj_castle", title: /brežišk|lendav/i },
  { source: "grad_fu", title: /tivoli|jakopič/i },
  { source: "bicycle_expedition", title: /india|knoxville|kranj/i },
  { source: "trail_in_slovenia_4", title: /celjsk|jezersk|kranjsko|madžar/i }
];
const badForTopic = (item) => {
  const source = decodeURIComponent(String(item?.heroImage?.sourceUrl || "").replace(/%(?![0-9A-F]{2})/gi,"%25")).toLowerCase();
  const title = String(item?.title || "");
  return BAD_SOURCE_HINTS.some(x => source.includes(x.source) && x.title.test(title));
};
const sourceKey = photo => String(photo?.sourceUrl || photo?.src || "")
  .toLowerCase().replace(/[?#].*$/, "").replace(/%20/g, "_").replace(/_\((?:cropped)\)/ig, "")
  .replace(/_\(cropped\)(?=\.)/ig, "").replace(/_cropped(?=\.)/ig, "");
const itemKey = item => String(item?.id || item?.title || "");
function category(item) {
  const text = [item?.title, item?.category].filter(Boolean).join(" ").toLowerCase();
  if (/cricket|india squad|world cup 2019/.test(text)) return "cricket";
  if (/vrem|neviht|arso|požarn|plohe|točo|toco/.test(text)) return "weather";
  if (/koles|bicikl|cycling|bike shop|biketopia|eurovelo/.test(text)) return "cycling";
  if (/planin|pohod|hiking|mountain|gore|triglav|via alpina|celjsk.{0,10}koča/.test(text)) return "mountains";
  if (/kulinar|ižina|recept|tradicij.{0,15}hrana/.test(text)) return "food";
  if (/muzej|dedišč|grad|lendav|tivoli|razstav|umetn/.test(text)) return "culture";
  if (/turiz|turist/.test(text)) return "tourism";
  return "culture";
}
function candidates(item) {
  switch (category(item)) {
    case "cycling": return CYCLING;
    case "mountains": return MOUNTAINS;
    case "weather": return WEATHER;
    case "culture": return CULTURE;
    case "food": return FOOD;
    case "cricket": return [CRICKET];
    default: return TOURISM;
  }
}
const allocationCache = new WeakMap();
export function uniqueArticlePhotos(allArticles = []) {
  if (allocationCache.has(allArticles)) return allocationCache.get(allArticles);
  const photos = new Map(), used = new Set();
  const ordered = [...allArticles].sort((a,b) => itemKey(a).localeCompare(itemKey(b)));
  // Preserve good unique article photos before picking any new illustrative substitutes.
  for (const article of ordered) {
    const photo = legacyPhoto(article);
    const key = sourceKey(photo);
    if (key && !used.has(key) && !badForTopic(article)) {
      photos.set(itemKey(article), photo);
      used.add(key);
    }
  }
  for (const article of ordered) {
    const id = itemKey(article);
    if (photos.has(id)) continue;
    const substitute = candidates(article).find(photo => photo && !used.has(sourceKey(photo)));
    if (substitute) {
      photos.set(id, substitute);
      used.add(sourceKey(substitute));
    } else {
      photos.set(id, null);
    }
  }
  allocationCache.set(allArticles, photos);
  return photos;
}
export function articlePhotoForItem(item = {}, allArticles = []) {
  if (!allArticles.length) return legacyPhoto(item);
  return uniqueArticlePhotos(allArticles).get(itemKey(item)) || null;
}
