"""Full swarm intelligence stack — mission, PSO, formation, LAN, DTN, adapter."""

from __future__ import annotations

import numpy as np

from data import load_reference_record
from mesie.library.domain_corpus import load_domain_corpus
from mesie.swarm.dtn_store import DelayTolerantStore
from mesie.swarm.drone_adapter import DronePlatform, DronePlatformAdapter
from mesie.swarm.formation import FormationController
from mesie.swarm.mission_planner import SwarmMissionPlanner, load_mission_presets
from mesie.swarm.task_allocation import ParticleSwarmAllocator, SwarmTask


def test_mission_planner_ew():
    corpus = load_domain_corpus()
    q = load_reference_record("defense_ew_spectrum_reference")
    rep = SwarmMissionPlanner(corpus).execute_mission(q, preset_id="ew", n_agents=200, jam_ground=True)
    assert rep.ok
    assert rep.tasks_allocated >= 2
    assert rep.platform_commands >= 5


def test_pso_allocation():
    tasks = [SwarmTask("a", "intercept", 1.0, np.array([10, 10, 0]), 0.9)]
    rep = ParticleSwarmAllocator().allocate(32, tasks)
    assert rep.ok


def test_formation_reform():
    rep = FormationController().simulate(50, attrition_rate=0.2)
    assert rep.reform_after_attrition
    assert rep.min_separation_m >= 2.0


def test_dtn_and_adapter():
    dtn = DelayTolerantStore()
    b = dtn.enqueue("t", {"x": 1})
    assert b.bundle_id.startswith("dtn-")
    ad = DronePlatformAdapter(DronePlatform.SIM)
    ad.connect()
    ad.dispatch_spectral_threat("d1", threat=True, route_id="r", score=0.8)
    assert ad.status().connected


def test_mission_presets():
    p = load_mission_presets()
    assert len(p["presets"]) >= 4