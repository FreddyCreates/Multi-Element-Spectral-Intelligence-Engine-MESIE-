# Start-MarketPush.ps1 - full market production push
$ErrorActionPreference = "Stop"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
Set-Location $Root

Write-Host "MESIE MARKET PUSH v1.2.0" -ForegroundColor Cyan

# Production stack alive
& (Join-Path $Root "Start-MESIEProduction.ps1")

# Token manifest + sample mint
python -c "from mesie.tokens.dual_bridge import write_manifest, mint_receipt_token; import json; write_manifest(); print(json.dumps(mint_receipt_token({'event':'market_push','version':'1.2.0'}), indent=2))"

# Market release zip
python scripts/package_market_release.py

# Market portal fork
python scripts/build_market_portal_fork.py

# Git init all forks
& (Join-Path $Root "scripts\init_career_fork_repos.ps1")

Write-Host ""
Write-Host "MARKET READY" -ForegroundColor Green
Write-Host "  Charter:    deliverables/market/MESIE_CHARTER.md"
Write-Host "  5 Business: deliverables/market/FIVE_BUSINESSES.json"
Write-Host "  Research:   deliverables/research/packs/"
Write-Host "  Tokens:     deliverables/tokens/MESIE_TOKEN_MANIFEST.json"
Write-Host "  Zip:        deliverables/market/MESIE_MARKET_RELEASE_1.2.0.zip"
Write-Host "  Websites:   .\scripts\serve_market_sites.ps1"
Write-Host "  GitHub:     .\scripts\publish_market_github.ps1  (after gh auth login)"