# MESIE / MAESI SDK — PowerShell entry (full terminal peer)
# Usage: . .\scripts\MESIE.ps1
#        Get-MESIETools
#        Invoke-MESIETool proof-substrate
#        Open-MESIETerminal

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:MesieRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $script:MesieRoot

function Get-MESIERoot {
    return $script:MesieRoot
}

function Get-MESIETools {
    python -m mesie.tools.cli list
}

function Invoke-MESIETool {
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$ToolId,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Extra
    )
    $extra = ($Extra -join " ").Trim()
    if ($extra) {
        python -m mesie.tools.cli run $ToolId $extra
    } else {
        python -m mesie.tools.cli run $ToolId
    }
    if ($LASTEXITCODE -ne 0) { throw "MESIE tool '$ToolId' failed with exit $LASTEXITCODE" }
}

function Invoke-MESIEReadiness {
    python scripts/run_neuroswarm_readiness.py @args
}

function Invoke-MESIEProofSubstrate {
    param([switch]$Verify)
    if ($Verify) {
        python scripts/run_proof_substrate.py --verify
    } else {
        python scripts/run_proof_substrate.py
    }
}

function Open-MESIETerminal {
    param([string]$Command)
    $args = @("open-terminal")
    if ($Command) { $args += @("--command", $Command) }
    python -m mesie.tools.cli @args
}

function Enter-MESIEShell {
    python -m mesie.tools.cli shell
}

function Show-MESIESurfaces {
    python -c "from mesie.sdk.terminal import open_surfaces; import json; print(json.dumps(open_surfaces(), indent=2))"
}

Write-Host "MESIE SDK loaded — root: $script:MesieRoot" -ForegroundColor Cyan
Write-Host "Commands: Get-MESIETools | Invoke-MESIETool <id> | Enter-MESIEShell | Open-MESIETerminal" -ForegroundColor DarkGray