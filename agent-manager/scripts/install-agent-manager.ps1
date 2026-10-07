$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

function Resolve-Python {
    $candidates = @()
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $candidates += @{ Exe = "py"; Args = @("-3.12") }
        $candidates += @{ Exe = "py"; Args = @("-3") }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $candidates += @{ Exe = "python"; Args = @() }
    }
    $known = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python313\python.exe"
    )
    foreach ($p in $known) { if (Test-Path $p) { $candidates += @{ Exe=$p; Args=@() } } }
    foreach ($c in $candidates) {
        try {
            $probe = @($c.Args) + @("-c","import sys; print(sys.executable)")
            $out = & $c.Exe @probe 2>$null
            if ($LASTEXITCODE -eq 0 -and $out) { return $c }
        } catch {}
    }
    throw "Python 3 was not found. Install Python 3.12, reopen PowerShell, and run this installer again."
}

$python = Resolve-Python
if (-not (Test-Path ".venv")) { & $python.Exe @($python.Args) -m venv .venv }
$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { throw "Virtual environment was not created: $venvPython" }

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt
New-Item -ItemType Directory -Force data | Out-Null

$root=(Get-Location).Path
$run=Join-Path $root 'run.py'
$taskOk=$true
schtasks /Create /TN "AgentManagerV3" /TR "`"$venvPython`" `"$run`"" /SC ONLOGON /RL LIMITED /F | Out-Null
if ($LASTEXITCODE -ne 0) { $taskOk=$false }
schtasks /Create /TN "AgentManagerV3-Guardian" /TR "`"$venvPython`" -m manager.guardian_v3" /SC ONLOGON /RL LIMITED /F | Out-Null
if ($LASTEXITCODE -ne 0) { $taskOk=$false }

if (-not $taskOk) {
    $startup = [Environment]::GetFolderPath("Startup")
    $cmd = Join-Path $startup "AgentManagerV3.cmd"
    @"
@echo off
cd /d "$root"
start "" /min powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "$root\scripts\start-stack-v4.ps1"
"@ | Set-Content -Path $cmd -Encoding ASCII
    Write-Warning "Scheduled Task creation was denied. Installed current-user Startup fallback instead: $cmd"
} else {
    Write-Host "Windows startup tasks installed." -ForegroundColor Green
}
Write-Host "Agent Manager V3 dependencies are installed." -ForegroundColor Green
$startup = [Environment]::GetFolderPath("Startup")
$stackCmd = Join-Path $startup "AgentManagerV4-Stack.cmd"
@"
@echo off
cd /d "$root"
start "" /min powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "$root\scripts\start-stack-v4.ps1"
"@ | Set-Content -Path $stackCmd -Encoding ASCII
Write-Host "Current-user 24/7 startup registered: $stackCmd" -ForegroundColor Green
Write-Host "Next: .\scripts\start-stack-v4.ps1"
