# Read-only Agent Manager V6 diagnostics. No process restarts, writes, or token output.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$managerRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path $managerRoot -Parent

function Read-LocalApi([string]$Url) {
    try {
        return [pscustomobject]@{
            reachable = $true
            value = (Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 5)
            error = $null
        }
    } catch {
        return [pscustomobject]@{
            reachable = $false
            value = $null
            error = $_.Exception.Message
        }
    }
}

function Git-Value([string[]]$Arguments) {
    try {
        $output = & git -C $repoRoot @Arguments 2>$null
        if ($LASTEXITCODE -eq 0) { return (($output | Out-String).Trim()) }
    } catch {}
    return $null
}

$manager = Read-LocalApi 'http://127.0.0.1:8787/health'
$project = Read-LocalApi 'http://127.0.0.1:8000/health'
$ollama = Read-LocalApi 'http://127.0.0.1:11434/api/tags'
$incidents = Read-LocalApi 'http://127.0.0.1:8787/incidents'
$email = Read-LocalApi 'http://127.0.0.1:8787/email-status'
$commands = Read-LocalApi 'http://127.0.0.1:8787/email-command-status'
$coder = Read-LocalApi 'http://127.0.0.1:8787/coder-brain'

$openIncidents = @()
if ($incidents.reachable -and $null -ne $incidents.value.incidents) {
    $openIncidents = @(
        $incidents.value.incidents |
        Where-Object { $_.status -ne 'resolved' } |
        Select-Object id, severity, component, status, first_seen, last_seen
    )
}

$managerInfo = [ordered]@{ reachable = $manager.reachable; error = $manager.error }
if ($manager.reachable) {
    $managerInfo.ok = $manager.value.ok
    $managerInfo.version = $manager.value.version
    $managerInfo.write_enabled = $manager.value.write_enabled
    $managerInfo.reported_open_incidents = $manager.value.open_incidents
}

$projectInfo = [ordered]@{ reachable = $project.reachable; error = $project.error }
if ($project.reachable) {
    $projectInfo.ok = $project.value.ok
    $projectInfo.version = $project.value.version
}

$emailInfo = [ordered]@{ reachable = $email.reachable; error = $email.error }
if ($email.reachable) {
    $emailInfo.state = $email.value.state
    $emailInfo.interval_hours = $email.value.interval_hours
    $emailInfo.queued = @($email.value.queue | Where-Object { $_.status -ne 'sent' }).Count
}

$commandInfo = [ordered]@{ reachable = $commands.reachable; error = $commands.error }
if ($commands.reachable) {
    $commandInfo.gmail_state = $commands.value.gmail_state
    $commandInfo.enabled = $commands.value.command_bus.enabled
    $commandInfo.poll_seconds = $commands.value.command_bus.poll_seconds
    $commandInfo.recent_count = @($commands.value.recent).Count
}

$report = [ordered]@{
    timestamp_utc = (Get-Date).ToUniversalTime().ToString('o')
    git = [ordered]@{
        branch = Git-Value @('branch', '--show-current')
        commit = Git-Value @('rev-parse', 'HEAD')
        local_changes = Git-Value @('status', '--porcelain')
    }
    write_mode = [ordered]@{
        user = [Environment]::GetEnvironmentVariable('AGENT_MANAGER_WRITE_ENABLED', 'User')
        process = [Environment]::GetEnvironmentVariable('AGENT_MANAGER_WRITE_ENABLED', 'Process')
        runtime = $(if ($manager.reachable) { $manager.value.write_enabled } else { $null })
    }
    manager = $managerInfo
    project_visibility = $projectInfo
    ollama = [ordered]@{
        reachable = $ollama.reachable
        model_names = $(if ($ollama.reachable) { @($ollama.value.models | ForEach-Object { $_.name }) } else { @() })
        error = $ollama.error
    }
    incidents = [ordered]@{
        reachable = $incidents.reachable
        open_count = $openIncidents.Count
        open = $openIncidents
        error = $incidents.error
    }
    gmail_reporting = $emailInfo
    gmail_commands = $commandInfo
    coder_endpoint = [ordered]@{ reachable = $coder.reachable; error = $coder.error }
}

$report | ConvertTo-Json -Depth 8
