$ErrorActionPreference="Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

function Port-Up([int]$Port) {
  return [bool](Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1)
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
  if($url){ $env:COLIBRI_BASE_URL=$url }
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
  if (-not (Port-Up 8787)) {
    Start-Process $py -ArgumentList "run.py" -WorkingDirectory (Get-Location) -WindowStyle Hidden
    Start-Sleep -Seconds 3
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
