"""Design Reality Ecosystem smoke tests."""

from __future__ import annotations

from mesie.design.registry import DESIGN_CORES, design_ecosystem_manifest, paradigm_count
from mesie.design.protocols import DESIGN_PROTOCOLS
from mesie.design.orchestrator import orchestrate_design_brief
from mesie.design.core_engine import invoke_paradigm_agent


def test_ten_cores_two_hundred_paradigms():
    assert len(DESIGN_CORES) == 10
    assert paradigm_count() == 200


def test_forty_two_protocols():
    assert len(DESIGN_PROTOCOLS) >= 40


def test_orchestrate_realitas():
    r = orchestrate_design_brief("core_realitas", {"showcase": "test"})
    assert r["ok"] is True
    assert r["orchestration"]["agents_invoked"] == 20


def test_invoke_threejs_agent():
    r = invoke_paradigm_agent("core_geometrica", "threejs_webgl", {"brief": {}})
    assert r["ok"] is True
    assert "Agent Geometria Triangula" in str(r)


def test_manifest():
    m = design_ecosystem_manifest()
    assert m["paradigm_count"] == 200
    assert m["protocol_bus"]["protocol_count"] >= 40