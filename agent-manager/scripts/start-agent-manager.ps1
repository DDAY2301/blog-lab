$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

# Windows PowerShell does not automatically refresh User-scope environment
# variables in an already-open terminal. Hydrate known Agent Manager settings
# before spawning child processes so persistent configuration changes take
# effect on the next restart without requiring a new shell or logon.
$runtimeEnvNames = @(
  'AGENT_MANAGER_WRITE_ENABLED',
  'AGENT_MANAGER_ROOTS',
  'PROJECT_VISIBILITY_ROOT',
  'AGENT_MANAGER_LOW_MEMORY_MODE',
  'AGENT_MANAGER_CONTEXT',
  'AGENT_MANAGER_MODEL',
  'AGENT_MANAGER_AI_PRIORITY',
  'OLLAMA_MAX_LOADED_MODELS',
  'OLLAMA_NUM_PARALLEL',
  'OLLAMA_CONTEXT_LENGTH',
  'OLLAMA_KEEP_ALIVE',
  'OLLAMA_FAST_KEEP_ALIVE',
  'AGENT_MANAGER_OLLAMA_KEEP_ALIVE',
  'MODEL_CONCURRENCY',
  'VISUAL_QA_CONCURRENCY',
  'PRODUCTION_WORKERS',
  'AGENT_MANAGER_GITHUB_TOKEN',
  'GH_TOKEN',
  'GITHUB_TOKEN',
  'FLEET_LOCAL_TOKEN',
  'FLEET_AGENT_TOKEN',
  'GMAIL_REPORTING_ENABLED',
  'GMAIL_COMMANDS_ENABLED',
  'GMAIL_COMMAND_ALLOWED_SENDERS',
  'GMAIL_COMMAND_POLL_SECONDS',
  'GMAIL_OAUTH_CLIENT_FILE',
  'GMAIL_OAUTH_TOKEN_FILE',
  'GMAIL_FROM_EMAIL',
  'REPORT_TO_EMAIL'
)

foreach ($name in $runtimeEnvNames) {
  $userValue = [Environment]::GetEnvironmentVariable($name, 'User')
  if (-not [string]::IsNullOrWhiteSpace($userValue)) {
    [Environment]::SetEnvironmentVariable($name, $userValue, 'Process')
  }
}

$py='.\.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { throw 'Run scripts\install-agent-manager.ps1 first.' }
Start-Process $py -ArgumentList '-m','manager.guardian_v3' -WindowStyle Hidden
Start-Process $py -ArgumentList 'run.py' -WindowStyle Hidden
Start-Sleep -Seconds 2
Invoke-RestMethod http://127.0.0.1:8787/health | ConvertTo-Json -Depth 8
