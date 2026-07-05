param([switch]$ForgeOnly, [switch]$Serve)

$ErrorActionPreference = "Continue"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
Set-Location $Root

Write-Host "MESIE Model Platforms — MVP + Workers + Protocol Bridge" -ForegroundColor Cyan
python scripts/forge_model_platforms.py

if ($ForgeOnly) { exit 0 }

Write-Host ""
Write-Host "Web surfaces:" -ForegroundColor Green
Write-Host "  websites/platform-hub/index.html   — command hub (all services)"
Write-Host "  websites/model-hub/index.html      — catalog + encode + forge + benchmark"
Write-Host "  websites/solus-console/index.html  — SOLUS formal stack"
Write-Host "  websites/auro-studio/index.html    — Auro native speaking"
Write-Host "  websites/producer-lab/index.html   — ML producer pipeline"
Write-Host "  websites/computing-family/index.html — 8 products + squads"
Write-Host "  websites/reality-engine/index.html — design reality 3D"
Write-Host "  websites/enterprise-4k/index.html  — enterprise command"
Write-Host ""
Write-Host "API (processor :8750):" -ForegroundColor Green
Write-Host "  GET  /processor/models"
Write-Host "  GET  /processor/platform"
Write-Host "  POST /processor/platform/{service_id}/invoke"
Write-Host ""
Write-Host "Manifests: deliverables/platform/" -ForegroundColor Yellow

if ($Serve) {
    Write-Host "Starting virtual processor..." -ForegroundColor Cyan
    python -m mesie.processor --serve
}