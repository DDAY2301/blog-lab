param(
  [ValidateSet("efficient","quality")]
  [string]$Profile = "efficient",
  [switch]$InstallQwen36,
  [switch]$PersistEnv = $true
)

$ErrorActionPreference = "Stop"

function Require-Command([string]$Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "$Name ni nameščen ali ni v PATH."
  }
}

function Ensure-Ollama {
  try {
    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5 | Out-Null
  } catch {
    Write-Host "Zaganjam Ollama ..."
    Start-Process -WindowStyle Hidden ollama -ArgumentList "serve"
    Start-Sleep -Seconds 4
    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 10 | Out-Null
  }
}

function Install-HfModel([string]$Source, [string]$Alias) {
  Write-Host "Prenašam / preverjam $Source ..." -ForegroundColor Cyan
  & ollama run $Source "Reply exactly READY and nothing else."
  if ($LASTEXITCODE -ne 0) { throw "Ollama import ni uspel za $Source" }

  & ollama cp $Source $Alias
  if ($LASTEXITCODE -ne 0) {
    $modelfile = Join-Path $env:TEMP ("BlogLab-" + ($Alias -replace "[^A-Za-z0-9_-]","_") + ".Modelfile")
    @"
FROM $Source
PARAMETER num_ctx 16384
PARAMETER temperature 0.10
PARAMETER top_p 0.90
"@ | Set-Content -Path $modelfile -Encoding UTF8
    & ollama create $Alias -f $modelfile
    Remove-Item $modelfile -Force -ErrorAction SilentlyContinue
    if ($LASTEXITCODE -ne 0) { throw "Alias $Alias ni bilo mogoče ustvariti." }
  }
}

Require-Command "ollama"
Ensure-Ollama

$ramBytes = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$ramGB = [math]::Round($ramBytes / 1GB, 1)
$drive = (Get-Item $PSScriptRoot).PSDrive
$diskGB = if ($drive -and $drive.Free) { [math]::Round($drive.Free / 1GB, 1) } else { 0 }

Write-Host "System RAM: $ramGB GB"
Write-Host "Free disk: $diskGB GB"

& ollama pull "qwen2.5-coder:7b"
if ($LASTEXITCODE -ne 0) { throw "Fast 7B model ni bilo mogoče prenesti." }

if ($Profile -eq "quality") {
  $katQuant = "Q4_K_M"
  if ($ramGB -lt 28) {
    Write-Warning "Quality KAT Q4 potrebuje precej RAM-a. Preklapljam na IQ3_M."
    $katQuant = "IQ3_M"
  }
} else {
  $katQuant = if ($ramGB -ge 24) { "IQ3_M" } else { "Q3_K_M" }
}

$katSource = "hf.co/Abiray/KAT-Coder-V2.5-Dev-Imatrix-GGUF:$katQuant"
Install-HfModel $katSource "bloglab-katcoder-efficient"

$generalModel = "qwen2.5-coder:7b"
if ($InstallQwen36) {
  Write-Host "Nameščam opcijski Qwen3.6 coding/general fallback..." -ForegroundColor Cyan
  & ollama pull "qwen3.6:35b-a3b-coding"
  if ($LASTEXITCODE -eq 0) {
    $generalModel = "qwen3.6:35b-a3b-coding"
  } else {
    Write-Warning "Qwen3.6 fallback ni bil nameščen; ostaja hitri 7B model."
  }
}

if ($PersistEnv) {
  [Environment]::SetEnvironmentVariable("LOCAL_MODEL_ENABLED", "true", "User")
  [Environment]::SetEnvironmentVariable("LOCAL_MODEL_BASE_URL", "http://127.0.0.1:11434/v1/chat/completions", "User")
  [Environment]::SetEnvironmentVariable("LOCAL_GENERAL_MODEL", $generalModel, "User")
  [Environment]::SetEnvironmentVariable("LOCAL_CODER_MODEL", "bloglab-katcoder-efficient", "User")
  [Environment]::SetEnvironmentVariable("LOCAL_FAST_MODEL", "qwen2.5-coder:7b", "User")
  [Environment]::SetEnvironmentVariable("LOCAL_MODEL_TIMEOUT", "300", "User")
}

Write-Host ""
Write-Host "Blog Lab local AI profile:" -ForegroundColor Green
Write-Host "  Fast/general: $generalModel"
Write-Host "  Expert coder: bloglab-katcoder-efficient ($katQuant)"
Write-Host ""
& ollama list
Write-Host ""
Write-Host "Nato zaženi:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\test-local-ai-models.ps1"
