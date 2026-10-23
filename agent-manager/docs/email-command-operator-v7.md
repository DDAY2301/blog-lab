# Agent Manager V7 - upravljanje z e-posto

## Kaj je dejansko podprto

Agent Manager V4 z email-control V7 tece na namenskem Windows 11 racunalniku z 8 GB RAM-a. Nacin supervisor-only ne zaganja lokalnega BlogLab ali Project Visibility produkcijskega agenta; ohranja Manager, watchdog, Fleet Remote in Ollama, ki po AI odgovoru sprosti model.

**E-posta ni sama po sebi dokaz, da so OAuth, dovoljenja in oddaljeni tokeni nastavljeni.** Preveri stanje na lokalnem racunalniku. E-postni ukaz je dovoljen le iz natancno odobrenega naslova in s preverjeno Gmail pristnostjo (Gmail SENT ali Google DMARC=pass z ujemajoco domeno). Gesel in tokenov nikoli ne posiljaj po e-posti.

## Hiter pregled brez AI modela

Poslji iz avtoriziranega e-postnega naslova na Gmail racun, ki ga Manager bere:

| Zadeva e-poste | Rezultat |
| --- | --- |
| `[AGENT] POMOC` | Aktualni seznam ukazov in omejitev |
| `[AGENT] STATUS` | Povzetek flote in stanj (GitHub PV, BlogLab worker) |
| `[AGENT MANAGER] STATUS` | Zdravje Managerja, cilji, RAM, stevilo incidentov |
| `[AGENT] INCIDENTI` | Odprti incidenti, prioriteta in komponenta |
| `[AGENT] RAM` | Prosti RAM, CPU in disk |
| `[AGENT] MODELI` | Status razpolozljivih AI ponudnikov/modelov |
| `[AGENT] PREVERI AGENTE` | Takojsnje preverjanje registriranih servisov |
| `[AGENT] EMAIL STATUS` | Gmail OAuth in stanje komandnega loopa |
| `[AGENT] OPRAVILA` | Zadnjih 20 opravljenih/tekocih opravil |
| `[AGENT ALL] STATUS` | Celotni povzetek Agent Manager, PV in BlogLab |

Te kratke besede se usmerijo deterministicno, **brez nalaganja lokalnega Ollama modela**. V zadevi lahko navedes ukaz brez vsebine e-postnega sporocila.

## Ukazi, ki lahko sprozijo delovanje

| Zadeva | Primer besedila ali ukaza | Predpogoj |
| --- | --- | --- |
| `[AGENT MANAGER] VZDRZEVANJE` | Zazeni en nadzorni krog in zberi ugotovitve | Manager 8787 deluje |
| `[AGENT MANAGER] TEST EMAIL` | Preveri odhodno e-posto | Gmail OAuth send |
| `[AGENT MANAGER] POPRAVI KODO BLOG LAB` | Oglej si napako v urejevalniku slik, pripravi PR s testi | Lokalno zaupanja vreden GitHub repo in dovoljenja |
| `[AGENT BLOGLAB]` | Napiši osnutek clanka o kroznem gospodarstvu | BlogLab Cloudflare Worker + FLEET_AGENT_TOKEN |
| `[AGENT BLOGLAB]` | Preglej zadnjo objavo in preveri slike | Enako |
| `[AGENT BLOGLAB]` | Pripravi objavo in uporabi prilozene slike | Enako; priloge se obravnavajo kot nezaupan vhod |
| `[AGENT]` | Preveri BlogLab in Project Visibility ter razlozi incidente | Univerzalni nacrtovalnik; za kompleksne ukaze lahko uporabi Ollama |

**Project Visibility remote commands** v nacinu supervisor-only so zdaj omejeni na:
- `[AGENT PV] STATUS` - pregled trenutnega GitHub CI stanja, ne runtime API.
- `[AGENT PV] TEST API` - ob pravilno omejenem GitHub tokenu sprozi `agent-api-ci.yml` na GitHub Actions.
- `[AGENT PV] FRONTEND BENCHMARK` - na GitHub Actions sprozi `frontend-benchmark.yml`.
- Ostali ukazi (npr. gradnja novih spletnih strani, preflight lokalnega projekta, edit kode prek PV runtime) **niso** na voljo, dokler ni povezan posebej avtenticiran remote PV runner. GitHub workflow dispatch pomeni le sprejeto zahtevo, ne se rezultatov koncanega testa.

Token `AGENT_MANAGER_GITHUB_TOKEN` nastavi **lokalno** z dovoljenjem Actions: Read and write za repozitorij `DDAY2301/PROJEKT`; ne posiljaj tokena prek e-postnega ukaza. Diagnosticni workflow uporablja fiksno ime in fiksno vejo `main`, ne sprejema shell ukazov.


**Code fix** je zasnovan za branch, test in GitHub PR, brez samodejnega merge v produkcijsko vejo. Zgolj opisane moznosti v prirocniku ne dokazujejo pripravljene GitHub avtentikacije, lokalnega izvora kode ali dejanske uspesnosti posameznega ukaza.

## Priprava na lokalnem racunalniku

1. `git pull --ff-only origin agent-manager-v1` v `%LOCALAPPDATA%\AgentManagerV4\blog-lab`.
2. `& ".\scripts\email-control-v7.ps1" -Mode Check` iz direktorija `agent-manager`. Prikaze, ali sta Gmail ukazni nacin in OAuth dejansko pripravljena (brez izpisa tokenov).
3. Ce ni omogočeno, `& ".\scripts\email-control-v7.ps1" -Mode Enable -OwnerEmail "tvoj@naslov.si"`. To nastavi User environment na samo enega dovoljenega posiljatelja in zahteva preverjeno pristnost.
4. Ce OAuth zahteva ponovno pooblastitev (`AUTH_REQUIRED`), z lokalnim brskalnikom izvedi `& ".\scripts\email-control-v7.ps1" -Mode Authorize`; potreben je ze obstojeci Gmail OAuth client JSON. Kljucev ne lepi v klepet.
5. `& ".\scripts\restart-agent-manager.ps1"` in `& ".\scripts\email-control-v7.ps1" -Mode Check`. Nato po potrebi `-Mode SendTest` za odhodno sporocilo.
6. Poslji si `[AGENT] POMOC`, preveri, da pride `[AGENT RESULT]` odgovor. To je sele end-to-end dokaz poti od Gmaila do agenta in nazaj.

## Varnost

- Zahteva tocen email v `GMAIL_COMMAND_ALLOWED_SENDERS`, Gmail SENT ali poravnano DMARC pristnost, deduplikacijo message-ID, omejitev 4000 znakov in odstranitev citiranih starih odgovorov.
- `GMAIL_COMMAND_REQUIRE_AUTH=0` je nevaren legacy escape hatch; v produkciji ohrani `1`.
- Dokončna pooblastila za GitHub/code-fix/deploy morajo biti locena od Gmail nadzora; nevarna dejanja morajo potekati skozi preverljive policy gate in PR review.
- Dolgi univerzalni ukazi lahko aktivirajo AI, kar zacasno zmanjsa prosti RAM. Lokalni Focus profil uporablja `keep_alive=0s` po koncanem odgovoru.
- Osebni Gmail token je na lokalnem racunalniku; s ChatGPT Gmail vmesnikom ni enak. Status v ChatGPT ne dokazuje stanja lokalne storitve.
