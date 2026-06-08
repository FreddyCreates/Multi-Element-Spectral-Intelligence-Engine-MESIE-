"""Scenario simulation — military + enterprise real data."""

from __future__ import annotations

from mesie.scenarios.catalog import enterprise_scenarios, military_scenarios
from mesie.scenarios.simulator import ScenarioSimulator


def test_military_catalog():
    assert len(military_scenarios()) >= 6


def test_enterprise_catalog():
    assert len(enterprise_scenarios()) >= 6


def test_military_ew_scenario():
    spec = next(s for s in military_scenarios() if s["id"] == "mil_ew_contested_jam")
    rep = ScenarioSimulator().run_military(spec)
    assert rep.data_sources
    assert "defense_ew_spectrum_reference" in rep.data_sources[0]


def test_enterprise_factory_scenario():
    spec = next(s for s in enterprise_scenarios() if s["id"] == "ent_factory_vibration")
    rep = ScenarioSimulator().run_enterprise(spec)
    assert rep.metrics.get("enterprise_fast_ms", 999) < 500