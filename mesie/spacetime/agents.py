"""Position-bearing agents in simulated spacetime substrate."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

import numpy as np

Vec3 = Tuple[float, float, float]


@dataclass
class SpatialAgent:
    agent_id: str
    role: str
    position: Vec3
    velocity: Vec3 = (0.0, 0.0, 0.0)
    trust_score: float = 0.8
    zone_id: str = ""
    quarantined: bool = False
    influence_mass: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "position": list(self.position),
            "velocity": list(self.velocity),
            "trust_score": round(self.trust_score, 4),
            "zone_id": self.zone_id,
            "quarantined": self.quarantined,
            "influence_mass": self.influence_mass,
        }

    def distance_to(self, other: "SpatialAgent") -> float:
        a = np.array(self.position)
        b = np.array(other.position)
        return float(np.linalg.norm(a - b))


def default_agent_registry() -> List[SpatialAgent]:
    """Release-safe resident set — not full 21-agent spatium roster."""
    return [
        SpatialAgent("resident_alpha", "resident", (0.0, 0.0, 0.0), trust_score=0.95, influence_mass=2.0),
        SpatialAgent("resident_beta", "resident", (12.0, 0.0, 4.0), trust_score=0.9, influence_mass=1.5),
        SpatialAgent("defense_node_1", "defensive", (6.0, 8.0, 0.0), trust_score=0.92, influence_mass=1.2),
        SpatialAgent("honeypot_a", "honeypot", (24.0, -6.0, 2.0), trust_score=0.5, influence_mass=0.3),
        SpatialAgent("threat_probe", "threat", (30.0, 10.0, 5.0), trust_score=0.1, influence_mass=0.8),
        SpatialAgent("packet_relay", "data_packet", (4.0, -4.0, 1.0), trust_score=0.7, influence_mass=0.5),
    ]