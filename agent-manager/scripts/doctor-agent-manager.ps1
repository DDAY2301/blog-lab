$urls=@('http://127.0.0.1:8787/health','http://127.0.0.1:8787/system-map','http://127.0.0.1:8787/connections')
foreach($u in $urls){ try { Write-Host "PASS $u"; Invoke-RestMethod $u -TimeoutSec 5 | ConvertTo-Json -Depth 8 } catch { Write-Host "FAIL $u :: $($_.Exception.Message)" } }
