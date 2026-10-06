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

    foreach ($p in $known) {
        if (Test-Path $p) {
            $candidates += @{ Exe = $p; Args = @() }
        }
    }

    foreach ($c in $candidates) {
        try {
            $probeArgs = @($c.Args) + @("-c", "import sys; print(sys.executable)")
            $out = & $c.Exe @probeArgs 2>$null
            if ($LASTEXITCODE -eq 0 -and $out) {
                return $c
            }
        } catch {}
    }

    throw @"
Python 3 was not found.

Recommended fix:
  winget install -e --id Python.Python.3.12

Then close and reopen PowerShell and run this installer again.

If Python is already installed, Windows App Execution Aliases may be intercepting 'python'.
You can also verify with:
  py --version
  where.exe py
  where.exe python
"@
}

$python = Resolve-Python

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    & $python.Exe @($python.Args) -m venv .venv
}

$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment creation failed: $venvPython was not created."
}

Write-Host "Installing dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

New-Item -ItemType Directory -Force data | Out-Null

$root=(Get-Location).Path
$run=Join-Path $root 'run.py'
$guardianArgs="-m manager.guardian_v3"

schtasks /Create /TN "AgentManagerV3" /TR "`"$venvPython`" `"$run`"" /SC ONLOGON /RL LIMITED /F | Out-Null
schtasks /Create /TN "AgentManagerV3-Guardian" /TR "`"$venvPython`" $guardianArgs" /SC ONLOGON /RL LIMITED /F | Out-Null

Write-Host ""
Write-Host "Agent Manager V3 installed successfully." -ForegroundColor Green
Write-Host "Next: .\scripts\start-agent-manager.ps1"
