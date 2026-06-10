"""Bridge mission-world theater ticks through Paper 04 spacetime substrate."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from mesie.spacetime.routing import SpacetimeRouter
from mesie.spacetime.signals import SignalTier, classify_signal
from mesie.spacetime.substrate import SimulatedSpacetimeSubstrate, TickTrace
from mesie.spacetime.zones import default_zones


@dataclass
class TheaterSpacetimeResult:
    signal_tier: str
    source_zone: str
    target_zone: str
    route_action: str
    route_allowed: bool
    intelligence_target: str
    quarantined_agents: List[str] = field(default_factory=list)
    substrate_tick: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_tier": self.signal_tier,
            "source_zone": self.source_zone,
            "target_zone": self.target_zone,
            "route_action": self.route_action,
            "route_allowed": self.route_allowed,
            "intelligence_target": self.intelligence_target,
            "quarantined_agents": self.quarantined_agents,
            "substrate_tick": self.substrate_tick,
        }


class TheaterSpacetimeBridge:
    """Runs each mission-world tick through spatial tier routing + substrate advance."""

    def __init__(self) -> None:
        self._substrate = SimulatedSpacetimeSubstrate()
        self._router = SpacetimeRouter()
        self._zones = default_zones()
        self._zone_index = {z.zone_id: z for z in self._zones}
        self._routes_total = 0
        self._routes_allowed = 0
        self._hostile_ticks = 0
        self._shadow_ticks = 0

    def _source_zone(self, doctrine: str, jam_active: bool) -> str:
        if jam_active:
            return "shadow_buffer"
        if doctrine == "defense":
            return "command_core"
        return "field_ops"

    def _trust_from_theater(
        self,
        *,
        mission_ok: bool,
        threat_consensus: str,
        jam_active: bool,
        jam_failover_ok: bool,
        doctrine: str,
        attrition: float,
    ) -> tuple[float, bool, bool]:
        trust = 0.88 if mission_ok else 0.42
        adversary = False
        unknown = False
        tc = (threat_consensus or "").lower()
        if "hostile" in tc or "threat" in tc or (doctrine == "offense" and not mission_ok):
            adversary = True
            trust = 0.12
        elif jam_active and not jam_failover_ok:
            unknown = True
            trust = 0.45
        elif jam_active or "uncertain" in tc or "shadow" in tc:
            unknown = True
            trust = min(trust, 0.5)
        if attrition > 0.5:
            trust *= 0.85
        return trust, adversary, unknown

    def process_tick(
        self,
        *,
        operation_id: str,
        tick_idx: int,
        doctrine: str,
        mission_ok: bool,
        threat_consensus: str,
        jam_active: bool,
        jam_failover_ok: bool,
        attrition_cumulative: float,
    ) -> TheaterSpacetimeResult:
        trust, adversary, unknown = self._trust_from_theater(
            mission_ok=mission_ok,
            threat_consensus=threat_consensus,
            jam_active=jam_active,
            jam_failover_ok=jam_failover_ok,
            doctrine=doctrine,
            attrition=attrition_cumulative,
        )
        source_zone = self._source_zone(doctrine, jam_active)
        signal = classify_signal(
            signal_id=f"theater_{operation_id}_{tick_idx}",
            source_agent=f"theater_{operation_id}",
            payload_kind="mission_tick",
            trust_score=trust,
            adversary_flag=adversary,
            unknown_origin=unknown,
        )
        decision = self._router.route(
            signal,
            source_zone=source_zone,
            zones=self._zones,
            zone_index=self._zone_index,
        )
        trace: TickTrace = self._substrate.tick()

        self._routes_total += 1
        if decision.allowed:
            self._routes_allowed += 1
        if signal.tier == SignalTier.HOSTILE:
            self._hostile_ticks += 1
        elif signal.tier == SignalTier.SHADOW:
            self._shadow_ticks += 1

        return TheaterSpacetimeResult(
            signal_tier=signal.tier.value,
            source_zone=source_zone,
            target_zone=decision.target_zone,
            route_action=decision.action,
            route_allowed=decision.allowed,
            intelligence_target=decision.intelligence_target,
            quarantined_agents=list(trace.quarantined),
            substrate_tick=trace.tick,
        )

    def week_summary(self) -> Dict[str, Any]:
        return {
            "substrate_ticks": self._substrate.tick_count,
            "routes_total": self._routes_total,
            "routes_allowed": self._routes_allowed,
            "hostile_ticks": self._hostile_ticks,
            "shadow_ticks": self._shadow_ticks,
            "authority_state": "INTERNAL_RESEARCH",
            "claim_boundary": "repo_verified_architecture",
        }