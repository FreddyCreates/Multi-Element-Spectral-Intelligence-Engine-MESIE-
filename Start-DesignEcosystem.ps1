param([switch]$ForgeOnly)

$ErrorActionPreference = "Continue"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
Set-Location $Root

Write-Host "MESIE Design Reality Ecosystem" -ForegroundColor Cyan
Write-Host "  10 cores x 10 paradigms = 100 Latin intelligence agents"
Write-Host "  42 protocols | Three.js reality engine | native SOLUS/MESIE"
Write-Host ""

python scripts/forge_design_cores.py

if (-not $ForgeOnly) {
    Write-Host ""
    Write-Host "Surfaces:" -ForegroundColor Green
    Write-Host "  websites/reality-engine/index.html   (Core Realitas / Three.js)"
    Write-Host "  websites/computing-family/index.html"
    Write-Host "  GET http://127.0.0.1:8750/processor/design"
    Write-Host ""
    Write-Host "Manifest: deliverables/design/DESIGN_ECOSYSTEM_MANIFEST.json"
}