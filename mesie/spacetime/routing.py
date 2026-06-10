"""Bridge from spacetime substrate to operational intelligence routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from mesie.spacetime.signals import ClassifiedSignal, SignalTier
from mesie.spacetime.zones import Zone, route_allowed


@dataclass
class RouteDecision:
    signal_id: str
    tier: str
    source_zone: str
    target_zone: str
    action: str
    allowed: bool
    intelligence_target: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "tier": self.tier,
            "source_zone": self.source_zone,
            "target_zone": self.target_zone,
            "action": self.action,
            "allowed": self.allowed,
            "intelligence_target": self.intelligence_target,
        }


class SpacetimeRouter:
    """Maps classified signals to zone policy and internal intelligence targets."""

    INTELLIGENCE_MAP = {
        SignalTier.COOPERATIVE: "intelligence_engine",
        SignalTier.SHADOW: "workflow_engine",
        SignalTier.HOSTILE: "quarantine_sink",
    }

    def route(
        self,
        signal: ClassifiedSignal,
        *,
        source_zone: str,
        zones: List[Zone],
        zone_index: Dict[str, Zone],
    ) -> RouteDecision:
        tier = SignalTier(signal.tier)
        target_zone_id = source_zone
        action = signal.route_hint
        allowed = True
        intelligence = self.INTELLIGENCE_MAP[tier]

        if tier == SignalTier.HOSTILE:
            q = next((z for z in zones if z.quarantine), None)
            target_zone_id = q.zone_id if q else source_zone
            action = "quarantine"
            allowed = False
        elif tier == SignalTier.SHADOW:
            buf = next((z for z in zones if z.shadow_inspect), None)
            if buf:
                target_zone_id = buf.zone_id
            action = "inspect"
            z = zone_index.get(target_zone_id)
            allowed = route_allowed(z, tier) if z else False
        else:
            z = zone_index.get(source_zone)
            allowed = route_allowed(z, tier) if z else True

        return RouteDecision(
            signal_id=signal.signal_id,
            tier=signal.tier.value,
            source_zone=source_zone,
            target_zone=target_zone_id,
            action=action,
            allowed=allowed,
            intelligence_target=intelligence,
        )

    def to_bus_envelope(self, decision: RouteDecision) -> Dict[str, Any]:
        """Envelope compatible with mesie.internal_api message shape."""
        return {
            "topic": f"spacetime.route.{decision.tier}",
            "payload": {
                "signal_id": decision.signal_id,
                "action": decision.action,
                "target_zone": decision.target_zone,
                "engine": decision.intelligence_target,
            },
            "authority_state": "INTERNAL_RESEARCH",
            "claim_boundary": "repo_verified_architecture",
        }