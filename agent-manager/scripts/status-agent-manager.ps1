try { Invoke-RestMethod http://127.0.0.1:8787/health -TimeoutSec 3 | ConvertTo-Json -Depth 8 } catch { Write-Host 'AGENT MANAGER: NOT REACHABLE'; exit 1 }
