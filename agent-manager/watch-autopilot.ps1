$ErrorActionPreference = "Stop"

Write-Host "Agent Manager 24/7 Watcher - local/free mode"
Write-Host "Monitors failed workflows on main and opens validated repair PRs."

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) ni najden. Namesti ga in ponovno zaženi."
}

gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "Potreben je enkraten GitHub browser login..."
    gh auth login -h github.com -p https -w
}

gh auth setup-git

$env:AGENT_MANAGER_WRITE_ENABLED = "1"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}
& .\.venv\Scripts\pip.exe install -r requirements.txt

Write-Host "Watcher je aktiven. Preverjanje vsakih 5 minut."
& .\.venv\Scripts\python.exe -m manager.watcher --root .. --interval 300
