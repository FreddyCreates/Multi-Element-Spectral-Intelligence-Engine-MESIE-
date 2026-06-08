"""Swarm SDK — drone coordination, missions, field routing on MAESIClient."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from mesie.io.loaders import RecordInput
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mesie.swarm.mission_planner import MissionPlanReport


@dataclass
class SwarmSDKReport:
    version: str
    corpus_size: int
    domains: List[str]
    presets: int
    routing_ok: bool
    airgapped: bool
    sovereign: bool
    plain_summary: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "corpus_size": self.corpus_size,
            "domains": self.domains,
            "presets": self.presets,
            "routing_ok": self.routing_ok,
            "airgapped": self.airgapped,
            "sovereign": self.sovereign,
            "plain_summary": self.plain_summary,
            "details": self.details,
        }


class SwarmSDK:
    """Unified swarm API — missions, coordination, formation, adapter, mesh."""

    VERSION = "2.0.0"

    def __init__(self, *, seed: int = 42) -> None:
        from mesie.library.domain_corpus import load_domain_corpus
        from mesie.swarm.drone_adapter import DronePlatform, DronePlatformAdapter
        from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator
        from mesie.swarm.mission_planner import SwarmMissionPlanner
        from mesie.sovereign.sovereign_mesh import SovereignMesh

        self._corpus = load_domain_corpus()
        self._planner = SwarmMissionPlanner(self._corpus, seed=seed)
        self._coordinator = DecentralizedSwarmCoordinator(self._corpus, seed=seed)
        self._adapter = DronePlatformAdapter(DronePlatform.SIM)
        self._mesh = SovereignMesh()

    @property
    def corpus(self) -> list:
        return self._corpus

    def catalog(self) -> Dict[str, Any]:
        from mesie.library.domain_corpus import domain_catalog

        return domain_catalog()

    def presets(self) -> Dict[str, Any]:
        from mesie.swarm.mission_planner import load_mission_presets

        return load_mission_presets()

    def routing_validate(self) -> Dict[str, Any]:
        return self._coordinator.routing_validation()

    def coordinate(
        self,
        record: RecordInput,
        *,
        n_agents: int = 1000,
        jam_ground: bool = False,
        attrition_rate: float = 0.0,
        cluster_optimized: bool = True,
    ) -> Dict[str, Any]:
        return self._coordinator.coordinate(
            record,
            n_agents=n_agents,
            jam_ground=jam_ground,
            attrition_rate=attrition_rate,
            cluster_optimized=cluster_optimized,
        ).to_dict()

    def rf_ingest(self, *, simulated: bool = True, virtual_silicon: bool = False) -> Dict[str, Any]:
        from mesie.field_io.rf_adapter import LiveRFAdapter, RFAdapterConfig, RFSourceMode

        if virtual_silicon:
            rf = LiveRFAdapter(RFAdapterConfig(mode=RFSourceMode.VIRTUAL_SILICON))
            return rf.ingest_virtual_silicon().to_dict()
        rf = LiveRFAdapter(RFAdapterConfig(mode=RFSourceMode.SIM))
        return (rf.ingest_simulated() if simulated else rf.ingest_payload(b"")).to_dict()

    def mission_plan(
        self,
        record: RecordInput,
        *,
        preset_id: str = "ew",
        n_agents: int = 1000,
        jam_ground: bool = False,
        attrition_rate: float = 0.05,
    ) -> "MissionPlanReport":
        return self._planner.execute_mission(
            record,
            preset_id=preset_id,
            n_agents=n_agents,
            jam_ground=jam_ground,
            attrition_rate=attrition_rate,
        )

    def formation(self, n_agents: int = 100, *, attrition_rate: float = 0.1) -> Dict[str, Any]:
        from mesie.swarm.formation import FormationController

        return FormationController().simulate(n_agents, attrition_rate=attrition_rate).to_dict()

    def allocate_tasks(self, n_agents: int, *, method: str = "pso") -> Dict[str, Any]:
        import numpy as np
        from mesie.swarm.task_allocation import MARLTaskAllocator, ParticleSwarmAllocator, SwarmTask

        tasks = [
            SwarmTask(f"t{i}", t, 1.0 - i * 0.1, np.array([50 + i * 20, 30, 10]), 0.85)
            for i, t in enumerate(["intercept", "scan", "relay"])
        ]
        n = min(n_agents, 256)
        if method == "marl":
            return MARLTaskAllocator().allocate(n, tasks).to_dict()
        return ParticleSwarmAllocator().allocate(n, tasks).to_dict()

    def mesh_export(self) -> Dict[str, Any]:
        return self._mesh.export_bundle().to_dict()

    def adapter_status(self) -> Dict[str, Any]:
        self._adapter.connect()
        return self._adapter.status().to_dict()

    def status(self) -> SwarmSDKReport:
        routing = self.routing_validate()
        cat = self.catalog()
        presets = self.presets()
        return SwarmSDKReport(
            version=self.VERSION,
            corpus_size=cat["total_indexable"],
            domains=cat["domains"],
            presets=len(presets.get("presets", [])),
            routing_ok=routing.get("all_routes_ok", False),
            airgapped=bool(routing.get("sovereign_airgapped")),
            sovereign=True,
            plain_summary=(
                f"SwarmSDK v{self.VERSION}: {cat['total_indexable']} corpus records, "
                f"{len(presets.get('presets', []))} mission presets, routing={'OK' if routing.get('all_routes_ok') else 'FAIL'}."
            ),
            details={"routing": routing, "catalog": cat},
        )