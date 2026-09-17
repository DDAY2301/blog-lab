# Blog Lab Private Terminal

Zasebni terminal za upravljanje `DDAY2301/blog-lab`. Worker je pripravljen tako, da Cloudflare Builds lahko ostane nastavljen na root repozitorija (`/`), z `npm run build` in `npx wrangler deploy`. Root `wrangler.jsonc` kaže neposredno na `terminal/worker/src/index.js`.

## Dostop

Produkcijski Worker mora biti zaščiten s Cloudflare Access. Access policy naj dovoli samo dva konkretna operaterja. Worker uporablja Cloudflare Workers `ctx.access.getIdentity()` in nato naredi še dodatni pregled proti `ALLOWED_EMAILS`, zato je dostop zaprt tudi v primeru napačno preširoke Access policy.

## Potrebni runtime secrets

V Cloudflare Workerju:
- `GITHUB_DISPATCH_TOKEN` — fine-grained GitHub token samo za `DDAY2301/blog-lab`, z dovoljenjem za sprožanje Actions workflowov.
- `TERMINAL_COMMAND_KEY` — base64 zapis natanko 32 naključnih bajtov.
- `ALLOWED_EMAILS` — vejica-ločen allowlist obeh dovoljenih operaterjev.

V GitHub Actions secrets mora biti isti `TERMINAL_COMMAND_KEY`.

`TEAM_DOMAIN` in `POLICY_AUD` nista potrebna, ker produkcijski Worker uporablja Cloudflarejev native Access identity context.

## KV ni potreben

Terminal ne potrebuje Cloudflare KV. Ukazi ostanejo lokalno v brskalniku posameznega operaterja, status pa se osvežuje iz GitHub Actions prek anonimnega `request_id`. Ukaz je pred `workflow_dispatch` šifriran z AES-256-GCM, zato sam tekst ukaza ni poslan kot berljiv workflow input.

## URL

`workers_dev` je eksplicitno vključen v Wrangler konfiguraciji. Po uspešnem deployu Worker dobi `blog-lab-private-terminal.<account-subdomain>.workers.dev`, če ima Cloudflare račun nastavljen `workers.dev` subdomain.

Ko je produkcijski URL znan, ga je treba vpisati v `public/terminal-config.json` kot `terminalUrl`. Gumb `Prijava` na javni strani nato vodi neposredno v Cloudflare Access in po uspešni prijavi odpre terminal.

Javni health endpoint je `/health`; ne razkriva vrednosti skrivnosti, samo readiness in imena morebitnih manjkajočih nastavitev.

## Delovanje

- `Samodejno`: agent sam prepozna tip zahteve.
- `Članek`: uporabi obstoječ Blog Lab publisher in temo operaterja.
- `Sprememba strani`: Copilot spremeni samo dovoljene spletne datoteke, nato workflow izvede teste in build.
- `Nadzor agenta`: ustavitev/vklop in `automatic`, `draft`, `review` način.

Samostojni Blog Lab publisher še naprej dela po svojem urniku tudi brez terminala.

## Deployment source of truth

Cloudflare naj deploya iz root-a repozitorija. `wrangler.jsonc` v root-u je produkcijski source of truth in eksplicitno kaže na `terminal/worker/src/index.js`; zato ni treba spreminjati Cloudflare Root directory nastavitve iz `/`.
