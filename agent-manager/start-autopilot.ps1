$ErrorActionPreference = "Stop"

Write-Host "Agent Manager AUTOPILOT - local/free write mode"
Write-Host "Repairs are isolated in git worktrees and published as Pull Requests."
Write-Host "Direct merge to main is not enabled."

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git ni najden."
}

if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh auth status
    if ($LASTEXITCODE -ne 0) {
        Write-Host "GitHub login je potreben enkrat. Odpiram varen browser login..."
        gh auth login -h github.com -p https -w
    }
    gh auth setup-git
} elseif (-not $env:AGENT_MANAGER_GITHUB_TOKEN) {
    throw "Namesti GitHub CLI (gh) ali lokalno nastavi AGENT_MANAGER_GITHUB_TOKEN. Tokena ne vpisuj v klepet."
}

$env:AGENT_MANAGER_WRITE_ENABLED = "1"

& .\start.ps1
