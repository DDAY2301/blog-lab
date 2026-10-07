param(
  [string]$InstallDir = "$env:LOCALAPPDATA\AgentManager\colibri",
  [string]$ModelPath = ""
)
$ErrorActionPreference = "Stop"

Write-Host "Resolving latest stable Colibri release..." -ForegroundColor Cyan
$release = Invoke-RestMethod "https://api.github.com/repos/JustVugg/colibri/releases/latest" -Headers @{ "User-Agent"="AgentManagerV4" }
$tag = $release.tag_name
$nvidia = Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "NVIDIA" } | Select-Object -First 1
$preferred = if($nvidia){"windows-x86_64-cuda.zip"}else{"windows-x86_64.zip"}
$asset = $release.assets | Where-Object { $_.name -like "*$preferred" } | Select-Object -First 1
if(-not $asset){
  $asset = $release.assets | Where-Object { $_.name -like "*windows-x86_64.zip" } | Select-Object -First 1
}
if(-not $asset){ throw "No supported Windows x86_64 Colibri asset found in $tag." }

$mem = Get-CimInstance Win32_ComputerSystem
$ramGB = [math]::Round($mem.TotalPhysicalMemory / 1GB, 1)
$installDrive = (Split-Path -Qualifier $InstallDir).TrimEnd(":")
if(-not $installDrive){ $installDrive=(Get-Location).Drive.Name }
$drive = Get-PSDrive -Name $installDrive
$freeGB = [math]::Round($drive.Free / 1GB, 1)

Write-Host "Colibri $tag hardware preflight"
Write-Host "Asset: $($asset.name)"
Write-Host "RAM: $ramGB GB"
Write-Host "Free disk: $freeGB GB"

New-Item -ItemType Directory -Force $InstallDir | Out-Null
$zip = Join-Path $env:TEMP $asset.name
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zip -UseBasicParsing

$sums = $release.assets | Where-Object { $_.name -eq "SHA256SUMS.txt" } | Select-Object -First 1
if($sums){
  $sumFile=Join-Path $env:TEMP "colibri-SHA256SUMS.txt"
  Invoke-WebRequest -Uri $sums.browser_download_url -OutFile $sumFile -UseBasicParsing
  $expected=(Get-Content $sumFile | Where-Object { $_ -match [regex]::Escape($asset.name) } | Select-Object -First 1).Split()[0].ToLower()
  if($expected){
    $actual=(Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
    if($actual -ne $expected){ throw "Colibri SHA256 verification failed." }
    Write-Host "SHA256 verified." -ForegroundColor Green
  }
}

Get-ChildItem $InstallDir -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive -Path $zip -DestinationPath $InstallDir -Force
Set-Content -Path (Join-Path $InstallDir "VERSION.txt") -Value $tag -Encoding ASCII

[Environment]::SetEnvironmentVariable("COLIBRI_HOME", $InstallDir, "User")
[Environment]::SetEnvironmentVariable("COLIBRI_BASE_URL", "http://127.0.0.1:8790/v1", "User")
[Environment]::SetEnvironmentVariable("AGENT_MANAGER_AI_PRIORITY", "colibri,ollama", "User")

if($ramGB -lt 16){
  Write-Warning "Colibri $tag engine is installed, but this PC is below the documented ~16 GB minimum RAM for the large streamed model class."
  Write-Host "Colibri is registered as STANDBY; Agent Manager will use Ollama until suitable hardware/model storage is available."
  Write-Host "No large model is downloaded automatically."
  exit 0
}

if($ModelPath){
  if(-not (Test-Path $ModelPath)){ throw "ModelPath does not exist: $ModelPath" }
  [Environment]::SetEnvironmentVariable("COLIBRI_MODEL_PATH", (Resolve-Path $ModelPath).Path, "User")
  Write-Host "Colibri model configured. Start with scripts\start-colibri.ps1" -ForegroundColor Green
}else{
  Write-Host "Colibri $tag engine installed at $InstallDir" -ForegroundColor Green
  Write-Host "No model path configured; provider remains STANDBY and Ollama remains active."
}
