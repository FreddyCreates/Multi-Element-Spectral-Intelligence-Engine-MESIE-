"""Platform services — catalog, bridge, worker gateway."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_unified_model_catalog():
    from mesie.platform.model_catalog import build_unified_model_catalog

    cat = build_unified_model_catalog()
    assert cat["protocol"] == "MESIE-UNIFIED-MODEL-CATALOG/1.0"
    assert cat["third_party_inference"] is False
    assert cat["model_count"] >= 10
    ids = {t["model_id"] for t in cat["tiers"]}
    assert "NOVA-50B-VIRTUAL" in ids
    assert "solus-reasoning-model" in ids
    assert "AuroNativeLM-v1" in ids


def test_platform_registry():
    from mesie.platform.registry import PLATFORM_SERVICES, platform_manifest, service_by_id

    assert len(PLATFORM_SERVICES) >= 12
    svc = service_by_id("model-hub")
    assert svc is not None
    assert svc.worker_action == "platform_models"
    manifest = platform_manifest()
    assert manifest["service_count"] == len(PLATFORM_SERVICES)
    assert "platform_hub" in manifest["surfaces"]


def test_mvp_bridge_envelope():
    from mesie.platform.mvp_bridge import bridge_envelope, bridge_manifest

    env = bridge_envelope("solus-console", payload={"record_id": "test"})
    assert env["ok"] is True
    assert env["envelope"]["service_id"] == "solus-console"
    assert env["envelope"]["protocol_binding"]["protocol_id"] == "P35"
    assert env["envelope"]["third_party_inference"] is False

    bridge = bridge_manifest()
    assert bridge["protocol"] == "MESIE-MVP-PROTOCOL-BRIDGE/1.0"
    assert len(bridge["bindings"]) >= 12


def test_worker_gateway_solus():
    from mesie.platform.worker_gateway import PlatformWorkerGateway

    gw = PlatformWorkerGateway(mission_id="pytest")
    out = gw.invoke("solus-console", payload={
        "frequencies": [1.0, 2.0, 3.0],
        "amplitudes": [0.5, 0.7, 0.9],
        "cycle_context": {"record_id": "pytest_cycle"},
    })
    assert out["ok"] is True
    solus = out["result"]["solus"]
    assert "conclusion" in solus
    assert solus["third_party"] is False


def test_worker_gateway_unknown():
    from mesie.platform.worker_gateway import PlatformWorkerGateway

    out = PlatformWorkerGateway().invoke("nonexistent-service")
    assert out["ok"] is False


def test_forge_script_writes_manifest():
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "scripts/forge_model_platforms.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert r.returncode == 0
    manifest = ROOT / "deliverables" / "platform" / "PLATFORM_MANIFEST.json"
    assert manifest.is_file()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["catalog"]["model_count"] >= 10
    assert data["platform"]["service_count"] >= 12