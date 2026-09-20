# Guardian Merge Checklist

Before merging the Production Guardian upgrade:

- GitHub Actions should run `Blog Lab Health Check`.
- GitHub Actions should run `Blog Lab Production Guardian`.
- The production Worker may still require Cloudflare redeploy if `/health` shows an older version.
- Add `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` only if direct deploy from Actions is desired.

After merge:

1. Open the private terminal in a fresh browser.
2. Check `/health`.
3. Run the `Blog Lab Production Guardian` workflow manually once.
