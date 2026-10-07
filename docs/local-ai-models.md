# Blog Lab local model stack

Blog Lab uses local-first routing to reduce paid AI usage while preserving the existing cloud fallbacks.

- Qwen3.6-35B-A3B: editorial writing and grounding review.
- KAT-Coder-V2.5-Dev: code/site changes and self-heal repair planning.
- qwen2.5-coder:7b: fast fallback.
- Vision remains separate because the open KAT-Coder release is text-only.

KAT-Coder-V2.5-Dev is a post-trained MoE coding model based on Qwen3.6-35B-A3B. The model has about 35B total parameters and about 3B active parameters per token; the full quantized weights still need RAM/VRAM.

## Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\install-local-ai-models.ps1 -Profile efficient
.\scripts\test-local-ai-models.ps1
```

The efficient profile creates stable aliases:
- `bloglab-qwen36-efficient`
- `bloglab-katcoder-efficient`

On a 6 GB RTX laptop GPU, the 35B-A3B weights do not fit fully in VRAM. The efficient profile uses compact GGUF quantizations and hybrid GPU/CPU/system-RAM inference. Use `-Profile quality` only when enough system memory is available for ~21-24 GB model weights plus KV cache.

## Routing

With `AI_PROVIDER=auto`:
1. local model if configured and reachable;
2. Workers AI;
3. external model;
4. Copilot where supported;
5. deterministic fallback where supported.

Editorial work uses `LOCAL_GENERAL_MODEL`. Coding/repair work uses `LOCAL_CODER_MODEL`.

## GitHub Actions

A GitHub-hosted runner cannot reach `127.0.0.1` on the Windows host. To use local models from scheduled workflows, expose a protected OpenAI-compatible endpoint and configure repository variables:
- `LOCAL_MODEL_ENABLED=true`
- `LOCAL_MODEL_BASE_URL=https://<protected-endpoint>/v1/chat/completions`
- `LOCAL_GENERAL_MODEL=bloglab-qwen36-efficient`
- `LOCAL_CODER_MODEL=bloglab-katcoder-efficient`
- `LOCAL_MODEL_TIMEOUT=300`

Optional secret:
- `LOCAL_MODEL_API_KEY`
