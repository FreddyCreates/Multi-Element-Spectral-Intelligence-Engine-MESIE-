#!/usr/bin/env python3
"""Validate trust/production_readiness bundle — paths, imports, quick pytest gate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "trust" / "production_readiness" / "MANIFEST.json"

TESTS = [
    "tests/test_deliverable_versioning.py",
    "tests/test_vp_mesh.py",
    "tests/test_universal_signals.py",
    "tests/test_virtual_processor.py",
    "tests/test_compute_fabric.py::test_chip_registry_four_skus",
    "tests/test_compute_fabric.py::test_mcp_shim_exposes_chip_and_signal_tools",
    "tests/test_compute_fabric.py::test_deploy_manifest_structure",
]


def main() -> int:
    if not MANIFEST.is_file():
        print("MANIFEST missing:", MANIFEST)
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    missing: list[str] = []
    for name, rel in manifest.get("components", {}).items():
        p = ROOT / rel
        if not p.exists():
            missing.append(f"{name}: {rel}")
    report = {
        "bundle": manifest.get("bundle"),
        "mesie_version": manifest.get("mesie_version"),
        "components_ok": len(manifest.get("components", {})) - len(missing),
        "missing": missing,
    }
    print(json.dumps(report, indent=2))
    if missing:
        return 1
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *TESTS, "-q", "--tb=line"],
        cwd=str(ROOT),
    )
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
