$ErrorActionPreference="Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

# Conservative local inference defaults keep the 24/7 stack stable on 8 GB-class Windows PCs.
$env:OLLAMA_MAX_LOADED_MODELS="1"
$env:OLLAMA_NUM_PARALLEL="1"
$env:OLLAMA_KEEP_ALIVE="60s"
$env:OLLAMA_FAST_KEEP_ALIVE="60s"
$env:AGENT_MANAGER_CONTEXT="8192"
$env:AGENT_MANAGER_OLLAMA_KEEP_ALIVE="60s"

function Port-Up([int]$Port) {
  return [bool](Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1)
}
function Test-ManagerHealth {
  try{
    $r=Invoke-RestMethod "http://127.0.0.1:8787/health" -TimeoutSec 3
    return [bool]$r.ok
  }catch{ return $false }
}

function Start-Ollama {
  if (Port-Up 11434) { return }
  $ollama = Get-Command ollama -ErrorAction SilentlyContinue
  if (-not $ollama) {
    $candidate="$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    if (Test-Path $candidate) { $ollama = Get-Item $candidate }
  }
  if ($ollama) {
    $path = if($ollama.Source){$ollama.Source}else{$ollama.FullName}
    Start-Process $path -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
  }
}

function Start-Colibri {
  & "$PSScriptRoot\start-colibri.ps1"
  $url=[Environment]::GetEnvironmentVariable("COLIBRI_BASE_URL","User")
  $profile=[Environment]::GetEnvironmentVariable("AGENT_MANAGER_COLIBRI_PROFILE","User")
  $model=[Environment]::GetEnvironmentVariable("COLIBRI_MODEL","User")
  if($url){ $env:COLIBRI_BASE_URL=$url }
  if($profile){ $env:AGENT_MANAGER_COLIBRI_PROFILE=$profile }
  if($model){ $env:COLIBRI_MODEL=$model }
}

function Start-ProjectVisibility {
  if (Port-Up 8000) { return }
  $root=[Environment]::GetEnvironmentVariable("PROJECT_VISIBILITY_ROOT","User")
  if (-not $root) { $root=$env:PROJECT_VISIBILITY_ROOT }
  if (-not $root -or -not (Test-Path $root)) { return }
  $py=Join-Path $root ".venv\Scripts\python.exe"
  if (-not (Test-Path $py)) { return }
  $secret=Join-Path $root "api\data\.app-secret"
  $env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
  if (-not $env:PROJECT_VISIBILITY_MODEL) { $env:PROJECT_VISIBILITY_MODEL="qwen2.5-coder:3b" }
  $env:OLLAMA_MODEL=$env:PROJECT_VISIBILITY_MODEL
  if (Test-Path $secret) { $env:APP_SECRET=(Get-Content $secret -Raw).Trim() }
  $env:VISUAL_QA_VISION="false"
  Start-Process $py -ArgumentList @("-m","uvicorn","api.server:app","--host","127.0.0.1","--port","8000") -WorkingDirectory $root -WindowStyle Hidden
  Start-Sleep -Seconds 3
}

function Import-GitHubAuth {
  if(Get-Command gh -ErrorAction SilentlyContinue){
    try{
      $token=(& gh auth token 2>$null).Trim()
      if($token){ $env:GITHUB_TOKEN=$token; $env:GH_TOKEN=$token }
    }catch{}
  }
}

function Start-Manager {
  $py=Join-Path (Get-Location) ".venv\Scripts\python.exe"
  if (-not (Test-Path $py)) { throw "Agent Manager venv missing. Run install-agent-manager.ps1 first." }

  if ((Port-Up 8787) -and -not (Test-ManagerHealth)) {
    Write-Warning "Manager owns/listens on 8787 but health is unresponsive. Running safe reconciler..."
    & $py -m manager.reconcile_v4 --manager
    if($LASTEXITCODE -ne 0){ throw "Port 8787 is not owned by the configured Agent Manager; refusing to terminate it." }
    Start-Sleep -Seconds 1
  }

  if (-not (Port-Up 8787)) {
    Start-Process $py -ArgumentList "run.py" -WorkingDirectory (Get-Location) -WindowStyle Hidden
    $deadline=(Get-Date).AddSeconds(20)
    while((Get-Date) -lt $deadline -and -not (Test-ManagerHealth)){ Start-Sleep -Milliseconds 750 }
    if(-not (Test-ManagerHealth)){ throw "Agent Manager process started but health did not recover." }
  }

  $guardian = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'manager.guardian_v3' } | Select-Object -First 1
  if (-not $guardian) {
    Start-Process $py -ArgumentList @("-m","manager.guardian_v3") -WorkingDirectory (Get-Location) -WindowStyle Hidden
  }
}

Import-GitHubAuth
Start-Ollama
Start-Colibri
Start-ProjectVisibility
Start-Manager
& "$PSScriptRoot\start-watchdog-v4.ps1"

Write-Host ""
Write-Host "Agent Manager V4 24/7 stack" -ForegroundColor Cyan
foreach($item in @(
  @{n="Ollama";p=11434},
  @{n="Colibri";p=8790},
  @{n="Project Visibility";p=8000},
  @{n="Agent Manager";p=8787}
)){
  $state=if(Port-Up $item.p){"UP"}else{"STANDBY/OFF"}
  Write-Host ("{0,-20} {1,-12} port {2}" -f $item.n,$state,$item.p)
}
if (Port-Up 8787) {
  Write-Host "Dashboard: http://127.0.0.1:8787/control" -ForegroundColor Green
}
