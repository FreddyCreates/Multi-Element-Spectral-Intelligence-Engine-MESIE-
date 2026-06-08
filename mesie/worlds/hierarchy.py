"""Scenario hierarchy — Theater → Campaign → Operation → Day → Tick."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

WORLDS_DIR = Path(__file__).resolve().parents[2] / "data" / "worlds"


@dataclass
class OperationSpec:
    id: str
    day: int
    phase: str
    doctrine: str
    preset: str
    primary_data: str
    n_agents: int
    jam_ground: bool
    attrition_rate: float
    secondary_data: Optional[str] = None
    library_refs: List[str] = field(default_factory=list)
    library_signal: Optional[str] = None
    enterprise_parallel: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "OperationSpec":
        return cls(
            id=d["id"],
            day=int(d["day"]),
            phase=d["phase"],
            doctrine=d.get("doctrine", "defense"),
            preset=d.get("preset", "ew"),
            primary_data=d["primary_data"],
            n_agents=int(d.get("n_agents", 500)),
            jam_ground=bool(d.get("jam_ground", False)),
            attrition_rate=float(d.get("attrition_rate", 0.05)),
            secondary_data=d.get("secondary_data"),
            library_refs=list(d.get("library_refs", [])),
            library_signal=d.get("library_signal"),
            enterprise_parallel=d.get("enterprise_parallel"),
        )


@dataclass
class WorldHierarchy:
    world_id: str
    label: str
    theater: str
    campaign: str
    operations: List[OperationSpec]
    ticks_per_day: int
    real_data_backbone: List[str]
    sim_mission_real_to_system: bool

    def operation_for_day(self, day: int) -> Optional[OperationSpec]:
        for op in self.operations:
            if op.day == day:
                return op
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "label": self.label,
            "theater": self.theater,
            "campaign": self.campaign,
            "operations": [op.__dict__ for op in self.operations],
            "ticks_per_day": self.ticks_per_day,
            "real_data_backbone": self.real_data_backbone,
        }


def load_world(name: str = "military_theater_week") -> WorldHierarchy:
    path = WORLDS_DIR / f"{name}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    h = raw["hierarchy"]
    return WorldHierarchy(
        world_id=raw["world_id"],
        label=raw["label"],
        theater=h["theater"],
        campaign=h["campaign"],
        operations=[OperationSpec.from_dict(o) for o in h["operations"]],
        ticks_per_day=int(raw.get("ticks_per_day", 8)),
        real_data_backbone=list(raw.get("real_data_backbone", [])),
        sim_mission_real_to_system=bool(raw.get("sim_mission_real_to_system", True)),
    )