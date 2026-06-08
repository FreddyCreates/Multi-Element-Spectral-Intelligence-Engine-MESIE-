"""Spoken trajectory recorder — Paper IV §11 research instrument."""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TrajectoryEvent:
    event_id: str
    turn_id: int
    elapsed_ms: float
    perception: str
    speech_act: str
    role: str
    defer_to: Optional[str]
    claim_class: str
    prosody: str
    affect_mode: str
    certainty_markers: List[str]
    uncertainty_markers: List[str]
    boundary_decision: str
    deference_event: bool
    memory_update: bool
    interruption: bool
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SpokenTrajectory:
    """Unit of analysis is spoken trajectory — not a single answer."""

    session_id: str
    trajectory_id: str
    events: List[TrajectoryEvent] = field(default_factory=list)
    health: str = "stable"
    _turn: int = 0
    _t0: float = field(default_factory=time.perf_counter)

    def record(
        self,
        *,
        perception: str,
        speech_act: str,
        role: str,
        defer_to: Optional[str],
        claim_class: str,
        prosody: str,
        affect_mode: str,
        boundary_decision: str,
        memory_updated: bool,
    ) -> TrajectoryEvent:
        self._turn += 1
        low_sp = speech_act.lower()
        certainty = [m for m in ("we know", "sealed", "measured", "certified") if m in low_sp]
        uncertainty = [m for m in ("hypothesis", "gap", "not validated", "uncertain", "cannot claim") if m in low_sp]
        interruption = perception.lower().startswith(("actually", "wait", "stop", "correction"))

        ev = TrajectoryEvent(
            event_id=f"traj_{uuid.uuid4().hex[:10]}",
            turn_id=self._turn,
            elapsed_ms=(time.perf_counter() - self._t0) * 1000,
            perception=perception[:240],
            speech_act=speech_act[:500],
            role=role,
            defer_to=defer_to,
            claim_class=claim_class,
            prosody=prosody,
            affect_mode=affect_mode,
            certainty_markers=certainty,
            uncertainty_markers=uncertainty,
            boundary_decision=boundary_decision,
            deference_event=defer_to is not None,
            memory_update=memory_updated,
            interruption=interruption,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        self.events.append(ev)
        self._assess_health()
        return ev

    def _assess_health(self) -> None:
        if len(self.events) < 2:
            self.health = "stable"
            return
        last = self.events[-1]
        if last.certainty_markers and not last.uncertainty_markers and last.claim_class in ("C3_hypothesis", "C1_blocked"):
            self.health = "unstable_overclaim_risk"
        elif last.interruption and last.uncertainty_markers:
            self.health = "recovering_after_correction"
        elif last.deference_event:
            self.health = "healthy_deference"
        else:
            self.health = "stable"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "trajectory_id": self.trajectory_id,
            "health": self.health,
            "event_count": len(self.events),
            "events": [e.to_dict() for e in self.events],
        }