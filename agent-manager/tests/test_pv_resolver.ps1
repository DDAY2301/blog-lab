$ErrorActionPreference = "Stop"
$fixture = Join-Path ([System.IO.Path]::GetTempPath()) ("pv-resolver-" + [guid]::NewGuid().ToString("N"))
$originalProcess = [Environment]::GetEnvironmentVariable("PROJECT_VISIBILITY_ROOT","Process")
$originalUser = [Environment]::GetEnvironmentVariable("PROJECT_VISIBILITY_ROOT","User")
$script = Join-Path $PSScriptRoot "../scripts/resolve-project-visibility-root.ps1"

try {
  New-Item -ItemType Directory -Force (Join-Path $fixture "api") | Out-Null
  Set-Content (Join-Path $fixture "api/server.py") -Value "app = object()"
  Set-Content (Join-Path $fixture "api/requirements.txt") -Value "fastapi"
  & git -C $fixture init -q
  if ($LASTEXITCODE -ne 0) { throw "git init failed" }
  & git -C $fixture remote add origin https://github.com/DDAY2301/PROJEKT.git
  if ($LASTEXITCODE -ne 0) { throw "git remote add failed" }

  $resolved = & $script -ProjectRoot $fixture
  if ($resolved -ne (Resolve-Path $fixture).ProviderPath) { throw "Existing project was not resolved" }
  if ([Environment]::GetEnvironmentVariable("PROJECT_VISIBILITY_ROOT","User") -ne $originalUser) {
    throw "Resolver unexpectedly mutated persistent User environment"
  }

  & git -C $fixture remote set-url origin https://github.com/another-owner/not-PROJEKT.git
  if ($LASTEXITCODE -ne 0) { throw "git remote update failed" }
  $rejected = $false
  try { $null = & $script -ProjectRoot $fixture } catch { $rejected = $true }
  if (-not $rejected) { throw "Resolver accepted a checkout with the wrong GitHub origin" }

  Write-Host "PASS: local PV root discovery, exact remote identity, no persistent mutation without -Persist"
} finally {
  [Environment]::SetEnvironmentVariable("PROJECT_VISIBILITY_ROOT", $originalProcess, "Process")
  Remove-Item -LiteralPath $fixture -Recurse -Force -ErrorAction SilentlyContinue
}
