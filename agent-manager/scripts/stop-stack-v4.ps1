$ErrorActionPreference="SilentlyContinue"
$ports=@(8787,8000,8790)
foreach($port in $ports){
  Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'manager.guardian_v3' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Write-Host "Manager, Project Visibility and Colibri processes stopped. Ollama left running."
