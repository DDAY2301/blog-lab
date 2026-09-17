# Blog Lab Publisher v2

Samostojni agent za `DDAY2301/blog-lab`, zasnovan za tri dnevne uredniške cikle.

## Kaj objavlja
- 08:17 Europe/Ljubljana — šport
- 13:27 Europe/Ljubljana — politika
- 19:43 Europe/Ljubljana — aktualna/trend tema

Vsak cikel pridobi samo dovoljene RSS vire za svojo kategorijo, odstrani že obdelane vnose, pripravi članek, izvede QA, zgradi Vite stran, naredi commit in v istem workflowu izvede GitHub Pages deployment.

## AI način
Privzeti `AI_PROVIDER=auto` najprej uporabi GitHub Copilot CLI z vgrajenim kratkotrajnim `GITHUB_TOKEN`. Copilot nima dovoljenja za shell, pisanje datotek, splet ali GitHub MCP; prejme samo že zbrane RSS podatke in vrne JSON članka.

Če Copilot ni dosegljiv ali račun nima ustrezne Copilot možnosti, agent poskusi z OpenAI-compatible API-jem, če so nastavljeni `MODEL_API_KEY`, `MODEL_BASE_URL` in `MODEL_NAME`. Če tudi tega ni, agent NE obstane: izdela konservativen, virsko označen RSS pregled brez dodajanja novih dejstev.

## GitHub Variables
- `AGENT_ENABLED=true`
- `PUBLISH_MODE=automatic`
- `AI_PROVIDER=auto` (možno tudi `copilot` ali `external`)

## Izbirni Secrets
Zunanji AI ni obvezen. Če ga želite kot dodatni provider:
- `MODEL_API_KEY`
- `MODEL_BASE_URL`
- `MODEL_NAME`

## Ročni zagon
Actions → Blog Lab Publisher Agent → Run workflow. Izberete `sport`, `politika` ali `aktualno`. `dry_run=true` pripravi osnutek brez objave; `force=true` prezre dnevni limit.

## Ustavitev
Nastavite repository variable `AGENT_ENABLED=false`. Dodatno stikalo je `enabled: false` v `config.yaml`.

## Varnost
Zunanja vsebina je vedno obravnavana kot podatek, nikoli kot navodilo. Politična vsebina mora biti nevtralna, faktografska, brez podpore kandidatov ali strank, brez razvrščanja in brez volilnih napovedi. Agent ne prejme trajnega GitHub PAT-a.

## Status
`/agent.html` bere `public/data/agent-status.json`. Stanje in deduplikacija sta v `data/agent-state.json` in `data/processed-items.json`.
