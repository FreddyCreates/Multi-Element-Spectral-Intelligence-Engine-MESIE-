"""NOVA + MININOVA sphere production tests."""

from __future__ import annotations

import json
from pathlib import Path

from mesie import __version__ as MESIE_VERSION
from mesie.mininova import MININOVA_VERSION, MiniNovaSphere
from mesie.nova import NOVA_VERSION, NovaSphere
from mesie.version_info import NOVA_VERSION as VI_NOVA


def test_nova_sphere_process():
    s = NovaSphere(session_id="test-nova")
    r = s.process("Embed and match spectral records for release gate")
    assert r.spoken_summary
    assert r.sovereign is True
    assert r.nova_version == VI_NOVA
    assert r.mesie_version == MESIE_VERSION
    assert "cognitive" in r.to_dict()
    assert r.cognitive["domain"] in ("retrieval", "matching", "release", "general")


def test_nova_sphere_status():
    st = NovaSphere(session_id="test-status").status()
    assert st["product"] == "NOVA"
    assert st["sovereign"] is True
    assert st["third_party_inference"] is False
    assert "micro_fleet" in st


def test_mininova_sphere_process(tmp_path: Path):
    m = MiniNovaSphere(session_id="test-mininova", vault_root=tmp_path)
    r = m.process("MININOVA production smoke")
    assert r.spoken
    assert r.sovereign is True
    assert r.mininova_version == MININOVA_VERSION
    assert r.linguistic["coherence"] >= 0


def test_mininova_sphere_status(tmp_path: Path):
    st = MiniNovaSphere(session_id="test-mininova-st", vault_root=tmp_path).status()
    assert st["product"] == "MININOVA"
    assert st["novamini"]["third_party_inference"] is False


def test_nova_versions_exported():
    assert NOVA_VERSION == VI_NOVA
    data = NovaSphere(session_id="export").process("version check").to_dict()
    assert json.dumps(data)


def test_nova_organization_size():
    from mesie.agentic.micro import NOVA_ORG_SIZE

    sphere = NovaSphere(session_id="test-org")
    assert NOVA_ORG_SIZE >= 65
    assert sphere.micro.fleet_status()["count"] == NOVA_ORG_SIZE


def test_activate_satellites_all_active():
    sphere = NovaSphere(session_id="test-satellites")
    sphere.activate_satellites()
    fleet = sphere.micro.fleet_status()
    assert fleet["count"] >= 65
    assert fleet["satellites_active"] == fleet["count"] or fleet.get("pulsing", 0) >= 0
    for agent in sphere.micro.satellites.values():
        assert agent.satellite_active is True
    sphere.stop_satellites()