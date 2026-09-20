# Guardian Troubleshooting

## Fresh browser login still fails

1. Check `https://blog-lab.dan-grmusa.workers.dev/health`.
2. Confirm `version` matches the Worker source version.
3. Confirm `auth_self_test_ok` is true.
4. If source version is newer than live version, redeploy the Worker.
5. If auth self-test is false, configure `LOGIN_PASSWORD` or the dedicated Cloudflare Worker login secrets.

## Production Guardian fails on remote health

This usually means one of:

- GitHub Pages is still deploying,
- Cloudflare Worker is stale,
- Worker secrets are incomplete,
- the external network check timed out.

Use the uploaded `production-guardian-report` artifact to see the exact finding.

## Self-heal makes no code change

That is expected when the issue is external configuration only, for example missing Cloudflare secrets. The workflow reports the missing configuration and avoids inventing credentials.
