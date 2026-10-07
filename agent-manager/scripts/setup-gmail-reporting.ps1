param(
  [Parameter(Mandatory=$true)]
  [string]$Recipient,
  [int]$IntervalHours = 3
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

# Persist first, even before OAuth exists. This lets the already-installed Manager
# expose /email-status as CLIENT_SECRET_REQUIRED rather than leaving an old process running.
$vars=@{
  "GMAIL_REPORTING_ENABLED"="1"
  "REPORT_TO_EMAIL"=$Recipient
  "GMAIL_OAUTH_CLIENT_FILE"=$clientFile
  "GMAIL_OAUTH_TOKEN_FILE"=$tokenFile
  "AGENT_MANAGER_EMAIL_INTERVAL_HOURS"=[string]$IntervalHours
}
foreach($entry in $vars.GetEnumerator()){
  [Environment]::SetEnvironmentVariable($entry.Key,$entry.Value,"User")
  Set-Item -Path ("Env:" + $entry.Key) -Value $entry.Value
}

Write-Host "Restarting Agent Manager so email status/settings endpoints use the current code..." -ForegroundColor Cyan
& "$PSScriptRoot\restart-agent-manager.ps1"
Start-Sleep -Seconds 4

if(-not (Test-Path $clientFile)){
  Write-Host ""
  Write-Host "Gmail OAuth client file is required:" -ForegroundColor Yellow
  Write-Host "  $clientFile"
  Write-Host ""
  Write-Host "Create a Google Cloud OAuth Desktop App and save its downloaded JSON here."
  Write-Host "Do not paste the client secret or token into chat."
  Write-Host ""
  try{
    $status=Invoke-RestMethod http://127.0.0.1:8787/email-status -TimeoutSec 10
    $status | ConvertTo-Json -Depth 8
  }catch{
    Write-Warning "Manager is running, but /email-status was not reachable yet: $($_.Exception.Message)"
  }
  exit 2
}

Write-Host "Installing/confirming Gmail OAuth dependencies..." -ForegroundColor Cyan
& $py -m pip install -r requirements.txt
if($LASTEXITCODE -ne 0){ throw "Dependency install failed." }

Write-Host ""
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
}catch{
  Write-Warning "Manager restarted but /email-status was not reachable yet: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "Gmail reporting configured." -ForegroundColor Green
Write-Host "Recipient: $Recipient"
Write-Host "Periodic status: every $IntervalHours hour(s)"
Write-Host "P0/P1 alerts: queued immediately and delivered by the next maintenance cycle."
