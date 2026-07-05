param(
    [switch]$Once,
    [int]$IntervalMinutes = 7,
    [switch]$SkipServers
)

$ErrorActionPreference = "Continue"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
Set-Location $Root

Write-Host ""
Write-Host "MESIE 4-Tier Market Ready — Sleep Mode" -ForegroundColor Cyan
Write-Host "  Tier 1 PROVE    -> ops-triad + production tiers"
Write-Host "  Tier 2 PACKAGE  -> quality-triad + tokens + FIVE_BUSINESSES"
Write-Host "  Tier 3 PLATFORM -> intel-triad + platforms + HERMES"
Write-Host "  Tier 4 SHIP     -> research-triad + portal + ICP"
Write-Host ""

python -m mesie.market.four_tier_loop --manifest

if (-not $SkipServers) {
    Write-Host "==> Persistent servers (:8750 :8765 :8767)" -ForegroundColor Yellow
    & (Join-Path $Root "Start-MESIE-Local.ps1") -SkipIcp -SkipJulia

    Write-Host "==> Autonomous orchestrator (background)" -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-WindowStyle", "Minimized", "-Command", "cd '$Root'; python -m mesie.server.autonomous_orchestrator" -ErrorAction SilentlyContinue
}

$intervalSec = [Math]::Max(180, $IntervalMinutes * 60)

if ($Once) {
    python -m mesie.market.four_tier_loop --once
} else {
    Write-Host ""
    Write-Host "SLEEP SAFE — market loop running every $IntervalMinutes min" -ForegroundColor Green
    Write-Host "  State: deliverables/market/FOUR_TIER_MARKET_READY_STATE.json"
    Write-Host "  Feed:  deliverables/market/FOUR_TIER_MARKET_READY_FEED.jsonl"
    Write-Host "  API:   GET http://127.0.0.1:8750/processor/market-ready"
    Write-Host "  Stop:  Ctrl+C in this window"
    Write-Host ""
    python -m mesie.market.four_tier_loop --interval $intervalSec
}