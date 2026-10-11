param(
  [ValidateSet("Check", "Enable", "Authorize", "SendTest")]
  [string]$Mode = "Check",
  [string]$OwnerEmail = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

function Read-User([string]$name) {
  return [Environment]::GetEnvironmentVariable($name, "User")
}
function Set-User([string]$name, [string]$value) {
  [Environment]::SetEnvironmentVariable($name, $value, "User")
  [Environment]::SetEnvironmentVariable($name, $value, "Process")
}
function Import-UserSettings {
  foreach ($name in @(
    "GMAIL_REPORTING_ENABLED", "GMAIL_COMMANDS_ENABLED",
    "GMAIL_COMMAND_ALLOWED_SENDERS", "GMAIL_COMMAND_REQUIRE_AUTH",
    "GMAIL_OAUTH_CLIENT_FILE", "GMAIL_OAUTH_TOKEN_FILE",
    "GMAIL_FROM_EMAIL", "REPORT_TO_EMAIL"
  )) {
    $value = Read-User $name
    if (-not [string]::IsNullOrWhiteSpace($value)) {
      [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
  }
}
function Check-Mail {
  Import-UserSettings
  $report = [ordered]@{
    reporting_enabled = ($env:GMAIL_REPORTING_ENABLED -eq "1")
    commands_enabled = ($env:GMAIL_COMMANDS_ENABLED -eq "1")
    strict_authentication = ($env:GMAIL_COMMAND_REQUIRE_AUTH -ne "0")
    owner_configured = (-not [string]::IsNullOrWhiteSpace($env:REPORT_TO_EMAIL))
    allowed_senders_configured = (-not [string]::IsNullOrWhiteSpace($env:GMAIL_COMMAND_ALLOWED_SENDERS))
    project_ci_token_configured = [bool](
      (Read-User "AGENT_MANAGER_GITHUB_TOKEN") -or (Read-User "GITHUB_TOKEN") -or (Read-User "GH_TOKEN")
    )
    bloglab_token_configured = [bool](Read-User "FLEET_AGENT_TOKEN")
    manager_available = $false
    gmail_state = "unknown"
    polling_enabled = $false
    poll_seconds = $null
  }
  try {
    $status = Invoke-RestMethod "http://127.0.0.1:8787/email-command-status" -TimeoutSec 5
    $report.manager_available = $true
    $report.gmail_state = [string]$status.gmail_state
    $report.polling_enabled = [bool]$status.command_bus.enabled
    $report.poll_seconds = $status.command_bus.poll_seconds
  } catch {
    $report.gmail_state = "manager_not_reachable"
  }
  return [PSCustomObject]$report
}

switch ($Mode) {
  "Enable" {
    Import-UserSettings
    $email = $OwnerEmail.Trim()
    if (-not $email) { $email = [string]$env:REPORT_TO_EMAIL }
    if ($email -notmatch "^[^\s@]+@[^\s@]+\.[^\s@]+$") {
      throw "Provide -OwnerEmail your-real-address@example.com. No passwords or OAuth tokens belong in this command."
    }
    $settings = [ordered]@{
      REPORT_TO_EMAIL = $email
      GMAIL_REPORTING_ENABLED = "1"
      GMAIL_COMMANDS_ENABLED = "1"
      GMAIL_COMMAND_ALLOWED_SENDERS = $email
      GMAIL_COMMAND_REQUIRE_AUTH = "1"
    }
    if (-not $env:GMAIL_FROM_EMAIL) {
      $settings.GMAIL_FROM_EMAIL = $email
    }
    foreach ($key in $settings.Keys) { Set-User $key $settings[$key] }
    Write-Host "Strict Gmail command mode configured for a single owner. No secrets were displayed." -ForegroundColor Green
    Write-Host "Restart only Agent Manager after configuring; authorize Gmail if check reports AUTH_REQUIRED." -ForegroundColor Yellow
    Check-Mail | Format-List
  }
  "Authorize" {
    Import-UserSettings
    if ($env:GMAIL_REPORTING_ENABLED -ne "1" -or $env:GMAIL_COMMANDS_ENABLED -ne "1") {
      throw "Run -Mode Enable first."
    }
    $py = Join-Path $root ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $py)) { throw "Missing Agent Manager .venv Python." }
    $client = $env:GMAIL_OAUTH_CLIENT_FILE
    if (-not $client) { $client = Join-Path $root "data\gmail-client-secret.json" }
    if (-not (Test-Path -LiteralPath $client)) {
      throw "Missing existing Gmail OAuth desktop client JSON; configure it locally (do not paste secrets into chat)."
    }
    Write-Host "Opening Google OAuth consent for Gmail modify and send scopes." -ForegroundColor Cyan
    & $py -m manager.gmail_v4 --authorize
    if ($LASTEXITCODE -ne 0) { throw "Gmail OAuth authorization failed." }
    Write-Host "OAuth completed locally. Restart Agent Manager to load the new credentials and settings." -ForegroundColor Green
  }
  "SendTest" {
    $state = Check-Mail
    if (-not $state.manager_available -or $state.gmail_state -ne "CONFIGURED" -or -not $state.polling_enabled) {
      throw "Gmail command receiver not ready. Run -Mode Check, then configure or authorize first."
    }
    $test = Invoke-RestMethod "http://127.0.0.1:8787/email/send-test" -Method POST -TimeoutSec 35
    Write-Host "Test email dispatched by the existing Agent Manager API." -ForegroundColor Green
    [PSCustomObject]@{ ok = $test.ok; implementation = $test.implementation } | Format-List
  }
  default {
    Check-Mail | Format-List
    Write-Host "Use: .\scripts\email-control-v7.ps1 -Mode Enable -OwnerEmail you@example.com" -ForegroundColor Cyan
    Write-Host "Then: .\scripts\email-control-v7.ps1 -Mode Authorize (only if OAuth is not ready)" -ForegroundColor Cyan
    Write-Host "Finally: .\scripts\email-control-v7.ps1 -Mode SendTest" -ForegroundColor Cyan
  }
}
