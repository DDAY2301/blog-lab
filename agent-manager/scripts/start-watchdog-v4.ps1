$ErrorActionPreference="Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$py=Join-Path (Get-Location) ".venv\Scripts\python.exe"
if(-not (Test-Path $py)){ throw "Agent Manager venv missing." }
$existing=Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'manager.watchdog_v4' } | Select-Object -First 1
if($existing){
  Write-Host "Watchdog V4 already running (PID $($existing.ProcessId))."
  exit 0
}
Start-Process $py -ArgumentList @("-m","manager.watchdog_v4") -WorkingDirectory (Get-Location) -WindowStyle Hidden
Write-Host "Watchdog V4 started."
