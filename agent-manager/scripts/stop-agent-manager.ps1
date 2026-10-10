$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

$py=Join-Path (Get-Location) ".venv\Scripts\python.exe"

# Stop the actual listener on 8787 only when it belongs to this Agent Manager.
if(Test-Path $py){
  & $py -m manager.reconcile_v4 --manager
  if($LASTEXITCODE -ne 0){ throw "Could not safely stop Agent Manager listener on port 8787." }
}

# Stop only this Manager's guardian(s). Processes can disappear during shutdown,
# so suppress benign races rather than printing misleading Stop-Process errors.
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
  Where-Object { $_.CommandLine -match 'manager\.guardian_v3' } |
  ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }
