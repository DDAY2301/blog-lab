param(
  [ValidateSet("Report", "Apply", "Restore")]
  [string]$Mode = "Report",
  [string]$ReportDirectory = ""
)

$ErrorActionPreference = "Stop"

# Safe low-memory profile for Windows 11 + Agent Manager + Project Visibility.
# This script does NOT stop processes, delete files, change services, change
# antivirus settings, disable updates, change power plans or require admin.
$settings = [ordered]@{
  OLLAMA_MAX_LOADED_MODELS       = "1"
  OLLAMA_NUM_PARALLEL            = "1"
  OLLAMA_KEEP_ALIVE              = "60s"
  OLLAMA_FAST_KEEP_ALIVE         = "60s"
  AGENT_MANAGER_OLLAMA_KEEP_ALIVE = "60s"
  MODEL_CONCURRENCY              = "1"
  VISUAL_QA_CONCURRENCY          = "1"
}

if (-not $ReportDirectory) {
  $localRoot = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { $env:TEMP }
  if (-not $localRoot) { $localRoot = [System.IO.Path]::GetTempPath() }
  $ReportDirectory = Join-Path $localRoot "AgentManagerV4\performance"
}
New-Item -ItemType Directory -Force -Path $ReportDirectory | Out-Null
$backupPath = Join-Path $ReportDirectory "windows11-ai-profile-backup.json"

function Get-UserSetting([string]$name) {
  return [Environment]::GetEnvironmentVariable($name, "User")
}

function Set-UserSetting([string]$name, [AllowNull()][string]$value) {
  [Environment]::SetEnvironmentVariable($name, $value, "User")
  [Environment]::SetEnvironmentVariable($name, $value, "Process")
}

function Get-Endpoint([string]$url) {
  try {
    $result = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 4
    return @{ reachable = $true; ok = [bool]$result.ok; version = [string]$result.version }
  } catch {
    return @{ reachable = $false; ok = $false; version = "" }
  }
}

function Get-SystemSnapshot {
  $snapshot = [ordered]@{
    utc = (Get-Date).ToUniversalTime().ToString("o")
    computer = [ordered]@{}
    cpu = [ordered]@{}
    memory = [ordered]@{}
    system_disk = [ordered]@{}
    pagefile_automatic = $null
    power_plan = ""
    top_memory_processes = @()
    startup_app_names = @()
    agent_manager = @{}
    project_visibility = @{}
    ollama_model_names = @()
    active_agent_incidents = $null
    ai_user_settings = [ordered]@{}
    recommendations = @()
  }

  try {
    $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    $snapshot.computer.os = [string]$os.Caption
    $snapshot.computer.version = [string]$os.Version
    $total = [double]$os.TotalVisibleMemorySize
    $free = [double]$os.FreePhysicalMemory
    $snapshot.memory.total_gb = [math]::Round($total / 1MB, 2)
    $snapshot.memory.available_gb = [math]::Round($free / 1MB, 2)
    if ($total -gt 0) { $snapshot.memory.used_percent = [math]::Round(100 * (1 - $free / $total), 1) }
  } catch { $snapshot.computer.note = "System CIM information unavailable" }

  try {
    $cpu = @(Get-CimInstance Win32_Processor -ErrorAction Stop)
    $snapshot.cpu.name = [string]$cpu[0].Name
    $snapshot.cpu.load_percent = [math]::Round((($cpu | Measure-Object LoadPercentage -Average).Average), 1)
  } catch { $snapshot.cpu.note = "CPU load unavailable" }

  try {
    $drive = if ($env:SystemDrive) { $env:SystemDrive } else { "C:" }
    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$drive'" -ErrorAction Stop
    if ($disk) {
      $snapshot.system_disk.free_gb = [math]::Round([double]$disk.FreeSpace / 1GB, 1)
      $snapshot.system_disk.total_gb = [math]::Round([double]$disk.Size / 1GB, 1)
    }
  } catch { $snapshot.system_disk.note = "Disk information unavailable" }

  try {
    $system = Get-CimInstance Win32_ComputerSystem -ErrorAction Stop
    $snapshot.pagefile_automatic = [bool]$system.AutomaticManagedPagefile
  } catch {}

  try {
    $power = & powercfg.exe /getactivescheme 2>$null
    $snapshot.power_plan = (($power | Out-String).Trim())
  } catch {}

  try {
    $snapshot.top_memory_processes = @(
      Get-Process -ErrorAction Stop |
      Sort-Object WorkingSet64 -Descending |
      Select-Object -First 12 |
      ForEach-Object {
        [ordered]@{
          name = [string]$_.ProcessName
          pid = [int]$_.Id
          working_set_mb = [math]::Round([double]$_.WorkingSet64 / 1MB, 1)
        }
      }
    )
  } catch {}

  try {
    $snapshot.startup_app_names = @(
      Get-CimInstance Win32_StartupCommand -ErrorAction Stop |
      ForEach-Object { [string]$_.Name } |
      Sort-Object -Unique
    )
  } catch {}

  $snapshot.agent_manager = Get-Endpoint "http://127.0.0.1:8787/health"
  $snapshot.project_visibility = Get-Endpoint "http://127.0.0.1:8000/health"

  try {
    $manager = Invoke-RestMethod -Uri "http://127.0.0.1:8787/health" -TimeoutSec 4
    $snapshot.agent_manager.write_enabled = $manager.write_enabled
    $snapshot.agent_manager.open_incidents = $manager.open_incidents
  } catch {}
  try {
    $ollama = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 4
    $snapshot.ollama_model_names = @($ollama.models | ForEach-Object { [string]$_.name })
  } catch {}

  try {
    $incidents = Invoke-RestMethod -Uri "http://127.0.0.1:8787/incidents" -TimeoutSec 4
    $snapshot.active_agent_incidents = @($incidents.incidents | Where-Object { $_.status -ne "resolved" }).Count
  } catch {}

  foreach ($key in $settings.Keys) {
    $snapshot.ai_user_settings[$key] = Get-UserSetting $key
  }

  if ($snapshot.memory.available_gb -ne $null -and $snapshot.memory.available_gb -lt 1.5) {
    $snapshot.recommendations += "Less than 1.5 GB available RAM: close unneeded browser tabs and nonessential background apps before launching local AI work."
  }
  if ($snapshot.cpu.load_percent -ne $null -and $snapshot.cpu.load_percent -gt 85) {
    $snapshot.recommendations += "CPU is highly utilized in this snapshot. Review the heaviest currently active processes in Task Manager."
  }
  if ($snapshot.system_disk.free_gb -ne $null -and $snapshot.system_disk.free_gb -lt 20) {
    $snapshot.recommendations += "Low disk space: review Windows Settings > System > Storage > Temporary files or Storage Sense."
  }
  if ($snapshot.pagefile_automatic -eq $false) {
    $snapshot.recommendations += "Enable Windows-managed paging file in Advanced system settings; do not disable the pagefile on an 8 GB machine."
  }
  if (-not $snapshot.project_visibility.reachable) {
    $snapshot.recommendations += "Project Visibility API on 127.0.0.1:8000 is offline: diagnose the existing checkout and startup separately."
  }
  if (-not $snapshot.agent_manager.reachable) {
    $snapshot.recommendations += "Agent Manager API on 127.0.0.1:8787 is offline: verify existing service before changing any runtime settings."
  }
  $snapshot.recommendations += "Review Windows Task Manager > Startup apps manually; keep security, backup, sync and hardware driver utilities you need."
  $snapshot.recommendations += "Do not disable Defender, Windows Update, SysMain, memory compression, or the paging file as a blanket performance tweak."
  return $snapshot
}

if ($Mode -eq "Apply") {
  if (-not (Test-Path -LiteralPath $backupPath -PathType Leaf)) {
    $before = [ordered]@{}
    foreach ($key in $settings.Keys) { $before[$key] = Get-UserSetting $key }
    [ordered]@{
      created_utc = (Get-Date).ToUniversalTime().ToString("o")
      user_variables = $before
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $backupPath -Encoding UTF8
    Write-Host "Saved reversible settings backup: $backupPath"
  }
  foreach ($key in $settings.Keys) { Set-UserSetting $key $settings[$key] }
  Write-Host "Applied user-scope low-memory AI settings. Already-running Ollama and agents are unchanged until a controlled restart." -ForegroundColor Green
} elseif ($Mode -eq "Restore") {
  if (-not (Test-Path -LiteralPath $backupPath -PathType Leaf)) {
    throw "No previous AI profile backup exists at $backupPath. Nothing changed."
  }
  $backup = Get-Content -LiteralPath $backupPath -Raw | ConvertFrom-Json
  foreach ($entry in $backup.user_variables.PSObject.Properties) {
    if ($settings.Contains($entry.Name)) {
      Set-UserSetting $entry.Name ([string]$entry.Value)
    }
  }
  Write-Host "Restored backed-up AI settings. Already-running services are unchanged until a controlled restart." -ForegroundColor Green
}

$report = Get-SystemSnapshot
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
$reportPath = Join-Path $ReportDirectory ("windows11-performance-" + $stamp + ".json")
$report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $reportPath -Encoding UTF8

Write-Host ""
Write-Host "Windows 11 + Agent Manager performance report" -ForegroundColor Cyan
Write-Host "Mode: $Mode"
Write-Host "RAM available (GB): $($report.memory.available_gb)"
Write-Host "CPU load (%): $($report.cpu.load_percent)"
Write-Host "Free system disk (GB): $($report.system_disk.free_gb)"
Write-Host "Windows-managed pagefile: $($report.pagefile_automatic)"
Write-Host "Agent Manager reachable: $($report.agent_manager.reachable)"
Write-Host "Project Visibility reachable: $($report.project_visibility.reachable)"
Write-Host "Active agent incidents: $($report.active_agent_incidents)"
Write-Host "Report saved: $reportPath"
Write-Host ""
$report.top_memory_processes | Format-Table -AutoSize
Write-Host "Recommendations:"
$report.recommendations | ForEach-Object { Write-Host "- $_" }
