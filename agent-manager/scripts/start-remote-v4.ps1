$ErrorActionPreference="Stop"
$root=Split-Path $PSScriptRoot -Parent
Set-Location $root

function Port-Up([int]$Port) {
  return [bool](Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1)
}

if(Port-Up 8788){
  try{
    $health=Invoke-RestMethod "http://127.0.0.1:8788/health" -TimeoutSec 3
    if($health.service -eq "agent-manager-fleet-remote"){
      Write-Host "Fleet Remote already healthy on port 8788."
      exit 0
    }
  }catch{}
  throw "Port 8788 is already in use by an unknown service."
}

foreach($name in @(
  "FLEET_REMOTE_PASSWORD",
  "FLEET_LOCAL_TOKEN",
  "FLEET_AGENT_TOKEN",
  "BLOG_LAB_WORKER_URL",
  "FLEET_REMOTE_HOSTNAME",
  "FLEET_TUNNEL_CONFIG",
  "FLEET_TUNNEL_NAME"
)){
  $value=[Environment]::GetEnvironmentVariable($name,"User")
  if($value){ Set-Item -Path ("Env:"+$name) -Value $value }
}
# Project Visibility consumes the same host-local token.
if($env:FLEET_LOCAL_TOKEN){ $env:PV_FLEET_TOKEN=$env:FLEET_LOCAL_TOKEN }

$py=Join-Path $root ".venv\Scripts\python.exe"
if(-not (Test-Path $py)){ throw "Agent Manager venv missing." }

Start-Process $py -ArgumentList @(
  "-m","uvicorn","manager.remote_v4:app",
  "--host","127.0.0.1","--port","8788"
) -WorkingDirectory $root -WindowStyle Hidden

$deadline=(Get-Date).AddSeconds(15)
do{
  Start-Sleep -Milliseconds 500
  try{
    $health=Invoke-RestMethod "http://127.0.0.1:8788/health" -TimeoutSec 2
    if($health.ok){
      Write-Host "Fleet Remote UP on 127.0.0.1:8788" -ForegroundColor Green
      exit 0
    }
  }catch{}
}while((Get-Date) -lt $deadline)

throw "Fleet Remote process started but health did not become ready."
