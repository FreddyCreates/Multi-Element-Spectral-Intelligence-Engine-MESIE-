"""Compute fabric — chip registry, ANN stats, fabric suite."""

from __future__ import annotations

from mesie.library.domain_corpus import load_domain_corpus
from mesie.sdk.fast_compute import FastSpectralCompute
from mesie.silicon.chip_registry import deploy_manifest, get_chip, list_chips
from mesie.silicon.virtual_chip import VirtualSiliconChip


def test_chip_registry_four_skus():
    skus = list_chips()
    assert len(skus) == 4
    ids = {s.chip_id for s in skus}
    assert "MESIE-VS1" in ids
    assert "MESIE-VS2-ANN" in ids
    assert "MESIE-VS3-EDGE" in ids
    assert "MESIE-VS4-ORBITAL" in ids


def test_deploy_manifest_structure():
    manifest = deploy_manifest()
    assert manifest["fabric_version"] == "1.2.0"
    assert len(manifest["skus"]) == 4
    assert "GET /processor/chips" in manifest["http_surface"]["chips"]


def test_fast_compute_ann_stats():
    fc = FastSpectralCompute()
    corpus = load_domain_corpus()
    fc.build_index(corpus[:8])
    stats = fc.benchmark_ann_p50(corpus[0], n_trials=20, top_k=3)
    assert stats.trials == 20
    assert stats.p50_ms >= 0
    assert stats.p95_ms >= stats.p50_ms
    assert stats.backend


def test_band_sign_lsh_candidates_subset():
    fc = FastSpectralCompute()
    corpus = load_domain_corpus()
    fc.build_index(corpus)
    q = fc.embed_one(corpus[0])
    pool = fc._candidate_indices(q)
    assert 0 < len(pool) <= len(corpus)


def test_virtual_chip_from_sku():
    vs2 = get_chip("MESIE-VS2-ANN")
    chip = VirtualSiliconChip.from_sku(vs2.chip_id)
    assert chip.spec.spectral_alu_width == 512
    cert = chip.certify()
    assert cert.benchmark_lane.ann_p95_ms >= cert.benchmark_lane.ann_p50_ms
    assert cert.benchmark_lane.ann_backend


def test_processor_list_chips():
    from mesie.processor.virtual_processor import VirtualProcessor

    proc = VirtualProcessor()
    result = proc.list_chips()
    assert result.ok
    assert len(result.output["skus"]) == 4


def test_processor_virtual_chip_sku():
    from mesie.processor.virtual_processor import VirtualProcessor

    proc = VirtualProcessor()
    result = proc.virtual_chip_certify(chip_id="MESIE-VS3-EDGE")
    assert result.ok
    assert result.output["chip_id"] == "MESIE-VS3-EDGE"
    assert result.output["spec"]["rf_frontends"] == 2


def test_virtual_chip_orbital_sku():
    chip = VirtualSiliconChip.from_sku("MESIE-VS4-ORBITAL")
    cert = chip.certify()
    assert cert.spec.ota_mac == "NSOT_multicast_orbital_v1"
    assert cert.ota_mesh.propagation_tier == "SHF/Satellite"
    assert cert.ota_mesh.nodes == 12
    assert cert.certified


def test_mcp_shim_exposes_chip_tools():
    from mesie.processor.mcp_server import TOOLS

    assert "processor_list_chips" in TOOLS
    assert "processor_virtual_chip" in TOOLS
    assert TOOLS["processor_list_chips"]["path"] == "/processor/chips"
    schema = TOOLS["processor_virtual_chip"]["inputSchema"]
    assert "MESIE-VS4-ORBITAL" in schema["properties"]["chip_id"]["enum"]
