"""Mission world week simulation."""

from __future__ import annotations

from mesie.worlds.hierarchy import load_world
from mesie.worlds.week_engine import MissionWorldWeekEngine


def test_world_hierarchy():
    w = load_world()
    assert len(w.operations) == 7
    assert w.sim_mission_real_to_system


def test_week_sim_compressed():
    state, report = MissionWorldWeekEngine().run_week(days=1)
    assert report.ticks_total >= 8
    assert report.peak_agents >= 500
    assert report.spacetime_summary.get("routes_total", 0) >= report.ticks_total
    assert state.ticks[0].spacetime_tier in ("cooperative", "shadow", "hostile")
    assert state.spacetime_summary.get("substrate_ticks", 0) >= report.ticks_total