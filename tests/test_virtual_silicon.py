"""Virtual silicon — RF HIL, OTA mesh, certification."""

from __future__ import annotations

from mesie.field_io.rf_adapter import LiveRFAdapter, RFAdapterConfig, RFSourceMode
from mesie.silicon.ota_mesh import run_ota_mesh_round
from mesie.silicon.rf_frontend import VirtualRFFrontEnd
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


def test_rf_adapter_virtual_silicon_mode():
    rf = LiveRFAdapter(RFAdapterConfig(mode=RFSourceMode.VIRTUAL_SILICON))
    rep = rf.ingest_virtual_silicon()
    assert rep.ok
    assert rep.silicon_certified
    assert rep.mode == "virtual_silicon"