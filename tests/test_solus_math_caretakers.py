"""Tests for SOLUS Logic Prover + Pattern Forge SDK caretakers."""

import numpy as np

from mesie.sdk import (
    MAESIClient,
    SDKSolusOrganism,
    SolusLogicProver,
    SolusPatternForge,
    SOLUS_BRAND,
    LOCAL_ENGINE,
    FORMAL_COMPOSITION,
    OWN_MODELS_ONLY,
)
from data import list_references, load_reference_record


def test_solus_brand_local():
    assert SOLUS_BRAND == "SOLUS"
    assert LOCAL_ENGINE == "solus-local"
    assert OWN_MODELS_ONLY is True
    assert "Logic" in FORMAL_COMPOSITION
    assert "Adaptation" in FORMAL_COMPOSITION


def test_logic_prover_prove():
    lp = SolusLogicProver()
    r = lp.caretaker_run("prove", theorem="sum of angles in triangle = 180")
    assert r.ok
    assert r.data["total_steps"] >= 3
    assert r.heart["sovereign"]
    assert r.brain["confidence"] > 0


def test_pattern_forge_xray():
    pf = SolusPatternForge()
    values = np.sin(np.linspace(0, 6, 24)).tolist()
    r = pf.caretaker_run("xray", values=values)
    assert r.ok
    assert r.data["n"] == 24
    assert "depths" in r.data


def test_organism_formal_models():
    org = SDKSolusOrganism()
    assert len(org.formal_model_ids) == 4
    assert len(org.caretaker_names) >= 4
    assert org.formula == FORMAL_COMPOSITION
    v = org.pulse()
    assert v.sovereign
    assert v.sdk_health in ("thriving", "stable", "watch")


def test_organism_tend_sdk():
    org = SDKSolusOrganism()
    out = org.tend_sdk({"technical_concepts": 20, "research_entries": 24, "speedup_ratio": 800})
    assert out["sovereign"]
    assert "logic_caretaker" in out
    assert "pattern_caretaker" in out


def test_maesi_client_organism_integration():
    refs = [load_reference_record(n) for n in list_references()[:3]]
    client = MAESIClient(fast=True, use_solus_caretakers=True)
    assert client.organism is not None
    report = client.run_full(refs, benchmark=True)
    assert report.solus_organism is not None
    assert report.solus_organism["brand"] == "SOLUS"