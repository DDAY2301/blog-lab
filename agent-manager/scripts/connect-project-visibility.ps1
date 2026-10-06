param(
  [string]$ManagerRoot = "",
  [string]$ProjectRoot = "",
  [string]$Model = "qwen2.5-coder:3b",
  [string]$VisualModel = "qwen2.5vl:3b"
)
$ErrorActionPreference="Stop"
if (-not $ManagerRoot) { $ManagerRoot = Split-Path $PSScriptRoot -Parent }
$ManagerRoot=(Resolve-Path $ManagerRoot).Path

function Test-Http([string]$Url,[int]$Timeout=5) {
  try { Invoke-RestMethod -Uri $Url -TimeoutSec $Timeout | Out-Null; return $true } catch { return $false }
}
function Find-Ollama {
  $cmd=Get-Command ollama -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $known=@(
    "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
    "$env:ProgramFiles\Ollama\ollama.exe"
  )
  foreach($p in $known){ if(Test-Path $p){ return $p } }
  throw "Ollama executable was not found."
}

$ollama=Find-Ollama
$ollamaDir=Split-Path $ollama -Parent
$env:Path="$ollamaDir;$env:Path"
if (-not (Test-Http "http://127.0.0.1:11434/api/tags")) {
  Start-Process -FilePath $ollama -ArgumentList "serve" -WindowStyle Hidden
  Start-Sleep -Seconds 4
}
if (-not (Test-Http "http://127.0.0.1:11434/api/tags")) { throw "Ollama API did not start." }

$tags=Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 10
if (@($tags.models.name) -notcontains $Model) {
  Write-Host "Pulling $Model..."
  & $ollama pull $Model
  if($LASTEXITCODE -ne 0){ throw "Could not pull $Model" }
}

if (-not $ProjectRoot) {
  $candidates=@(
    "$env:USERPROFILE\Documents\Project-Visibility",
    "$env:USERPROFILE\Documents\PROJEKT",
    "$env:USERPROFILE\Downloads\PROJEKT",
    "$env:USERPROFILE\Desktop\PROJEKT"
  )
  foreach($p in $candidates){
    if(Test-Path (Join-Path $p "api\start-local.ps1")) { $ProjectRoot=$p; break }
  }
}
if (-not $ProjectRoot) {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Git is required. Install Git for Windows first." }
  $ProjectRoot="$env:USERPROFILE\Documents\Project-Visibility"
  Write-Host "Cloning Project Visibility to $ProjectRoot..."
  git clone https://github.com/DDAY2301/PROJEKT.git $ProjectRoot
  if($LASTEXITCODE -ne 0){ throw "Git clone failed." }
}
$ProjectRoot=(Resolve-Path $ProjectRoot).Path

[Environment]::SetEnvironmentVariable("PROJECT_VISIBILITY_ROOT",$ProjectRoot,"User")
[Environment]::SetEnvironmentVariable("PROJECT_VISIBILITY_HEALTH_URL","http://127.0.0.1:8000/health","User")
[Environment]::SetEnvironmentVariable("OLLAMA_BASE_URL","http://127.0.0.1:11434","User")

$ghToken=$null
if(Get-Command gh -ErrorAction SilentlyContinue){
  try { $ghToken=(& gh auth token 2>$null).Trim() } catch {}
}
if($ghToken){ $env:GITHUB_TOKEN=$ghToken }

$helper=Join-Path $ManagerRoot "data\start-project-visibility.ps1"
New-Item -ItemType Directory -Force (Split-Path $helper -Parent) | Out-Null
$skip = if($ghToken){""}else{" -SkipGitHub"}
$helperText = @'
$ErrorActionPreference='Stop'
$env:Path='__OLLAMA_DIR__;' + $env:Path
$env:OLLAMA_KEEP_ALIVE='60s'
$token=$null
if(Get-Command gh -ErrorAction SilentlyContinue){ try { $token=(& gh auth token 2>$null).Trim() } catch {} }
if($token){ $env:GITHUB_TOKEN=$token }
Set-Location '__PROJECT_ROOT__'
& '.\api\start-local.ps1' -Model '__MODEL__' -VisualModel '__VISUAL__'__SKIP__
'@
$helperText=$helperText.Replace('__OLLAMA_DIR__',$ollamaDir).Replace('__PROJECT_ROOT__',$ProjectRoot).Replace('__MODEL__',$Model).Replace('__VISUAL__',$VisualModel).Replace('__SKIP__',$skip)
$helperText | Set-Content -Path $helper -Encoding UTF8

if (-not (Test-Http "http://127.0.0.1:8000/health" 2)) {
  Start-Process powershell.exe -ArgumentList @("-NoProfile","-WindowStyle","Minimized","-ExecutionPolicy","Bypass","-File",$helper)
  Write-Host "Starting Project Visibility. First run may install Python packages, Chromium and the vision model..."
}

$deadline=(Get-Date).AddMinutes(10)
while((Get-Date) -lt $deadline){
  if(Test-Http "http://127.0.0.1:8000/health" 3){ break }
  Start-Sleep -Seconds 5
}
if(-not (Test-Http "http://127.0.0.1:8000/health" 5)){
  throw "Project Visibility did not become healthy within 10 minutes. Open the minimized Project Visibility PowerShell window for the exact error."
}

$startup=[Environment]::GetFolderPath("Startup")
$pvCmd=Join-Path $startup "ProjectVisibility.cmd"
@"
@echo off
start "" /min powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "$helper"
"@ | Set-Content -Path $pvCmd -Encoding ASCII

Set-Location $ManagerRoot
& ".\scripts\restart-agent-manager.ps1"
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "CONNECTED" -ForegroundColor Green
Write-Host "Agent Manager:      http://127.0.0.1:8787/health"
Write-Host "Project Visibility: http://127.0.0.1:8000/health"
Write-Host "Ollama:             http://127.0.0.1:11434/api/tags"
Write-Host "Project root:       $ProjectRoot"
if($ghToken){ Write-Host "GitHub publishing:  CONNECTED via existing gh auth" } else { Write-Host "GitHub publishing:  SKIPPED - gh auth not available" }
