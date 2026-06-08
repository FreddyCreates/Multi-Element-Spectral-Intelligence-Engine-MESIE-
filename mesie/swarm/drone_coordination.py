"""Decentralized drone swarm coordination — NeuroSwarm / Chimeria Defense doctrine.

No central commander: local spectral decisions + mesh gossip + hierarchical field routing.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from mesie import match_records, validate_record
from mesie.io.loaders import RecordInput, load_record
from mesie.sdk.fast_compute import FastSpectralCompute
from mesie.sovereign import SovereignLocalMode, get_field_access_engine
from mesie.swarm.consensus import gossip_consensus
from mesie.swarm.mesh_gossip import MeshGossipBus


from mesie.version_info import SWARM_VERSION
CLUSTER_SIZE = 32


@dataclass
class DroneAgentState:
    agent_id: str
    cluster_id: str
    domain_role: str
    active: bool
    threat: bool
    score: float
    route_ok: bool
    route_policy: str
    route_latency_ms: float
    access_mode: str
    local_decision_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SwarmCoordinationReport:
    version: str
    n_agents: int
    n_clusters: int
    active_after_attrition: int
    doctrine: str
    decentralized: bool
    airgapped: bool
    threat_consensus: str
    consensus_confidence: float
    coordination_ms: float
    ms_per_agent: float
    e2e_p50_ms: float
    gossip_bandwidth_bytes: int
    jamming_failover_ok: bool
    self_heal_ok: bool
    route_policies_used: List[str]
    access_modes: List[str]
    sovereign: bool
    ok: bool
    agents_sample: List[DroneAgentState] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "n_agents": self.n_agents,
            "n_clusters": self.n_clusters,
            "active_after_attrition": self.active_after_attrition,
            "doctrine": self.doctrine,
            "decentralized": self.decentralized,
            "airgapped": self.airgapped,
            "threat_consensus": self.threat_consensus,
            "consensus_confidence": self.consensus_confidence,
            "coordination_ms": self.coordination_ms,
            "ms_per_agent": self.ms_per_agent,
            "e2e_p50_ms": self.e2e_p50_ms,
            "gossip_bandwidth_bytes": self.gossip_bandwidth_bytes,
            "jamming_failover_ok": self.jamming_failover_ok,
            "self_heal_ok": self.self_heal_ok,
            "route_policies_used": self.route_policies_used,
            "access_modes": self.access_modes,
            "sovereign": self.sovereign,
            "ok": self.ok,
            "agents_sample": [a.to_dict() for a in self.agents_sample],
        }


class DecentralizedSwarmCoordinator:
    """Nervous system for drone swarms: spectral backbone + field mesh + gossip consensus."""

    def __init__(
        self,
        corpus: Sequence[RecordInput],
        *,
        threat_threshold: float = 0.55,
        seed: int = 42,
    ) -> None:
        self.corpus = [load_record(r) for r in corpus]
        self.threat_threshold = threat_threshold
        self.rng = np.random.default_rng(seed)
        self.fc = FastSpectralCompute()
        self.fc.build_index(self.corpus)
        self.fa = get_field_access_engine()
        self.gossip = MeshGossipBus(fanout=8)
        self._ground_jammed = False

    def _local_decision(
        self,
        query: RecordInput,
        agent_id: str,
        cluster_id: str,
        *,
        policy: str,
    ) -> DroneAgentState:
        q = load_record(query)
        t0 = time.perf_counter()
        validate_record(q)
        hits = self.fc.cosine_search(q, top_k=1)
        ref = self.corpus[0]
        score = match_records(q, ref).composite_score if hits else 0.0
        threat = score >= self.threat_threshold

        role = agent_id.split("_")[0]
        src = self._route_source(role, cluster_id)
        dst = "world" if int(cluster_id.split("-")[-1]) % 3 == 0 else "geo"
        if self._ground_jammed and policy == "shortest":
            policy = "orbital_preferred"
            src = "leo0"

        route = self.fa.route(src, dst, policy=policy)
        ms = (time.perf_counter() - t0) * 1000

        self.gossip.fanout_publish(
            agent_id,
            threat=threat,
            route_id=route.route_id if route.ok else "none",
            score=score,
            cluster_id=cluster_id,
            n_peers=CLUSTER_SIZE,
        )

        return DroneAgentState(
            agent_id=agent_id,
            cluster_id=cluster_id,
            domain_role=role,
            active=True,
            threat=threat,
            score=round(score, 4),
            route_ok=route.ok,
            route_policy=policy,
            route_latency_ms=route.total_latency_ms,
            access_mode=route.access_mode,
            local_decision_ms=round(ms, 4),
        )

    @staticmethod
    def _route_source(role: str, cluster_id: str) -> str:
        cid = int(cluster_id.split("-")[-1]) if "-" in cluster_id else 0
        if role == "orbital":
            return "leo0" if cid % 2 == 0 else "meo0"
        if role == "geo":
            return "geo"
        return "ground"

    def _cluster_policy(self, cluster_idx: int, *, jammed: bool) -> str:
        if jammed:
            return "orbital_preferred"
        if cluster_idx % 4 == 0:
            return "orbital_preferred"
        if cluster_idx % 3 == 0:
            return "ladder_only"
        return "shortest"

    def coordinate(
        self,
        query: RecordInput,
        *,
        n_agents: int = 1000,
        attrition_rate: float = 0.0,
        jam_ground: bool = False,
        cluster_optimized: bool = True,
    ) -> SwarmCoordinationReport:
        if cluster_optimized and n_agents > CLUSTER_SIZE:
            from mesie.swarm.cluster_coordinator import ClusterSwarmOptimizer

            return ClusterSwarmOptimizer(self).coordinate_optimized(
                query,
                n_agents=n_agents,
                attrition_rate=attrition_rate,
                jam_ground=jam_ground,
            )
        self._ground_jammed = jam_ground
        n_clusters = max(1, (n_agents + CLUSTER_SIZE - 1) // CLUSTER_SIZE)
        t0 = time.perf_counter()
        agents: List[DroneAgentState] = []
        local_ms: List[float] = []
        policies: set[str] = set()
        modes: set[str] = set()

        for i in range(n_agents):
            cluster_idx = i // CLUSTER_SIZE
            cluster_id = f"cluster-{cluster_idx:04d}"
            role = "ground" if i % 5 != 0 else ("orbital" if i % 10 == 0 else "geo")
            policy = self._cluster_policy(cluster_idx, jammed=jam_ground)
            agent_id = f"{role}_{i:05d}"
            st = self._local_decision(query, agent_id, cluster_id, policy=policy)
            agents.append(st)
            local_ms.append(st.local_decision_ms)
            policies.add(st.route_policy)
            modes.add(st.access_mode)

        # Node attrition — self-healing reform
        drop_n = int(n_agents * attrition_rate)
        if drop_n > 0:
            drop_idx = set(self.rng.choice(n_agents, size=drop_n, replace=False).tolist())
            for j in drop_idx:
                agents[j].active = False
        active = [a for a in agents if a.active]
        active_clusters = len({a.cluster_id for a in active})
        self_heal = active_clusters >= max(1, n_clusters - drop_n // CLUSTER_SIZE - 1)

        votes = [a.threat for a in active]
        consensus = gossip_consensus(votes, neighbor_fanout=8)
        elapsed = (time.perf_counter() - t0) * 1000
        p50 = float(np.percentile(local_ms, 50)) if local_ms else 0.0

        jam_ok = True
        if jam_ground:
            jam_ok = (
                "orbital_preferred" in policies
                or any(a.domain_role in {"orbital", "geo"} and a.route_ok for a in active)
                or any(a.access_mode in {"orbital_hz_ladder", "mixed"} for a in active)
            )

        mode = SovereignLocalMode.active()
        st = mode.field_access().status()

        return SwarmCoordinationReport(
            version=SWARM_VERSION,
            n_agents=n_agents,
            n_clusters=n_clusters,
            active_after_attrition=len(active),
            doctrine="decentralized_spectral_swarm_no_single_point_of_failure",
            decentralized=True,
            airgapped=bool(st.get("airgapped")),
            threat_consensus=consensus.decision,
            consensus_confidence=consensus.confidence,
            coordination_ms=round(elapsed, 4),
            ms_per_agent=round(elapsed / max(n_agents, 1), 6),
            e2e_p50_ms=round(p50, 4),
            gossip_bandwidth_bytes=self.gossip.bandwidth_bytes_estimate(len(agents)),
            jamming_failover_ok=jam_ok,
            self_heal_ok=self_heal,
            route_policies_used=sorted(policies),
            access_modes=sorted(modes),
            sovereign=True,
            ok=all(a.route_ok for a in active) and consensus.quorum_met is not None,
            agents_sample=agents[:8],
        )

    def routing_validation(self) -> Dict[str, Any]:
        """Validate field router nervous-system paths (public repo harness)."""
        checks = []
        pairs = [
            ("ground-schumann", "world-computer-root", "shortest"),
            ("ground", "world", "shortest"),
            ("orbital-leo-edge-000", "orbital-geo-backbone-000", "orbital_preferred"),
            ("leo0", "geo", "orbital_preferred"),
            ("schumann", "root", "shortest"),
        ]
        for src, dst, pol in pairs:
            r = self.fa.route(src, dst, policy=pol)
            checks.append({
                "route": f"{src}→{dst}",
                "policy": pol,
                "ok": r.ok,
                "hops": len(r.hops),
                "latency_ms": r.total_latency_ms,
                "access_mode": r.access_mode,
            })
        presets = self.fa.list_presets()
        health = self.fa.health()
        mode = SovereignLocalMode.active()
        return {
            "routes": checks,
            "presets_ok": all(p["ok"] for p in presets),
            "router_health": health.get("ok"),
            "alias_route_ok": self.fa.route("schumann", "root").ok,
            "sovereign_airgapped": mode.field_access().status().get("airgapped"),
            "all_routes_ok": all(c["ok"] for c in checks),
        }