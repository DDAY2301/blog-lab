$ErrorActionPreference="Continue"

function Check-ManagerV4 {
  $url="http://127.0.0.1:8787/health"
  try{
    $r=Invoke-RestMethod $url -TimeoutSec 10
    $version=[string]$r.version
    if(-not $r.ok -or -not ($version -like "4.*")){
      Write-Host ("FAIL  Agent Manager  {0}  expected V4, got version={1}" -f $url,$version) -ForegroundColor Red
      $r | ConvertTo-Json -Depth 8
      return $false
    }
    Write-Host ("PASS  Agent Manager V4  {0}" -f $url) -ForegroundColor Green
    $r | ConvertTo-Json -Depth 8
    return $true
  }catch{
    Write-Host ("FAIL  Agent Manager  {0}  {1}" -f $url,$_.Exception.Message) -ForegroundColor Red
    return $false
  }
}

[void](Check-ManagerV4)

$checks=@(
  @{name="Managed Agents";url="http://127.0.0.1:8787/managed-agents"},
  @{name="AI Providers";url="http://127.0.0.1:8787/providers"},
  @{name="Project Visibility";url="http://127.0.0.1:8000/health"},
  @{name="Ollama";url="http://127.0.0.1:11434/api/tags"}
)

foreach($c in $checks){
  try{
    $r=Invoke-RestMethod $c.url -TimeoutSec 10
    Write-Host ("PASS  {0}  {1}" -f $c.name,$c.url) -ForegroundColor Green
    $r | ConvertTo-Json -Depth 8
  }catch{
    Write-Host ("FAIL  {0}  {1}  {2}" -f $c.name,$c.url,$_.Exception.Message) -ForegroundColor Red
  }
}

try{
  $base=[Environment]::GetEnvironmentVariable("COLIBRI_BASE_URL","User")
  if(-not $base){ $base=$env:COLIBRI_BASE_URL }
  if(-not $base){ throw "No Colibri endpoint configured." }
  $modelsUrl=($base.TrimEnd("/") -replace '/v1$','') + "/v1/models"
  $c=Invoke-RestMethod $modelsUrl -TimeoutSec 5
  Write-Host "PASS  Colibri active" -ForegroundColor Green
  $c | ConvertTo-Json -Depth 8
}catch{
  Write-Host "INFO  Colibri standby/off. Ollama fallback remains active." -ForegroundColor Yellow
}
