# Start MESIE web apps (processor :8750 serves /websites/*)
$ErrorActionPreference = "Stop"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
Set-Location $Root

$python = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "py" -ArgumentList "-3" }

Write-Host ""
Write-Host "MESIE Web Apps" -ForegroundColor Cyan
Write-Host "  Processor API:  http://127.0.0.1:8750"
Write-Host "  Platform Hub:   http://127.0.0.1:8750/websites/platform-hub/index.html"
Write-Host "  Reality Engine: http://127.0.0.1:8750/websites/reality-engine/index.html"
Write-Host "  All surfaces:   http://127.0.0.1:8750/processor/surfaces"
Write-Host ""

Start-Process "http://127.0.0.1:8750/websites/reality-engine/index.html"
& $python -m mesie.processor --serve
