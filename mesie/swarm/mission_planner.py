"""Swarm mission planner — spectral threat → tasks → formation → platform dispatch."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from mesie.io.loaders import RecordInput, load_record
from mesie.sovereign import SovereignLocalMode, get_field_access_engine
from mesie.swarm.consensus import gossip_consensus
from mesie.swarm.drone_adapter import DronePlatform, DronePlatformAdapter
from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator
from mesie.swarm.dtn_store import DelayTolerantStore
from mesie.swarm.formation import FormationController
from mesie.swarm.lan_gossip import LanGossipNode
from mesie.swarm.task_allocation import MARLTaskAllocator, ParticleSwarmAllocator, SwarmTask

PRESETS_PATH = Path(__file__).resolve().parents[2] / "library" / "swarm_mission_presets.json"
SWARM_ENGINE_VERSION = "2.0.0"


@dataclass
class MissionPlanReport:
    version: str
    mission_id: str
    preset: str
    n_agents: int
    threat_consensus: str
    spectral_score: float
    route_policy: str
    route_ok: bool
    tasks_allocated: int
    allocation_method: str
    formation: str
    formation_ok: bool
    lan_gossip_msgs: int
    dtn_pending: int
    platform_commands: int
    coordination_ms: float
    ms_per_agent: float
    decentralized: bool
    airgapped: bool
    sovereign: bool
    ok: bool
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "mission_id": self.mission_id,
            "preset": self.preset,
            "n_agents": self.n_agents,
            "threat_consensus": self.threat_consensus,
            "spectral_score": self.spectral_score,
            "route_policy": self.route_policy,
            "route_ok": self.route_ok,
            "tasks_allocated": self.tasks_allocated,
            "allocation_method": self.allocation_method,
            "formation": self.formation,
            "formation_ok": self.formation_ok,
            "lan_gossip_msgs": self.lan_gossip_msgs,
            "dtn_pending": self.dtn_pending,
            "platform_commands": self.platform_commands,
            "coordination_ms": self.coordination_ms,
            "ms_per_agent": self.ms_per_agent,
            "decentralized": self.decentralized,
            "airgapped": self.airgapped,
            "sovereign": self.sovereign,
            "ok": self.ok,
            "details": self.details,
        }


def load_mission_presets() -> Dict[str, Any]:
    if not PRESETS_PATH.exists():
        default = {
            "version": "1.0.0",
            "presets": [
                {"id": "strike", "label": "Cross-domain strike", "route_policy": "orbital_preferred", "formation": "v_shape", "tasks": ["intercept", "jam_resist", "spectral_confirm"]},
                {"id": "isr", "label": "ISR spectral sweep", "route_policy": "shortest", "formation": "grid", "tasks": ["scan", "match", "relay"]},
                {"id": "ew", "label": "EW contested defense", "route_policy": "orbital_preferred", "formation": "v_shape", "tasks": ["detect", "failover", "consensus"]},
                {"id": "swarm_forge", "label": "Swarm Forge training", "route_policy": "ladder_only", "formation": "grid", "tasks": ["train", "reform", "gossip_sync"]},
            ],
        }
        PRESETS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PRESETS_PATH.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return default
    return json.loads(PRESETS_PATH.read_text(encoding="utf-8"))


class SwarmMissionPlanner:
    """Full doctrine stack: routing nervous system + spectral + PSO/MARL + formation + LAN + DTN + adapter."""

    def __init__(self, corpus: Sequence[RecordInput], *, seed: int = 42) -> None:
        self.corpus = corpus
        self.coordinator = DecentralizedSwarmCoordinator(corpus, seed=seed)
        self.pso = ParticleSwarmAllocator(seed=seed)
        self.marl = MARLTaskAllocator(seed=seed)
        self.formation = FormationController(seed=seed)
        self.dtn = DelayTolerantStore()
        self.adapter = DronePlatformAdapter(DronePlatform.SIM, n_drones=100)
        self.lan: Optional[LanGossipNode] = None
        self.fa = get_field_access_engine()

    def _ensure_lan(self) -> LanGossipNode:
        if self.lan is None:
            self.lan = LanGossipNode(node_id="swarm-planner", port=37521)
            try:
                self.lan.start()
            except OSError:
                pass
        return self.lan

    def _build_tasks(self, preset: Dict[str, Any], spectral_urgency: float) -> List[SwarmTask]:
        tasks = []
        for i, ttype in enumerate(preset.get("tasks", ["patrol"])):
            tasks.append(
                SwarmTask(
                    task_id=f"task_{ttype}_{i}",
                    task_type=ttype,
                    priority=1.0 - i * 0.1,
                    position=np.array([50.0 + i * 15, 30.0 + i * 10, 10.0]),
                    spectral_urgency=spectral_urgency,
                )
            )
        return tasks

    def execute_mission(
        self,
        query: RecordInput,
        *,
        preset_id: str = "ew",
        n_agents: int = 1000,
        jam_ground: bool = False,
        attrition_rate: float = 0.05,
        use_marl: bool = False,
    ) -> MissionPlanReport:
        presets = load_mission_presets()
        preset = next((p for p in presets["presets"] if p["id"] == preset_id), presets["presets"][0])
        t0 = time.perf_counter()
        mission_id = f"mission-{preset_id}-{int(time.time())}"

        swarm_rep = self.coordinator.coordinate(
            query,
            n_agents=n_agents,
            jam_ground=jam_ground,
            attrition_rate=attrition_rate,
        )
        rec = load_record(query)
        spectral_score = swarm_rep.consensus_confidence

        policy = preset.get("route_policy", "orbital_preferred" if jam_ground else "shortest")
        src = "leo0" if jam_ground else "ground"
        route = self.fa.route(src, "world", policy=policy)

        tasks = self._build_tasks(preset, spectral_score)
        alloc_n = min(n_agents, 256)
        if use_marl or n_agents > 256:
            alloc = self.marl.allocate(alloc_n, tasks)
        else:
            alloc = self.pso.allocate(alloc_n, tasks)

        form_name = preset.get("formation", "v_shape")
        form_rep = self.formation.simulate(min(n_agents, 200), attrition_rate=attrition_rate)

        lan = self._ensure_lan()
        lan_msgs = 0
        for i in range(min(20, n_agents // 50)):
            lan.publish(
                threat=swarm_rep.threat_consensus == "engage",
                route_id=route.route_id,
                score=spectral_score,
                cluster_id=f"cluster-{i:03d}",
            )
            lan_msgs += 1
        if jam_ground:
            self.dtn.enqueue("swarm-planner", {"mission": mission_id, "failover": "orbital"})

        self.adapter.connect()
        cmds = []
        for a in swarm_rep.agents_sample[:5]:
            cmds.append(
                self.adapter.dispatch_spectral_threat(
                    a.agent_id,
                    threat=a.threat,
                    route_id=route.route_id,
                    score=a.score,
                )
            )
        self.adapter.dispatch_formation(form_name, [c.agent_id for c in cmds])
        flushed = self.adapter.flush_commands()

        elapsed = (time.perf_counter() - t0) * 1000
        mode = SovereignLocalMode.active()

        ok = (
            swarm_rep.ok
            and route.ok
            and alloc.ok
            and form_rep.ok
            and (not jam_ground or swarm_rep.jamming_failover_ok)
        )

        return MissionPlanReport(
            version=SWARM_ENGINE_VERSION,
            mission_id=mission_id,
            preset=preset_id,
            n_agents=n_agents,
            threat_consensus=swarm_rep.threat_consensus,
            spectral_score=round(spectral_score, 4),
            route_policy=policy,
            route_ok=route.ok,
            tasks_allocated=len(alloc.assignments),
            allocation_method=alloc.method,
            formation=form_rep.formation,
            formation_ok=form_rep.ok,
            lan_gossip_msgs=lan_msgs,
            dtn_pending=self.dtn.pending_count(),
            platform_commands=len(flushed),
            coordination_ms=round(elapsed, 4),
            ms_per_agent=round(elapsed / max(n_agents, 1), 6),
            decentralized=True,
            airgapped=bool(mode.field_access().status().get("airgapped")),
            sovereign=True,
            ok=ok,
            details={
                "swarm": swarm_rep.to_dict(),
                "allocation": alloc.to_dict(),
                "formation": form_rep.to_dict(),
                "routing": self.coordinator.routing_validation(),
                "lan": lan.status(),
                "adapter": self.adapter.status().to_dict(),
            },
        )