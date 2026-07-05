"""Forge HERMES fleet — wrangler.toml, ICP CLI, JSON packages, SDK bundles."""

from __future__ import annotations

import json
import shutil
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.hermes.nova_protocol import build_nova_protocol_hermes
from mesie.hermes.registry import HERMES_WORKERS, hermes_manifest
from mesie.hermes.worker_templates import root_wrangler_toml, worker_js, wrangler_worker_toml
from mesie.version_info import HERMES_VERSION, MESIE_VERSION

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deliverables" / "hermes"
WORKERS_DIR = OUT / "workers"
PACKAGES_DIR = OUT / "packages"
ICP_DIR = OUT / "icp"
SDK_DIR = OUT / "sdk"


def _icp_cli_manifest() -> Dict[str, Any]:
    icp_root = ROOT / "icp" / "sovereign-cloud"
    return {
        "protocol": "HERMES-ICP-CLI/1.0",
        "hermes_version": HERMES_VERSION,
        "dfx_version": "0.15+",
        "networks": ["local", "ic"],
        "commands": [
            {"cmd": "dfx start --background", "role": "local replica"},
            {"cmd": "dfx deploy sovereign_registry", "role": "registry canister"},
            {"cmd": "dfx deploy sovereign_colony", "role": "colony + HERMES anchor"},
            {"cmd": "python -m mesie.cloud.icp_bridge --sync", "role": "edge → ICP proof sync"},
        ],
        "canister_map_path": str(icp_root / "canister_ids.json"),
        "hermes_embed": True,
        "nova_protocol": "NOVA-PROTOCOL-CLEAN-INTERNET/1.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _deploy_scripts() -> None:
    ps1 = OUT / "deploy.ps1"
    sh = OUT / "deploy.sh"
    ps1.write_text(
        """# HERMES one-shot deploy — ItsnotAILabs / NOVA PROTOCOL
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "HERMES Fleet deploy" -ForegroundColor Cyan
python "$Root/../../scripts/forge_hermes_fleet.py"

if (Get-Command wrangler -ErrorAction SilentlyContinue) {
  Get-ChildItem "$Root/workers" -Directory | ForEach-Object {
    Write-Host "Deploy $($_.Name)..." -ForegroundColor Green
    Push-Location $_.FullName
    wrangler deploy 2>&1 | Out-Host
    Pop-Location
  }
} else {
  Write-Host "wrangler not found — pack ready at deliverables/hermes/" -ForegroundColor Yellow
}
""",
        encoding="utf-8",
    )
    sh.write_text(
        """#!/usr/bin/env bash
# HERMES one-shot deploy — ItsnotAILabs / NOVA PROTOCOL
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo "HERMES Fleet deploy"
python "$ROOT/../../scripts/forge_hermes_fleet.py"
if command -v wrangler >/dev/null 2>&1; then
  for d in "$ROOT/workers"/*/; do
    echo "Deploy $(basename "$d")..."
    (cd "$d" && wrangler deploy)
  done
else
  echo "wrangler not found — pack ready at deliverables/hermes/"
fi
""",
        encoding="utf-8",
    )


def _sdk_manifest() -> Dict[str, Any]:
    return {
        "protocol": "HERMES-SDK-PACK/1.0",
        "brand": "ItsnotAILabs",
        "packages": [
            {"name": "@itsnotailabs/hermes-ingest", "entry": "ingest_client.ts"},
            {"name": "@itsnotailabs/hermes-embed", "entry": "embed_client.ts"},
            {"name": "@itsnotailabs/hermes-clean", "entry": "clean_feed.ts"},
            {"name": "@mesie/maesi-sdk", "entry": "mesie/sdk/__init__.py"},
        ],
        "targets": ["cloudflare-worker", "icp-canister", "python-edge", "typescript"],
        "one_shot": "hermes-deploy-shot",
        "mesie_version": MESIE_VERSION,
        "hermes_version": HERMES_VERSION,
    }


def _worker_package(w: Any) -> Dict[str, Any]:
    return {
        "protocol": "HERMES-WORKER-PACKAGE/1.0",
        "worker_id": w.worker_id,
        "slot": w.slot,
        "title": w.title,
        "route": w.route,
        "operations": list(w.operations),
        "generates": list(w.generates),
        "ai_ingest": w.category in ("ingestion", "large_data", "embedding", "clean_internet"),
        "embedding_depth": w.category in ("embedding", "retrieval", "large_data"),
        "deploy_artifacts": list(w.generates),
        "processor_proxy": w.processor_proxy,
        "third_party_inference": False,
    }


def forge_hermes_fleet(*, zip_sdk: bool = True) -> Dict[str, Any]:
    """Generate all HERMES artifacts — ready to run / one-shot deploy."""
    if OUT.exists():
        shutil.rmtree(OUT, ignore_errors=True)
    WORKERS_DIR.mkdir(parents=True, exist_ok=True)
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    ICP_DIR.mkdir(parents=True, exist_ok=True)
    SDK_DIR.mkdir(parents=True, exist_ok=True)

    forged_workers: List[str] = []
    for w in HERMES_WORKERS:
        wdir = WORKERS_DIR / w.worker_id
        wdir.mkdir(parents=True, exist_ok=True)
        (wdir / "index.js").write_text(worker_js(w), encoding="utf-8")
        (wdir / "wrangler.toml").write_text(wrangler_worker_toml(w), encoding="utf-8")
        pkg = _worker_package(w)
        (PACKAGES_DIR / f"{w.worker_id}.json").write_text(
            json.dumps(pkg, indent=2) + "\n", encoding="utf-8"
        )
        forged_workers.append(w.worker_id)

    (OUT / "wrangler.toml").write_text(root_wrangler_toml(HERMES_WORKERS), encoding="utf-8")
    (ICP_DIR / "HERMES_ICP_CLI.json").write_text(
        json.dumps(_icp_cli_manifest(), indent=2) + "\n", encoding="utf-8"
    )
    (ICP_DIR / "deploy_icp.sh").write_text(
        "#!/usr/bin/env bash\ncd \"$(dirname \"$0\")/../../icp/sovereign-cloud\" && dfx deploy\n",
        encoding="utf-8",
    )
    sdk = _sdk_manifest()
    (SDK_DIR / "HERMES_SDK_MANIFEST.json").write_text(json.dumps(sdk, indent=2) + "\n", encoding="utf-8")
    for name in ("ingest_client.ts", "embed_client.ts", "clean_feed.ts"):
        (SDK_DIR / name).write_text(_ts_stub(name), encoding="utf-8")

    nova = build_nova_protocol_hermes()
    (OUT / "NOVA_PROTOCOL_HERMES.json").write_text(json.dumps(nova, indent=2) + "\n", encoding="utf-8")

    manifest = hermes_manifest()
    manifest["forged_workers"] = forged_workers
    manifest["artifacts"] = {
        "wrangler_root": str(OUT / "wrangler.toml"),
        "workers_dir": str(WORKERS_DIR),
        "icp_cli": str(ICP_DIR / "HERMES_ICP_CLI.json"),
        "sdk": str(SDK_DIR / "HERMES_SDK_MANIFEST.json"),
        "nova_protocol": str(OUT / "NOVA_PROTOCOL_HERMES.json"),
    }
    (OUT / "HERMES_FLEET_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    deploy_shot = {
        "protocol": "HERMES-DEPLOY-SHOT/1.0",
        "ready": True,
        "steps": ["forge", "wrangler_deploy", "icp_anchor", "sdk_publish"],
        "scripts": {
            "powershell": str(OUT / "deploy.ps1"),
            "bash": str(OUT / "deploy.sh"),
            "icp": str(ICP_DIR / "deploy_icp.sh"),
        },
        "worker_count": len(HERMES_WORKERS),
    }
    (OUT / "DEPLOY_SHOT.json").write_text(json.dumps(deploy_shot, indent=2) + "\n", encoding="utf-8")
    _deploy_scripts()

    zip_path = OUT / "hermes-sdk.zip"
    if zip_sdk:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in SDK_DIR.iterdir():
                if f.is_file():
                    zf.write(f, f"sdk/{f.name}")
            for f in PACKAGES_DIR.glob("*.json"):
                zf.write(f, f"packages/{f.name}")

    return {
        "ok": True,
        "worker_count": len(forged_workers),
        "out": str(OUT),
        "manifest": str(OUT / "HERMES_FLEET_MANIFEST.json"),
        "deploy_shot": str(OUT / "DEPLOY_SHOT.json"),
        "sdk_zip": str(zip_path) if zip_sdk else None,
    }


def _ts_stub(name: str) -> str:
    if "ingest" in name:
        return """/** @itsnotailabs/hermes-ingest — NOVA PROTOCOL clean ingest */
export async function hermesIngest(record: object, base = "https://hermes-ingest.workers.dev") {
  const r = await fetch(`${base}/hermes/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ record, provenance_hash: crypto.randomUUID() }),
  });
  return r.json();
}
"""
    if "embed" in name:
        return """/** @itsnotailabs/hermes-embed — ST-φ edge embed client */
export async function hermesEmbed(text: string, model = "ST-φ-256", base = "https://hermes-embed.workers.dev") {
  const r = await fetch(`${base}/hermes/embed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ payload: text, model }),
  });
  return r.json();
}
"""
    return """/** @itsnotailabs/hermes-clean — NOVA clean internet feed filter */
export function cleanFeedRules() {
  return {
    block_unverified_claims: true,
    require_provenance_hash: true,
    spectral_validate: true,
    third_party_inference: false,
  };
}
"""