$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$py='.\.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { throw 'Run scripts\install-agent-manager.ps1 first.' }
Start-Process $py -ArgumentList '-m','manager.guardian_v3' -WindowStyle Hidden
Start-Process $py -ArgumentList 'run.py' -WindowStyle Hidden
Start-Sleep -Seconds 2
Invoke-RestMethod http://127.0.0.1:8787/health | ConvertTo-Json -Depth 8
