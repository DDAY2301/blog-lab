$ErrorActionPreference="Continue"
function Probe([string]$Name,[string]$Url){
  try{
    $r=Invoke-RestMethod $Url -TimeoutSec 5
    [pscustomobject]@{Component=$Name;State="UP";Detail=($r | ConvertTo-Json -Compress -Depth 4)}
  }catch{
    [pscustomobject]@{Component=$Name;State="DOWN";Detail=$_.Exception.Message}
  }
}
$rows=@()
$rows+=Probe "Agent Manager" "http://127.0.0.1:8787/health"
$rows+=Probe "Project Visibility" "http://127.0.0.1:8000/health"
$rows+=Probe "Ollama" "http://127.0.0.1:11434/api/tags"
try{
  $rows+=Probe "Colibri" ([Environment]::GetEnvironmentVariable("COLIBRI_BASE_URL","User").TrimEnd("/v1")+"/health")
}catch{
  $rows+=[pscustomobject]@{Component="Colibri";State="STANDBY";Detail="Not configured"}
}
$watchdog=Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'manager.watchdog_v4' } | Select-Object -First 1
$rows+=[pscustomobject]@{Component="Watchdog";State=$(if($watchdog){"UP"}else{"DOWN"});Detail=$(if($watchdog){"PID $($watchdog.ProcessId)"}else{"not running"})}
$rows | Format-Table -AutoSize
