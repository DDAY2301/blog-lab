$ErrorActionPreference="Stop"
$home = [Environment]::GetEnvironmentVariable("COLIBRI_HOME","User")
$model = [Environment]::GetEnvironmentVariable("COLIBRI_MODEL_PATH","User")
if (-not $home) { $home = "$env:LOCALAPPDATA\AgentManager\colibri-v2" }
if (-not $model) { Write-Host "Colibri STANDBY: no COLIBRI_MODEL_PATH configured."; exit 0 }
$coli = Join-Path $home "coli.cmd"
if (-not (Test-Path $coli)) { $coli = Join-Path $home "coli" }
if (-not (Test-Path $coli)) { throw "Colibri launcher not found. Run install-colibri-v2.ps1 first." }

$existing = Get-NetTCPConnection -State Listen -LocalPort 8790 -ErrorAction SilentlyContinue
if ($existing) { Write-Host "Colibri already listening on 8790."; exit 0 }

Start-Process -FilePath $coli -ArgumentList @(
  "serve",
  "--model", $model,
  "--host", "127.0.0.1",
  "--port", "8790",
  "--model-id", "colibri-local"
) -WorkingDirectory $home -WindowStyle Hidden
Start-Sleep -Seconds 5
try {
  Invoke-RestMethod http://127.0.0.1:8790/v1/models -TimeoutSec 10 | ConvertTo-Json -Depth 6
} catch {
  Write-Warning "Colibri process was started but API is not ready yet: $($_.Exception.Message)"
}
