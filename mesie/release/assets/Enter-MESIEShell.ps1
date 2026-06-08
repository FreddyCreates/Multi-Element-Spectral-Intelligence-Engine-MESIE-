# Open MESIE SDK in a dedicated PowerShell session (pip install or dev checkout).
if ($env:MESIE_HOME) {
    $ConfigDir = $env:MESIE_HOME
} else {
    $ConfigDir = Join-Path $HOME ".mesie"
}
$MesiePs1 = Join-Path $ConfigDir "MESIE.ps1"
if (-not (Test-Path $MesiePs1)) {
    mesie-bootstrap | Out-Null
}

$openCmd = "if (Test-Path '$MesiePs1') { . '$MesiePs1' }; Write-Host 'MESIE shell ready — Start-MESIECopilot' -ForegroundColor Green"

if (Get-Command wt.exe -ErrorAction SilentlyContinue) {
    wt.exe powershell -NoExit -ExecutionPolicy Bypass -Command $openCmd
} else {
    Start-Process powershell -ArgumentList @(
        "-NoExit", "-ExecutionPolicy", "Bypass",
        "-Command", $openCmd
    )
}