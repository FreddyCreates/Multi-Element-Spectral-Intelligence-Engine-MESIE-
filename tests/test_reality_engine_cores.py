"""Reality Engine Cores — 10 cores × 20 languages × 40+ protocols."""

from __future__ import annotations

from mesie.design.languages import CANONICAL_LANGUAGES, CANONICAL_PROTOCOL_COUNT
from mesie.design.reality_engine import RealityEngine
from mesie.design.reality_stack import FRONT_LAYER, MIDDLE_LAYER, BACK_LAYER
from mesie.design.registry import DESIGN_CORES, paradigm_count
from mesie.design.protocols import DESIGN_PROTOCOLS


def test_two_hundred_paradigms():
    assert len(DESIGN_CORES) == 10
    assert paradigm_count() == 200
    for core in DESIGN_CORES:
        assert len(core.paradigms) == 20


def test_forty_canonical_protocols():
    assert CANONICAL_PROTOCOL_COUNT == 40
    assert len(DESIGN_PROTOCOLS) >= 40


def test_twenty_languages_catalog():
    assert len(CANONICAL_LANGUAGES) == 20


def test_reality_stack_layers():
    assert FRONT_LAYER.layer_id == "front"
    assert MIDDLE_LAYER.layer_id == "middle"
    assert BACK_LAYER.layer_id == "back"


def test_reality_engine_status():
    st = RealityEngine().status()
    assert st["paradigm_count"] == 200
    assert st["paradigms_per_core"] == 20
    assert "stack" in st


def test_reality_engine_invoke_geometrica():
    from mesie.design.envelope import RealityEngineEnvelope

    env = RealityEngineEnvelope(
        agent_id="pytest-reality",
        core_id="core_geometrica",
        brief={"scene": "test"},
        paradigm_id="threejs_webgl",
    )
    out = RealityEngine().invoke(env)
    assert out["ok"]
    assert out["core_id"] == "core_geometrica"
    assert out["reality_class"] == "unreal_class_web"
