$ErrorActionPreference="SilentlyContinue"
Set-Location (Split-Path $PSScriptRoot -Parent)

$home=[Environment]::GetEnvironmentVariable("COLIBRI_HOME","User")
if($home -and (Test-Path (Join-Path $home "c\coli"))){
  Push-Location $home
  & py -3 c\coli stop 2>$null | Out-Null
  Pop-Location
}

$py=Join-Path (Get-Location) ".venv\Scripts\python.exe"
if(Test-Path $py){
  & $py -m manager.reconcile_v4 --project-visibility
  if($LASTEXITCODE -ne 0){
    Write-Warning "Project Visibility listener was not stopped because ownership could not be verified."
  }

  & $py -m manager.reconcile_v4 --manager
  if($LASTEXITCODE -ne 0){
    Write-Warning "Manager listener was not stopped because ownership could not be verified."
  }
}

Get-CimInstance Win32_Process | Where-Object {
  $_.CommandLine -match 'manager.guardian_v3|manager.watchdog_v4' -and
  $_.CommandLine -match 'Agent-Manager'
} | ForEach-Object {
  Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Write-Host "Owned Manager, Guardian, Watchdog, Project Visibility and Colibri processes stopped. Ollama left running."
