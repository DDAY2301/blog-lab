# Agent Manager v0.1

Local-first supervisor for discovering, evaluating and gradually improving AI-agent repositories.

## Goal

Agent Manager is a management layer above existing agents. Version 0.1 focuses on four safe capabilities:

1. discover agent-related code and configuration;
2. calculate a deterministic health score;
3. use a local Ollama model for a second-pass engineering review;
4. expose everything through a local FastAPI API.

It does **not** modify production code automatically in v0.1. Repair and PR generation are the next layer, after baseline/evaluation is reliable.

## Cost model

The default runtime has no paid model API dependency.

- LLM server: Ollama on localhost
- API/server: FastAPI
- storage in v0.1: local filesystem / repository
- CI tests: ordinary GitHub Actions, no hosted LLM required
- preferred coding model: `qwen3-coder:30b`
- fallback models: `qwen2.5-coder:7b`, `devstral`

A smaller installed Ollama model is selected automatically when the preferred model is unavailable.

## Windows quick start

Open PowerShell in this directory:

```powershell
.\start.ps1
```

Then open:

```text
http://127.0.0.1:8787/docs
```

### Optional stronger local coding model

```powershell
ollama pull qwen3-coder:30b
```

If the machine is too small for that model, keep an existing smaller coding model installed. The manager automatically falls back.

## API

### Health

```http
GET /health
```

Shows Agent Manager status and whether Ollama is reachable.

### Local models

```http
GET /models
```

Lists installed Ollama models and the selected model.

### Scan repositories

```http
POST /scan
Content-Type: application/json

{
  "roots": [
    "C:\\Projects\\blog-lab",
    "C:\\Projects\\other-agent"
  ]
}
```

Returns deterministic repository inventory and health scores.

### Review one repository

```http
POST /review
Content-Type: application/json

{
  "root": "C:\\Projects\\blog-lab",
  "use_ai": true
}
```

Returns:

- repository snapshot;
- score 0-100;
- test/workflow/security/recovery findings;
- local AI review;
- prioritized improvements.

## Environment variables

Copy `.env.example` values into the environment when needed.

Important variables:

- `OLLAMA_BASE_URL`
- `AGENT_MANAGER_MODEL`
- `AGENT_MANAGER_FALLBACK_MODELS`
- `AGENT_MANAGER_ROOTS`

## Architecture

```text
repositories
    |
    v
RepositoryScanner
    |
    +--> deterministic HealthReport
    |
    v
AgentEvaluator
    |
    v
local Ollama model
    |
    v
ReviewResult
    |
    v
FastAPI
```

## Safety model

The manager is intentionally read-only in this first milestone.

Future repair flow:

```text
detect -> reproduce -> propose patch -> isolated branch -> tests -> review -> PR
```

Direct edits to `main` are not part of the manager's repair path.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Next implementation milestones

- Agent Registry with persistent history
- GitHub repository discovery
- prompt quality evaluator
- regression/eval suites
- code repair worker
- sandboxed patch validation
- automatic repair branches and pull requests
- manager dashboard
- A2A Agent Card support
- MCP tool gateway
