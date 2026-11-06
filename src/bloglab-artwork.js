// Stable painterly variety on smaller editorial cards.
// Keep existing category paintings as hero/large images, so visual identity stays intact.
export const LJUBLJANA_PAINTINGS = Object.freeze([
  "/art/painted/ljubljana-grad.png",
  "/art/painted/ljubljana-tromostovje.png",
  "/art/painted/ljubljana-zmajski-most.png",
  "/art/painted/ljubljana-ljubljanica.png"
]);

export function stableArtworkIndex(value) {
  const seed = String(value ?? "bloglab");
  let hash = 2166136261;
  for (let i = 0; i < seed.length; i++) {
    hash ^= seed.charCodeAt(i);
    hash = Math.imul(hash, 16777619) >>> 0;
  }
  return hash % LJUBLJANA_PAINTINGS.length;
}

// Editorial illustrations, not literal photographs of the event/location.
// Outdoor/sport topics continue using sport paintings; bigger banners do not change.
export function magazineCardArtwork(item, category, fallback) {
  if (category === "sport") return fallback;
  const seed = item?.id || item?.title || "";
  if (!seed) return fallback;
  // ~75% Ljubljana city views; keep occasional original category paintings.
  if (stableArtworkIndex("original:" + seed) === 0) return fallback;
  return LJUBLJANA_PAINTINGS[stableArtworkIndex(seed)];
}
