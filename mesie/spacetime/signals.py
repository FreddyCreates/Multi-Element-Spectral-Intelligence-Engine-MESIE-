"""Three-tier signal classification — Paper 04 cooperative / hostile / shadow."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class SignalTier(str, Enum):
    COOPERATIVE = "cooperative"
    HOSTILE = "hostile"
    SHADOW = "shadow"


@dataclass
class ClassifiedSignal:
    signal_id: str
    tier: SignalTier
    source_agent: str
    payload_kind: str
    confidence: float
    route_hint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "tier": self.tier.value,
            "source_agent": self.source_agent,
            "payload_kind": self.payload_kind,
            "confidence": round(self.confidence, 4),
            "route_hint": self.route_hint,
        }


def classify_signal(
    *,
    signal_id: str,
    source_agent: str,
    payload_kind: str,
    trust_score: float,
    adversary_flag: bool = False,
    unknown_origin: bool = False,
) -> ClassifiedSignal:
    """Bounded tier classifier — design proposal, not production EW classifier."""
    if adversary_flag or trust_score < 0.2:
        tier = SignalTier.HOSTILE
        hint = "quarantine_or_drop"
    elif unknown_origin or 0.2 <= trust_score < 0.55:
        tier = SignalTier.SHADOW
        hint = "inspect_and_isolate"
    else:
        tier = SignalTier.COOPERATIVE
        hint = "operational_route"

    return ClassifiedSignal(
        signal_id=signal_id,
        tier=tier,
        source_agent=source_agent,
        payload_kind=payload_kind,
        confidence=max(0.0, min(1.0, trust_score if tier == SignalTier.COOPERATIVE else 1.0 - trust_score)),
        route_hint=hint,
    )