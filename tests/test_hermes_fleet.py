"""HERMES fleet — 12 workers, forge, NOVA protocol, 20 extended alphas."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_hermes_registry():
    from mesie.hermes.registry import HERMES_WORKERS, hermes_manifest

    assert len(HERMES_WORKERS) == 12
    manifest = hermes_manifest()
    assert manifest["protocol"] == "HERMES-FLEET/1.0"
    assert manifest["brand"] == "ItsnotAILabs"
    assert manifest["icp_embedded"] is True
    ids = {w.worker_id for w in HERMES_WORKERS}
    assert "hermes-deploy-shot" in ids
    assert "hermes-clean-feed" in ids


def test_nova_protocol():
    from mesie.hermes.nova_protocol import build_nova_protocol_hermes

    nova = build_nova_protocol_hermes()
    assert nova["protocol"] == "NOVA-PROTOCOL-CLEAN-INTERNET/1.0"
    assert nova["clean_feed_doctrine"]["third_party_inference"] is False
    assert len(nova["icp_cloud_embedding"]["hermes_routes"]) == 12


def test_forge_hermes_fleet():
    from mesie.hermes.forge import forge_hermes_fleet

    result = forge_hermes_fleet()
    assert result["ok"] is True
    assert result["worker_count"] == 12
    out = ROOT / "deliverables" / "hermes"
    assert (out / "HERMES_FLEET_MANIFEST.json").is_file()
    assert (out / "wrangler.toml").is_file()
    assert (out / "NOVA_PROTOCOL_HERMES.json").is_file()
    assert (out / "DEPLOY_SHOT.json").is_file()
    assert (out / "workers" / "hermes-embed" / "index.js").is_file()
    assert (out / "icp" / "HERMES_ICP_CLI.json").is_file()
    assert (out / "sdk" / "HERMES_SDK_MANIFEST.json").is_file()


def test_hermes_executor():
    from mesie.hermes.executor import HermesExecutor

    forge_hermes_fleet = __import__("mesie.hermes.forge", fromlist=["forge_hermes_fleet"]).forge_hermes_fleet
    forge_hermes_fleet(zip_sdk=False)

    ex = HermesExecutor()
    clean = ex.invoke("hermes-clean-feed")
    assert clean["ok"] is True
    assert "block_unverified_claims" in clean["result"]["clean_feed"]

    deploy = ex.invoke("hermes-deploy-shot", payload={"forge": False})
    assert deploy["ok"] is True


def test_extended_alpha_harnesses():
    from mesie.harness.alpha_registry import ALPHA_HARNESSES, harness_manifest

    assert len(ALPHA_HARNESSES) >= 31
    ids = {h.harness_id for h in ALPHA_HARNESSES}
    assert "hermes_fleet" in ids
    assert "nova_clean_internet" in ids
    assert "platform_hermes_mvp" in ids
    manifest = harness_manifest()
    assert manifest["harness_count"] >= 31


def test_forge_script():
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "scripts/forge_hermes_fleet.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["worker_count"] == 12
    assert data["alpha_harness_count"] >= 31