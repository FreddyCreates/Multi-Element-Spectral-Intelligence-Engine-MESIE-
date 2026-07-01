"""Micro agent orchestrator — spawn careers, satellites, and fleet status."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from mesie.agentic.micro.brain import MiniBrain
from mesie.agentic.micro.career import CAREER_REGISTRY, MicroCareer
from mesie.agentic.micro.satellite import SatelliteAgent, TaskFn


@dataclass
class MicroOrchestrator:
    """Fleet manager for activated micro sub-agents."""

    satellites: Dict[str, SatelliteAgent] = field(default_factory=dict)
    _task_registry: Dict[MicroCareer, TaskFn] = field(default_factory=dict, init=False)

    def register_task(self, career: MicroCareer, fn: TaskFn) -> None:
        self._task_registry[career] = fn

    def spawn(
        self,
        career: MicroCareer,
        *,
        interval_s: Optional[float] = None,
        goals: Optional[List[str]] = None,
        satellite: bool = False,
    ) -> SatelliteAgent:
        spec = CAREER_REGISTRY[career]
        brain = MiniBrain.birth(career, goals=goals)
        task = self._task_registry.get(career, self._default_task(career))
        agent = SatelliteAgent(
            brain=brain,
            task_fn=task,
            interval_s=interval_s or spec.default_interval_s,
        )
        self.satellites[brain.agent_id] = agent
        if satellite:
            agent.launch_satellite()
        return agent

    def run_all_once(self) -> List[Dict[str, Any]]:
        return [a.run_once() for a in self.satellites.values()]

    def stop_all(self) -> None:
        for a in self.satellites.values():
            a.stop()

    def agents_for_career(self, career: MicroCareer) -> List[SatelliteAgent]:
        return [a for a in self.satellites.values() if a.brain.career == career]

    def ensure_satellite(self, career: MicroCareer, *, immediate: bool = False) -> SatelliteAgent:
        """Spawn or activate timer loop for a career."""
        existing = self.agents_for_career(career)
        if existing:
            agent = existing[0]
            if not agent.satellite_active:
                agent.launch_satellite(immediate=immediate)
            return agent
        agent = self.spawn(career, satellite=False)
        agent.launch_satellite(immediate=immediate)
        return agent

    def fleet_status(self) -> Dict[str, Any]:
        from mesie.agentic.micro.career import CAREER_REGISTRY, NOVA_ORG_SIZE, MicroCareer

        agents = [a.status for a in self.satellites.values()]
        pulsing = sum(1 for a in agents if a.get("cycles", 0) > 0)
        teams: Dict[str, int] = {}
        for a in agents:
            try:
                spec = CAREER_REGISTRY[MicroCareer(a["career"])]
                teams[spec.team.value] = teams.get(spec.team.value, 0) + 1
            except ValueError:
                pass
        return {
            "count": len(self.satellites),
            "expected": NOVA_ORG_SIZE,
            "pulsing": pulsing,
            "teams": teams,
            "agents": agents,
            "ts": time.time(),
        }

    @staticmethod
    def _default_task(career: MicroCareer) -> TaskFn:
        def _task(brain: MiniBrain) -> Dict[str, Any]:
            return {
                "ok": True,
                "career": career.value,
                "mission": brain.spec.mission,
                "note": "default micro pulse",
            }

        return _task