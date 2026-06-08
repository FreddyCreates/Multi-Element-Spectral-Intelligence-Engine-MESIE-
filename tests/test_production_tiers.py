"""Production tier 1 + tier 2 smoke tests."""

from __future__ import annotations

from mesie.evaluation.mlperf_submit import MLPerfSubmissionPack
from mesie.field_io.rf_adapter import LiveRFAdapter, RFAdapterConfig, RFSourceMode
from mesie.production.appliance import ProductionAppliance
from mesie.swarm.cluster_coordinator import ClusterSwarmOptimizer
from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator
from data import load_reference_record
from mesie.library.domain_corpus import load_domain_corpus


def test_mlperf_submission():
    p = MLPerfSubmissionPack().generate(n_trials=50)
    assert p["valid"]
    assert len(p["results"]) >= 6
    assert p["compliance"]["community_formal_pack"]
    assert p["credibility"]["virtual_silicon_backed"]


def test_rf_adapter_sim():
    rf = LiveRFAdapter(RFAdapterConfig(mode=RFSourceMode.SIM))
    rep = rf.ingest_simulated()
    assert rep.ok
    assert rep.field_coherence > 0


def test_cluster_optimizer_10k():
    corpus = load_domain_corpus()
    q = load_reference_record("defense_ew_spectrum_reference")
    coord = DecentralizedSwarmCoordinator(corpus)
    rep = ClusterSwarmOptimizer(coord).coordinate_optimized(q, n_agents=10000, jam_ground=True)
    assert rep.ok
    assert rep.ms_per_agent < 0.5


def test_tier1_health():
    h = ProductionAppliance().health()
    assert h.airgapped
    assert h.corpus_size >= 12


def test_tier1_narrative_export():
    path = ProductionAppliance().export_narrative()
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "MAESI_SDK_Major_Benchmarks" in text
    assert "Tier 1" in text