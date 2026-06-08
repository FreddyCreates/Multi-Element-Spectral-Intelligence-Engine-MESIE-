"""Mission world week simulation."""

from __future__ import annotations

from mesie.worlds.hierarchy import load_world
from mesie.worlds.week_engine import MissionWorldWeekEngine


def test_world_hierarchy():
    w = load_world()
    assert len(w.operations) == 7
    assert w.sim_mission_real_to_system


def test_week_sim_compressed():
    _, report = MissionWorldWeekEngine().run_week(days=1)
    assert report.ticks_total >= 8
    assert report.peak_agents >= 500