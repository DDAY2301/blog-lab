param(
  [ValidateSet("efficient","quality")]
  [string]$Profile = "efficient",
  [string]$ModelDir = "$env:USERPROFILE\.bloglab\models",
  [switch]$PersistEnv = $true
)

$ErrorActionPreference = "Stop"

function Require-Command([string]$Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "$Name ni nameščen ali ni v PATH."
  }
}

function Download-IfMissing([string]$Url, [string]$OutFile) {
  if (Test-Path $OutFile) {
    Write-Host "Obstoji: $OutFile"
    return
  }
  Write-Host "Prenašam $(Split-Path $OutFile -Leaf) ..."
  New-Item -ItemType Directory -Force -Path (Split-Path $OutFile) | Out-Null
  & curl.exe -L --fail --retry 3 --retry-delay 5 --output $OutFile $Url
  if ($LASTEXITCODE -ne 0) { throw "Prenos ni uspel: $Url" }
}

function Create-GgufModel([string]$Alias, [string]$Gguf, [int]$Context, [double]$Temperature) {
  $modelfile = Join-Path $env:TEMP ("BlogLab-" + ($Alias -replace "[^A-Za-z0-9_-]","_") + ".Modelfile")
  @"
FROM $Gguf
PARAMETER num_ctx $Context
PARAMETER temperature $Temperature
PARAMETER top_p 0.90
PARAMETER repeat_penalty 1.05
"@ | Set-Content -Path $modelfile -Encoding UTF8
  Write-Host "Ustvarjam Ollama model $Alias ..."
  & ollama create $Alias -f $modelfile
  if ($LASTEXITCODE -ne 0) { throw "ollama create ni uspel za $Alias" }
  Remove-Item $modelfile -Force -ErrorAction SilentlyContinue
}

Require-Command "ollama"
Require-Command "curl.exe"

try {
  Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5 | Out-Null
} catch {
  Write-Host "Zaganjam Ollama ..."
  Start-Process -WindowStyle Hidden ollama -ArgumentList "serve"
  Start-Sleep -Seconds 4
}

$ramBytes = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$ramGB = [math]::Round($ramBytes / 1GB, 0)
Write-Host "System RAM: $ramGB GB"

if ($Profile -eq "efficient") {
  if ($ramGB -lt 16) {
    Write-Warning "Manj kot 16 GB RAM: 35B-A3B modeli bodo zelo omejeni. Obdržan bo 7B fallback."
  }
  $qwenFile = Join-Path $ModelDir "Qwen3.6-35B-A3B-IQ2_XXS.gguf"
  $katFile  = Join-Path $ModelDir "KAT-Coder-V2.5-Dev-IQ2XXS.gguf"

  Download-IfMissing "https://huggingface.co/bartowski/Qwen_Qwen3.6-35B-A3B-GGUF/resolve/main/Qwen_Qwen3.6-35B-A3B-IQ2_XXS.gguf?download=true" $qwenFile
  Download-IfMissing "https://huggingface.co/Ninnix96/KAT-Coder-V2.5-Dev-gguf/resolve/main/KAT-Coder-V2.5-Dev-IQ2XXS-w2Q2K-AProjQ8-SExpQ8-OutQ8-imatrix.gguf?download=true" $katFile

  Create-GgufModel "bloglab-qwen36-efficient" $qwenFile 32768 0.20
  Create-GgufModel "bloglab-katcoder-efficient" $katFile 32768 0.10
} else {
  Write-Host "Quality profil: približno 21-24 GB uteži na model; na 6 GB VRAM bo večina inference na CPU/RAM."
  & ollama pull "qwen3.6:35b-a3b-q4_K_M"
  if ($LASTEXITCODE -ne 0) { throw "Qwen3.6 Q4 pull ni uspel." }
  & ollama pull "frob/kat-coder-v2.5-dev:35b-a3b-q4_K_M"
  if ($LASTEXITCODE -ne 0) { throw "KAT-Coder Q4 pull ni uspel." }

  @"
FROM qwen3.6:35b-a3b-q4_K_M
PARAMETER num_ctx 32768
PARAMETER temperature 0.20
PARAMETER top_p 0.90
"@ | Set-Content "$env:TEMP\BlogLab-Qwen.Modelfile" -Encoding UTF8
  & ollama create "bloglab-qwen36-efficient" -f "$env:TEMP\BlogLab-Qwen.Modelfile"

  @"
FROM frob/kat-coder-v2.5-dev:35b-a3b-q4_K_M
PARAMETER num_ctx 32768
PARAMETER temperature 0.10
PARAMETER top_p 0.90
"@ | Set-Content "$env:TEMP\BlogLab-KAT.Modelfile" -Encoding UTF8
  & ollama create "bloglab-katcoder-efficient" -f "$env:TEMP\BlogLab-KAT.Modelfile"
}

& ollama pull "qwen2.5-coder:7b"

if ($PersistEnv) {
  [Environment]::SetEnvironmentVariable("LOCAL_MODEL_ENABLED", "true", "User")
  [Environment]::SetEnvironmentVariable("LOCAL_MODEL_BASE_URL", "http://127.0.0.1:11434/v1/chat/completions", "User")
  [Environment]::SetEnvironmentVariable("LOCAL_GENERAL_MODEL", "bloglab-qwen36-efficient", "User")
  [Environment]::SetEnvironmentVariable("LOCAL_CODER_MODEL", "bloglab-katcoder-efficient", "User")
  [Environment]::SetEnvironmentVariable("LOCAL_FAST_MODEL", "qwen2.5-coder:7b", "User")
  [Environment]::SetEnvironmentVariable("LOCAL_MODEL_TIMEOUT", "300", "User")
}

Write-Host ""
Write-Host "Nameščeni modeli:"
& ollama list
Write-Host ""
Write-Host "Nato zaženi:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\test-local-ai-models.ps1"
