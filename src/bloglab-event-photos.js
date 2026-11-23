/**
 * Licensed, genuinely different illustrative photographs for public events.
 *
 * Every photo below has a confirmed free-to-use Unsplash photo page, an author,
 * a stable CDN identity and an explicit disclaimer. Never pretend these
 * photographs show the advertised Slovenian event or venue.
 *
 * Assign by EVENT ID inside a TOPIC bucket, not by category alone, and never
 * recycle an image if a new feed has more events than the vetted bank.
 */
const U = (id, slug, author, alt) => Object.freeze({
  src: `https://images.unsplash.com/${id}?auto=format&fit=crop&w=1280&q=82`,
  sourceUrl: `https://unsplash.com/photos/${slug}`,
  author,
  license: "Unsplash License",
  licenseUrl: "https://unsplash.com/license",
  alt,
  note: "Arhivska/ilustrativna fotografija, ne prikazuje napovedanega dogodka."
});

const BANK = Object.freeze({
  music: Object.freeze([
    U("photo-1778011390422-a4d4bd8936a7", "crowd-with-hands-up-at-a-bright-concert-stage-z0R4XB25ozI", "Jonathan Ikemura", "Občinstvo na koncertu"),
    U("photo-1666722658862-682f3248bdc0", "a-crowd-of-people-in-a-dark-room-with-a-stage-and-lights-ZC8ZNgOEMOU", "Fabian Bächli", "Občinstvo v temni dvorani"),
    U("photo-1759719440818-98681ed4c6b8", "crowd-at-a-concert-with-stage-lights-and-disco-ball-3Xbl9Rgf6hY", "Brooke Balentine", "Disco krogla nad koncertnim občinstvom"),
    U("photo-1768054182948-9c05cecb8ef2", "dj-performing-for-a-crowd-with-stage-lights-VUgiRWaoLbc", "Nicolás Flor", "DJ pred občinstvom"),
    U("photo-1758550445758-165aeab5b26e", "crowd-enjoying-a-concert-with-blue-stage-lights-ubwn8GI9-2o", "Marcel Strauß", "Koncertno občinstvo v modri svetlobi"),
    U("photo-1768053917161-34fc3365c9b2", "concert-crowd-illuminated-by-bright-stage-lights-SoxF20A3YZc", "Nicolás Flor", "Koncertne luči v vijoličnih tonih"),
    U("photo-1657208431551-cbf415b8ef26", "a-crowd-of-people-at-a-concert-QOajY0MNp8Y", "Scarlett Alt", "Barvna svetloba na koncertnem odru"),
    U("photo-1722332998970-f2335db8ab6d", "a-crowd-of-people-watching-a-concert-on-stage-o7wPTlBgQ98", "Ben Wicks", "Občinstvo na plesnem koncertu"),
    U("photo-1547210841-2ceb0c5f0679", "person-using-dj-mixer-CfBlMP12zT8", "Krys Amon", "DJ mešalna miza v klubu"),
    U("photo-1755508159006-d93494f2ee4c", "close-up-of-a-dj-mixer-with-many-knobs-ICpXcmAwOG8", "Alexander", "Detajl DJ mešalne mize"),
    U("photo-1572575156811-2ae050d748d8", "person-using-dj-mixer-LmGLU3eNwCg", "Zorik D", "DJ oprema med nastopom"),
    U("photo-1762505190706-21a8367be3a1", "dj-mixing-music-on-a-console-bNKfIdwsQbw", "Shoham Avisrur", "DJ za glasbeno mešalno mizo"),
    U("photo-1780292837660-20b1de9bbdac", "person-with-long-hair-headbanging-vigorously-black-and-white-TbRVusWz87w", "Diego Apolo", "Občinstvo na alternativnem koncertu"),
    U("photo-1772187727779-fdcdde1b307d", "dj-mixing-music-on-turntables-at-a-party-kYQtV-Cl66U", "foto DIAL", "DJ med nastopom v klubu"),
    U("photo-1686605894626-3f13b282d3b5", "two-people-standing-in-front-of-a-fountain-at-night-vxzqv57hNyc", "Miguel Alcântara", "Ljubljana ponoči")
  ]),
  stage: Object.freeze([
    U("photo-1713514116766-d9be318edaf8", "an-empty-theater-with-red-curtains-and-seats-25OeoEKoNP8", "Richard Heinen", "Gledališki oder z rdečo zaveso"),
    U("photo-1578920570481-305090930f1d", "a-group-of-people-standing-on-top-of-a-stage-t0WFxtrUgSc", "Hulki Okan Tabak", "Plesna predstava na odru"),
    U("photo-1578920567217-494c895e1ece", "a-couple-of-people-that-are-dancing-on-a-stage-Z3rRKj4e6FE", "Hulki Okan Tabak", "Plesalka med odrsko predstavo"),
    U("photo-1578920568769-3c1b145bc9ea", "a-blurry-photo-of-a-man-and-a-woman-dancing-qlBjCgBAYAU", "Hulki Okan Tabak", "Gibanje med plesno predstavo"),
    U("photo-1773487997562-96a3efdc1b6e", "two-actors-rehearsing-a-play-on-stage-QoI8OnIgQzI", "Metin Ozer", "Igralca med odrsko vajo")
  ]),
  gallery: Object.freeze([
    U("photo-1770747717041-069127dad7d8", "people-walk-through-a-modern-art-gallery-exhibition-Yxq8sdl20Hs", "Evgeniy Bezkorovayniy", "Obiskovalci sodobne galerije"),
    U("photo-1769117618903-0d0ad84f4db3", "three-people-stand-in-an-art-gallery-exhibition-yjZSIfCnxkI", "Helena Lopes", "Obiskovalci galerijske razstave"),
    U("photo-1773761541805-24e73c6a7bd4", "museum-exhibit-with-screens-displaying-various-media-cBtqEiAe7nQ", "Jimmy Liu", "Multimedijska muzejska razstava")
  ]),
  books: Object.freeze([
    U("photo-1764728671460-34931d8261f5", "a-library-aisle-with-bookshelves-and-sunlight-through-window-xmeRBPunJR8", "Jason Leung", "Knjižne police v knjižnici")
  ]),
  food: Object.freeze([
    U("photo-1764397514727-32cbff5e5f9b", "chef-garnishes-grilled-octopus-with-greens-and-lemon-5umII9sO79s", "Tomi Saputra", "Kulinarično ustvarjanje in serviranje hrane"),
    U("photo-1686605895479-4fe62587d804", "a-restaurant-at-night-with-lights-on-the-windows-zSCbmDeDPTA", "Miguel Alcântara", "Gostinska ulica v Ljubljani")
  ])
});

export function eventPhotoKind(item = {}) {
  const text = [item.type, item.title].filter(Boolean).join(" ").toLowerCase();
  if (/exhibition|installation|mapping|razstav/.test(text)) return "gallery";
  if (/literar|kosovel|knjig/.test(text)) return "books";
  if (/theatre|theater|ballet|tragedy|drama|comedy|documentary solo|gledali/.test(text)) return "stage";
  if (/gourmet|culinary|omakase|food and drink|gastronom/.test(text)) return "food";
  return "music";
}

function eventKey(item = {}) {
  return String(item.id || [item.title, item.startAt].join("|"));
}

/**
 * Deterministic bijective assignment within a topic:
 * order by stable ID, not current date/filter/view.
 * Changing order/filters does not repeat the same photo on the page.
 */
export function eventPhotoForItem(item = {}, allEvents = []) {
  const key = eventKey(item);
  const category = eventPhotoKind(item);
  const pool = BANK[category] || [];
  const peers = (Array.isArray(allEvents) && allEvents.length ? allEvents : [item])
    .filter(e => eventPhotoKind(e) === category)
    .slice()
    .sort((a,b) => eventKey(a).localeCompare(eventKey(b)));
  const index = peers.findIndex(e => eventKey(e) === key);
  // If a later feed contains more events than verified photos, prefer an honest
  // photo-free card to a repeated or unrelated image.
  return index < 0 ? null : (pool[index] || null);
}

export const EVENT_PHOTO_BANK = BANK;
