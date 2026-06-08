"""MAESI SDK v1.4 swarm integration."""

from __future__ import annotations

from data import load_reference_record
from mesie.sdk import MAESIClient, SwarmSDK, __sdk_version__


def test_sdk_version():
    assert __sdk_version__ == "1.4.0"


def test_maesi_swarm_property():
    client = MAESIClient()
    assert client.swarm is not None
    st = client.swarm.status()
    assert st.corpus_size >= 12
    assert st.routing_ok


def test_maesi_swarm_mission():
    client = MAESIClient()
    q = load_reference_record("defense_ew_spectrum_reference")
    rep = client.swarm_mission(q, preset_id="ew", n_agents=100, jam_ground=True)
    assert rep.ok