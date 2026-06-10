"""Bounded geometric zones with semantic operational roles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np

from mesie.spacetime.agents import SpatialAgent, Vec3
from mesie.spacetime.signals import SignalTier


@dataclass
class Zone:
    zone_id: str
    role: str
    center: Vec3
    radius: float
    allow_cooperative: bool = True
    block_hostile: bool = False
    shadow_inspect: bool = False
    quarantine: bool = False

    def contains(self, position: Vec3) -> bool:
        c = np.array(self.center)
        p = np.array(position)
        return float(np.linalg.norm(p - c)) <= self.radius

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "role": self.role,
            "center": list(self.center),
            "radius": self.radius,
            "allow_cooperative": self.allow_cooperative,
            "block_hostile": self.block_hostile,
            "shadow_inspect": self.shadow_inspect,
            "quarantine": self.quarantine,
        }


def default_zones() -> List[Zone]:
    return [
        Zone("command_core", "operational", (0.0, 0.0, 0.0), 15.0, allow_cooperative=True),
        Zone("field_ops", "operational", (12.0, 0.0, 4.0), 12.0, allow_cooperative=True),
        Zone("shadow_buffer", "inspection", (18.0, 2.0, 3.0), 8.0, shadow_inspect=True, block_hostile=True),
        Zone("quarantine_hold", "quarantine", (35.0, 12.0, 6.0), 10.0, quarantine=True, block_hostile=True, allow_cooperative=False),
        Zone("honeypot_surface", "honeypot", (24.0, -6.0, 2.0), 6.0, shadow_inspect=True),
    ]


def zone_for_agent(agent: SpatialAgent, zones: List[Zone]) -> str:
    for z in zones:
        if z.contains(agent.position):
            return z.zone_id
    return ""


def route_allowed(zone: Zone, tier: SignalTier) -> bool:
    if tier == SignalTier.HOSTILE:
        return not zone.block_hostile and not zone.quarantine
    if tier == SignalTier.SHADOW:
        return zone.shadow_inspect or zone.allow_cooperative
    return zone.allow_cooperative