# Blog Lab Private Terminal

Zasebni terminal za upravljanje `DDAY2301/blog-lab`. Worker je pripravljen tako, da Cloudflare Builds ostane nastavljen na root repozitorija (`/`), z `npm run build` in `npx wrangler deploy`. Root `wrangler.jsonc` kaže neposredno na `terminal/worker/src/index.js`.

## Brezplačni način dostopa

Terminal ne uporablja Cloudflare Zero Trust/Access, zato za prijavo ni potrebna aktivacija Zero Trust plačilnega profila ali kartice. Prijava je vgrajena neposredno v Worker.

Dovoljena operaterja sta fiksno omejena na:
- `dan.grmusa@gmail.com`
- `maj@klemenc.org`

Vsak lahko uporablja svoje geslo, shranjeno samo kot Cloudflare Worker secret. Za združljivost s starejšo namestitvijo je podprt tudi skupni `LOGIN_PASSWORD`; če je nastavljen namenski uporabniški secret, ima ta prednost. Po uspešni prijavi Worker ustvari podpisano `HttpOnly`, `Secure`, `SameSite=Lax` sejo z veljavnostjo 12 ur. Seja je podpisana s HMAC ključem, izpeljanim iz `TERMINAL_COMMAND_KEY`, in se ne shranjuje v GitHub repo.

## Potrebni Cloudflare Worker secrets

- `GITHUB_DISPATCH_TOKEN` — fine-grained GitHub token samo za `DDAY2301/blog-lab`, z dovoljenjem za sprožanje Actions workflowov.
- `TERMINAL_COMMAND_KEY` — base64 zapis natanko 32 naključnih bajtov.
- `DAN_LOGIN_PASSWORD` — močno geslo za `dan.grmusa@gmail.com`, najmanj 16 znakov.
- `MAJ_LOGIN_PASSWORD` — močno geslo za `maj@klemenc.org`, najmanj 16 znakov.
- `LOGIN_PASSWORD` — opcijski skupni kompatibilni fallback za obe dovoljeni e-pošti; uporablja se samo, če ga želiš ohraniti iz stare konfiguracije.

V GitHub Actions secrets mora biti isti `TERMINAL_COMMAND_KEY`.

Gesel, tokenov ali ključa ne zapisuj v source code, GitHub Variables ali commit zgodovino.

## Cena in infrastruktura

Worker uporablja običajni Cloudflare Workers Free plan. Zero Trust ni potreben. Javni Blog Lab ostane na GitHub Pages, zasebni terminal pa na `https://blog-lab.dan-grmusa.workers.dev/`.

Repo je javen, zato standardni GitHub-hosted Actions runnerji za ta projekt ne porabljajo plačljivih minut. Samostojni publisher teče po svojem urniku tudi, ko terminal ni odprt. Terminal je serverless in je dosegljiv kadarkoli brez lokalnega računalnika; Worker se izvede ob zahtevi, GitHub Actions pa izvajajo dejanske agente in objave.

## Zasebnost ukazov

Ukazi ostanejo lokalno v brskalniku posameznega operaterja kot zgodovina uporabniškega vmesnika. Pred `workflow_dispatch` se ukaz AES-256-GCM šifrira s `TERMINAL_COMMAND_KEY`, zato čisti tekst ukaza ni poslan kot berljiv GitHub Actions input. Runner ga dešifrira samo začasno za izvedbo.

## URL in javni gumb Prijava

`workers_dev` je vključen v Wrangler konfiguraciji. Produkcijski Worker je `blog-lab` in uporablja URL:

`https://blog-lab.dan-grmusa.workers.dev/`

Ta URL je vpisan v `public/terminal-config.json`. Gumb `Prijava` na javni strani vodi neposredno na vgrajeno prijavo terminala.

Javni `/health` endpoint ne razkriva skrivnosti. Vrne samo osnovno readiness stanje in način avtentikacije.

## Delovanje terminala

- `Samodejno`: agent sam prepozna tip zahteve.
- `Članek`: uporabi obstoječ Blog Lab publisher in temo operaterja.
- `Sprememba strani`: Copilot spremeni samo dovoljene spletne datoteke, nato workflow izvede teste in build.
- `Nadzor agenta`: ustavitev/vklop in `automatic`, `draft`, `review` način.

Varnostne poti `.github/`, `terminal/`, `agents/operator-terminal/`, `AGENTS.md`, `requirements-agent.txt` in `.env*` ostanejo zaščitene pred samodejnim urejanjem skozi terminal.

## Deployment source of truth

Cloudflare deploya iz root-a repozitorija. `wrangler.jsonc` v root-u je produkcijski source of truth in kaže na `terminal/worker/src/index.js`; zato Cloudflare Root directory ostane `/`.


## Samodejno odkrivanje in popravilo napak

Repo vsebuje `.github/workflows/self-heal.yml` in `agents/self-heal/repair.py`.

Self-heal se zažene:
- po neuspehu Private Operator Terminal ali Blog Lab Publisher Agent workflowa;
- ob relevantnih pushih na `main`;
- vsako uro kot produkcijski watchdog;
- ročno prek GitHub Actions.

Preverja Python sintakso, operator/publisher/self-heal teste, Vite build, Worker JavaScript sintakso, Wrangler dry-run, javno stran in Worker `/health`. Ob programski napaki zbere diagnostic log, poišče najmanjši popravek prek razpoložljive AI verige, spremembo uporabi samo v dovoljenih poteh, ponovno izvede vse validatorje in šele nato commitne na `main`. Če validator pade, se sprememba povrne.

Self-heal ne sme sam spreminjati `.github/`, `agents/operator-terminal/`, `agents/self-heal/`, skrivnosti ali credentialov. S tem watchdog ne more odstraniti lastnih varnostnih omejitev.

Če je produkcijski Worker zastarel in sta v GitHub Secrets nastavljena `CLOUDFLARE_API_TOKEN` ter `CLOUDFLARE_ACCOUNT_ID`, ga watchdog lahko neposredno ponovno deploya. Brez teh secretov ostane Cloudflare Git Builds primarni deployment mehanizem.
