$ErrorActionPreference = "Stop"

Write-Host "Agent Manager v0.1 - local/free mode"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python ni najden."
}

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw "Ollama ni najden. Namesti Ollama in nato ponovno zaženi skripto."
}

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5 | Out-Null
} catch {
    Write-Host "Zaganjam Ollama..."
    Start-Process -WindowStyle Hidden ollama -ArgumentList "serve"
    Start-Sleep -Seconds 3
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\pip.exe install -r requirements.txt

Write-Host ""
Write-Host "API: http://127.0.0.1:8787"
Write-Host "Docs: http://127.0.0.1:8787/docs"
Write-Host ""
& .\.venv\Scripts\python.exe run.py
