# Start MESIE Reality Capsula — React + Node + Rust
$ErrorActionPreference = "Stop"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
$Capsula = Join-Path $Root "apps\reality-capsula"
Set-Location $Capsula

Write-Host ""
Write-Host "MESIE Reality Capsula" -ForegroundColor Cyan
Write-Host "  React client:  http://127.0.0.1:5173"
Write-Host "  Node API:      http://127.0.0.1:8780"
Write-Host "  Processor:     http://127.0.0.1:8750 (required)"
Write-Host ""

# Processor health
try {
  $r = Invoke-WebRequest -Uri "http://127.0.0.1:8750/processor/status" -TimeoutSec 3 -UseBasicParsing
  Write-Host "  Processor: LIVE" -ForegroundColor Green
} catch {
  Write-Host "  Processor: OFFLINE — start in another terminal:" -ForegroundColor Yellow
  Write-Host "    python -m mesie.processor --serve"
  Write-Host ""
}

# Rust (optional)
if (Get-Command cargo -ErrorAction SilentlyContinue) {
  Write-Host "  Building Rust core..." -ForegroundColor DarkGray
  Push-Location (Join-Path $Capsula "rust-core")
  cargo build --release 2>&1 | Out-Null
  Pop-Location
  Write-Host "  Rust: built" -ForegroundColor Green
} else {
  Write-Host "  Rust: cargo not found — JS fallback" -ForegroundColor Yellow
}

# Node deps
if (-not (Test-Path "node_modules")) {
  Write-Host "  npm install..." -ForegroundColor DarkGray
  npm install
}

Start-Process "http://127.0.0.1:5173"
npm run dev
