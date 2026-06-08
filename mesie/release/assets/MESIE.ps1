# MESIE / MAESI SDK — PowerShell module (pip install + ~/.mesie bootstrap)
# Usage: . "$env:USERPROFILE\.mesie\MESIE.ps1"
#        Start-MESIECopilot -Tier samgov

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($env:MESIE_HOME) {
    $script:MesieConfigDir = $env:MESIE_HOME
} else {
    $script:MesieConfigDir = Join-Path $HOME ".mesie"
}

function Get-MESIEConfigDir {
    return $script:MesieConfigDir
}

function Get-MESIETools {
    mesie-tools list
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
        mesie-tools run $ToolId $extra
    } else {
        mesie-tools run $ToolId
    }
    if ($LASTEXITCODE -ne 0) { throw "MESIE tool '$ToolId' failed with exit $LASTEXITCODE" }
}

function Invoke-MESIEReadiness {
    mesie-tools run neuroswarm-readiness @args
}

function Invoke-MESIEProofSubstrate {
    param([switch]$Verify)
    if ($Verify) {
        mesie-tools run proof-substrate --verify
    } else {
        mesie-tools run proof-substrate
    }
}

function Open-MESIETerminal {
    param([string]$Command)
    $args = @("open-terminal")
    if ($Command) { $args += @("--command", $Command) }
    mesie-tools @args
}

function Enter-MESIEShell {
    mesie-tools shell
}

function Show-MESIESurfaces {
    mesie-tools surfaces
}

function Start-MESIECopilot {
    param(
        [ValidateSet("sovereign", "samgov", "research")]
        [string]$Tier = "sovereign"
    )
    maesi --tier $Tier
}

function Install-MESIEBootstrap {
    param([switch]$InstallProfile)
    if ($InstallProfile) {
        mesie-bootstrap --install-profile
    } else {
        mesie-bootstrap
    }
}

Write-Host "MESIE SDK loaded — config: $script:MesieConfigDir" -ForegroundColor Cyan
Write-Host "Copilot: Start-MESIECopilot [-Tier sovereign|samgov|research]" -ForegroundColor DarkGray