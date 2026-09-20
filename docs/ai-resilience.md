# Blog Lab AI resilience

Runtime order:
1. Cloudflare Workers AI through `env.AI.run()`.
2. Model fallback list from `WORKERS_AI_MODELS`, then built-in defaults.
3. Optional AI Gateway when `AI_GATEWAY_ID` or `WORKERS_AI_GATEWAY_ID` is set.
4. GitHub Actions external model fallback when `MODEL_API_KEY`, `MODEL_BASE_URL`, and `MODEL_NAME` are configured.
5. Deterministic fallback publisher if AI providers are unavailable.

Endpoints:
- `GET /health` shows AI model fallbacks and AI Gateway readiness.
- `GET /api/ai/diagnostics` tests live model fallback and requires `Authorization: Bearer <TERMINAL_COMMAND_KEY>`.

Optional Cloudflare Worker variables/secrets:
- `AI_GATEWAY_ID=default`
- `AI_GATEWAY_CACHE_TTL=900`
- `AI_GATEWAY_SKIP_CACHE=false`
- `WORKERS_AI_MODELS=@cf/zai-org/glm-4.7-flash,@cf/meta/llama-3.1-8b-instruct-fp8,@cf/google/gemma-3-12b-it`

Optional GitHub Actions repository secrets:
- `MODEL_API_KEY`
- `MODEL_BASE_URL`
- `MODEL_NAME`
