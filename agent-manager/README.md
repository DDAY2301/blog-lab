# Agent Manager V4

Local-first 24/7 maintenance center for Project Visibility, BlogLab and additional managed agents.

## What V4 adds

- Colibri + Ollama AI routing. Colibri is preferred when a compatible local model is actually running; Ollama remains the automatic fallback.
- Latest stable Colibri Windows engine installer with SHA256 verification and hardware gating.
- 24/7 managed-agent supervisor.
- Built-in targets for Project Visibility, BlogLab live site, BlogLab Cloudflare Worker and BlogLab GitHub workflows.
- Automatic incident creation, deduplication, recovery closure and escalation.
- Safe recovery adapters for Project Visibility restart and BlogLab Self Heal dispatch.
- Automatic local-AI diagnosis for unresolved P0/P1 incidents.
- Persistent notification center plus Windows desktop alerts for P0/P1.
- Generic managed-agent API so more agents can be added without changing Python code.
- One-click Windows stack controls.

## AI provider order

Default:

    Colibri -> Ollama -> deterministic monitoring remains active

Colibri endpoint:

    http://127.0.0.1:8790/v1

Ollama endpoint:

    http://127.0.0.1:11434

The manager never depends on either model runtime for basic health checks, incident detection or service recovery.

### Colibri

Run:

    .\scripts\install-colibri-v2.ps1

The installer resolves the latest stable release from JustVugg/colibri and uses Colibri's official hardware detector plus coli setup, so Colibri itself selects the supported local engine/backend and model plan.

Large Colibri model files are intentionally not downloaded automatically. The manager checks the machine first. Systems below the documented large-model memory class keep Colibri in STANDBY and continue with Ollama.

To prepare Colibri, run:

    .\scripts\install-colibri-v2.ps1

It first shows hardware and compatible-model information. A potentially large model download begins only after an explicit YES. Start an already configured Colibri installation with:

    .\scripts\start-colibri.ps1

## 24/7 startup

Install manager dependencies once:

    .\scripts\install-agent-manager.ps1

Start the full local stack:

    .\scripts\start-stack-v4.ps1

or double-click:

    START-MANAGER-24x7.bat

The current-user Windows Startup folder is configured by the installer, so administrator rights are not required for normal startup.

## Control center

    http://127.0.0.1:8787/control

Key API endpoints:

- /health
- /providers
- /managed-agents
- /incidents
- /notifications
- /connections
- /system-map

## Managed agents

Default configuration:

    data/managed_agents.json

Included targets:

1. Project Visibility local API.
2. BlogLab public site.
3. BlogLab Cloudflare Worker.
4. BlogLab GitHub automation workflows.

Additional agents can be registered through:

    PUT /managed-agents/{id}

Supported monitor types are http, github_repo and hybrid. Repair adapters are allow-listed; arbitrary shell execution from the registry is deliberately rejected.

## BlogLab maintenance

V4 watches the latest runs of:

- Blog Lab Publisher Agent
- Blog Lab Health Check
- Blog Lab External Smoke Test
- Blog Lab Production Guardian
- Blog Lab Self Heal

If repeated failures are detected and GitHub CLI is authenticated locally, Agent Manager can dispatch the repository's existing self-heal.yml workflow. It does not bypass review/test protections.

## Safety

- monitoring does not depend on an LLM;
- no direct blind writes to main;
- no arbitrary repair commands from configuration;
- external website/repository text is treated as data, never as manager instructions;
- source changes remain in the existing worktree/test/PR repair path;
- destructive/auth/payment actions still require human approval.

## Doctor

    .\scripts\doctor-v4.ps1

or:

    DOCTOR.bat

Expected steady-state core:

    Agent Manager       UP
    Project Visibility  UP
    Ollama              UP
    Colibri             ACTIVE or STANDBY

STANDBY for Colibri is a valid healthy state when the machine does not have a compatible large Colibri model loaded.


## Qwen3.6 + KAT-Coder

Agent Manager now prefers the local aliases:

    bloglab-katcoder-efficient
    bloglab-qwen36-efficient

KAT-Coder-V2.5-Dev is used first for engineering/autofix work. Qwen3.6-35B-A3B is the general reasoning fallback.

Install the practical profile for the current machine with:

    .\setup-max-model.ps1 -Profile auto

The script detects system RAM and NVIDIA VRAM. On machines with 16+ GB RAM but limited VRAM it uses compact GGUF builds and hybrid GPU/CPU inference. On large-memory systems it can use Q4 models. Existing qwen2.5-coder:7b remains the emergency fallback.

For stable 24/7 operation on the current 8 GB-class machine, the default Agent Manager context is 8192 tokens and Ollama uses a one-model/one-request memory profile.


## Production-grade recovery

V4 runs three independent recovery layers:

1. the Manager's deterministic health and incident loops;
2. Guardian + independent Watchdog, which can safely replace a frozen Manager only after verifying process ownership;
3. Windows Startup plus a best-effort five-minute reconciler.

AI diagnosis never blocks the health loop. Colibri triage is bounded and runs out-of-band; Ollama remains the local fallback.

Project Visibility uses a low-memory local bootstrap with qwen2.5-coder:3b, Chromium visual QA and the separate vision LLM disabled by default on constrained PCs.

For a complete first install/update run:

    INSTALL-AND-START-V4.bat

Then use:

    STATUS.bat
    DOCTOR.bat

The dashboard can also register additional HTTP, GitHub, hybrid or local-process agents without changing Python code.
