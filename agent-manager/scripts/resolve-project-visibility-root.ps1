param(
  [string]$ProjectRoot = "",
  [switch]$Persist
)

$ErrorActionPreference = "Stop"

# Only discover the operator's existing Project Visibility checkout.
# Never clone, install, or search unrelated user profiles.
function Test-ProjectVisibilityRoot([string]$Candidate) {
  if ([string]::IsNullOrWhiteSpace($Candidate)) { return $null }
  $resolved = Resolve-Path -LiteralPath $Candidate -ErrorAction SilentlyContinue
  if (-not $resolved) { return $null }
  $path = [string]$resolved.ProviderPath

  if (-not (Test-Path -LiteralPath (Join-Path $path "api\server.py") -PathType Leaf)) { return $null }
  if (-not (Test-Path -LiteralPath (Join-Path $path "api\requirements.txt") -PathType Leaf)) { return $null }
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { return $null }

  $origin = ""
  try { $origin = ((& git -C $path remote get-url origin 2>$null) | Out-String).Trim() } catch {}
  if ($origin -notmatch '(?i)github\.com[:/]DDAY2301/PROJEKT(?:\.git)?/?$') { return $null }
  return $path
}

$candidates = @()
if ($ProjectRoot) {
  $candidates = @($ProjectRoot)
} else {
  $homeDir = [string]$env:USERPROFILE
  $candidates = @(
    [Environment]::GetEnvironmentVariable("PROJECT_VISIBILITY_ROOT", "User"),
    [Environment]::GetEnvironmentVariable("PROJECT_VISIBILITY_ROOT", "Process")
  )
  if ($homeDir) {
    foreach ($suffix in @(
      "PROJEKT", "Project-Visibility",
      "Documents\PROJEKT", "Documents\Project-Visibility",
      "Desktop\PROJEKT", "Desktop\Project-Visibility",
      "Downloads\PROJEKT", "Downloads\Project-Visibility",
      "Projects\PROJEKT", "Repos\PROJEKT", "source\repos\PROJEKT"
    )) {
      $candidates += (Join-Path $homeDir $suffix)
    }
  }
}

$matches = [System.Collections.Generic.List[string]]::new()
foreach ($candidate in $candidates) {
  $valid = Test-ProjectVisibilityRoot ([string]$candidate)
  if ($valid -and -not $matches.Contains($valid)) { $matches.Add($valid) }
}

if ($matches.Count -eq 0) {
  throw "Project Visibility checkout not found. Provide -ProjectRoot with the path to the existing DDAY2301/PROJEKT clone. No new clone was created."
}
if ($matches.Count -gt 1) {
  throw ("Multiple Project Visibility checkouts found: " + ($matches -join " | ") + ". Set PROJECT_VISIBILITY_ROOT explicitly to avoid running the wrong copy.")
}

$selected = $matches[0]
if ($Persist) {
  [Environment]::SetEnvironmentVariable("PROJECT_VISIBILITY_ROOT", $selected, "User")
}
[Environment]::SetEnvironmentVariable("PROJECT_VISIBILITY_ROOT", $selected, "Process")
Write-Output $selected
