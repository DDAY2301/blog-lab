# Guardian Secret Requirements

The Production Guardian does not store secrets in source code.

## Required for existing terminal

- `GITHUB_DISPATCH_TOKEN`
- `TERMINAL_COMMAND_KEY`
- `LOGIN_PASSWORD` or dedicated `DAN_LOGIN_PASSWORD` / `MAJ_LOGIN_PASSWORD` in Cloudflare Worker secrets

## Required only for direct Worker redeploy

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

## Optional for AI-assisted self-heal

- `COPILOT_GITHUB_TOKEN`, or
- `MODEL_API_KEY`, `MODEL_BASE_URL`, `MODEL_NAME`

If AI providers are not configured, deterministic guardian checks and repairs still work.
