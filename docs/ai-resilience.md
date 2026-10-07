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


## Local-first Qwen3.6 / KAT-Coder routing

Blog Lab can prefer a local OpenAI-compatible endpoint before Workers AI, external paid APIs or Copilot.

Task routing:
- Editorial generation and grounding review: `LOCAL_GENERAL_MODEL` (recommended alias: `bloglab-qwen36-efficient`).
- Site edits and self-heal repair plans: `LOCAL_CODER_MODEL` (recommended alias: `bloglab-katcoder-efficient`).
- Existing deterministic and remote providers remain fallbacks.

Local Windows/Ollama example:

```text
LOCAL_MODEL_ENABLED=true
LOCAL_MODEL_BASE_URL=http://127.0.0.1:11434/v1/chat/completions
LOCAL_GENERAL_MODEL=bloglab-qwen36-efficient
LOCAL_CODER_MODEL=bloglab-katcoder-efficient
```

GitHub-hosted Actions cannot reach `127.0.0.1` on the user's PC. To let scheduled cloud workflows use these local models, expose a protected OpenAI-compatible endpoint and set repository variables `LOCAL_MODEL_ENABLED=true`, `LOCAL_MODEL_BASE_URL`, `LOCAL_GENERAL_MODEL`, `LOCAL_CODER_MODEL`, plus optional secret `LOCAL_MODEL_API_KEY`. If no reachable local endpoint is configured, the workflow falls back to the existing provider chain.
