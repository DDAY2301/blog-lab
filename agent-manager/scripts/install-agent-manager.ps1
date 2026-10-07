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

# Remove startup artifacts created by older V3 installers so V4 owns one stack.
$startup=[Environment]::GetFolderPath("Startup")
foreach($legacy in @("AgentManagerV3.cmd","ProjectVisibility.cmd")){
    $p=Join-Path $startup $legacy
    if(Test-Path $p){ Remove-Item $p -Force -ErrorAction SilentlyContinue }
}
foreach($task in @("AgentManagerV3","AgentManagerV3-Guardian")){
    schtasks /Delete /TN $task /F 2>$null | Out-Null
}

$stackScript=Join-Path $root "scripts\start-stack-v4.ps1"
$stackCmd=Join-Path $startup "AgentManagerV4-Stack.cmd"
@"
@echo off
cd /d "$root"
start "" /min powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "$stackScript"
"@ | Set-Content -Path $stackCmd -Encoding ASCII
Write-Host "Current-user startup registered: $stackCmd" -ForegroundColor Green

# Best-effort recurring reconciler. Startup + watchdog remains the fallback if Task Scheduler denies it.
$taskCommand="powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$stackScript`""
schtasks /Create /TN "AgentManagerV4-Reconcile" /TR $taskCommand /SC MINUTE /MO 5 /F 2>$null | Out-Null
if($LASTEXITCODE -eq 0){
    Write-Host "5-minute recovery task registered." -ForegroundColor Green
}else{
    Write-Warning "Task Scheduler did not allow the recurring recovery task. Startup + Watchdog will still provide recovery."
}

Write-Host "Agent Manager V4 dependencies are installed." -ForegroundColor Green
Write-Host "Next: .\scripts\start-stack-v4.ps1"
