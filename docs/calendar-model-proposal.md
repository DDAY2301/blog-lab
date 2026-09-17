# Calendar model proposal

Status: review draft — not connected to the production UI.

## Why this is needed

The current application stores only long-form posts in `starterArticles`. It has no event entity, calendar routes, rolling date windows, event status lifecycle, or faceted filtering. Adding daily listings as articles would create thin and expiring pages, duplicate search intent, and clutter the feed.

## Minimal safe architecture

1. Keep `starterArticles` exclusively for durable editorial content.
2. Add event records in `src/data/events.js`.
3. Add pure selectors in `src/lib/eventSelectors.js`:
   - active events;
   - today in Europe/Ljubljana;
   - this weekend;
   - next 14 calendar days;
   - free;
   - nightlife;
   - family;
   - English-friendly;
   - starting within three hours.
4. Add one `CalendarPage` with stable views controlled by query parameters or stable routes. Do not generate a separate post per daily run.
5. Keep expired records out of active views. Retain them only if an archive is intentionally implemented.
6. Display `lastCheckedAt` and always link to the official source.
7. Only publish a record when `status === "confirmed"`. Show postponed, cancelled and sold-out states clearly.
8. Store unknown values as `null`; never infer price, language or accessibility.
9. Create a stable event identity from organizer/source ID when available, otherwise from normalized title + start time + venue.
10. On every import, merge by `eventId`, update `lastCheckedAt`, and record changes rather than creating duplicates.

## Proposed event schema

```js
{
  eventId: "stable-string",
  title: "Official title",
  summary: "One to three original sentences.",
  category: "music | theatre | exhibition | food | market | family | sport | nightlife | other",
  startAt: "ISO 8601 with Europe/Ljubljana offset",
  endAt: "ISO 8601 or null",
  timezone: "Europe/Ljubljana",
  venue: { name: "", address: "", city: "Ljubljana", region: "Central Slovenia" },
  price: { amount: null, currency: "EUR", label: null, free: null },
  ticketUrl: null,
  officialUrl: "https://...",
  sourceName: "",
  languages: [],
  touristFriendly: true,
  familyFriendly: null,
  accessibility: null,
  indoorOutdoor: "indoor | outdoor | mixed | unknown",
  status: "confirmed | postponed | cancelled | sold_out | unconfirmed",
  lastCheckedAt: "ISO 8601"
}
```

## Required implementation before production publishing

- Build the data module and selectors.
- Add stable calendar navigation without replacing the existing article views.
- Add filter controls and empty/error states.
- Add tests for Ljubljana-local date boundaries, daylight-saving time, weekend calculations and duplicate merging.
- Confirm that old `localStorage` article data remains intact.
- Run `npm run build`.
- Deploy to a preview or review branch and visually verify desktop/mobile rendering.
- Only then merge to `main` and start automated event updates.

## Research notes for 17–30 September 2026

The companion file `src/data/events.draft.js` contains verified candidates from multiple official sources. Fields not explicitly published by the source remain `null`. Outdoor plans should be rechecked against the live forecast and organizer status within 24 hours.

Sources checked on 17 September 2026:
- Ljubljana Tourism events calendar
- Ljubljana Castle events
- Cankarjev dom programme
- SNG Opera in balet Ljubljana
- National Gallery of Slovenia
- Kino Šiška event archive
- Metelkova mesto programme
