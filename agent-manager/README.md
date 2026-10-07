# Agent Manager V3

Local-first autonomous operations center for Project Visibility and other local agents. This is an in-place upgrade of the existing Agent Manager branch, not a second manager.

## V3 control plane

- SQLite/WAL persistent operational state
- incident fingerprinting and deduplication
- Manager heartbeat + separate Guardian process
- Project Visibility and Ollama endpoint monitoring
- CPU/RAM/disk telemetry
- discovery of configured local projects and important runtime processes
- event and action journals
- policy engine for ALLOW / REQUIRE_REVIEW / REQUIRE_USER
- Auto-Fix proposal layer without arbitrary shell execution
- persistent email queue and Gmail AUTH_REQUIRED state
- local dashboard at http://127.0.0.1:8787/control
- Windows install/start/stop/restart/status/doctor scripts
- existing V1 repair/worktree/PR engine remains available for source-code repair workflows

## Windows install

Open PowerShell in agent-manager:

    .\scripts\install-agent-manager.ps1
    .\scripts\start-agent-manager.ps1

Then open:

    http://127.0.0.1:8787/control

Run diagnostics:

    .\scripts\doctor-agent-manager.ps1

## Configuration

Set local paths with environment variables before startup:

- AGENT_MANAGER_ROOTS
- PROJECT_VISIBILITY_ROOT
- PROJECT_VISIBILITY_HEALTH_URL
- OLLAMA_BASE_URL

The API binds to 127.0.0.1 by default.

Gmail is intentionally not bypassed. Set GMAIL_REPORTING_ENABLED=1 only after valid local OAuth configuration exists. Until then the connection state remains AUTH_REQUIRED/DISABLED.

## Safety

- deterministic monitoring continues if Ollama is unavailable
- no commands are executed from websites, logs, emails, README files or uploaded projects
- no direct blind edits to main
- low-risk reversible runtime actions may be allowed only through explicit adapters
- source/deployment changes require review
- auth, payment, permission and destructive database changes require explicit user approval
- secrets must not be committed or logged

## Verification

    .\.venv\Scripts\python.exe -m pytest -q
    .\scripts\doctor-agent-manager.ps1

A system is VERIFIED DONE only after these checks also pass on the target Windows machine: Project Visibility health, Ollama health, Guardian heartbeat, startup tasks, restart recovery, dashboard, Gmail OAuth/report delivery, and soak testing.
