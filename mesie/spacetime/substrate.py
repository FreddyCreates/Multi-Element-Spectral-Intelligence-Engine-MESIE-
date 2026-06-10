"""Simulated spacetime substrate — tick engine for agent placement and zone ops."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from mesie.spacetime.agents import SpatialAgent, default_agent_registry
from mesie.spacetime.forces import communication_reach, gravitational_influence, influence_matrix
from mesie.spacetime.routing import RouteDecision, SpacetimeRouter
from mesie.spacetime.signals import ClassifiedSignal, classify_signal
from mesie.spacetime.zones import Zone, default_zones, zone_for_agent


@dataclass
class TickTrace:
    tick: int
    agent_positions: Dict[str, List[float]]
    routes: List[Dict[str, Any]]
    quarantined: List[str]
    zone_occupancy: Dict[str, List[str]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SpacetimeReport:
    ticks_run: int
    routes_total: int
    routes_allowed: int
    quarantine_events: int
    containment_ok: bool
    mean_tick_ms: float
    traces: List[TickTrace]
    authority_state: str = "INTERNAL_RESEARCH"
    claim_boundary: str = "repo_verified_architecture"
    design_posture: str = "experimental_framework_not_production_security"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["traces"] = [t.to_dict() for t in self.traces]
        return d


class SimulatedSpacetimeSubstrate:
    """Paper 04 architecture — spatial embedding for agent coordination."""

    def __init__(
        self,
        agents: Optional[List[SpatialAgent]] = None,
        zones: Optional[List[Zone]] = None,
    ) -> None:
        self.agents = list(agents or default_agent_registry())
        self.zones = list(zones or default_zones())
        self._zone_index = {z.zone_id: z for z in self.zones}
        self._router = SpacetimeRouter()
        self._tick = 0

    @property
    def tick_count(self) -> int:
        return self._tick

    def _update_zones(self) -> Dict[str, List[str]]:
        occ: Dict[str, List[str]] = {z.zone_id: [] for z in self.zones}
        for a in self.agents:
            zid = zone_for_agent(a, self.zones)
            a.zone_id = zid
            if zid:
                occ[zid].append(a.agent_id)
        return occ

    def _emit_signals(self) -> List[ClassifiedSignal]:
        signals: List[ClassifiedSignal] = []
        for a in self.agents:
            if a.role in ("data_packet", "resident", "threat"):
                signals.append(
                    classify_signal(
                        signal_id=f"sig_{a.agent_id}_{self._tick}",
                        source_agent=a.agent_id,
                        payload_kind=a.role,
                        trust_score=a.trust_score,
                        adversary_flag=a.role == "threat",
                        unknown_origin=a.role == "honeypot",
                    )
                )
        return signals

    def _apply_forces(self, dt: float = 0.1) -> None:
        for a in self.agents:
            if a.quarantined or a.role in ("defensive", "honeypot"):
                continue
            force = np.zeros(3)
            for b in self.agents:
                if a.agent_id == b.agent_id:
                    continue
                if not communication_reach(a, b):
                    continue
                mag, direction = gravitational_influence(b, a)
                if b.role == "threat":
                    mag *= -1.2
                force += mag * np.array(direction)
            pos = np.array(a.position) + force * dt
            a.position = tuple(pos.tolist())  # type: ignore[assignment]
            a.velocity = tuple((force * dt).tolist())  # type: ignore[assignment]

    def _quarantine_hostile(self, decisions: List[RouteDecision]) -> int:
        count = 0
        qzone = next((z for z in self.zones if z.quarantine), None)
        for d in decisions:
            if d.action != "quarantine":
                continue
            agent = next((a for a in self.agents if a.agent_id in d.signal_id), None)
            if not agent:
                continue
            agent.quarantined = True
            agent.trust_score = 0.0
            if qzone:
                agent.position = qzone.center
                agent.zone_id = qzone.zone_id
            count += 1
        return count

    def tick(self) -> TickTrace:
        self._tick += 1
        self._apply_forces()
        occupancy = self._update_zones()
        signals = self._emit_signals()
        routes: List[RouteDecision] = []
        for sig in signals:
            src = next((a for a in self.agents if a.agent_id == sig.source_agent), None)
            src_zone = src.zone_id if src else ""
            routes.append(self._router.route(sig, source_zone=src_zone, zones=self.zones, zone_index=self._zone_index))
        self._quarantine_hostile(routes)
        return TickTrace(
            tick=self._tick,
            agent_positions={a.agent_id: list(a.position) for a in self.agents},
            routes=[r.to_dict() for r in routes],
            quarantined=[a.agent_id for a in self.agents if a.quarantined],
            zone_occupancy=occupancy,
        )

    def run(self, *, ticks: int = 20) -> SpacetimeReport:
        t0 = time.perf_counter()
        traces: List[TickTrace] = []
        routes_total = 0
        routes_allowed = 0
        quarantine_events = 0

        for _ in range(ticks):
            tr = self.tick()
            traces.append(tr)
            for r in tr.routes:
                routes_total += 1
                if r.get("allowed"):
                    routes_allowed += 1
            quarantine_events = max(quarantine_events, len(tr.quarantined))

        elapsed = (time.perf_counter() - t0) * 1000
        hostile_contained = all(
            a.quarantined or a.zone_id == "quarantine_hold" or a.role != "threat"
            for a in self.agents
            if a.role == "threat"
        )

        return SpacetimeReport(
            ticks_run=ticks,
            routes_total=routes_total,
            routes_allowed=routes_allowed,
            quarantine_events=quarantine_events,
            containment_ok=hostile_contained,
            mean_tick_ms=round(elapsed / max(ticks, 1), 4),
            traces=traces[-5:],
        )

    def influence_snapshot(self) -> Dict[str, Dict[str, float]]:
        return influence_matrix(self.agents)