param(
  [Parameter(Mandatory=$true)]
  [string]$Recipient,
  [int]$IntervalHours = 3,
  [switch]$EnableCommands,
  [string]$AllowedSenders = "",
  [int]$CommandPollSeconds = 30
)

$ErrorActionPreference="Stop"
$managerRoot=Split-Path $PSScriptRoot -Parent
Set-Location $managerRoot

$py=Join-Path $managerRoot ".venv\Scripts\python.exe"
if(-not (Test-Path $py)){
  throw "Agent Manager virtual environment is missing. Run scripts\install-agent-manager.ps1 first."
}

$clientFile=Join-Path $managerRoot "data\gmail-client-secret.json"
$tokenFile=Join-Path $managerRoot "data\gmail-token.json"
$IntervalHours=[math]::Max(1,[math]::Min(168,$IntervalHours))
$CommandPollSeconds=[math]::Max(15,[math]::Min(3600,$CommandPollSeconds))
if(-not $AllowedSenders){ $AllowedSenders=$Recipient }

function Test-GmailDesktopOAuthClient([string]$Path){
  if(-not $Path -or -not (Test-Path -LiteralPath $Path)){ return $false }
  try{
    $json=Get-Content -LiteralPath $Path -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
    return [bool](
      $json.installed -and
      $json.installed.client_id -and
      $json.installed.client_secret -and
      $json.installed.auth_uri -and
      $json.installed.token_uri
    )
  }catch{
    return $false
  }
}

function Find-GmailDesktopOAuthClient {
  $candidateRoots=@(
    (Join-Path $env:USERPROFILE "Downloads"),
    (Join-Path $env:USERPROFILE "Desktop"),
    (Join-Path $env:USERPROFILE "Documents"),
    (Join-Path $env:USERPROFILE "OneDrive\Downloads"),
    (Join-Path $env:USERPROFILE "OneDrive\Desktop"),
    (Join-Path $env:USERPROFILE "OneDrive\Documents")
  ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique

  $candidates=@()
  foreach($root in $candidateRoots){
    try{
      $candidates += Get-ChildItem -LiteralPath $root -File -Filter "*.json" -Recurse -ErrorAction SilentlyContinue |
        Where-Object {
          $_.Name -match '(?i)(client|secret|oauth|credential)' -or
          $_.DirectoryName -match '(?i)(google|oauth)'
        }
    }catch{}
  }

  foreach($candidate in ($candidates | Sort-Object LastWriteTime -Descending)){
    if(Test-GmailDesktopOAuthClient $candidate.FullName){
      return $candidate
    }
  }
  return $null
}

# Persist first so the Manager always exposes the intended Gmail state.
$vars=@{
  "GMAIL_REPORTING_ENABLED"="1"
  "REPORT_TO_EMAIL"=$Recipient
  "GMAIL_FROM_EMAIL"=$Recipient
  "GMAIL_OAUTH_CLIENT_FILE"=$clientFile
  "GMAIL_OAUTH_TOKEN_FILE"=$tokenFile
  "AGENT_MANAGER_EMAIL_INTERVAL_HOURS"=[string]$IntervalHours
  "GMAIL_COMMANDS_ENABLED"=$(if($EnableCommands){"1"}else{"0"})
  "GMAIL_COMMAND_ALLOWED_SENDERS"=$AllowedSenders
  "GMAIL_COMMAND_POLL_SECONDS"=[string]$CommandPollSeconds
}
foreach($entry in $vars.GetEnumerator()){
  [Environment]::SetEnvironmentVariable($entry.Key,$entry.Value,"User")
  Set-Item -Path ("Env:" + $entry.Key) -Value $entry.Value
}

# If the canonical file is missing or invalid, discover the actual Google Desktop OAuth
# download in the user's normal folders and copy it into the existing Manager data folder.
if(-not (Test-GmailDesktopOAuthClient $clientFile)){
  if(Test-Path -LiteralPath $clientFile){
    Write-Warning "Existing Gmail OAuth client file is not a valid Google Desktop OAuth client JSON: $clientFile"
  }

  Write-Host "Searching this Windows profile for a downloaded Google Desktop OAuth client JSON..." -ForegroundColor Cyan
  $found=Find-GmailDesktopOAuthClient
  if($found){
    Write-Host ("Found OAuth Desktop client: {0}" -f $found.FullName) -ForegroundColor Green
    Copy-Item -LiteralPath $found.FullName -Destination $clientFile -Force
    Write-Host ("Using: {0}" -f $clientFile) -ForegroundColor Green
  }
}

Write-Host "Restarting Agent Manager so email status/settings endpoints use the current settings..." -ForegroundColor Cyan
& "$PSScriptRoot\restart-agent-manager.ps1"
Start-Sleep -Seconds 4

if(-not (Test-GmailDesktopOAuthClient $clientFile)){
  Write-Host ""
  Write-Host "No valid Google OAuth Desktop App JSON was found on this computer." -ForegroundColor Yellow
  Write-Host "Expected final path:"
  Write-Host "  $clientFile"
  Write-Host ""
  Write-Host "A browser window will open at Google Cloud Credentials." -ForegroundColor Cyan
  Write-Host "Create/download: OAuth client ID -> Desktop app."
  Write-Host "Save the downloaded JSON normally (Downloads is fine), then run this same script again."
  Write-Host "Do not paste the client secret or token into chat."
  try { Start-Process "https://console.cloud.google.com/apis/credentials" } catch {}
  Write-Host ""
  try{
    $status=Invoke-RestMethod http://127.0.0.1:8787/email-status -TimeoutSec 10
    $status | ConvertTo-Json -Depth 8
  }catch{
    Write-Warning "Manager is running, but /email-status was not reachable yet: $($_.Exception.Message)"
  }
  exit 2
}

Write-Host "Validated Google Desktop OAuth client JSON: $clientFile" -ForegroundColor Green
Write-Host "Installing/confirming Gmail OAuth dependencies..." -ForegroundColor Cyan
& $py -m pip install -r requirements.txt
if($LASTEXITCODE -ne 0){ throw "Dependency install failed." }

Write-Host ""
if($EnableCommands){
  Write-Host "Email command mode requested. Google will ask for Gmail modify access so Agent Manager can read command emails, mark them processed, and reply." -ForegroundColor Cyan
}else{
  Write-Host "Reporting-only Gmail mode requested." -ForegroundColor Cyan
}
Write-Host "Opening Google OAuth authorization in your browser..." -ForegroundColor Cyan
& $py -m manager.gmail_v4 --authorize
if($LASTEXITCODE -ne 0){ throw "Gmail OAuth authorization failed." }

Write-Host ""
Write-Host "Sending test message to $Recipient..." -ForegroundColor Cyan
& $py -m manager.gmail_v4 --test
if($LASTEXITCODE -ne 0){ throw "Gmail test message failed." }

Write-Host ""
Write-Host "Restarting Agent Manager after OAuth authorization..." -ForegroundColor Cyan
& "$PSScriptRoot\restart-agent-manager.ps1"
Start-Sleep -Seconds 4

try{
  $status=Invoke-RestMethod http://127.0.0.1:8787/email-status -TimeoutSec 10
  $status | ConvertTo-Json -Depth 8
  if([string]$status.state -ne "CONFIGURED"){
    throw "Gmail did not reach CONFIGURED state. Current state: $($status.state)"
  }
}catch{
  throw "Gmail post-authorization verification failed: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "Gmail reporting configured and test message submitted successfully." -ForegroundColor Green
Write-Host "Recipient: $Recipient"
Write-Host "Periodic status: every $IntervalHours hour(s)"
if($EnableCommands){
  Write-Host "Email command bus: ENABLED" -ForegroundColor Green
  Write-Host "Allowed senders: $AllowedSenders"
  Write-Host "Command polling: every $CommandPollSeconds second(s)"
  Write-Host "Command subjects: [AGENT], [AGENT ALL], [AGENT MANAGER], [AGENT PV], [AGENT BLOGLAB]"
  try{
    $commandStatus=Invoke-RestMethod http://127.0.0.1:8787/email-command-status -TimeoutSec 10
    $commandStatus | ConvertTo-Json -Depth 8
  }catch{
    Write-Warning "Command status endpoint was not reachable yet: $($_.Exception.Message)"
  }
}
Write-Host "P0/P1 alerts: queued immediately and delivered by the next maintenance cycle."
