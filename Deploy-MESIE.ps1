# Deploy-MESIE.ps1 — one-command sovereign production deploy
# Package → start NOVA runtime → start Virtual Processor → verify health
param(
    [switch]$Package,
    [switch]$DevKit,
    [switch]$Surface,
    [switch]$Mesh,
    [switch]$Official,
    [switch]$ICP,
    [ValidateSet("local", "ic")]
    [string]$IcpNetwork = "local",
    [switch]$VerifyOnly,
    [string]$BindHost = "127.0.0.1",
    [int]$ProcessorPort = 8750,
    [int]$NovaTimeoutSec = 180,
    [int]$ProcessorTimeoutSec = 90
)

$ErrorActionPreference = "Stop"

$Root = if ($env:MESIE_ROOT) { $env:MESIE_ROOT } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$env:MESIE_ROOT = $Root
Set-Location $Root

$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
$StatePath = Join-Path $Root "deliverables\nova\NOVA_RUNTIME_STATE.json"
$ProcessorUrl = "http://${BindHost}:${ProcessorPort}/processor/status"
$NovaRuntimeUrl = "http://${BindHost}:${ProcessorPort}/processor/nova-runtime"

function Write-Step([string]$Msg) {
    Write-Host ""
    Write-Host "==> $Msg" -ForegroundColor Cyan
}

function Test-HttpOk([string]$Url, [int]$TimeoutSec = 4) {
    try {
        $req = [System.Net.HttpWebRequest]::Create($Url)
        $req.Method = "GET"
        $req.Timeout = $TimeoutSec * 1000
        $resp = $req.GetResponse()
        $ok = ([int]$resp.StatusCode -eq 200)
        $resp.Close()
        return $ok
    } catch {
        return $false
    }
}

function Test-NovaRuntimeAlive {
    if (-not (Test-Path $StatePath)) { return $false }
    try {
        $st = Get-Content $StatePath -Raw | ConvertFrom-Json
        $age = ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) - [double]$st.ts
        $orgOk = ($st.micro_org.size -ge 65)
        return ($st.never_stop -and $orgOk -and ($age -lt 180))
    } catch {
        return $false
    }
}

function Test-ProcessRunning([string]$Pattern) {
    $procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue
    foreach ($p in $procs) {
        if ($p.CommandLine -and $p.CommandLine -match $Pattern) {
            return $true
        }
    }
    return $false
}

function Start-MesieBackground([string]$Label, [string[]]$CommandArgs, [string]$MatchPattern, [string]$LogName) {
    if (Test-ProcessRunning $MatchPattern) {
        Write-Host "  $Label already running (matched process)" -ForegroundColor DarkGray
        return $true
    }
    $logDir = Join-Path $Root "deliverables\deploy\logs"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $stdout = Join-Path $logDir "$LogName.out.log"
    $stderr = Join-Path $logDir "$LogName.err.log"
    $env:MESIE_ROOT = $Root
    Start-Process -FilePath $Python `
        -ArgumentList $CommandArgs `
        -WorkingDirectory $Root `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr | Out-Null
    Write-Host "  Started $Label (background, logs: deliverables/deploy/logs/$LogName.*.log)" -ForegroundColor Green
    return $true
}

function Wait-ForHealth {
    param(
        [scriptblock]$Predicate,
        [string]$Label,
        [int]$TimeoutSec
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        if (& $Predicate) {
            Write-Host "  OK $Label" -ForegroundColor Green
            return $true
        }
        Start-Sleep -Seconds 2
    }
    Write-Host "  TIMEOUT $Label" -ForegroundColor Yellow
    return $false
}

Write-Host ""
Write-Host "MESIE Sovereign Deploy" -ForegroundColor White
Write-Host "  Root: $Root"
Write-Host "  Processor: $ProcessorUrl"

if ($VerifyOnly) {
    Write-Step "Verify only"
    $nova = Test-NovaRuntimeAlive
    $proc = Test-HttpOk $ProcessorUrl
    $arch = Test-HttpOk "http://${BindHost}:${ProcessorPort}/processor/architecture"
    Write-Host "  NOVA state fresh: $nova"
    Write-Host "  Processor HTTP:   $proc"
    Write-Host "  Architecture API: $arch"
    if (-not ($nova -and $proc)) { exit 1 }
    exit 0
}

if ($Official) {
    Write-Step "Generate official commercial pack (tests + certifications + docs)"
    & $Python scripts/run_official_commercial_pack.py --quick --bundle
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Official pack partial - see deliverables/processor/official/" -ForegroundColor Yellow
    } else {
        Write-Host "  Official bundle ready" -ForegroundColor Green
    }
}

if ($Package) {
    Write-Step "Package services"
    & $Python scripts/package_services.py --all
    & $Python scripts/package_services.py --deploy virtual-processor --target powershell --apply
    & $Python scripts/package_services.py --deploy robotics-satellite --target local-http --apply
    Write-Host "  Service bundles + launchers ready" -ForegroundColor Green
}

if ($DevKit) {
    Write-Step "Package developer kit zip"
    & $Python scripts/package_processor_devkit.py
}

Write-Step "Start NOVA runtime (70 careers + robotics)"
if (Test-NovaRuntimeAlive) {
    Write-Host "  NOVA already alive (fresh state file)" -ForegroundColor DarkGray
} else {
    Start-MesieBackground "NOVA Runtime" @("scripts/run_nova_runtime.py") "run_nova_runtime" "nova-runtime"
    $novaOk = Wait-ForHealth { (Test-NovaRuntimeAlive) -or (Test-ProcessRunning "run_nova_runtime") } "NOVA runtime" $NovaTimeoutSec
    if (-not $novaOk) { Write-Host "  NOVA still booting - check deliverables/deploy/logs/nova-runtime.err.log" -ForegroundColor Yellow }
}

Write-Step "Start Virtual Processor HTTP :$ProcessorPort"
if (Test-HttpOk $ProcessorUrl 2) {
    Write-Host "  Processor already responding" -ForegroundColor DarkGray
} else {
    Start-MesieBackground "Virtual Processor" @("-m", "mesie.processor", "--serve", "--host", $BindHost, "--port", "$ProcessorPort") "mesie.processor" "virtual-processor"
    $procOk = Wait-ForHealth { Test-HttpOk $ProcessorUrl 8 } "processor/status" $ProcessorTimeoutSec
    if (-not $procOk) { Write-Host "  Processor still starting - check deliverables/deploy/logs/virtual-processor.err.log" -ForegroundColor Yellow }
}

if ($Mesh) {
    Write-Step "Start VP-MESH supervisor (virtual processor network)"
    if (-not (Test-ProcessRunning "run_vp_mesh")) {
        Start-MesieBackground "VP-MESH" @("scripts/run_vp_mesh.py", "--supervise") "run_vp_mesh" "vp-mesh"
        Start-Sleep -Seconds 3
    } else {
        Write-Host "  VP-MESH already running" -ForegroundColor DarkGray
    }
    $meshOk = Test-HttpOk "http://${BindHost}:${ProcessorPort}/processor/mesh" 8
    Write-Host "  mesh API: $(if ($meshOk) { 'OK' } else { 'starting' })" -ForegroundColor $(if ($meshOk) { 'Green' } else { 'Yellow' })
}

if ($Surface) {
    Write-Step "Start Medina Surface :8760"
    $surfaceUrl = "http://${BindHost}:8760/surface/status"
    if (-not (Test-HttpOk $surfaceUrl 2)) {
        Start-MesieBackground "Medina Surface" @("scripts/medina_surface.py", "--serve") "medina_surface" "medina-surface"
        Wait-ForHealth { Test-HttpOk $surfaceUrl 8 } "surface/status" $ProcessorTimeoutSec | Out-Null
    } else {
        Write-Host "  Surface already responding" -ForegroundColor DarkGray
    }
}

Write-Step "Health verification"
$checks = [ordered]@{
    processor_status = Test-HttpOk $ProcessorUrl
    nova_runtime_api = Test-HttpOk $NovaRuntimeUrl
    architecture     = Test-HttpOk "http://${BindHost}:${ProcessorPort}/processor/architecture"
    market_research  = Test-HttpOk "http://${BindHost}:${ProcessorPort}/processor/market-research"
    nova_state_file  = Test-NovaRuntimeAlive
}

$checks["nova_process"] = Test-ProcessRunning "run_nova_runtime"
$checks["processor_process"] = Test-ProcessRunning "mesie.processor"
if ($Mesh) {
    $checks["mesh_api"] = Test-HttpOk "http://${BindHost}:${ProcessorPort}/processor/mesh" 8
    $checks["mesh_process"] = Test-ProcessRunning "run_vp_mesh"
}

$allOk = $true
$critical = @("processor_status", "nova_process")
foreach ($k in $checks.Keys) {
    $ok = $checks[$k]
    $color = if ($ok) { "Green" } else { "Yellow" }
    Write-Host ("  {0,-20} {1}" -f $k, $(if ($ok) { "OK" } else { "FAIL" })) -ForegroundColor $color
    if ($critical -contains $k -and -not $ok) { $allOk = $false }
}

if ($ICP) {
    Write-Step "Deploy sovereign cloud to ICP ($IcpNetwork)"
    $icpScript = Join-Path $Root "Deploy-SovereignCloud-ICP.ps1"
    if (Test-Path $icpScript) {
        & $icpScript -Network $IcpNetwork -IcpOnly -BindHost $BindHost -ProcessorPort $ProcessorPort
        $checks["icp_manifest"] = Test-Path (Join-Path $Root "deliverables\icp\SOVEREIGN_CLOUD_PLATFORM_MANIFEST.json")
    } else {
        Write-Host "  Deploy-SovereignCloud-ICP.ps1 not found" -ForegroundColor Yellow
    }
}

Write-Step "Deploy summary"
Write-Host "  NOVA feed:    deliverables/nova/NOVA_RUNTIME_FEED.jsonl"
Write-Host "  NOVA state:   deliverables/nova/NOVA_RUNTIME_STATE.json"
Write-Host "  Robotics log: deliverables/processor/robotics_satellite.jsonl"
Write-Host "  Devkit zip:   deliverables/processor/VIRTUAL_PROCESSOR_DEVKIT.zip"
Write-Host "  Official:     deliverables/processor/official/"
Write-Host "  Official zip: deliverables/processor/VIRTUAL_PROCESSOR_OFFICIAL_BUNDLE.zip"
Write-Host "  ICP manifest: deliverables/icp/SOVEREIGN_CLOUD_PLATFORM_MANIFEST.json"
Write-Host "  ICP project:  icp/sovereign-cloud/"
Write-Host ""
Write-Host "  API examples:"
Write-Host "    GET  $ProcessorUrl"
Write-Host "    GET  $NovaRuntimeUrl"
Write-Host "    POST http://${BindHost}:${ProcessorPort}/processor/read-signal"
Write-Host "    POST http://${BindHost}:${ProcessorPort}/processor/generate-text"
Write-Host ""
Write-Host "  Foreground (optional - same stack, visible windows):"
Write-Host "    .\Start-NovaRuntime.ps1"
Write-Host "    .\Start-VirtualProcessor.ps1"
Write-Host ""

if ($allOk) {
    Write-Host "DEPLOY OK - sovereign stack is running." -ForegroundColor Green
    exit 0
}

Write-Host "DEPLOY PARTIAL - some checks failed; re-run or use -VerifyOnly" -ForegroundColor Yellow
exit 1