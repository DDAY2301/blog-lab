$ErrorActionPreference = "Stop"

Write-Host "Agent Manager - MAX CAPABILITY model setup"
Write-Host ""

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw "Ollama ni najden."
}

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5 | Out-Null
} catch {
    Write-Host "Zaganjam Ollama..."
    Start-Process -WindowStyle Hidden ollama -ArgumentList "serve"
    Start-Sleep -Seconds 3
}

$ramBytes = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$ramGB = [math]::Round($ramBytes / 1GB, 0)
Write-Host "Detected system RAM: $ramGB GB"

# Choose the strongest practical local model for available system memory.
# Users with very large workstations can still manually install the 125B
# qwen3.8-flash-next model; auto-max will always prefer it when installed.
if ($ramGB -ge 48) {
    $model = "qwen3.8:27b-q8_0"
} elseif ($ramGB -ge 28) {
    $model = "qwen3.8:27b"
} elseif ($ramGB -ge 20) {
    $model = "devstral-small-2"
} else {
    $model = "qwen2.5-coder:7b"
}

Write-Host "Installing strongest practical model for this machine: $model"
ollama pull $model
if ($LASTEXITCODE -ne 0) {
    throw "Ollama model download failed."
}

Write-Host ""
Write-Host "Installed models:"
ollama list
Write-Host ""
Write-Host "Agent Manager is configured as AGENT_MANAGER_MODEL=auto-max."
Write-Host "It will always choose the strongest installed model from its capability ranking."
