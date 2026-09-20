# Guardian Operations

## Manual check

Run from GitHub Actions or locally:

```bash
python agents/production-guardian/guardian.py check --strict-remote --report logs/guardian-report.json
```

## Deterministic repair

```bash
python agents/production-guardian/guardian.py repair
```

This only repairs deterministic hygiene items such as guardian npm scripts, manifest file and log folder marker.

## Autonomous repair

AI-assisted repair remains in `agents/self-heal/repair.py`. The hardened workflow validates output and opens a Pull Request instead of pushing directly to `main`.

## Deployment drift

If `/health` shows a stale Worker version, the workflow can redeploy the Worker only when these GitHub secrets exist:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Without those secrets, the workflow reports the exact issue and leaves source code unchanged.
