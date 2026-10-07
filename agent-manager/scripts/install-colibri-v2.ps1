param(
  [string]$InstallDir = "",
  [ValidateSet("ask","engine-only","decision","recommended")]
  [string]$Mode = "ask"
)
$ErrorActionPreference = "Stop"

$managerRoot=Split-Path $PSScriptRoot -Parent
if(-not $InstallDir){
  # Keep Colibri inside the existing Agent Manager installation.
  $InstallDir=Join-Path $managerRoot "data\colibri-src"
}

function Require([string]$Name,[string]$Hint) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) { throw "$Name is required. $Hint" }
}
Require "git" "Install Git for Windows."
Require "py" "Install Python 3.12 and reopen PowerShell."

$release=Invoke-RestMethod "https://api.github.com/repos/JustVugg/colibri/releases/latest" -Headers @{"User-Agent"="AgentManagerV4"}
$tag=$release.tag_name
Write-Host "Colibri latest stable: $tag" -ForegroundColor Cyan
Write-Host "Installing inside existing Agent Manager: $InstallDir" -ForegroundColor Cyan

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
Write-Host "=== COLIBRI HARDWARE PREFLIGHT ===" -ForegroundColor Cyan
& py -3 c\setup_hw.py --json
if($LASTEXITCODE -ne 0){ Pop-Location; throw "Colibri hardware detection failed." }
Write-Host ""
Write-Host "=== COLIBRI GENERATIVE MODELS THAT FIT ===" -ForegroundColor Cyan
& py -3 c\coli setup --list
if($LASTEXITCODE -ne 0){ Pop-Location; throw "Colibri model compatibility scan failed." }
Pop-Location

[Environment]::SetEnvironmentVariable("COLIBRI_HOME",$InstallDir,"User")
[Environment]::SetEnvironmentVariable("AGENT_MANAGER_AI_PRIORITY","colibri,ollama","User")

if($Mode -eq "ask"){
  Write-Host ""
  Write-Host "Recommended Agent Manager architecture for this PC:" -ForegroundColor Green
  Write-Host "  LAYA        = Colibri decision/triage engine (~842 MB download, ~1.7 GB RAM when active)"
  Write-Host "                + Ollama qwen2.5-coder:3b for explanations/code repair."
  Write-Host "  RECOMMENDED = Colibri's recommended generative model (can be tens/hundreds of GB)."
  Write-Host "  NONE        = install Colibri control layer only; keep Colibri STANDBY."
  $choice=(Read-Host "Type LAYA, RECOMMENDED, or NONE").Trim().ToUpperInvariant()
  if($choice -eq "LAYA"){ $Mode="decision" }
  elseif($choice -eq "RECOMMENDED"){ $Mode="recommended" }
  else{ $Mode="engine-only" }
}

if($Mode -eq "engine-only"){
  Write-Host "Colibri control layer installed in STANDBY. Ollama remains active." -ForegroundColor Yellow
  exit 0
}

$occupied=Get-NetTCPConnection -State Listen -LocalPort 8790 -ErrorAction SilentlyContinue
if($occupied){ throw "Port 8790 is already in use. Stop the conflicting process before configuring Colibri." }

if($Mode -eq "decision"){
  $managerPy=Join-Path $managerRoot ".venv\Scripts\python.exe"
  if(-not (Test-Path $managerPy)){ throw "Agent Manager Python environment is required before installing Laya." }

  $modelDir=Join-Path $managerRoot "data\models\laya"
  New-Item -ItemType Directory -Force $modelDir | Out-Null
  Write-Host "Installing Hugging Face downloader into the existing Agent Manager venv..."
  & $managerPy -m pip install --disable-pip-version-check "huggingface_hub>=0.35,<2"
  if($LASTEXITCODE -ne 0){ throw "Could not install huggingface_hub." }

  $env:AGENT_MANAGER_LAYA_DIR=$modelDir

  # Windows PowerShell 5.1 can mangle multiline native-command arguments passed to python -c.
  # Keep the Python payload on one line so quoting is deterministic.
  $pyCode='from huggingface_hub import snapshot_download; import os; snapshot_download(repo_id="convaiinnovations/laya", local_dir=os.environ["AGENT_MANAGER_LAYA_DIR"], allow_patterns=["model.safetensors","rl_agent_config.json","encoder/*","tokenizer/*"])'

  Write-Host "Downloading Colibri Laya decision checkpoint (~842 MB) into existing Manager data..."
  & $managerPy -c $pyCode
  if($LASTEXITCODE -ne 0){ throw "Laya checkpoint download failed." }

  Push-Location $InstallDir
  Write-Host "Configuring Colibri System One decision service..."
  & py -3 c\coli setup --yes --model-dir $modelDir --no-start --host 127.0.0.1 --port 8790
  if($LASTEXITCODE -ne 0){ Pop-Location; throw "Colibri Laya setup failed for $modelDir." }
  Pop-Location

  [Environment]::SetEnvironmentVariable("AGENT_MANAGER_COLIBRI_PROFILE","decision-laya","User")
  [Environment]::SetEnvironmentVariable("COLIBRI_MODEL","laya","User")
  [Environment]::SetEnvironmentVariable("COLIBRI_MODEL_PATH",$modelDir,"User")

  $os=Get-CimInstance Win32_OperatingSystem
  $freeGB=[math]::Round(($os.FreePhysicalMemory * 1KB) / 1GB,2)
  Write-Host "Laya configured inside existing Agent Manager. Current free RAM: $freeGB GB." -ForegroundColor Green
  if($freeGB -lt 2.2){
    Write-Warning "Colibri will stay STANDBY until at least ~2.2 GB RAM is free. Ollama remains active meanwhile."
  }else{
    Write-Host "Enough free RAM detected for the lightweight decision engine."
  }
  exit 0
}

if($Mode -eq "recommended"){
  $answer=Read-Host "Colibri's recommended generative model may download tens or hundreds of GB. Type YES to continue"
  if($answer -ne "YES"){
    Write-Host "Large model download cancelled. Colibri remains STANDBY." -ForegroundColor Yellow
    exit 0
  }
  Push-Location $InstallDir
  & py -3 c\coli setup --yes --no-start --host 127.0.0.1 --port 8790
  if($LASTEXITCODE -ne 0){ Pop-Location; throw "Colibri setup failed. Run coli logs --install." }
  Pop-Location
  [Environment]::SetEnvironmentVariable("AGENT_MANAGER_COLIBRI_PROFILE","generative","User")
  Write-Host "Colibri recommended generative model configured inside existing Agent Manager." -ForegroundColor Green
}
