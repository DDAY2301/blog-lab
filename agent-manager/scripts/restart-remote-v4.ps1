$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $py)) {
  throw "Agent Manager Python environment is missing."
}

# Only the verified Fleet Remote uvicorn process serving port 8788 is stopped.
# Manager 8787, Ollama 11434, Guardian, Watchdog and tunnel stay online.
& $py -m manager.reconcile_v4 --remote
if ($LASTEXITCODE -ne 0) {
  throw "Refusing to stop Fleet Remote: port 8788 owner is not verified."
}

& "$PSScriptRoot\start-remote-v4.ps1"
if ($LASTEXITCODE -ne 0) {
  throw "Fleet Remote startup failed."
}
$health = Invoke-RestMethod "http://127.0.0.1:8788/health" -TimeoutSec 5
if (-not $health.ok -or $health.service -ne "agent-manager-fleet-remote") {
  throw "Fleet Remote failed post-restart health verification."
}
Write-Host "Fleet Remote restarted with current Python code on 8788." -ForegroundColor Green
