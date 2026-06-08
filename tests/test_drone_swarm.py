"""Drone swarm coordination — routing, consensus, jamming, attrition."""

from __future__ import annotations

from data import load_reference_record
from mesie.library.domain_corpus import load_domain_corpus
from mesie.swarm.consensus import gossip_consensus
from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator


def test_routing_validation():
    swarm = DecentralizedSwarmCoordinator(load_domain_corpus())
    r = swarm.routing_validation()
    assert r["all_routes_ok"]
    assert r["presets_ok"]
    assert r["alias_route_ok"]
    assert r["sovereign_airgapped"]


def test_gossip_consensus():
    c = gossip_consensus([True] * 60 + [False] * 40)
    assert c.decision == "engage"
    assert c.quorum_met


def test_swarm_100_agents():
    corpus = load_domain_corpus()
    q = load_reference_record("defense_ew_spectrum_reference")
    rep = DecentralizedSwarmCoordinator(corpus).coordinate(q, n_agents=100)
    assert rep.ok
    assert rep.e2e_p50_ms < 50.0


def test_jamming_failover():
    corpus = load_domain_corpus()
    q = load_reference_record("rf_jamming_profile_reference")
    rep = DecentralizedSwarmCoordinator(corpus).coordinate(q, n_agents=200, jam_ground=True)
    assert rep.jamming_failover_ok


def test_attrition_self_heal():
    corpus = load_domain_corpus()
    q = load_reference_record("defense_ew_spectrum_reference")
    rep = DecentralizedSwarmCoordinator(corpus).coordinate(q, n_agents=500, attrition_rate=0.1)
    assert rep.self_heal_ok
    assert rep.active_after_attrition >= 400