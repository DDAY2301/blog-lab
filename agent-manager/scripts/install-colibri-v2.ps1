param(
  [string]$InstallDir = "$env:LOCALAPPDATA\AgentManager\colibri-src",
  [switch]$InstallRecommended
)
$ErrorActionPreference = "Stop"

function Require([string]$Name,[string]$Hint) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) { throw "$Name is required. $Hint" }
}
Require "git" "Install Git for Windows."
Require "py" "Install Python 3.12 and reopen PowerShell."

$api="https://api.github.com/repos/JustVugg/colibri/releases/latest"
$release=Invoke-RestMethod $api -Headers @{"User-Agent"="AgentManagerV4"}
$tag=$release.tag_name
Write-Host "Colibri latest stable: $tag" -ForegroundColor Cyan

if (-not (Test-Path (Join-Path $InstallDir ".git"))) {
  New-Item -ItemType Directory -Force (Split-Path $InstallDir -Parent) | Out-Null
  git clone --depth 1 --branch $tag https://github.com/JustVugg/colibri.git $InstallDir
  if($LASTEXITCODE -ne 0){ throw "Colibri clone failed." }
} else {
  Push-Location $InstallDir
  git fetch --tags --force
  git checkout -f $tag
  Pop-Location
}

Push-Location $InstallDir
Write-Host ""
Write-Host "=== HARDWARE ===" -ForegroundColor Cyan
& py -3 c\setup_hw.py --json
if($LASTEXITCODE -ne 0){ throw "Colibri hardware detection failed." }

Write-Host ""
Write-Host "=== MODELS THAT FIT THIS PC ===" -ForegroundColor Cyan
& py -3 c\coli setup --list
if($LASTEXITCODE -ne 0){ throw "Colibri model compatibility scan failed." }

[Environment]::SetEnvironmentVariable("COLIBRI_HOME",$InstallDir,"User")
[Environment]::SetEnvironmentVariable("AGENT_MANAGER_AI_PRIORITY","colibri,ollama","User")

$doInstall=$InstallRecommended
if(-not $InstallRecommended){
  $answer=Read-Host "Install Colibri's recommended model now? This may download tens or hundreds of GB. Type YES to continue"
  $doInstall=($answer -eq "YES")
}

if($doInstall){
  $occupied=Get-NetTCPConnection -State Listen -LocalPort 8790 -ErrorAction SilentlyContinue
  if($occupied){ throw "Port 8790 is already in use. Stop that process before configuring Colibri." }
  Write-Host "Installing the model Colibri recommends for this hardware..." -ForegroundColor Yellow
  & py -3 c\coli setup --yes --no-start --host 127.0.0.1 --port 8790
  if($LASTEXITCODE -ne 0){ throw "Colibri setup failed. Run: py -3 c\coli logs --install" }
  $status=& py -3 c\coli status --json
  $status | Set-Content (Join-Path $InstallDir "agent-manager-status.json") -Encoding UTF8
  Write-Host "Colibri model setup complete." -ForegroundColor Green
} else {
  Write-Host "Colibri engine/control layer installed in STANDBY. Ollama remains the active fallback." -ForegroundColor Yellow
  Write-Host "Run this script again when you want to install the recommended Colibri model."
}
Pop-Location

Write-Host "Colibri integration ready at: $InstallDir" -ForegroundColor Green
