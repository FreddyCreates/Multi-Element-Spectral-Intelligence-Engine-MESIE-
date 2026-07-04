"""Virtual silicon — RF HIL, OTA mesh, certification."""

from __future__ import annotations

from mesie.field_io.rf_adapter import LiveRFAdapter, RFAdapterConfig, RFSourceMode
from mesie.silicon.ota_mesh import run_ota_mesh_round
from mesie.silicon.rf_frontend import VirtualRFFrontEnd
from mesie.silicon.vs1_spec import BASELINE_CHIP_ID, baseline_sovereign_profile, virtual_silicon_catalog
from mesie.silicon.virtual_chip import VirtualSiliconChip


def test_rf_hil_certified():
    hil = VirtualRFFrontEnd().run_hil_loop()
    assert hil.certified
    assert hil.virtual_silicon
    assert hil.field_coherence > 0.3


def test_ota_mesh_multicast():
    rep = run_ota_mesh_round(n_nodes=4, rounds=2)
    assert rep.over_the_air
    assert rep.ok
    assert rep.frames_received >= 4


def test_virtual_silicon_chip_certify():
    chip = VirtualSiliconChip()
    cert = chip.certify()
    assert cert.certified
    assert cert.rf_hil.certified
    assert cert.ota_mesh.ok


def test_vs1_baseline_sovereign_profile():
    profile = baseline_sovereign_profile()
    assert profile["chip_id"] == BASELINE_CHIP_ID
    assert profile["baseline_sovereign"] is True
    assert len(profile["components"]) == 3
    assert profile["brand"] == "ItsnotAILabs"


def test_virtual_silicon_catalog():
    cat = virtual_silicon_catalog()
    assert cat["baseline"]["chip_id"] == "MESIE-VS1"
    assert len(cat["sku_family"]) >= 3
    assert any(s["chip_id"] == "MESIE-VS1" for s in cat["skus"])
    vs1 = next(s for s in cat["skus"] if s["chip_id"] == "MESIE-VS1")
    assert vs1["baseline_sovereign"] is True
    assert vs1["sku_family_rank"] == 1


def test_vs1_cert_includes_architectural_meta():
    chip = VirtualSiliconChip.from_sku("MESIE-VS1")
    payload = chip.certify().to_dict(sku_meta=chip._sku_cert_meta())
    assert payload["baseline_sovereign"] is True
    assert "architectural_role" in payload
    assert "component_interpretations" in payload
    assert len(payload["sovereign_use_cases"]) >= 3


def test_rf_adapter_virtual_silicon_mode():
    rf = LiveRFAdapter(RFAdapterConfig(mode=RFSourceMode.VIRTUAL_SILICON))
    rep = rf.ingest_virtual_silicon()
    assert rep.ok
    assert rep.silicon_certified
    assert rep.mode == "virtual_silicon"