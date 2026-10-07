param(
  [string]$InstallDir = "$env:LOCALAPPDATA\AgentManager\colibri-v2",
  [string]$ModelPath = ""
)
$ErrorActionPreference = "Stop"

$release = "v2.0.0"
$asset = "colibri-v2.0.0-windows-x86_64.zip"
$url = "https://github.com/JustVugg/colibri/releases/download/$release/$asset"

$mem = Get-CimInstance Win32_ComputerSystem
$ramGB = [math]::Round($mem.TotalPhysicalMemory / 1GB, 1)
$drive = Get-PSDrive -Name ((Get-Location).Drive.Name)
$freeGB = [math]::Round($drive.Free / 1GB, 1)

Write-Host "Colibri v2.0.0 hardware preflight" -ForegroundColor Cyan
Write-Host "RAM: $ramGB GB"
Write-Host "Free disk on current drive: $freeGB GB"

New-Item -ItemType Directory -Force $InstallDir | Out-Null
$zip = Join-Path $env:TEMP $asset

if (-not (Test-Path (Join-Path $InstallDir "coli.cmd"))) {
  Write-Host "Downloading Colibri v2.0.0 Windows engine..."
  Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
  Expand-Archive -Path $zip -DestinationPath $InstallDir -Force
}

[Environment]::SetEnvironmentVariable("COLIBRI_HOME", $InstallDir, "User")
[Environment]::SetEnvironmentVariable("COLIBRI_BASE_URL", "http://127.0.0.1:8790/v1", "User")
[Environment]::SetEnvironmentVariable("AGENT_MANAGER_AI_PRIORITY", "colibri,ollama", "User")

if ($ramGB -lt 16) {
  Write-Warning "Colibri engine is installed, but this PC has less than the documented ~16 GB minimum RAM for the large streamed models. Agent Manager will keep Colibri in STANDBY and use Ollama as the active provider."
  Write-Host "No large Colibri model was downloaded."
  exit 0
}

if ($ModelPath) {
  $coli = Join-Path $InstallDir "coli.cmd"
  if (-not (Test-Path $coli)) { $coli = Join-Path $InstallDir "coli" }
  if (-not (Test-Path $coli)) { throw "Colibri launcher not found in $InstallDir" }
  [Environment]::SetEnvironmentVariable("COLIBRI_MODEL_PATH", $ModelPath, "User")
  Write-Host "Model path configured: $ModelPath"
  Write-Host "Use scripts\start-colibri.ps1 to start the OpenAI-compatible endpoint."
} else {
  Write-Host "Colibri v2.0.0 engine installed in: $InstallDir"
  Write-Host "Set COLIBRI_MODEL_PATH later when a compatible model is available."
}
