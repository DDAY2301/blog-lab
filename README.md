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

## Dovoljenja za agente

Vsak urednik potrebuje lasten GitHub račun, povezan s ChatGPT, in dovoljenje
`Write` za ta repozitorij. API-ključi in osebni žetoni ne sodijo v kodo.
