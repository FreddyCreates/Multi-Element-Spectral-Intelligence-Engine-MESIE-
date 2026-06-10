"""Paper 04 evaluation — routing, containment, latency, failure modes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from mesie.spacetime.signals import SignalTier, classify_signal
from mesie.spacetime.substrate import SimulatedSpacetimeSubstrate
from mesie.spacetime.zones import default_zones, route_allowed


@dataclass
class EvalCase:
    name: str
    passed: bool
    detail: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_spacetime_eval(*, ticks: int = 24) -> Dict[str, Any]:
    cases: List[EvalCase] = []

    coop = classify_signal(
        signal_id="t1", source_agent="r1", payload_kind="resident",
        trust_score=0.9,
    )
    cases.append(EvalCase(
        "cooperative_routes_operational",
        coop.tier == SignalTier.COOPERATIVE and coop.route_hint == "operational_route",
        coop.tier.value,
    ))

    hostile = classify_signal(
        signal_id="t2", source_agent="x1", payload_kind="threat",
        trust_score=0.05, adversary_flag=True,
    )
    cases.append(EvalCase(
        "hostile_tier_quarantine_hint",
        hostile.tier == SignalTier.HOSTILE and hostile.route_hint == "quarantine_or_drop",
        hostile.tier.value,
    ))

    shadow = classify_signal(
        signal_id="t3", source_agent="h1", payload_kind="honeypot",
        trust_score=0.4, unknown_origin=True,
    )
    cases.append(EvalCase(
        "shadow_tier_inspect",
        shadow.tier == SignalTier.SHADOW,
        shadow.route_hint,
    ))

    z = default_zones()[2]
    cases.append(EvalCase(
        "zone_blocks_hostile_in_buffer",
        not route_allowed(z, SignalTier.HOSTILE) and route_allowed(z, SignalTier.SHADOW),
        z.zone_id,
    ))

    substrate = SimulatedSpacetimeSubstrate()
    report = substrate.run(ticks=ticks)
    cases.append(EvalCase(
        "simulation_containment",
        report.containment_ok,
        f"quarantine_events={report.quarantine_events}",
    ))
    cases.append(EvalCase(
        "simulation_latency",
        report.mean_tick_ms < 500.0,
        f"mean_tick_ms={report.mean_tick_ms}",
    ))
    cases.append(EvalCase(
        "routing_volume",
        report.routes_total >= ticks,
        f"routes={report.routes_total}",
    ))

    passed = sum(1 for c in cases if c.passed)
    return {
        "authority_state": "INTERNAL_RESEARCH",
        "claim_boundary": "repo_verified_architecture",
        "design_posture": "experimental_framework_not_production_security",
        "passed": passed,
        "total": len(cases),
        "ready": passed == len(cases),
        "cases": [c.to_dict() for c in cases],
        "simulation": report.to_dict(),
    }