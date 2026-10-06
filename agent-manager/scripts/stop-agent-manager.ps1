Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'manager.guardian_v3|agent-manager.*run.py|run.py' } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force } catch {} }
