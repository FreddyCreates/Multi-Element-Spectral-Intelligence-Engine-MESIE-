"""Cluster edge fabric — interior DC corpus + OTA mesh + STAR swarm on LAN."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from data import load_reference_record
from mesie.library.domain_corpus import load_domain_corpus
from mesie.production.deployment_doctrine import DeploymentClass
from mesie.production.interior_datacenter import InteriorDataCenter
from mesie.silicon.ota_mesh import run_ota_mesh_round
from mesie.swarm.cluster_coordinator import ClusterSwarmOptimizer
from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator
from mesie.version_info import CLUSTER_EDGE_VERSION

DELIVERABLES = Path(__file__).resolve().parents[2] / "deliverables"


@dataclass
class ClusterEdgeNodeReport:
    node_id: str
    role: str
    corpus_shards: int
    ota_frames_received: int
    ms_per_agent: float
    jam_failover_ok: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClusterEdgeReport:
    fabric_version: str
    deployment_class: str
    n_nodes: int
    interior_dc_shards: int
    interior_dc_bytes: int
    ota_mesh_ok: bool
    ota_frames_received: int
    swarm_agents: int
    cluster_ms_per_agent: float
    cluster_optimized_win: bool
    nodes: List[ClusterEdgeNodeReport]
    sovereign: bool
    airgapped: bool
    cloud_required: bool
    ok: bool
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["nodes"] = [n.to_dict() for n in self.nodes]
        return d


class ClusterEdgeFabric:
    """Tier 2 cluster edge — interior DC feeds multi-node OTA + swarm coordination."""

    def __init__(self, *, n_nodes: int = 4, n_agents: int = 1000) -> None:
        self.n_nodes = n_nodes
        self.n_agents = n_agents
        self.interior_dc = InteriorDataCenter()

    def run(self) -> ClusterEdgeReport:
        dc = self.interior_dc.catalog()
        corpus = load_domain_corpus()
        query = load_reference_record("defense_ew_spectrum_reference")

        ota = run_ota_mesh_round(n_nodes=self.n_nodes, rounds=5)

        coord = DecentralizedSwarmCoordinator(corpus)
        cluster_rep = ClusterSwarmOptimizer(coord).coordinate_optimized(
            query, n_agents=self.n_agents, jam_ground=True
        )

        per_node_agents = max(1, self.n_agents // self.n_nodes)
        nodes: List[ClusterEdgeNodeReport] = []
        for i in range(self.n_nodes):
            nodes.append(
                ClusterEdgeNodeReport(
                    node_id=f"cluster-edge-{i:02d}",
                    role="leader" if i == 0 else "follower",
                    corpus_shards=max(1, dc.total_shards // self.n_nodes),
                    ota_frames_received=max(0, ota.frames_received // self.n_nodes),
                    ms_per_agent=round(cluster_rep.ms_per_agent, 6),
                    jam_failover_ok=cluster_rep.jamming_failover_ok,
                )
            )

        cluster_win = cluster_rep.ms_per_agent < 0.5
        ok = ota.ok and cluster_rep.ok and cluster_win and cluster_rep.jamming_failover_ok

        return ClusterEdgeReport(
            fabric_version=CLUSTER_EDGE_VERSION,
            deployment_class=DeploymentClass.CLUSTER_EDGE.value,
            n_nodes=self.n_nodes,
            interior_dc_shards=dc.total_shards,
            interior_dc_bytes=dc.total_bytes,
            ota_mesh_ok=ota.ok,
            ota_frames_received=ota.frames_received,
            swarm_agents=self.n_agents,
            cluster_ms_per_agent=cluster_rep.ms_per_agent,
            cluster_optimized_win=cluster_win,
            nodes=nodes,
            sovereign=True,
            airgapped=True,
            cloud_required=False,
            ok=ok,
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def export(self, path: Optional[Path] = None) -> Path:
        report = self.run()
        out = path or DELIVERABLES / "MESIE_Cluster_Edge_Report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            __import__("json").dumps(report.to_dict(), indent=2),
            encoding="utf-8",
        )
        return out