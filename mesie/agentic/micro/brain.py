"""Mini brain — compact state machine for micro agents."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from mesie.agentic.micro.career import CareerSpec, MicroCareer


@dataclass
class MiniBrain:
    """Lightweight cognitive state for a micro satellite agent."""

    agent_id: str
    career: MicroCareer
    spec: CareerSpec
    goals: List[str] = field(default_factory=list)
    memory: List[Dict[str, Any]] = field(default_factory=list)
    coherence: float = 0.618
    cycles: int = 0
    last_pulse: float = field(default_factory=time.time)
    alive: bool = True

    @classmethod
    def birth(cls, career: MicroCareer, goals: Optional[List[str]] = None) -> "MiniBrain":
        from mesie.agentic.micro.career import CAREER_REGISTRY

        spec = CAREER_REGISTRY[career]
        return cls(
            agent_id=f"micro-{career.value}-{uuid.uuid4().hex[:8]}",
            career=career,
            spec=spec,
            goals=goals or [spec.mission],
        )

    def pulse(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        self.cycles += 1
        self.last_pulse = time.time()
        self.memory.append({"ts": self.last_pulse, "obs": observation})
        if len(self.memory) > 32:
            self.memory = self.memory[-32:]
        success = observation.get("ok", True)
        self.coherence = min(0.99, self.coherence * 0.9 + (0.1 if success else -0.05))
        return {
            "agent_id": self.agent_id,
            "career": self.career.value,
            "cycles": self.cycles,
            "coherence": round(self.coherence, 4),
            "goals": self.goals,
        }

    def retire(self) -> None:
        self.alive = False

    def status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "career": self.career.value,
            "team": self.spec.team.value,
            "title": self.spec.title,
            "cycles": self.cycles,
            "coherence": round(self.coherence, 4),
            "alive": self.alive,
            "goals": self.goals,
        }