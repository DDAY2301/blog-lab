# Blog Lab Private Terminal

Zasebni terminal za upravljanje `DDAY2301/blog-lab`. Worker je pripravljen tako, da Cloudflare Builds lahko ostane nastavljen na root repozitorija (`/`), z `npm run build` in `npx wrangler deploy`. Root `wrangler.jsonc` kaže neposredno na `terminal/worker/src/index.js`.

## Dostop

Produkcijski Worker mora biti zaščiten s Cloudflare Access. Access policy naj dovoli samo Dana in Maja prek njunih e-mail naslovov. Worker preveri podpis `Cf-Access-Jwt-Assertion`, issuer, Access application AUD in nato še e-mail allowlist.

## Potrebni runtime secrets

V Cloudflare Workerju:
- `GITHUB_DISPATCH_TOKEN` — fine-grained GitHub token samo za `DDAY2301/blog-lab`, z `Actions: write`.
- `TERMINAL_COMMAND_KEY` — base64 zapis natanko 32 naključnih bajtov.
- `ALLOWED_EMAILS` — `dan.grmusa@gmail.com,maj@klemenc.org`.
- `TEAM_DOMAIN` — `https://<team-name>.cloudflareaccess.com`.
- `POLICY_AUD` — Application Audience (AUD) tag Access aplikacije.

V GitHub Actions secrets mora biti isti `TERMINAL_COMMAND_KEY`.

## KV ni več potreben

Terminal ne potrebuje Cloudflare KV. Ukazi ostanejo lokalno v brskalniku posameznega operaterja, status pa se na približno štiri sekunde osveži iz GitHub Actions prek anonimnega `request_id`. Ukaz je pred `workflow_dispatch` šifriran z AES-256-GCM, zato sam tekst ukaza ni poslan kot berljiv workflow input.

## URL

`workers_dev` je eksplicitno vključen v Wrangler konfiguraciji. Po uspešnem deployu naj Worker dobi `blog-lab-private-terminal.<account-subdomain>.workers.dev`, če ima Cloudflare račun nastavljen `workers.dev` subdomain.

Javni health endpoint je `/health`; ne razkriva vrednosti skrivnosti, samo pove ali sta potrebni runtime skrivnosti nastavljeni.

## Delovanje

- `Samodejno`: agent sam prepozna tip zahteve.
- `Članek`: uporabi obstoječ Blog Lab publisher in temo operaterja.
- `Sprememba strani`: Copilot spremeni samo dovoljene spletne datoteke, nato workflow izvede teste in build.
- `Nadzor agenta`: ustavitev/vklop in `automatic`, `draft`, `review` način.

Samostojni Blog Lab publisher še naprej dela po svojem urniku tudi brez terminala.

## Deployment source of truth

Cloudflare naj deploya iz root-a repozitorija. `wrangler.jsonc` v root-u je produkcijski source of truth in eksplicitno kaže na `terminal/worker/src/index.js`; zato ni treba spreminjati Cloudflare Root directory nastavitve iz `/`.
