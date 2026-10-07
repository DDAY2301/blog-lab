$ErrorActionPreference="Continue"
$checks=@(
  @{name="Agent Manager";url="http://127.0.0.1:8787/health"},
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
  $c=Invoke-RestMethod http://127.0.0.1:8790/v1/models -TimeoutSec 5
  Write-Host "PASS  Colibri active" -ForegroundColor Green
  $c | ConvertTo-Json -Depth 8
}catch{
  Write-Host "INFO  Colibri standby/off. Ollama fallback remains active." -ForegroundColor Yellow
}
