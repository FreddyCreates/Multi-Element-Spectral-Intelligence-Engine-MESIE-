"""Persistent mission world state — the system treats this as operational truth."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

STATE_DIR = Path(__file__).resolve().parents[2] / "library" / "mission_worlds"


@dataclass
class TickRecord:
    sim_day: int
    tick: int
    sim_hour: int
    operation_id: str
    phase: str
    threat_consensus: str
    ms_per_agent: float
    jam_active: bool
    attrition_cumulative: float
    agents_active: int
    narrative: str
    ok: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MissionWorldState:
    world_id: str
    theater: str
    campaign: str
    sim_day: int = 1
    sim_hour: int = 0
    mission_clock_started: str = ""
    jam_level: float = 0.0
    attrition_cumulative: float = 0.0
    agents_deployed_peak: int = 0
    operations_completed: int = 0
    ticks: List[TickRecord] = field(default_factory=list)
    operational_mode: str = "LIVE_SIM"

    def advance_hour(self, hours: int = 3) -> None:
        self.sim_hour += hours
        while self.sim_hour >= 24:
            self.sim_hour -= 24
            self.sim_day += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "theater": self.theater,
            "campaign": self.campaign,
            "sim_day": self.sim_day,
            "sim_hour": self.sim_hour,
            "mission_clock_started": self.mission_clock_started,
            "jam_level": self.jam_level,
            "attrition_cumulative": self.attrition_cumulative,
            "agents_deployed_peak": self.agents_deployed_peak,
            "operations_completed": self.operations_completed,
            "operational_mode": self.operational_mode,
            "tick_count": len(self.ticks),
            "ticks": [t.to_dict() for t in self.ticks],
        }

    def save(self) -> Path:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        path = STATE_DIR / f"{self.world_id}_state.json"
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path