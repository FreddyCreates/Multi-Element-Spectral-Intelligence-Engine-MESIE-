# Start-EnterpriseExecution.ps1 — unify 3 repos, run enterprise DAG
param([string]$Mission = "enterprise-ship", [string[]]$Skip = @())

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "ENTERPRISE EXECUTION ENGINE" -ForegroundColor Cyan
Write-Host "  3 repos | 14 products | 13-node DAG"

$skipArg = if ($Skip.Count) { @("--skip") + $Skip } else { @() }
python -m mesie.enterprise.execution_engine --mission $Mission @skipArg

Write-Host ""
Write-Host "Thread:" -ForegroundColor Green (Get-Content "deliverables\enterprise\UNIFIED_REPO_THREAD.json" -Raw | ConvertFrom-Json).thread_intact
Write-Host "State: deliverables\enterprise\EXECUTION_ENGINE_STATE.json"
Write-Host "Docs:  deliverables\enterprise\ENTERPRISE_EXECUTION_ENGINE.md"