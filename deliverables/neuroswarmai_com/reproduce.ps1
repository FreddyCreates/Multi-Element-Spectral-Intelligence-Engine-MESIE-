# NeuroSwarmAI / MESIE — full PowerShell repro harness (edge contested)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot
. (Join-Path $RepoRoot "scripts\MESIE.ps1")

Write-Host "=== MESIE Edge Repro (PowerShell) ===" -ForegroundColor Cyan
Write-Host "Root: $RepoRoot"

Invoke-MESIEProofSubstrate
Invoke-MESIETool interior-datacenter
Invoke-MESIETool cluster-edge
python scripts/run_neuroswarm_readiness.py

Write-Host "Done. Evidence: deliverables\neuroswarmai_com\evidence_manifest.json" -ForegroundColor Green