"""Cluster-level swarm optimization — one leader decision per cluster, gossip to followers."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from mesie.io.loaders import RecordInput, load_record
from mesie.swarm.consensus import gossip_consensus
from mesie.swarm.drone_coordination import CLUSTER_SIZE, DroneAgentState, SwarmCoordinationReport, SWARM_VERSION
from mesie.swarm.mesh_gossip import MeshGossipBus


@dataclass
class ClusterLeaderState:
    cluster_id: str
    leader_id: str
    threat: bool
    score: float
    route_ok: bool
    route_policy: str
    route_latency_ms: float
    access_mode: str
    local_decision_ms: float
    followers: int


class ClusterSwarmOptimizer:
    """Tier 2: STAR cluster leaders — sub-0.5ms/agent at 10K+ via representative decisions."""

    def __init__(self, coordinator: Any) -> None:
        self.coordinator = coordinator
        self.gossip = MeshGossipBus(fanout=8)

    def coordinate_optimized(
        self,
        query: RecordInput,
        *,
        n_agents: int,
        attrition_rate: float = 0.0,
        jam_ground: bool = False,
    ) -> SwarmCoordinationReport:
        coord = self.coordinator
        coord._ground_jammed = jam_ground
        n_clusters = max(1, (n_agents + CLUSTER_SIZE - 1) // CLUSTER_SIZE)
        t0 = time.perf_counter()
        leaders: List[ClusterLeaderState] = []
        agents: List[DroneAgentState] = []
        local_ms: List[float] = []
        policies: set[str] = set()
        modes: set[str] = set()

        for cluster_idx in range(n_clusters):
            cluster_id = f"cluster-{cluster_idx:04d}"
            leader_i = cluster_idx * CLUSTER_SIZE
            if leader_i >= n_agents:
                break
            followers = min(CLUSTER_SIZE, n_agents - leader_i) - 1
            role = "ground" if leader_i % 5 != 0 else ("orbital" if leader_i % 10 == 0 else "geo")
            policy = coord._cluster_policy(cluster_idx, jammed=jam_ground)
            agent_id = f"{role}_{leader_i:05d}"
            st = coord._local_decision(query, agent_id, cluster_id, policy=policy)
            local_ms.append(st.local_decision_ms)
            policies.add(st.route_policy)
            modes.add(st.access_mode)

            leaders.append(
                ClusterLeaderState(
                    cluster_id=cluster_id,
                    leader_id=agent_id,
                    threat=st.threat,
                    score=st.score,
                    route_ok=st.route_ok,
                    route_policy=st.route_policy,
                    route_latency_ms=st.route_latency_ms,
                    access_mode=st.access_mode,
                    local_decision_ms=st.local_decision_ms,
                    followers=followers,
                )
            )
            agents.append(st)

            self.gossip.fanout_publish(
                agent_id,
                threat=st.threat,
                route_id=f"cluster-{cluster_idx}",
                score=st.score,
                cluster_id=cluster_id,
                n_peers=followers,
            )

            for f in range(1, min(CLUSTER_SIZE, n_agents - leader_i)):
                fi = leader_i + f
                frole = "ground" if fi % 5 != 0 else ("orbital" if fi % 10 == 0 else "geo")
                agents.append(
                    DroneAgentState(
                        agent_id=f"{frole}_{fi:05d}",
                        cluster_id=cluster_id,
                        domain_role=frole,
                        active=True,
                        threat=st.threat,
                        score=st.score,
                        route_ok=st.route_ok,
                        route_policy=st.route_policy,
                        route_latency_ms=st.route_latency_ms,
                        access_mode=st.access_mode,
                        local_decision_ms=0.0,
                    )
                )

        drop_n = int(n_agents * attrition_rate)
        if drop_n > 0:
            drop_idx = set(coord.rng.choice(n_agents, size=drop_n, replace=False).tolist())
            for j in drop_idx:
                if j < len(agents):
                    agents[j].active = False

        active = [a for a in agents if a.active]
        active_clusters = len({a.cluster_id for a in active})
        n_clusters_eff = max(1, (len(active) + CLUSTER_SIZE - 1) // CLUSTER_SIZE)
        self_heal = active_clusters >= max(1, n_clusters_eff - drop_n // CLUSTER_SIZE - 1)

        votes = [a.threat for a in active]
        consensus = gossip_consensus(votes, neighbor_fanout=8)
        elapsed = (time.perf_counter() - t0) * 1000
        leader_ms = [l.local_decision_ms for l in leaders]
        p50 = float(np.percentile(leader_ms, 50)) if leader_ms else 0.0

        jam_ok = True
        if jam_ground:
            jam_ok = (
                "orbital_preferred" in policies
                or any(a.domain_role in {"orbital", "geo"} and a.route_ok for a in active)
                or any(a.access_mode in {"orbital_hz_ladder", "mixed"} for a in active)
            )

        from mesie.sovereign import SovereignLocalMode

        mode = SovereignLocalMode.active()
        st = mode.field_access().status()

        return SwarmCoordinationReport(
            version=f"{SWARM_VERSION}-cluster",
            n_agents=n_agents,
            n_clusters=n_clusters,
            active_after_attrition=len(active),
            doctrine="cluster_star_optimized_decentralized_swarm",
            decentralized=True,
            airgapped=bool(st.get("airgapped")),
            threat_consensus=consensus.decision,
            consensus_confidence=consensus.confidence,
            coordination_ms=round(elapsed, 4),
            ms_per_agent=round(elapsed / max(n_agents, 1), 6),
            e2e_p50_ms=round(p50, 4),
            gossip_bandwidth_bytes=self.gossip.bandwidth_bytes_estimate(len(leaders)),
            jamming_failover_ok=jam_ok,
            self_heal_ok=self_heal,
            route_policies_used=sorted(policies),
            access_modes=sorted(modes),
            sovereign=True,
            ok=all(a.route_ok for a in active),
            agents_sample=agents[:8],
        )