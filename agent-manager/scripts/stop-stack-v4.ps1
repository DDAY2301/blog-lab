$ErrorActionPreference="SilentlyContinue"
$home=[Environment]::GetEnvironmentVariable("COLIBRI_HOME","User")
if($home -and (Test-Path (Join-Path $home "c\coli"))){
  Push-Location $home
  & py -3 c\coli stop 2>$null | Out-Null
  Pop-Location
}
$ports=@(8788,8787,8000)
foreach($port in $ports){
  Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}
$fleetConfig=[Environment]::GetEnvironmentVariable("FLEET_TUNNEL_CONFIG","User")
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'manager.guardian_v3|manager.watchdog_v4' -or
    ($fleetConfig -and $_.Name -like 'cloudflared*' -and $_.CommandLine -match [regex]::Escape($fleetConfig))
  } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Write-Host "Manager, Fleet Remote, Guardian, Watchdog, Project Visibility, Fleet Tunnel and Colibri processes stopped. Ollama left running."
