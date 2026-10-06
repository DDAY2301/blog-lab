$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python not found in PATH.' }
if (-not (Test-Path .venv)) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force data | Out-Null
$root=(Get-Location).Path
$py=Join-Path $root '.venv\Scripts\python.exe'
$run=Join-Path $root 'run.py'
schtasks /Create /TN "AgentManagerV3" /TR "`"$py`" `"$run`"" /SC ONLOGON /RL LIMITED /F | Out-Null
schtasks /Create /TN "AgentManagerV3-Guardian" /TR "`"$py`" -m manager.guardian_v3" /SC ONLOGON /RL LIMITED /F | Out-Null
Write-Host 'Installed Agent Manager V3 startup tasks.'
