$ErrorActionPreference="SilentlyContinue"
$home=[Environment]::GetEnvironmentVariable("COLIBRI_HOME","User")
if($home -and (Test-Path (Join-Path $home "c\coli"))){
  Push-Location $home
  & py -3 c\coli stop 2>$null | Out-Null
  Pop-Location
}
$ports=@(8787,8000)
foreach($port in $ports){
  Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'manager.guardian_v3|manager.watchdog_v4' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Write-Host "Manager, Guardian, Watchdog, Project Visibility and Colibri processes stopped. Ollama left running."
