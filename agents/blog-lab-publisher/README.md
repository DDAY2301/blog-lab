# Blog Lab Publisher

Samostojni scheduled agent za repozitorij `DDAY2301/blog-lab`.

## Arhitektura
GitHub Actions → Python agent → RSS/Atom → AI provider → QA → `src/App.jsx` → state JSON → commit → obstoječi Pages workflow.

Agent se ne izvaja neprekinjeno. GitHub Actions ga prebudi ob 08:17, 13:27 in 19:43 po `Europe/Ljubljana`. Ročni zagon podpira `dry_run` in `force`.

## GitHub Variables
- `AGENT_ENABLED=true`
- `PUBLISH_MODE=automatic|draft|review`

## GitHub Secrets
- `MODEL_API_KEY`
- `MODEL_BASE_URL`
- `MODEL_NAME`

Če ključi manjkajo, agent varno izvede tehnični cikel in zaključi brez lažne objave.

## Ustavitev
Repository → Settings → Secrets and variables → Actions → Variables → `AGENT_ENABLED=false`. Lahko tudi nastavite `enabled: false` v `config.yaml`.

## Diagnostika
Status je v `public/data/agent-status.json`, napake QA pa v `logs/`. Nadzorna stran: `/agent.html`.

## Omejitve
Scheduled workflow mora biti na default veji, da se samodejno izvaja. GitHub lahko scheduled workflow v javnem neaktivnem repozitoriju po daljšem obdobju izklopi. Zunanji AI in RSS viri imajo lastne kvote/omejitve.
