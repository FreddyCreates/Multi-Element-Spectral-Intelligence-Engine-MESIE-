param([switch]$ForgeOnly, [switch]$Serve)

$ErrorActionPreference = "Continue"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
Set-Location $Root

Write-Host "HERMES Fleet — NOVA PROTOCOL · ItsnotAILabs" -ForegroundColor Cyan
python scripts/forge_hermes_fleet.py

if ($ForgeOnly) { exit 0 }

Write-Host ""
Write-Host "12 Cloudflare Workers:" -ForegroundColor Green
Write-Host "  deliverables/hermes/workers/     — index.js + wrangler.toml each"
Write-Host "  deliverables/hermes/wrangler.toml"
Write-Host "  deliverables/hermes/icp/         — HERMES_ICP_CLI.json"
Write-Host "  deliverables/hermes/sdk/         — SDK + hermes-sdk.zip"
Write-Host "  deliverables/hermes/DEPLOY_SHOT.json"
Write-Host ""
Write-Host "Web: websites/hermes-fleet/index.html" -ForegroundColor Yellow
Write-Host "API: GET /processor/hermes · POST /processor/hermes/forge" -ForegroundColor Yellow
Write-Host "Alphas: 31 harnesses (11 base + 20 HERMES extended)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Deploy: deliverables/hermes/deploy.ps1" -ForegroundColor Cyan

if ($Serve) {
    python -m mesie.processor --serve
}