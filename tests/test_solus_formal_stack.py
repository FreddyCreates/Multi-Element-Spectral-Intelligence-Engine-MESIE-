"""SOLUS formal stack — Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation."""

from data import list_references, load_reference_record
from mesie.sdk import FORMAL_COMPOSITION, SolusFormalStack, composition_manifest
from mesie.sdk.solus import SolusAdaptationModel, SolusEmergenceModel, SolusReasoningModel


def test_composition_manifest_own_models():
    m = composition_manifest()
    assert m["third_party"] is False
    assert m["sovereign"] is True
    assert m["formula"] == FORMAL_COMPOSITION
    layers = {x["layer"] for x in m["models"]}
    assert layers == {"logic", "reasoning", "emergence", "adaptation"}


def test_formal_stack_compose_cycle():
    ref = load_reference_record(list_references()[0])
    comp = ref.components[0]
    stack = SolusFormalStack()
    out = stack.compose_cycle(
        comp.frequency.tolist(),
        comp.amplitude.tolist(),
        cycle_context={"record_id": ref.record_id, "match_score": 0.8, "valid": True},
    )
    assert out["third_party"] is False
    assert out["own_models_only"] is True
    assert out["formula"] == FORMAL_COMPOSITION
    assert set(out["formal_models"].keys()) == {"logic", "reasoning", "emergence", "adaptation"}
    assert out["composition_hash"]
    assert out["conclusion"]


def test_reasoning_model_infer():
    model = SolusReasoningModel()
    r = model.run(
        logic_data={"average_confidence": 0.85, "complexity": {"normalized": 0.4}},
        signal_ratio=0.7,
        cycle_context={"match_score": 0.75, "valid": True, "anomaly": 1.0},
    )
    assert r.layer == "reasoning"
    assert r.third_party is False
    assert r.data["composite_score"] > 0


def test_emergence_model_resonate():
    model = SolusEmergenceModel()
    import numpy as np

    vals = np.sin(np.linspace(0, 6, 32)).tolist()
    r = model.run(vals)
    assert r.layer == "emergence"
    assert "emergence_score" in r.data


def test_adaptation_model_recalibrates():
    model = SolusAdaptationModel()
    for i in range(10):
        r = model.run({"match_score": 0.5 + i * 0.02}, composite_score=0.6 + i * 0.01)
    assert r.data["cycles_seen"] == 10
    assert "thresholds" in r.data