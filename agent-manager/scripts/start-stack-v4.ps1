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

function Get-ManagerHealth {
  try {
    return Invoke-RestMethod "http://127.0.0.1:8787/health" -TimeoutSec 3
  } catch {
    return $null
  }
}

function Test-ManagerHealth {
  $r=Get-ManagerHealth
  return [bool]($r -and $r.ok)
}

function Stop-LegacyV3Manager {
  $health=Get-ManagerHealth
  if(-not $health){ return $false }

  $version=[string]$health.version
  $mode=[string]$health.mode
  if(-not ($version -like "3.*" -and $mode -eq "maximum-local")){
    return $false
  }

  Write-Host "Legacy Agent Manager V3 detected on port 8787. Upgrading to V4..." -ForegroundColor Yellow

  $listeners=Get-NetTCPConnection -State Listen -LocalPort 8787 -ErrorAction SilentlyContinue
  foreach($listener in $listeners){
    if($listener.OwningProcess){
      try{
        $proc=Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
        if($proc -and $proc.CommandLine -match 'run\.py'){
          Stop-Process -Id $listener.OwningProcess -Force -ErrorAction Stop
        }else{
          throw "Port 8787 reports the V3 signature but the listener is not a recognized run.py process."
        }
      }catch{
        throw "Could not stop verified legacy V3 listener: $($_.Exception.Message)"
      }
    }
  }

  # A legacy Guardian could otherwise bring the old V3 process back.
  Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'manager\.guardian_v3' } |
    ForEach-Object {
      try { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } catch {}
    }

  $deadline=(Get-Date).AddSeconds(10)
  while((Get-Date) -lt $deadline -and (Port-Up 8787)){ Start-Sleep -Milliseconds 300 }
  if(Port-Up 8787){ throw "Legacy V3 listener did not release port 8787." }

  Write-Host "Legacy V3 stopped. V4 can now take ownership of port 8787." -ForegroundColor Green
  return $true
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
  try {
    & "$PSScriptRoot\start-colibri.ps1"
  } catch {
    Write-Warning "Colibri startup failed: $($_.Exception.Message)"
    Write-Warning "Continuing with Ollama fallback so the 24/7 Manager can still start."
  }

  $url=[Environment]::GetEnvironmentVariable("COLIBRI_BASE_URL","User")
  $profile=[Environment]::GetEnvironmentVariable("AGENT_MANAGER_COLIBRI_PROFILE","User")
  $model=[Environment]::GetEnvironmentVariable("COLIBRI_MODEL","User")
  if($url){ $env:COLIBRI_BASE_URL=$url }
  if($profile){ $env:AGENT_MANAGER_COLIBRI_PROFILE=$profile }
  if($model){ $env:COLIBRI_MODEL=$model }
}

function Start-ProjectVisibility {
  if (Port-Up 8000) {
    try {
      $health=Invoke-RestMethod "http://127.0.0.1:8000/health" -TimeoutSec 4
      if ($health -and $health.ok) {
        Write-Host "Project Visibility already healthy on port 8000." -ForegroundColor Green
        return
      }
    } catch {}
    Write-Warning "Port 8000 is occupied but Project Visibility health is not confirmed. Refusing to start a duplicate service."
    return
  }

  $hint=[Environment]::GetEnvironmentVariable("PROJECT_VISIBILITY_ROOT","User")
  if (-not $hint) { $hint=$env:PROJECT_VISIBILITY_ROOT }
  try {
    $resolver=Join-Path $PSScriptRoot "resolve-project-visibility-root.ps1"
    if ($hint) { $root=& $resolver -ProjectRoot $hint -Persist }
    else { $root=& $resolver -Persist }
  } catch {
    Write-Warning ("Project Visibility not connected: " + $_.Exception.Message)
    return
  }

  $root=[string]$root
  $py=Join-Path $root ".venv\Scripts\python.exe"
  if (-not (Test-Path -LiteralPath $py -PathType Leaf)) {
    Write-Warning "Project Visibility checkout located at '$root' but its .venv is missing. Use the existing connect-project-visibility.ps1 -ProjectRoot path to install dependencies."
    return
  }

  $env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
  if (-not $env:PROJECT_VISIBILITY_MODEL) { $env:PROJECT_VISIBILITY_MODEL="qwen2.5-coder:3b" }
  $env:OLLAMA_MODEL=$env:PROJECT_VISIBILITY_MODEL
  foreach ($secretSuffix in @("api\data\app-secret.txt","api\data\.app-secret")) {
    $secret=Join-Path $root $secretSuffix
    if (Test-Path -LiteralPath $secret -PathType Leaf) {
      $env:APP_SECRET=(Get-Content -LiteralPath $secret -Raw).Trim()
      break
    }
  }
  $env:VISUAL_QA_VISION="false"
  $fleetToken=[Environment]::GetEnvironmentVariable("FLEET_LOCAL_TOKEN","User")
  if (-not $fleetToken) { $fleetToken=[Environment]::GetEnvironmentVariable("PV_FLEET_TOKEN","User") }
  if ($fleetToken) { $env:PV_FLEET_TOKEN=$fleetToken }

  try {
    $pvProcess=Start-Process $py -ArgumentList @("-m","uvicorn","api.server:app","--host","127.0.0.1","--port","8000") -WorkingDirectory $root -WindowStyle Hidden -PassThru
    $deadline=(Get-Date).AddSeconds(15)
    while ((Get-Date) -lt $deadline) {
      try {
        $health=Invoke-RestMethod "http://127.0.0.1:8000/health" -TimeoutSec 2
        if ($health -and $health.ok) {
          Write-Host "Project Visibility connected at $root" -ForegroundColor Green
          return
        }
      } catch {}
      $pvProcess.Refresh()
      if ($pvProcess.HasExited) { break }
      Start-Sleep -Seconds 1
    }
    Write-Warning "Project Visibility was launched from '$root' but health is not confirmed. Run the existing API in a visible terminal to inspect startup errors."
  } catch {
    Write-Warning ("Project Visibility startup failed: " + $_.Exception.Message)
  }
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

  if(Port-Up 8787){
    $health=Get-ManagerHealth

    if($health -and ([string]$health.version -like "3.*") -and ([string]$health.mode -eq "maximum-local")){
      [void](Stop-LegacyV3Manager)
    }
    elseif($health -and ([string]$health.version -like "4.*")){
      Write-Host "Agent Manager V4 already healthy on port 8787."
    }
    elseif(-not $health){
      Write-Warning "Port 8787 is listening but Manager health is unresponsive. Running safe ownership reconciler..."
      & $py -m manager.reconcile_v4 --manager
      if($LASTEXITCODE -ne 0){ throw "Port 8787 is not owned by this Agent Manager; refusing to terminate it." }
      Start-Sleep -Seconds 1
    }
    else{
      throw "Unexpected service is listening on port 8787. Refusing to replace it automatically."
    }
  }

  if (-not (Port-Up 8787)) {
    Start-Process $py -ArgumentList "run.py" -WorkingDirectory (Get-Location) -WindowStyle Hidden
    $deadline=(Get-Date).AddSeconds(20)
    while((Get-Date) -lt $deadline -and -not (Test-ManagerHealth)){ Start-Sleep -Milliseconds 750 }
    if(-not (Test-ManagerHealth)){ throw "Agent Manager process started but health did not recover." }

    $health=Get-ManagerHealth
    if(-not $health -or -not ([string]$health.version -like "4.*")){
      throw "Port 8787 came up, but it is not Agent Manager V4."
    }
  }

  $guardian = Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match 'manager\.guardian_v3' } |
    Select-Object -First 1
  if (-not $guardian) {
    Start-Process $py -ArgumentList @("-m","manager.guardian_v3") -WorkingDirectory (Get-Location) -WindowStyle Hidden
  }
}

function Start-RemoteControl {
  try {
    & "$PSScriptRoot\start-remote-v4.ps1"
  } catch {
    Write-Warning "Fleet Remote startup failed: $($_.Exception.Message)"
  }
}

function Start-FleetTunnel {
  $config=[Environment]::GetEnvironmentVariable("FLEET_TUNNEL_CONFIG","User")
  if(-not $config -or -not (Test-Path $config)){ return }

  $existing=Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "cloudflared*" -and $_.CommandLine -match [regex]::Escape($config) } |
    Select-Object -First 1
  if($existing){ return }

  $cloudflared=Get-Command cloudflared -ErrorAction SilentlyContinue
  if(-not $cloudflared){
    $candidate="C:\Program Files (x86)\cloudflared\cloudflared.exe"
    if(Test-Path $candidate){ $cloudflared=Get-Item $candidate }
  }
  if(-not $cloudflared){
    Write-Warning "Fleet tunnel config exists but cloudflared is not installed."
    return
  }
  $cf=if($cloudflared.Source){$cloudflared.Source}else{$cloudflared.FullName}
  Start-Process $cf -ArgumentList @("tunnel","--config",$config,"run") -WindowStyle Hidden
  Start-Sleep -Seconds 2
}

Import-GitHubAuth
Start-Ollama
Start-Colibri
Start-ProjectVisibility
Start-Manager
Start-RemoteControl
Start-FleetTunnel
& "$PSScriptRoot\start-watchdog-v4.ps1"

Write-Host ""
Write-Host "Agent Manager V4 24/7 stack" -ForegroundColor Cyan
foreach($item in @(
  @{n="Ollama";p=11434},
  @{n="Colibri";p=8790},
  @{n="Project Visibility";p=8000},
  @{n="Agent Manager";p=8787},
  @{n="Fleet Remote";p=8788}
)){
  $state=if(Port-Up $item.p){"UP"}else{"STANDBY/OFF"}
  Write-Host ("{0,-20} {1,-12} port {2}" -f $item.n,$state,$item.p)
}
if (Port-Up 8787) {
  $health=Get-ManagerHealth
  Write-Host ("Manager version: {0}" -f $health.version) -ForegroundColor Green
  Write-Host "Dashboard: http://127.0.0.1:8787/control" -ForegroundColor Green
  if(Port-Up 8788){
    Write-Host "Fleet Remote: http://127.0.0.1:8788" -ForegroundColor Green
    $hostName=[Environment]::GetEnvironmentVariable("FLEET_REMOTE_HOSTNAME","User")
    if($hostName){ Write-Host ("Remote URL: https://"+$hostName) -ForegroundColor Green }
  }
}
