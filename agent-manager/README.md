# Agent Manager v0.3

Local-first supervisor for discovering, evaluating and safely improving AI-agent repositories.

## Current capabilities

1. repository and agent discovery;
2. deterministic health score (0-100);
3. local Ollama engineering review;
4. persistent local Agent Registry with previous score tracking;
5. safe repair planning that produces a candidate unified diff;
6. protected-path validation before any repair can progress;
7. FastAPI control surface;
8. isolated GitHub CI validation.

The current repair engine is **plan-only**: it can propose and validate a patch, but it does not write into production repositories yet. The next milestone is sandbox apply -> tests -> repair branch -> PR.

## Free/local stack

- LLM runtime: Ollama on localhost
- preferred model: `qwen3-coder:30b`
- fallbacks: `qwen2.5-coder:7b`, `devstral`
- API: FastAPI
- state: local JSON registry
- tests: pytest
- source control / review: GitHub branch + PR
- no paid LLM API is required

## Windows quick start

Open PowerShell in `agent-manager`:

```powershell
.\start.ps1
```

Then open:

```text
http://127.0.0.1:8787/docs
```

Optional stronger model:

```powershell
ollama pull qwen3-coder:30b
```

If that model is too large for the machine, keep a smaller installed coding model; Agent Manager automatically falls back.

## API

### Health

```http
GET /health
```

### Installed / selected local models

```http
GET /models
```

### Scan repositories without storing them

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

### Discover and persist agents in Registry

```http
POST /registry/discover
Content-Type: application/json

{
  "roots": [
    "C:\\Projects\\blog-lab",
    "C:\\Projects\\other-agent"
  ]
}
```

### List known agents

```http
GET /registry
```

### Full engineering review

```http
POST /review
Content-Type: application/json

{
  "root": "C:\\Projects\\blog-lab",
  "use_ai": true
}
```

### Prepare a safe repair candidate

```http
POST /repair/plan
Content-Type: application/json

{
  "root": "C:\\Projects\\blog-lab",
  "objective": "Improve the publisher agent recovery logic without changing current publishing behaviour."
}
```

The response includes the chosen local model, repair plan, candidate unified diff, suggested test commands, risk level and patch validation result.

## Repair security

Before a candidate can become executable, Agent Manager rejects paths including:

- `.git/`
- `.env*`
- `secrets/`
- `credentials/`
- parent-directory traversal such as `../`

The execution layer will add further gates before write access is enabled.

## Architecture

```text
repositories
    |
    v
RepositoryScanner
    |
    +--> HealthReport
    |
    +--> AgentRegistry ---------> history / score drift
    |
    +--> AgentEvaluator --------> local Ollama
    |
    +--> RepairPlanner ---------> local Ollama
                               |
                               v
                         unified diff
                               |
                               v
                        path validation
                               |
                               v
                         [next milestone]
                    sandbox -> tests -> PR
```

## Environment

See `.env.example`.

Main variables:

- `OLLAMA_BASE_URL`
- `AGENT_MANAGER_MODEL`
- `AGENT_MANAGER_FALLBACK_MODELS`
- `AGENT_MANAGER_ROOTS`
- `AGENT_MANAGER_STATE`

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The development branch also has an isolated GitHub Actions workflow that runs compile, unit tests and a FastAPI import smoke test.

## Next milestones

1. sandboxed patch application;
2. automatic test-command detection;
3. before/after health and regression comparison;
4. repair branch creation and automatic Pull Request;
5. prompt-specific eval suite;
6. GitHub repository discovery across the account;
7. A2A 1.0 transport using the official SDK;
8. MCP tool gateway;
9. web dashboard;
10. scheduled autonomous review loop.
