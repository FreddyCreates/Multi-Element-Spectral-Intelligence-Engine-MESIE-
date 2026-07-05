# HERMES one-shot deploy — ItsnotAILabs / NOVA PROTOCOL
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "HERMES Fleet deploy" -ForegroundColor Cyan
python "$Root/../../scripts/forge_hermes_fleet.py"

if (Get-Command wrangler -ErrorAction SilentlyContinue) {
  Get-ChildItem "$Root/workers" -Directory | ForEach-Object {
    Write-Host "Deploy $($_.Name)..." -ForegroundColor Green
    Push-Location $_.FullName
    wrangler deploy 2>&1 | Out-Host
    Pop-Location
  }
} else {
  Write-Host "wrangler not found — pack ready at deliverables/hermes/" -ForegroundColor Yellow
}
