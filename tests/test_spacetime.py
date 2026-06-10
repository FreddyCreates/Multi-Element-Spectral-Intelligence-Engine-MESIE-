"""Tests for Paper 04 simulated spacetime architecture."""

import pytest

from mesie.spacetime import (
    PAPER04_AUTHORITY,
    PAPER04_CLAIM_BOUNDARY,
    SimulatedSpacetimeSubstrate,
    classify_signal,
    default_agent_registry,
    default_zones,
    run_spacetime_eval,
)
from mesie.spacetime.signals import SignalTier


class TestSignalClassification:
    def test_cooperative(self):
        s = classify_signal(signal_id="a", source_agent="r", payload_kind="x", trust_score=0.9)
        assert s.tier == SignalTier.COOPERATIVE

    def test_hostile(self):
        s = classify_signal(signal_id="b", source_agent="t", payload_kind="x", trust_score=0.1, adversary_flag=True)
        assert s.tier == SignalTier.HOSTILE

    def test_shadow(self):
        s = classify_signal(signal_id="c", source_agent="h", payload_kind="x", trust_score=0.4, unknown_origin=True)
        assert s.tier == SignalTier.SHADOW


class TestSubstrate:
    def test_default_registry(self):
        assert len(default_agent_registry()) >= 5
        assert len(default_zones()) >= 4

    def test_simulation_runs(self):
        sub = SimulatedSpacetimeSubstrate()
        report = sub.run(ticks=10)
        assert report.ticks_run == 10
        assert report.routes_total > 0

    def test_authority_constants(self):
        assert PAPER04_AUTHORITY == "INTERNAL_RESEARCH"
        assert PAPER04_CLAIM_BOUNDARY == "repo_verified_architecture"


class TestSpacetimeEval:
    def test_eval_green(self):
        result = run_spacetime_eval(ticks=12)
        assert result["ready"] is True
        assert result["passed"] == result["total"]


class TestWorldIntegration:
    def test_theater_bridge_wired(self):
        from mesie.worlds.week_engine import MissionWorldWeekEngine

        _, report = MissionWorldWeekEngine().run_week(days=1)
        assert "Spacetime routes" in " ".join(report.findings)
        assert report.spacetime_summary["routes_total"] > 0