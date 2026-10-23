param(
  [string]$Hostname = "control.bloglab.eu",
  [string]$TunnelName = "AgentManagerV4-Fleet",
  [switch]$SkipTunnel
)

$ErrorActionPreference="Stop"
$root=Split-Path $PSScriptRoot -Parent
Set-Location $root

function New-UrlToken([int]$Bytes=32){
  $data=New-Object byte[] $Bytes
  [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($data)
  return [Convert]::ToBase64String($data).TrimEnd('=').Replace('+','-').Replace('/','_')
}

function Ensure-UserSecret([string]$Name,[int]$Bytes=32){
  $value=[Environment]::GetEnvironmentVariable($Name,"User")
  if(-not $value){
    $value=New-UrlToken $Bytes
    [Environment]::SetEnvironmentVariable($Name,$value,"User")
  }
  Set-Item -Path ("Env:"+$Name) -Value $value
  return $value
}

$remotePassword=Ensure-UserSecret "FLEET_REMOTE_PASSWORD" 24
$localToken=Ensure-UserSecret "FLEET_LOCAL_TOKEN" 32
$fleetAgentToken=Ensure-UserSecret "FLEET_AGENT_TOKEN" 32

[Environment]::SetEnvironmentVariable("PV_FLEET_TOKEN",$localToken,"User")
[Environment]::SetEnvironmentVariable("BLOG_LAB_WORKER_URL","https://blog-lab.dan-grmusa.workers.dev","User")
[Environment]::SetEnvironmentVariable("FLEET_REMOTE_HOSTNAME",$Hostname,"User")
$env:PV_FLEET_TOKEN=$localToken
$env:BLOG_LAB_WORKER_URL="https://blog-lab.dan-grmusa.workers.dev"
$env:FLEET_REMOTE_HOSTNAME=$Hostname

Write-Host "Local Fleet secrets are configured in the Windows user environment." -ForegroundColor Green

$blogLabSecretSynced=$false
$gh=Get-Command gh -ErrorAction SilentlyContinue
if($gh){
  try{
    & gh auth status *> $null
    if($LASTEXITCODE -eq 0){
      $fleetAgentToken | & gh secret set FLEET_AGENT_TOKEN --repo DDAY2301/blog-lab
      if($LASTEXITCODE -ne 0){ throw "gh secret set failed" }
      $blogLabSecretSynced=$true
      Write-Host "GitHub secret FLEET_AGENT_TOKEN synchronized." -ForegroundColor Green
      & gh workflow run deploy-worker.yml --repo DDAY2301/blog-lab --ref main
      if($LASTEXITCODE -eq 0){
        Write-Host "BlogLab Worker redeploy requested." -ForegroundColor Green
      }else{
        Write-Warning "Could not trigger deploy-worker.yml. Trigger it manually after merge."
      }
    }else{
      Write-Warning "GitHub CLI is installed but not authenticated. Run: gh auth login"
    }
  }catch{
    Write-Warning "Could not sync FLEET_AGENT_TOKEN through GitHub CLI: $($_.Exception.Message)"
  }
}else{
  Write-Warning "GitHub CLI (gh) is not installed. FLEET_AGENT_TOKEN must be added as a repository secret before BlogLab fleet commands work."
}

if(-not $SkipTunnel){
  function Find-Cloudflared {
    $cmd=Get-Command cloudflared -ErrorAction SilentlyContinue
    if($cmd){ return $cmd }

    $candidates=@(
      "C:\Program Files (x86)\cloudflared\cloudflared.exe",
      "C:\Program Files\cloudflared\cloudflared.exe",
      "$env:LOCALAPPDATA\Microsoft\WinGet\Links\cloudflared.exe"
    )
    foreach($candidate in $candidates){
      if(Test-Path $candidate){ return Get-Item $candidate }
    }

    $wingetRoot="$env:LOCALAPPDATA\Microsoft\WinGet\Packages"
    if(Test-Path $wingetRoot){
      $found=Get-ChildItem $wingetRoot -Filter "cloudflared.exe" -File -Recurse -ErrorAction SilentlyContinue |
        Select-Object -First 1
      if($found){ return $found }
    }
    return $null
  }

  $cloudflared=Find-Cloudflared
  if(-not $cloudflared){
    $winget=Get-Command winget -ErrorAction SilentlyContinue
    if($winget){
      Write-Host "cloudflared is missing. Installing Cloudflare Tunnel with winget..." -ForegroundColor Cyan
      & winget install --id Cloudflare.cloudflared -e --source winget --accept-package-agreements --accept-source-agreements
      if($LASTEXITCODE -ne 0){
        Write-Warning "winget could not install Cloudflare.cloudflared."
      }
      $machinePath=[Environment]::GetEnvironmentVariable("Path","Machine")
      $userPath=[Environment]::GetEnvironmentVariable("Path","User")
      $env:Path="$machinePath;$userPath"
      $cloudflared=Find-Cloudflared
    }
  }
  if(-not $cloudflared){
    throw "cloudflared is still not available after automatic discovery/install. Run 'winget install --id Cloudflare.cloudflared -e' and rerun this setup."
  }

  $cf=if($cloudflared.Source){$cloudflared.Source}else{$cloudflared.FullName}
  $cfDir=Split-Path $cf -Parent
  if($cfDir -and -not (($env:Path -split ';') -contains $cfDir)){
    $env:Path="$env:Path;$cfDir"
  }
  Write-Host ("Using cloudflared: "+$cf) -ForegroundColor Green

  $cert=Join-Path $env:USERPROFILE ".cloudflared\cert.pem"
  if(-not (Test-Path $cert)){
    Write-Host "Cloudflare browser authorization is required once." -ForegroundColor Cyan
    & $cf tunnel login
    if($LASTEXITCODE -ne 0 -or -not (Test-Path $cert)){
      throw "Cloudflare tunnel login did not complete."
    }
  }

  $listRaw=& $cf tunnel list --output json 2>$null
  $tunnels=@()
  if($listRaw){ $tunnels=$listRaw | ConvertFrom-Json }
  $tunnel=$tunnels | Where-Object { $_.name -eq $TunnelName } | Select-Object -First 1
  if(-not $tunnel){
    & $cf tunnel create $TunnelName
    if($LASTEXITCODE -ne 0){ throw "Could not create Cloudflare tunnel $TunnelName" }
    $listRaw=& $cf tunnel list --output json 2>$null
    $tunnels=$listRaw | ConvertFrom-Json
    $tunnel=$tunnels | Where-Object { $_.name -eq $TunnelName } | Select-Object -First 1
  }
  if(-not $tunnel){ throw "Tunnel was created but its ID could not be resolved." }

  $tunnelId=[string]$tunnel.id
  $credentials=Join-Path $env:USERPROFILE (".cloudflared\"+$tunnelId+".json")
  if(-not (Test-Path $credentials)){ throw "Tunnel credentials file missing: $credentials" }

  $config=Join-Path $root "data\fleet-tunnel.yml"
  @"
tunnel: $tunnelId
credentials-file: $($credentials.Replace('\','/'))
ingress:
  - hostname: $Hostname
    service: http://127.0.0.1:8788
  - service: http_status:404
"@ | Set-Content -Path $config -Encoding UTF8

  [Environment]::SetEnvironmentVariable("FLEET_TUNNEL_CONFIG",$config,"User")
  [Environment]::SetEnvironmentVariable("FLEET_TUNNEL_NAME",$TunnelName,"User")
  $env:FLEET_TUNNEL_CONFIG=$config
  $env:FLEET_TUNNEL_NAME=$TunnelName

  Write-Host "Routing $Hostname to the Fleet tunnel..." -ForegroundColor Cyan
  & $cf tunnel route dns $TunnelName $Hostname
  if($LASTEXITCODE -ne 0){
    Write-Warning "DNS route may already exist. Verify $Hostname in Cloudflare DNS."
  }
}

Write-Host ""
Write-Host "Restarting the existing V4 stack so Project Visibility and all Fleet services inherit the new tokens..." -ForegroundColor Cyan
& "$PSScriptRoot\stop-stack-v4.ps1"
Start-Sleep -Seconds 2
& "$PSScriptRoot\start-stack-v4.ps1"

Write-Host ""
Write-Host "Verifying local Fleet Remote..." -ForegroundColor Cyan
$remoteDeadline=(Get-Date).AddSeconds(20)
$remoteHealth=$null
do{
  try{ $remoteHealth=Invoke-RestMethod "http://127.0.0.1:8788/health" -TimeoutSec 3 }catch{}
  if($remoteHealth -and $remoteHealth.ok){ break }
  Start-Sleep -Seconds 1
}while((Get-Date) -lt $remoteDeadline)
if(-not $remoteHealth -or -not $remoteHealth.ok){
  throw "Fleet Remote did not become healthy on 127.0.0.1:8788."
}

Write-Host "Verifying Project Visibility Fleet bridge..." -ForegroundColor Cyan
try{
  $pvBody=@{command="status"} | ConvertTo-Json -Compress
  $pvFleet=Invoke-RestMethod -Method Post "http://127.0.0.1:8000/internal/fleet/command" -Headers @{"x-fleet-token"=$localToken} -ContentType "application/json" -Body $pvBody -TimeoutSec 20
  if(-not $pvFleet.ok){ throw "Project Visibility Fleet bridge returned ok=false." }
  Write-Host "Project Visibility Fleet bridge OK." -ForegroundColor Green
}catch{
  throw "Project Visibility Fleet bridge is not ready. Pull DDAY2301/PROJEKT main into PROJECT_VISIBILITY_ROOT, then rerun this setup. Detail: $($_.Exception.Message)"
}

if($blogLabSecretSynced){
  Write-Host "Waiting for the BlogLab Worker to receive the Fleet service token..." -ForegroundColor Cyan
  $workerDeadline=(Get-Date).AddSeconds(120)
  $workerHealth=$null
  do{
    try{ $workerHealth=Invoke-RestMethod "$env:BLOG_LAB_WORKER_URL/health" -TimeoutSec 8 }catch{}
    if($workerHealth -and $workerHealth.fleet_agent_ready){ break }
    Start-Sleep -Seconds 8
  }while((Get-Date) -lt $workerDeadline)
  if($workerHealth -and $workerHealth.fleet_agent_ready){
    Write-Host "BlogLab Fleet bridge OK." -ForegroundColor Green
  }else{
    Write-Warning "BlogLab Worker is online but fleet_agent_ready is not true yet. The GitHub deploy may still be running; rerun setup or check deploy-worker.yml."
  }
}

Write-Host ""
Write-Host "Fleet Remote configured." -ForegroundColor Green
Write-Host "Local:  http://127.0.0.1:8788"
if(-not $SkipTunnel){ Write-Host ("Remote: https://"+$Hostname) -ForegroundColor Green }
Write-Host ""
Write-Host "Remote login password has been copied to the clipboard." -ForegroundColor Yellow
Set-Clipboard -Value $remotePassword
Write-Host "Paste it into the Fleet login page. Do not paste it into chat."
