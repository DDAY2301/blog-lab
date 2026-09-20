# Blog Lab

GitHub Pages različica strani Blog Lab.

## Lokalni zagon

```bash
npm ci
npm run dev
```

## Objavljanje strani

Vsaka sprememba na veji `main` sproži GitHub Actions in objavo na GitHub Pages.

Objavljeni začetni članki so v polju `starterArticles` v datoteki
`src/App.jsx`. Urednik v brskalniku dodatne članke shranjuje lokalno v
`localStorage`; ti članki niso skupni med napravami. Za trajno in skupno
objavo mora agent dodati članek v `starterArticles` ter spremembo poslati na
`main` ali prek pull requesta.

## Production Guardian

Blog Lab ima dodan produkcijski guardian sloj za health monitoring, deploy drift preverjanje, cross-browser login readiness, credential scan in varni autoupdate/self-heal tok.

Uporabni ukazi:

```bash
npm run guardian:check
npm run guardian:repair
npm run test:guardian
```

Glavne datoteke:

- `agents/production-guardian/guardian.py`
- `.github/workflows/production-guardian.yml`
- `.github/workflows/self-heal.yml`
- `public/guardian-manifest.json`
- `docs/production-guardian.md`

Guardian popravek ne gre neposredno v produkcijo brez preverjanj: spremembe se pripravijo v ločeni veji in kot Pull Request po testih, build-u, Worker testih in Wrangler dry-run preverjanju.

## Dovoljenja za agente

Vsak urednik potrebuje lasten GitHub račun, povezan s ChatGPT, in dovoljenje
`Write` za ta repozitorij. API-ključi in osebni žetoni ne sodijo v kodo.
