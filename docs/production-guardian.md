# Blog Lab Production Guardian

Production Guardian je varni autoupdate/self-heal sloj za obstoječi Blog Lab produkt. Ne zamenja obstoječega publisherja, operator terminala ali Cloudflare Workerja; doda nadzor, diagnostiko, varno popravljanje in validiran PR tok okoli sistema.

## Kaj varuje

- javno GitHub Pages stran: `https://dday2301.github.io/blog-lab/`
- zasebni terminal: `https://blog-lab.dan-grmusa.workers.dev/`
- Cloudflare Worker `/health`
- cross-browser login in auth self-test
- terminal command-understanding/write-check sistem
- GitHub Actions tokove za publisher, terminal, health, smoke, E2E in self-heal
- očitne credential/token napake v tracked datotekah
- deploy drift med source kodo Workerja in produkcijskim Workerjem

## Komponente

| Komponenta | Namen |
|---|---|
| `agents/production-guardian/guardian.py` | Lokalni in CI guardian engine za health, manifest in deterministični repair. |
| `.github/workflows/production-guardian.yml` | Urni nadzor, ročni zagon in auto-update PR za deterministične popravke. |
| `.github/workflows/self-heal.yml` | AI-assisted repair po ponavljajočih se napakah, z dodatnim guardian validiranjem in PR tokom. |
| `public/guardian-manifest.json` | Javni manifest z zmožnostmi, zaščitenimi potmi in produkcijskimi endpointi. |
| `logs/.gitkeep` | Ohrani mapo za lokalna/CI poročila brez commitanja runtime logov. |

## Varni autoupdate princip

Guardian ne dela nevarnega samospreminjanja produkcije. Uporablja varno zaporedje:

1. zazna napako ali drift,
2. zbere poročilo,
3. izvede deterministični repair ali sproži AI-assisted self-heal,
4. preveri protected paths in credential-like vsebino,
5. zažene teste, build, Worker JS teste in Wrangler dry-run,
6. ustvari ločeno vejo,
7. odpre Pull Request,
8. `main` se spremeni šele po združitvi.

Neposreden Cloudflare redeploy je dovoljen samo za sinhronizacijo že obstoječe `main` kode, in samo če sta v GitHub secrets nastavljena `CLOUDFLARE_API_TOKEN` in `CLOUDFLARE_ACCOUNT_ID`.

## Lokalni ukazi

```bash
npm run guardian:check
npm run guardian:repair
npm run test:guardian
```

Za strožji produkcijski check:

```bash
python agents/production-guardian/guardian.py check --strict-remote --fail-on-warning
```

## Kaj se ne popravlja samodejno

- manjkajoči secret/tokeni,
- spremembe auth/encryption kode brez dodatne validacije,
- spremembe `.github/`, `agents/self-heal/`, `agents/operator-terminal/`, `requirements-agent.txt`, `.env*`,
- poslovne ali uredniške odločitve,
- politične/pravne vsebine brez ločenega preverjanja virov.

## Potrebni secrets za polni produkcijski način

- `TERMINAL_COMMAND_KEY` — že uporablja terminal/self-heal.
- `GITHUB_DISPATCH_TOKEN` — za operator terminal.
- `LOGIN_PASSWORD` ali `DAN_LOGIN_PASSWORD`/`MAJ_LOGIN_PASSWORD` — Cloudflare Worker secrets.
- `CLOUDFLARE_API_TOKEN` in `CLOUDFLARE_ACCOUNT_ID` — samo za direct Worker redeploy iz GitHub Actions.
- opcijsko `MODEL_API_KEY`, `MODEL_BASE_URL`, `MODEL_NAME` ali `COPILOT_GITHUB_TOKEN` — za AI-assisted repair provider.
