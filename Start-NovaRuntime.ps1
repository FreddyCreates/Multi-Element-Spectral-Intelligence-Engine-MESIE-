# NOVA Runtime — never stop. 70 careers + robotics swarm.
$ErrorActionPreference = "Stop"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { "C:\Users\Medin\Multi-Element-Spectral-Intelligence-Engine-MESIE-" }
$env:MESIE_ROOT = $Root

Write-Host "NOVA Runtime Supervisor"
Write-Host "  70 micro careers (real tasks, timer satellites)"
Write-Host "  robotics_satellite (fusion + LRC + threat_p50)"
Write-Host "  feed: deliverables/nova/NOVA_RUNTIME_FEED.jsonl"
Write-Host "  NEVER STOP — watchdog restarts dead workers"
Write-Host ""

Set-Location $Root
python scripts/run_nova_runtime.py