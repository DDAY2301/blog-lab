param(
    [ValidateSet("Preflight","Activate","Upgrade")]
    [string]$Mode = "Preflight"
)

$ErrorActionPreference = "Stop"
$agent = Split-Path $PSScriptRoot -Parent
$repo = Split-Path $agent -Parent
$py = Join-Path $agent ".venv\Scripts\python.exe"
$needBranch = "agent-manager-v1"

function Assert-ManagerState {
    $health = Invoke-RestMethod "http://127.0.0.1:8787/health" -TimeoutSec 5
    if (-not $health.ok -or -not $health.supervisor_only) {
        throw "Manager is not healthy in supervisor-only mode. No update performed."
    }
    return $health
}

function Test-Preflight {
    if (-not (Test-Path -LiteralPath $py)) {
        throw "Missing existing Agent Manager Python environment."
    }
    $branch = (& git -C $repo branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or $branch -ne $needBranch) {
        throw "Expected Git branch agent-manager-v1. Current: $branch"
    }
    $dirty = & git -C $repo status --porcelain
    if ($LASTEXITCODE -ne 0 -or $dirty) {
        throw "Repository contains uncommitted changes. Safely resolve them before activation."
    }
    $env:PYTHONPATH = $agent
    # Smoke tests must never touch the live 24/7 Manager SQLite database.
    $previousDb = $env:AGENT_MANAGER_DB
    $testDb = Join-Path $env:TEMP "agent-manager-v8-preflight-$PID.sqlite"
    $env:AGENT_MANAGER_DB = $testDb
    Push-Location $agent
    try {
        & $py -m pytest -q tests
        if ($LASTEXITCODE -ne 0) {
            throw "V8 regression tests failed; V7 will remain untouched."
        }
        & $py -c "import manager.mail_commands_v4, manager.remote_run_watcher_v8; print('V8 imports OK')"
        if ($LASTEXITCODE -ne 0) {
            throw "V8 import smoke failed; V7 will remain untouched."
        }
    } finally {
        Pop-Location
        $env:AGENT_MANAGER_DB = $previousDb
        Remove-Item -LiteralPath $testDb -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath "$testDb-wal" -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath "$testDb-shm" -ErrorAction SilentlyContinue
    }
    $health = Assert-ManagerState
    $token = [Environment]::GetEnvironmentVariable("AGENT_MANAGER_GITHUB_TOKEN","User")
    if (-not $token) {
        $token = [Environment]::GetEnvironmentVariable("GITHUB_TOKEN","User")
    }
    $free = [math]::Round(
        (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 2
    )
    [PSCustomObject]@{
        version_before = $health.version
        supervisor_only = $health.supervisor_only
        gmail = $health.gmail
        github_token_present = [bool]$token
        free_ram_gb = $free
        version_under_test = "V8 email command engine (Manager V4 base)"
        code_verified = $true
    } | Format-List
}

if ($Mode -eq "Upgrade") {
    $branch = (& git -C $repo branch --show-current).Trim()
    if ($branch -ne $needBranch) { throw "Expected agent-manager-v1, got $branch" }
    $dirty = & git -C $repo status --porcelain
    if ($LASTEXITCODE -ne 0 -or $dirty) {
        throw "Uncommitted work detected. Not pulling or restarting."
    }
    $priorSha = (& git -C $repo rev-parse HEAD).Trim()
    $marker = Join-Path $agent "data\v8-pre-upgrade-commit.tmp"
    Write-Host "Fetching reviewed Manager code..." -ForegroundColor Cyan
    & git -C $repo pull --ff-only origin $needBranch
    if ($LASTEXITCODE -ne 0) {
        throw "Fast-forward Git update failed; Manager was not restarted."
    }
    Set-Content -Path $marker -Value $priorSha -Encoding ASCII
    Write-Host "Saved pre-upgrade revision SHA for a deliberate rollback." -ForegroundColor Cyan
}

if ($Mode -in @("Upgrade","Activate")) {
    # Update missing Python requirements before changing a running service.
    # No local Project Visibility production worker is launched.
    & $py -m pip install -r (Join-Path $agent "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        throw "Installing existing Manager dependencies failed; no restart."
    }
}

Test-Preflight
if ($Mode -eq "Preflight") {
    Write-Host "Preflight PASS. No services restarted, no Windows settings changed." -ForegroundColor Green
    return
}

# Safely back up the exact SQLite database before touching running processes.
# A separate Python file avoids Windows PowerShell 5.1 quoting of multiline -c.
$dbSetting = [Environment]::GetEnvironmentVariable("AGENT_MANAGER_DB", "Process")
if ([string]::IsNullOrWhiteSpace($dbSetting)) {
    $dbSetting = [Environment]::GetEnvironmentVariable("AGENT_MANAGER_DB", "User")
}
if ([string]::IsNullOrWhiteSpace($dbSetting)) {
    $database = Join-Path $agent "data\agent_manager.db"
} elseif ([System.IO.Path]::IsPathRooted($dbSetting)) {
    $database = $dbSetting
} else {
    $database = Join-Path $agent $dbSetting
}
if (-not (Test-Path -LiteralPath $database -PathType Leaf)) {
    throw "SQLite database does not exist at expected path: $database. No restart."
}
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = Join-Path $agent "data\agent_manager-before-v8-$timestamp.sqlite"
$backupTool = Join-Path $PSScriptRoot "backup_sqlite_v8.py"
if (-not (Test-Path -LiteralPath $backupTool -PathType Leaf)) {
    throw "Verified SQLite backup helper is missing. No restart."
}
& $py $backupTool --source $database --destination $backup
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $backup -PathType Leaf)) {
    throw "SQLite hot backup/verification failed. No restart or V8 switch."
}
if ((Get-Item -LiteralPath $backup).Length -le 0) {
    throw "SQLite backup is empty. No restart or V8 switch."
}
Write-Host "Verified consistent SQLite backup: $backup" -ForegroundColor Green

$originalPilot = [Environment]::GetEnvironmentVariable("AGENT_MANAGER_EMAIL_V8_ENABLED", "User")
[Environment]::SetEnvironmentVariable("AGENT_MANAGER_EMAIL_V8_ENABLED", "1", "User")
[Environment]::SetEnvironmentVariable("AGENT_MANAGER_EMAIL_V8_ENABLED", "1", "Process")
try {
    Write-Host "Restarting Agent Manager only; PV/BlogLab production workers remain remote." -ForegroundColor Cyan
    & "$PSScriptRoot\restart-agent-manager.ps1"
    $health = Assert-ManagerState
    if (-not $health.email_v8_enabled -or -not $health.pv_remote_verifier) {
        throw "V8 pilot mode not active after restart."
    }
    & "$PSScriptRoot\restart-remote-v4.ps1"
    $remote = Invoke-RestMethod "http://127.0.0.1:8788/health" -TimeoutSec 5
    if (-not $remote.ok) {
        throw "Fleet Remote failed health check after restart."
    }
    $state = Invoke-RestMethod "http://127.0.0.1:8787/email-command-status" -TimeoutSec 5
    Write-Host "V8 pilot active; Gmail end-to-end remains to be confirmed." -ForegroundColor Green
    [PSCustomObject]@{
        manager_up = $health.ok
        supervisor_only = $health.supervisor_only
        remote_up = $remote.ok
        pv_watcher = $health.pv_remote_verifier.status
        gmail_status = $health.gmail
        commands_enabled = $state.command_bus.enabled
        v8_enabled = $health.email_v8_enabled
    } | Format-List
} catch {
    Write-Warning "V8 activation failed. Restoring previous email control mode."
    [Environment]::SetEnvironmentVariable(
        "AGENT_MANAGER_EMAIL_V8_ENABLED", $originalPilot, "User"
    )
    [Environment]::SetEnvironmentVariable(
        "AGENT_MANAGER_EMAIL_V8_ENABLED", $originalPilot, "Process"
    )
    try {
        & "$PSScriptRoot\restart-agent-manager.ps1"
        Write-Host "Previous mail mode requested after failed V8 activation." -ForegroundColor Yellow
    } catch {
        Write-Warning "Automatic fallback restart failed. Verify port 8787 using the existing stack script."
    }
    throw
}
