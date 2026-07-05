# Start-PersistentServers.ps1 — never-stop virtual MESIE servers
$ErrorActionPreference = "Stop"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
Set-Location $Root

Write-Host "MESIE Persistent Virtual Servers v1.2.0" -ForegroundColor Cyan
Write-Host "  :8750 Virtual Processor"
Write-Host "  :8765 Universal MCP"
Write-Host "  :8767 Career Hub (1000 careers)"
Write-Host "  :8770 Sovereign OS dashboard"
Write-Host "  ML recursive loop (5 min)"
Write-Host ""

python scripts/run_persistent_servers.py