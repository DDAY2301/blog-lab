# Blog Lab Private Terminal

Zasebni operaterski terminal za Blog Lab. Javna stran ostane na GitHub Pages; terminal teče kot ločen Cloudflare Worker in je zaklenjen s Cloudflare Access.

## Varnostni model

1. Cloudflare Access mora biti vključen za Worker production URL.
2. Access policy dovoli samo dva konkretna e-mail naslova in uporablja One-Time PIN ali drug zaupanja vreden IdP.
3. Worker dodatno preveri e-mail proti secretu `ALLOWED_EMAILS`.
4. Ukaz se pred pošiljanjem v GitHub AES-256-GCM šifrira. Javni GitHub Actions input zato ne vsebuje berljivega ukaza.
5. Worker hrani zasebno zgodovino ukazov v KV največ 30 dni.
6. GitHub workflow dešifrira ukaz samo v začasno datoteko runnerja in jo ob koncu izbriše.
7. Terminalski AI ne sme spreminjati `.github/`, `terminal/`, `agents/operator-terminal/`, `AGENTS.md`, `requirements-agent.txt` ali `.env*`.

## Cloudflare nastavitev

V mapi `terminal/worker`:

```bash
npm install
npx wrangler kv namespace create COMMANDS
```

Vrnjeni KV namespace ID vpiši v `wrangler.jsonc` namesto `REPLACE_WITH_KV_NAMESPACE_ID`.

Nato nastavi Worker secrets:

```bash
npx wrangler secret put ALLOWED_EMAILS
npx wrangler secret put GITHUB_DISPATCH_TOKEN
npx wrangler secret put TERMINAL_COMMAND_KEY
```

- `ALLOWED_EMAILS`: dva dovoljena naslova, ločena z vejico.
- `GITHUB_DISPATCH_TOKEN`: fine-grained GitHub token samo za `DDAY2301/blog-lab` z `Actions: write`.
- `TERMINAL_COMMAND_KEY`: base64 zapis natanko 32 naključnih bajtov, npr. rezultat `openssl rand -base64 32`.

Isto vrednost `TERMINAL_COMMAND_KEY` dodaj tudi kot GitHub Actions secret v repozitoriju.

Deploy:

```bash
npx wrangler deploy
```

V Cloudflare Workers > Access vključi zaščito produkcijskega Worker URL-ja. V Access policy dodaj samo oba dovoljena e-mail naslova. Za e-mail prijavo omogoči One-Time PIN.

## Uporaba

Terminal podpira:

- `Samodejno`: sam prepozna ali gre za članek, nadzor ali spremembo strani;
- `Članek`: ukaz uporabi kot uredniško temo in za dejstva poišče nove RSS rezultate;
- `Sprememba strani`: Copilot uredi dovoljene spletne datoteke, nato workflow izvede teste in build;
- `Nadzor agenta`: ukazi za ustavitev/vklop in `automatic`, `draft`, `review` način.

Blog publisher še naprej samostojno teče po svojem urniku tudi brez odprtega terminala.
