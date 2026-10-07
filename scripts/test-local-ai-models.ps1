param(
  [string]$BaseUrl = "http://127.0.0.1:11434/v1/chat/completions",
  [string]$GeneralModel = "bloglab-qwen36-efficient",
  [string]$CoderModel = "bloglab-katcoder-efficient"
)

$ErrorActionPreference = "Stop"

function Test-Model([string]$Model, [string]$Prompt) {
  $body = @{
    model = $Model
    messages = @(
      @{ role = "system"; content = "Return one compact JSON object only." },
      @{ role = "user"; content = $Prompt }
    )
    temperature = 0.1
    response_format = @{ type = "json_object" }
  } | ConvertTo-Json -Depth 8

  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  $result = Invoke-RestMethod -Uri $BaseUrl -Method Post -ContentType "application/json" -Body $body -TimeoutSec 600
  $sw.Stop()
  Write-Host "OK $Model  $([math]::Round($sw.Elapsed.TotalSeconds,1))s"
  Write-Host $result.choices[0].message.content
  Write-Host ""
}

Test-Model $GeneralModel '{"task":"Give a two-sentence Slovenian travel intro about Ljubljana without inventing facts."}'
Test-Model $CoderModel '{"task":"Return a safe minimal code-edit plan for changing a CSS border radius from 12px to 16px.","format":{"summary":"","edits":[]}}'
