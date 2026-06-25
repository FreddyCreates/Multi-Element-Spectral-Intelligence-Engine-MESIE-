# MESIE Virtual Processor — HTTP compute server (port 8750)
$ErrorActionPreference = "Stop"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { "C:\Users\Medin\Multi-Element-Spectral-Intelligence-Engine-MESIE-" }
$env:MESIE_ROOT = $Root

Write-Host "MESIE Virtual Processor"
Write-Host "  HTTP :8750 — embed/match/benchmark/exec"
Write-Host "  LRC ledger: .processor_vault/"
Write-Host ""

Set-Location $Root
python -m mesie.processor --serve
