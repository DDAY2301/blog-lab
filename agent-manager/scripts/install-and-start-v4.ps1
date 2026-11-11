$ErrorActionPreference="Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$root=(Get-Location).Path

function Ask-Yes([string]$Prompt){
  $a=Read-Host "$Prompt Type YES to continue"
  return $a -eq "YES"
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " AGENT MANAGER V4 - FINAL LOCAL 24/7 INSTALLER" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Manager runtime
& "$PSScriptRoot\install-agent-manager.ps1"

# 2. Ollama: required fallback/runtime for this hardware class
$ollama=Get-Command ollama -ErrorAction SilentlyContinue
if(-not $ollama){
  $known="$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
  if(Test-Path $known){ $ollama=Get-Item $known }
}
if(-not $ollama){
  if(Get-Command winget -ErrorAction SilentlyContinue -and (Ask-Yes "Ollama is missing. Install Ollama for the current PC?")){
    winget install -e --id Ollama.Ollama
    if($LASTEXITCODE -ne 0){ throw "Ollama installation failed." }
    $known="$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    if(Test-Path $known){ $env:Path="$(Split-Path $known -Parent);$env:Path" }
  }else{
    throw "Ollama is required. Install it, reopen PowerShell, and rerun this installer."
  }
}

# 3. GitHub CLI is optional for monitoring but required for automatic BlogLab self-heal dispatch.
if(-not (Get-Command gh -ErrorAction SilentlyContinue)){
  if(Get-Command winget -ErrorAction SilentlyContinue -and (Ask-Yes "GitHub CLI is missing. Install it so BlogLab self-heal can run automatically?")){
    winget install -e --id GitHub.cli
    if($LASTEXITCODE -eq 0){
      $ghCandidates=@("$env:ProgramFiles\GitHub CLI\gh.exe","$env:LOCALAPPDATA\Programs\GitHub CLI\gh.exe")
      foreach($g in $ghCandidates){ if(Test-Path $g){ $env:Path="$(Split-Path $g -Parent);$env:Path"; break } }
    }
  }
}
if(Get-Command gh -ErrorAction SilentlyContinue){
  & gh auth status 2>$null
  if($LASTEXITCODE -ne 0){
    Write-Host "GitHub CLI is installed but not authenticated." -ForegroundColor Yellow
    if(Ask-Yes "Open GitHub CLI login now?"){
      & gh auth login
    }
  }else{
    Write-Host "GitHub CLI: authenticated." -ForegroundColor Green
  }
}else{
  Write-Warning "GitHub CLI unavailable. BlogLab will be monitored, but GitHub self-heal dispatch remains AUTH_REQUIRED."
}

# 4. Project Visibility direct low-memory bootstrap.
& "$PSScriptRoot\connect-project-visibility.ps1" -ManagerRoot $root -Model "qwen2.5-coder:3b"

# 5. Colibri latest stable integration. Model download always needs explicit YES inside its installer.
if(Ask-Yes "Prepare the latest stable Colibri integration now?"){
  & "$PSScriptRoot\install-colibri-v2.ps1"
}else{
  Write-Host "Colibri setup skipped for now. Ollama remains fully active and Manager will show Colibri STANDBY." -ForegroundColor Yellow
}

# 6. Start the entire local stack and independent watchdog.
& "$PSScriptRoot\start-stack-v4.ps1"
Start-Sleep -Seconds 5

# 7. Verification.
& "$PSScriptRoot\doctor-v4.ps1"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host " INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Manager:            http://127.0.0.1:8787/control"
Write-Host "Project Visibility: http://127.0.0.1:8000/dashboard.html"
Write-Host ""
Write-Host "V4 will restart through Windows Startup + Watchdog."
Write-Host "A best-effort 5-minute Task Scheduler reconciler is also installed where Windows permits it."
Start-Process "http://127.0.0.1:8787/control"
