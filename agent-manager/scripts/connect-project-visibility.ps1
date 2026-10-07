param(
  [string]$ManagerRoot = "",
  [string]$ProjectRoot = "",
  [string]$Model = "qwen2.5-coder:3b"
)
$ErrorActionPreference="Stop"

if(-not $ManagerRoot){ $ManagerRoot=Split-Path $PSScriptRoot -Parent }
$ManagerRoot=(Resolve-Path $ManagerRoot).Path

function Test-Http([string]$Url,[int]$Timeout=5){
  try{ Invoke-RestMethod -Uri $Url -TimeoutSec $Timeout | Out-Null; return $true }catch{ return $false }
}
function Find-Python {
  if(Get-Command py -ErrorAction SilentlyContinue){ return @{Exe="py";Args=@("-3.12")} }
  $p="$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
  if(Test-Path $p){ return @{Exe=$p;Args=@()} }
  throw "Python 3.12 is required."
}
function Find-Ollama {
  $cmd=Get-Command ollama -ErrorAction SilentlyContinue
  if($cmd){ return $cmd.Source }
  $p="$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
  if(Test-Path $p){ return $p }
  throw "Ollama is required."
}

$python=Find-Python
$ollama=Find-Ollama
$ollamaDir=Split-Path $ollama -Parent
$env:Path="$ollamaDir;$env:Path"

if(-not (Test-Http "http://127.0.0.1:11434/api/tags")){
  Start-Process $ollama -ArgumentList "serve" -WindowStyle Hidden
  Start-Sleep -Seconds 4
}
if(-not (Test-Http "http://127.0.0.1:11434/api/tags")){ throw "Ollama API did not start." }

$tags=Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 10
if(@($tags.models.name) -notcontains $Model){
  Write-Host "Pulling local coding model $Model..."
  & $ollama pull $Model
  if($LASTEXITCODE -ne 0){ throw "Could not pull $Model." }
}

if(-not $ProjectRoot){
  $candidates=@(
    [Environment]::GetEnvironmentVariable("PROJECT_VISIBILITY_ROOT","User"),
    "$env:USERPROFILE\Documents\Project-Visibility",
    "$env:USERPROFILE\Documents\PROJEKT",
    "$env:USERPROFILE\Downloads\PROJEKT",
    "$env:USERPROFILE\Desktop\PROJEKT"
  ) | Where-Object { $_ }
  foreach($p in $candidates){
    if(Test-Path (Join-Path $p "api\requirements.txt")){ $ProjectRoot=$p; break }
  }
}
if(-not $ProjectRoot){
  if(-not (Get-Command git -ErrorAction SilentlyContinue)){ throw "Git for Windows is required to clone Project Visibility." }
  $ProjectRoot="$env:USERPROFILE\Documents\Project-Visibility"
  Write-Host "Cloning Project Visibility..."
  git clone https://github.com/DDAY2301/PROJEKT.git $ProjectRoot
  if($LASTEXITCODE -ne 0){ throw "Project Visibility clone failed." }
}
$ProjectRoot=(Resolve-Path $ProjectRoot).Path
Set-Location $ProjectRoot

$venv=Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if(-not (Test-Path $venv)){
  Write-Host "Creating Project Visibility Python environment..."
  & $python.Exe @($python.Args) -m venv .venv
  if($LASTEXITCODE -ne 0){ throw "Could not create Project Visibility venv." }
}
& $venv -m pip install --upgrade pip wheel setuptools
if($LASTEXITCODE -ne 0){ throw "Could not prepare pip." }
& $venv -m pip install --disable-pip-version-check -r "api\requirements.txt"
if($LASTEXITCODE -ne 0){ throw "Project Visibility dependency install failed." }

# Chromium is deterministic visual QA; the separate vision LLM is deliberately disabled on low-memory local operation.
try{
  $probe=& $venv -c "from pathlib import Path; from playwright.sync_api import sync_playwright; p=sync_playwright().start(); x=Path(p.chromium.executable_path); p.stop(); print('ok' if x.exists() else 'missing')"
  if($probe -ne "ok"){
    Write-Host "Installing Chromium visual QA engine..."
    & $venv -m playwright install chromium
  }
}catch{
  Write-Warning "Chromium QA install could not be verified; Project Visibility can still start."
}

$secretFile=Join-Path $ProjectRoot "api\data\.app-secret"
New-Item -ItemType Directory -Force (Split-Path $secretFile -Parent) | Out-Null
if(-not (Test-Path $secretFile)){
  $secret=& $venv -c "import secrets; print(secrets.token_urlsafe(48))"
  Set-Content -Path $secretFile -Value $secret -NoNewline -Encoding UTF8
}
$env:APP_SECRET=(Get-Content $secretFile -Raw).Trim()
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
$env:OLLAMA_MODEL=$Model
$env:VISUAL_QA_VISION="false"
$env:GITHUB_OWNER="DDAY2301"

if(Get-Command gh -ErrorAction SilentlyContinue){
  try{
    $token=(& gh auth token 2>$null).Trim()
    if($token){ $env:GITHUB_TOKEN=$token }
  }catch{}
}

[Environment]::SetEnvironmentVariable("PROJECT_VISIBILITY_ROOT",$ProjectRoot,"User")
[Environment]::SetEnvironmentVariable("PROJECT_VISIBILITY_HEALTH_URL","http://127.0.0.1:8000/health","User")
[Environment]::SetEnvironmentVariable("PROJECT_VISIBILITY_MODEL",$Model,"User")
[Environment]::SetEnvironmentVariable("OLLAMA_BASE_URL","http://127.0.0.1:11434","User")

# Apply the same values to this process so the very first Manager start can
# immediately use Project Visibility recovery without waiting for a new login shell.
$env:PROJECT_VISIBILITY_ROOT=$ProjectRoot
$env:PROJECT_VISIBILITY_HEALTH_URL="http://127.0.0.1:8000/health"
$env:PROJECT_VISIBILITY_MODEL=$Model
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434"

if(-not (Test-Http "http://127.0.0.1:8000/health" 2)){
  $listener=Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if($listener){
    throw "Port 8000 is already occupied but Project Visibility health is not responding. Stop the conflicting process first."
  }
  Start-Process $venv -ArgumentList @("-m","uvicorn","api.server:app","--host","127.0.0.1","--port","8000") -WorkingDirectory $ProjectRoot -WindowStyle Hidden
}

$deadline=(Get-Date).AddMinutes(3)
while((Get-Date) -lt $deadline -and -not (Test-Http "http://127.0.0.1:8000/health" 3)){
  Start-Sleep -Seconds 3
}
if(-not (Test-Http "http://127.0.0.1:8000/health" 5)){ throw "Project Visibility did not become healthy." }

Set-Location $ManagerRoot
Write-Host ""
Write-Host "Project Visibility CONNECTED" -ForegroundColor Green
Write-Host "Root:      $ProjectRoot"
Write-Host "Health:    http://127.0.0.1:8000/health"
Write-Host "Dashboard: http://127.0.0.1:8000/dashboard.html"
Write-Host "Model:     $Model"
Write-Host "Vision LLM: OFF (Chromium QA remains enabled)"
