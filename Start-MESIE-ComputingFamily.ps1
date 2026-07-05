param(
    [int]$Trials = 200,
    [int]$McTrials = 100,
    [switch]$SkipSquads
)

$ErrorActionPreference = "Continue"
$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
Set-Location $Root

Write-Host "MESIE COMPUTING FAMILY — Full Official Benchmarks" -ForegroundColor Cyan
Write-Host ""

$args = @("scripts/run_mesie_computing_family_benchmarks.py", "--trials", $Trials, "--mc-trials", $McTrials)
if ($SkipSquads) { $args += "--skip-squads" }
python @args
exit $LASTEXITCODE