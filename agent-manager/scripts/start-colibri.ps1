$ErrorActionPreference="Stop"

# Do not use $home here: PowerShell treats variable names case-insensitively,
# so $home collides with the built-in read-only $HOME variable.
$managerRoot=Split-Path $PSScriptRoot -Parent
$colibriHome=[Environment]::GetEnvironmentVariable("COLIBRI_HOME","User")
if(-not $colibriHome -or -not (Test-Path $colibriHome)){
  $colibriHome=Join-Path $managerRoot "data\colibri-src"
}

if(-not (Test-Path (Join-Path $colibriHome "c\coli"))){
  Write-Host "Colibri STANDBY: official control script not installed." -ForegroundColor Yellow
  exit 0
}

$profile=[Environment]::GetEnvironmentVariable("AGENT_MANAGER_COLIBRI_PROFILE","User")
if($profile -eq "decision-laya"){
  $os=Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
  if($os){
    $freeGB=[math]::Round(($os.FreePhysicalMemory * 1KB) / 1GB,2)
    if($freeGB -lt 2.2){
      Write-Host "Colibri Laya STANDBY: only $freeGB GB RAM is free; 2.2 GB safety threshold required." -ForegroundColor Yellow
      exit 0
    }
  }
}

Push-Location $colibriHome
try {
  $statusRaw=& py -3 c\coli status --json 2>$null
  $status=$null
  try{ $status=$statusRaw | ConvertFrom-Json }catch{}

  if($status -and $status.server -and $status.server.state -eq "ready"){
    $url=$status.server.urls.openai_base_url
    if($url){
      [Environment]::SetEnvironmentVariable("COLIBRI_BASE_URL",$url,"User")
      $env:COLIBRI_BASE_URL=$url
    }
    Write-Host "Colibri already READY: $url" -ForegroundColor Green
    exit 0
  }

  $setupReady=$false
  if($status -and $status.install){
    $setupReady=($status.install.phase -in @("ready","started"))
  }

  if(-not $setupReady){
    Write-Host "Colibri STANDBY: no configured model. Run INSTALL-COLIBRI-V2.bat later if desired." -ForegroundColor Yellow
    exit 0
  }

  & py -3 c\coli start --background --no-browser
  if($LASTEXITCODE -ne 0){ throw "Colibri start failed." }

  $deadline=(Get-Date).AddMinutes(3)
  do{
    Start-Sleep -Seconds 3
    $raw=& py -3 c\coli status --json 2>$null
    try{ $status=$raw | ConvertFrom-Json }catch{ $status=$null }
  }while((Get-Date) -lt $deadline -and (-not $status -or $status.server.state -ne "ready"))

  if($status -and $status.server.state -eq "ready"){
    $url=$status.server.urls.openai_base_url
    if($url){
      [Environment]::SetEnvironmentVariable("COLIBRI_BASE_URL",$url,"User")
      $env:COLIBRI_BASE_URL=$url
    }
    Write-Host "Colibri READY: $url" -ForegroundColor Green
  }else{
    Write-Warning "Colibri did not reach READY. Ollama fallback will remain active."
  }
}
finally {
  Pop-Location
}
