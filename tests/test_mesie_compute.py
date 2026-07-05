"""Tests for MESIE COMPUTE — ST-φ, φ-Kernel, hub, tri-agent squads."""

from __future__ import annotations

import numpy as np

from mesie.compute.hub import MESIEComputeHub
from mesie.compute.phi_kernel import PhiKernel
from mesie.compute.spectral_transformer import SpectralTransformerPhi, STPhiConfig, list_st_phi_models
from mesie.compute.tri_agent_squads import SQUADS, list_squads
from mesie.compute.virtual_products import _base_catalog, load_products, save_products


def test_st_phi_encode():
    st = SpectralTransformerPhi(STPhiConfig(d_model=128, n_heads=4, n_layers=2))
    vec = st.encode({"research": "spectral", "phi": 0.618})
    assert vec.shape == (128,)
    bench = st.benchmark(trials=20)
    assert bench.encode_p50_ms >= 0
    assert bench.encode_p50_ms < 50  # fast edge target


def test_st_phi_models():
    models = list_st_phi_models()
    assert len(models) >= 3


def test_phi_kernel_compress():
    k = PhiKernel()
    vec = np.random.randn(256)
    rec = k.compress_embedding(vec)
    assert rec.compressed_bytes < rec.raw_bytes
    idx = k.export_index()
    assert idx["slice_count"] >= 1


def test_virtual_products_catalog():
    products = _base_catalog()
    assert any(p.sku == "MESIE-COMPUTE-EDGE" for p in products)
    assert any(p.sku.startswith("ST-φ") for p in products)


def test_tri_agent_squads_structure():
    squads = list_squads()
    assert len(squads) >= 3
    for s in squads:
        assert len(s["agents"]) == 3


def test_compute_hub_encode():
    hub = MESIEComputeHub(model_id="ST-φ-128")
    r = hub.encode("enterprise spectral benchmark")
    assert r["ok"] is True
    assert r["dims"] == 128
    assert r["native"] is True


def test_save_load_products(tmp_path, monkeypatch):
    import mesie.compute.virtual_products as vp

    path = tmp_path / "products.json"
    monkeypatch.setattr(vp, "PRODUCTS_STATE", path)
    save_products(_base_catalog())
    loaded = load_products()
    assert len(loaded) >= 8