import { keyForLjubljana, eventIsFuture, eventHref } from "./bloglab-taxonomy.js";

// Venue-first nightlife curation. Only records previously checked and marked
// confirmed by the events pipeline may appear; never fabricate a lineup.
const VENUES = /metelkov|klub k4|\bk4\b|gala hala|channel zero|gromka|publika|menza pri koritu|jalla jalla|tiffany|monokel|cvetličarna|kino šiška|cirkus klub/i;
const PROGRAMME = /\b(dj|rave|party|dance|club|night|live|gig|house|techno|dnb|drum|bass|jazz|concert|music)\b|koncert|glasb|zabav|klub|elektron|žur|ples|after|festival|nastop|synth/i;
const EXCLUDED = /razstav|muzej|delavnica|konferenc|predavanje|exhibition|workshop|seminar/i;

export function isNightlifeEvent(event) {
  if (!event || event.status !== "confirmed" || !event.startAt ||
      !/^https:\/\//.test(event.url || "")) return false;
  const venue = [event.place, event.source].filter(Boolean).join(" ");
  const programme = [event.title, event.type].filter(Boolean).join(" ");
  return VENUES.test(venue + " " + programme) &&
    PROGRAMME.test(venue + " " + programme) && !EXCLUDED.test(programme);
}

// A Saturday 02:00 after-party belongs to Friday night. Use Slovenia local time,
// not UTC calendar day, when assigning nightlife to its Friday/Saturday slot.
export function nightlifeKey(event) {
  const start = new Date(event?.startAt);
  if (!Number.isFinite(start.getTime())) return "";
  return keyForLjubljana(new Date(start.getTime() - 6 * 60 * 60 * 1000));
}

export function nightlifeForDay(events, dateKey) {
  return (Array.isArray(events) ? events : []).filter(isNightlifeEvent)
    .filter((event) => nightlifeKey(event) === dateKey)
    .sort((a, b) => new Date(a.startAt) - new Date(b.startAt));
}

export function pastNightlife(events, today) {
  return (Array.isArray(events) ? events : []).filter(isNightlifeEvent)
    .filter((event) => !eventIsFuture(event, today))
    .filter((event) => {
      const key = nightlifeKey(event);
      if (!key) return false;
      return [5, 6, 0].includes(new Date(key + "T12:00:00Z").getUTCDay());
    }).sort((a, b) => new Date(b.startAt) - new Date(a.startAt));
}

// Keep the actual event links; these navigate to internal detail pages with
// an outbound official source. No fake ticket links.
export const nightlifeEventLink = eventHref;
