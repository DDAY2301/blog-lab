$ErrorActionPreference="Continue"

function Probe([string]$Name,[string]$Url){
  try{
    $r=Invoke-RestMethod -Uri $Url -TimeoutSec 5
    return [pscustomobject]@{
      Component=$Name
      State="UP"
      Detail=($r | ConvertTo-Json -Compress -Depth 4)
    }
  }catch{
    return [pscustomobject]@{
      Component=$Name
      State="DOWN"
      Detail=$_.Exception.Message
    }
  }
}

$rows=@()
$rows+=Probe "Agent Manager" "http://127.0.0.1:8787/health"
$rows+=Probe "Project Visibility" "http://127.0.0.1:8000/health"
$rows+=Probe "Ollama" "http://127.0.0.1:11434/api/tags"

$base=[Environment]::GetEnvironmentVariable("COLIBRI_BASE_URL","User")
if(-not $base){ $base=$env:COLIBRI_BASE_URL }
if($base){
  $health=($base -replace '/v1/?$','') + "/health"
  $rows+=Probe "Colibri" $health
}else{
  $rows+=[pscustomobject]@{
    Component="Colibri"
    State="STANDBY"
    Detail="No configured Colibri model/API. Ollama fallback remains active."
  }
}

$watchdog=Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'manager\.watchdog_v4' } |
  Select-Object -First 1

$rows+=[pscustomobject]@{
  Component="Watchdog"
  State=$(if($watchdog){"UP"}else{"DOWN"})
  Detail=$(if($watchdog){"PID $($watchdog.ProcessId)"}else{"not running"})
}

$guardian=Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'manager\.guardian_v3' } |
  Select-Object -First 1

$rows+=[pscustomobject]@{
  Component="Guardian"
  State=$(if($guardian){"UP"}else{"DOWN"})
  Detail=$(if($guardian){"PID $($guardian.ProcessId)"}else{"not running"})
}

$rows | Format-Table -AutoSize
