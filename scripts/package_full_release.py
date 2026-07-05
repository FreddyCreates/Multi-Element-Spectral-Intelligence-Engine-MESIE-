#!/usr/bin/env python3
"""Package FULL MESIE release — docs, demos, compute, sovereign cloud, research."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "release" / "MESIE_FULL_RELEASE.zip"

SKIP_SUFFIXES = {".pyc", ".zip"}
SKIP_PARTS = {"__pycache__", "node_modules", ".dfx", "target", ".git"}
MAX_FILE_BYTES = 50 * 1024 * 1024  # skip nested archives / huge artifacts

INCLUDE = [
    "mesie/compute",
    "mesie/cloud",
    "mesie/sovereign_os",
    "mesie/research",
    "mesie/domains/acoustic_metamaterial.py",
    "icp/sovereign-cloud",
    "mcp-colonies",
    "sovereign-os",
    "demos",
    "deliverables/release/MASTER_RELEASE.md",
    "deliverables/release/VIDEO_SCRIPT.md",
    "deliverables/release/DEMO_GUIDE.md",
    "deliverables/compute",
    "deliverables/cloudcolony/TRIPLE_PROTOCOL_MANIFEST.json",
    "deliverables/icp/docs",
    "deliverables/research",
    "deliverables/processor/official",
    "docs/papers",
    "scripts/package_full_release.py",
    "scripts/run_official_commercial_pack.py",
    "scripts/sync_icp_bridge.py",
    "scripts/export_cloudcolony_repo.py",
    "Deploy-FullRelease.ps1",
    "Deploy-MESIE.ps1",
    "Deploy-SovereignCloud-ICP.ps1",
    "Deploy-Capsula.ps1",
    "Start-MESIECompute.ps1",
    "Start-SovereignColony.ps1",
    "Start-SovereignOS.ps1",
    "Start-VirtualProcessor.ps1",
    "CHANGELOG.md",
]


def _skip_file(path: Path) -> bool:
    if path.resolve() == OUT.resolve():
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    if any(part in SKIP_PARTS for part in path.parts):
        return True
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return True
    except OSError:
        return True
    return False


def _add(zf: zipfile.ZipFile, rel: str, count: list) -> None:
    p = ROOT / rel
    if p.is_file():
        if not _skip_file(p):
            zf.write(p, rel.replace("\\", "/"))
            count[0] += 1
        return
    if not p.is_dir():
        return
    for f in p.rglob("*"):
        if f.is_file() and not _skip_file(f):
            zf.write(f, f.relative_to(ROOT).as_posix())
            count[0] += 1


def main() -> int:
    # Generate artifacts
    from mesie.research.acoustic_metamaterial_agent import run_research_agent
    from mesie.cloud.triple_protocol import write_triple_manifest
    from mesie.compute.hub import MESIEComputeHub

    run_research_agent()
    write_triple_manifest()
    try:
        MESIEComputeHub().full_benchmark(trials=10)
    except Exception:
        pass

    OUT.parent.mkdir(parents=True, exist_ok=True)
    count = [0]
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in INCLUDE:
            _add(zf, rel, count)
        zf.writestr(
            "RELEASE_README.txt",
            "MESIE FULL RELEASE — CloudColony.io × @ItsnotAILabs\n"
            "Beta: July 30, 2026\n"
            "Start: .\\Deploy-FullRelease.ps1\n"
            "Docs: deliverables/release/MASTER_RELEASE.md\n"
            "Demo: demos/index.html\n"
            "Video script: deliverables/release/VIDEO_SCRIPT.md\n",
        )

    manifest = {
        "product": "MESIE Full Release",
        "version": "1.0.0",
        "beta_launch": "2026-07-30",
        "zip": str(OUT),
        "files": count[0],
        "components": [
            "MESIE COMPUTE + ST-φ",
            "Sovereign Cloud ICP",
            "Triple Protocol",
            "Acoustic Metamaterial Research",
            "Commercial Official Pack",
            "Demos + Video Script",
        ],
    }
    manifest_path = ROOT / "deliverables" / "release" / "RELEASE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())