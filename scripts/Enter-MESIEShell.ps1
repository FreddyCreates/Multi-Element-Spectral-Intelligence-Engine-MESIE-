# Open MESIE SDK in a dedicated PowerShell session with helpers loaded.
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$MesiePs1 = Join-Path $RepoRoot "scripts\MESIE.ps1"

if (Get-Command wt.exe -ErrorAction SilentlyContinue) {
    wt.exe powershell -NoExit -ExecutionPolicy Bypass -Command "Set-Location '$RepoRoot'; . '$MesiePs1'; Write-Host 'MESIE shell ready.' -ForegroundColor Green"
} else {
    Start-Process powershell -ArgumentList @(
        "-NoExit", "-ExecutionPolicy", "Bypass",
        "-Command", "Set-Location '$RepoRoot'; . '$MesiePs1'; Write-Host 'MESIE shell ready.' -ForegroundColor Green"
    )
}