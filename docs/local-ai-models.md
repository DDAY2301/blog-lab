# Blog Lab local model stack

Blog Lab uses a tiered local-first model profile so routine work stays cheap and fast while difficult repository repairs can use a much stronger expert model.

- `qwen2.5-coder:7b`: fast/general local fallback for normal work.
- `KAT-Coder-V2.5-Dev`: expert coding/self-heal model, based on Qwen3.6-35B-A3B.
- `qwen3.6:35b-a3b-coding`: optional larger fallback; not installed by default to avoid duplicating ~20+ GB of weights.
- Vision remains separate because the open KAT-Coder release is text-only.

KAT-Coder-V2.5-Dev is a 35B-total Mixture-of-Experts model with roughly 3B active parameters per token. The quantized weights still require substantial RAM/disk, so the efficient profile installs one KAT expert quantization and keeps normal tasks on the 7B fast path.

## Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\scripts\install-local-ai-models.ps1 -Profile efficient
.\scripts\test-local-ai-models.ps1
```

The efficient profile:
- keeps `qwen2.5-coder:7b` as the routine/general model;
- imports verified `Abiray/KAT-Coder-V2.5-Dev-Imatrix-GGUF` through Ollama;
- creates stable alias `bloglab-katcoder-efficient`;
- chooses `IQ3_M` on machines with enough RAM, otherwise `Q3_K_M`.

To additionally install the larger Qwen3.6 coding fallback:

```powershell
.\scripts\install-local-ai-models.ps1 -Profile efficient -InstallQwen36
```

Do not install both large models unless you actually need them; KAT is already post-trained from Qwen3.6 and is the preferred expert coder.

## Routing

With local models configured:
1. routine/general work uses `LOCAL_GENERAL_MODEL` (normally 7B);
2. self-heal/code repair uses `LOCAL_CODER_MODEL` (KAT expert);
3. Workers AI/external providers remain fallbacks according to the existing provider chain.

## GitHub Actions

A GitHub-hosted runner cannot reach `127.0.0.1` on the Windows host. To use local models from scheduled workflows, expose a protected OpenAI-compatible endpoint and configure repository variables:
- `LOCAL_MODEL_ENABLED=true`
- `LOCAL_MODEL_BASE_URL=https://<protected-endpoint>/v1/chat/completions`
- `LOCAL_GENERAL_MODEL=qwen2.5-coder:7b`
- `LOCAL_CODER_MODEL=bloglab-katcoder-efficient`
- `LOCAL_MODEL_TIMEOUT=300`

Optional secret:
- `LOCAL_MODEL_API_KEY`
