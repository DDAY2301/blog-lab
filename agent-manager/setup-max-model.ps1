param(
  [ValidateSet("auto","efficient","quality")]
  [string]$Profile = "auto",
  [string]$ModelDir = "$env:USERPROFILE\.agent-manager\models"
)

$ErrorActionPreference = "Stop"

Write-Host "Agent Manager - Qwen3.6 + KAT-Coder model setup"
Write-Host ""

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw "Ollama ni najden."
}
if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    throw "curl.exe ni najden."
}

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5 | Out-Null
} catch {
    Write-Host "Zaganjam Ollama..."
    Start-Process -WindowStyle Hidden ollama -ArgumentList "serve"
    Start-Sleep -Seconds 4
}

$ramBytes = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
$ramGB = [math]::Round($ramBytes / 1GB, 0)
$vramGB = 0
try {
    $raw = (& nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>$null | Select-Object -First 1)
    if ($raw) { $vramGB = [math]::Round(([double]$raw) / 1024, 0) }
} catch {}

Write-Host "System RAM: $ramGB GB"
Write-Host "GPU VRAM:   $vramGB GB"

if ($Profile -eq "auto") {
    if ($ramGB -ge 32 -and $vramGB -ge 20) {
        $Profile = "quality"
    } elseif ($ramGB -ge 16) {
        $Profile = "efficient"
    } else {
        $Profile = "fallback"
    }
}

function Download-IfMissing([string]$Url, [string]$OutFile) {
    if (Test-Path $OutFile) {
        Write-Host "Obstoji: $OutFile"
        return
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $OutFile) | Out-Null
    Write-Host "Prenašam $(Split-Path $OutFile -Leaf) ..."
    & curl.exe -L --fail --retry 3 --retry-delay 5 --output $OutFile $Url
    if ($LASTEXITCODE -ne 0) { throw "Prenos ni uspel: $Url" }
}

function Create-GgufModel([string]$Alias, [string]$Gguf, [double]$Temperature) {
    $modelfile = Join-Path $env:TEMP ("AgentManager-" + ($Alias -replace "[^A-Za-z0-9_-]","_") + ".Modelfile")
    @"
FROM $Gguf
PARAMETER num_ctx 32768
PARAMETER temperature $Temperature
PARAMETER top_p 0.90
PARAMETER repeat_penalty 1.05
"@ | Set-Content -Path $modelfile -Encoding UTF8
    & ollama create $Alias -f $modelfile
    if ($LASTEXITCODE -ne 0) { throw "ollama create ni uspel za $Alias" }
    Remove-Item $modelfile -Force -ErrorAction SilentlyContinue
}

if ($Profile -eq "quality") {
    Write-Host "Quality profil: Q4 modeli (~21-24 GB uteži na model)."
    ollama pull qwen3.6:35b-a3b-q4_K_M
    if ($LASTEXITCODE -ne 0) { throw "Qwen3.6 pull ni uspel." }
    ollama pull frob/kat-coder-v2.5-dev:35b-a3b-q4_K_M
    if ($LASTEXITCODE -ne 0) { throw "KAT-Coder pull ni uspel." }

    @"
FROM qwen3.6:35b-a3b-q4_K_M
PARAMETER num_ctx 32768
PARAMETER temperature 0.20
PARAMETER top_p 0.90
"@ | Set-Content "$env:TEMP\AgentManager-Qwen.Modelfile" -Encoding UTF8
    ollama create bloglab-qwen36-efficient -f "$env:TEMP\AgentManager-Qwen.Modelfile"

    @"
FROM frob/kat-coder-v2.5-dev:35b-a3b-q4_K_M
PARAMETER num_ctx 32768
PARAMETER temperature 0.10
PARAMETER top_p 0.90
"@ | Set-Content "$env:TEMP\AgentManager-KAT.Modelfile" -Encoding UTF8
    ollama create bloglab-katcoder-efficient -f "$env:TEMP\AgentManager-KAT.Modelfile"
}
elseif ($Profile -eq "efficient") {
    Write-Host "Efficient profil: kompaktni IQ2 GGUF modeli za hybrid GPU/CPU inference."
    $qwenFile = Join-Path $ModelDir "Qwen3.6-35B-A3B-IQ2_XXS.gguf"
    $katFile  = Join-Path $ModelDir "KAT-Coder-V2.5-Dev-IQ2XXS.gguf"

    Download-IfMissing "https://huggingface.co/bartowski/Qwen_Qwen3.6-35B-A3B-GGUF/resolve/main/Qwen_Qwen3.6-35B-A3B-IQ2_XXS.gguf?download=true" $qwenFile
    Download-IfMissing "https://huggingface.co/Ninnix96/KAT-Coder-V2.5-Dev-gguf/resolve/main/KAT-Coder-V2.5-Dev-IQ2XXS-w2Q2K-AProjQ8-SExpQ8-OutQ8-imatrix.gguf?download=true" $katFile

    Create-GgufModel "bloglab-qwen36-efficient" $qwenFile 0.20
    Create-GgufModel "bloglab-katcoder-efficient" $katFile 0.10
}
else {
    Write-Warning "Manj kot 16 GB RAM: 35B-A3B modelov ne nameščam avtomatsko. Uporabljam 7B fallback."
}

ollama pull qwen2.5-coder:7b
if ($LASTEXITCODE -ne 0) { throw "Fallback model download failed." }

[Environment]::SetEnvironmentVariable("AGENT_MANAGER_MODEL", "auto-max", "User")
[Environment]::SetEnvironmentVariable("AGENT_MANAGER_CONTEXT", "32768", "User")

Write-Host ""
Write-Host "Installed models:"
ollama list
Write-Host ""
Write-Host "Priority:"
Write-Host "  1) bloglab-katcoder-efficient"
Write-Host "  2) bloglab-qwen36-efficient"
Write-Host "  3) existing coding fallbacks"
