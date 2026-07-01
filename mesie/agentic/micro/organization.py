"""NOVA micro organization — boot 70 careers across 12 teams."""

from __future__ import annotations

from typing import Dict, List, Optional

from mesie.agentic.micro.career import (
    CAREER_REGISTRY,
    NOVA_ORG_SIZE,
    TEAM_REGISTRY,
    MicroCareer,
    MicroTeam,
)
from mesie.agentic.micro.orchestrator import MicroOrchestrator
from mesie.agentic.micro.tasks import register_production_tasks


def all_careers() -> List[MicroCareer]:
    return list(CAREER_REGISTRY.keys())


def careers_for_team(team: MicroTeam) -> List[MicroCareer]:
    return list(TEAM_REGISTRY.get(team, []))


def boot_nova_organization(
    micro: MicroOrchestrator,
    *,
    satellite: bool = False,
    careers: Optional[List[MicroCareer]] = None,
) -> int:
    """Spawn full NOVA agentic organization."""
    register_production_tasks(micro)
    targets = careers or all_careers()
    for career in targets:
        if micro.agents_for_career(career):
            continue
        micro.spawn(career, satellite=satellite)
    return len(micro.satellites)


def activate_nova_organization(
    micro: MicroOrchestrator,
    *,
    careers: Optional[List[MicroCareer]] = None,
    staggered: bool = True,
) -> Dict[str, int]:
    """Activate timer loops for entire organization (or subset)."""
    import time

    from mesie.agentic.micro.task_tiers import TaskTier, tier_for

    register_production_tasks(micro)
    targets = careers or all_careers()
    for i, career in enumerate(targets):
        immediate = not staggered and tier_for(career) == TaskTier.LIGHT
        micro.ensure_satellite(career, immediate=immediate)
        if staggered and i % 10 == 9:
            time.sleep(0.05)
    status = micro.fleet_status()
    teams: Dict[str, int] = {}
    for agent in status["agents"]:
        spec = CAREER_REGISTRY[MicroCareer(agent["career"])]
        teams[spec.team.value] = teams.get(spec.team.value, 0) + 1
    return {
        "total": status["count"],
        "teams": teams,
        "expected": NOVA_ORG_SIZE,
    }


def organization_status(micro: MicroOrchestrator) -> Dict[str, object]:
    """Fleet status grouped by team with production metrics."""
    raw = micro.fleet_status()
    teams: Dict[str, Dict[str, object]] = {}
    pulsing = 0
    active_satellites = 0
    for agent in raw["agents"]:
        career = MicroCareer(agent["career"])
        spec = CAREER_REGISTRY[career]
        team = spec.team.value
        if team not in teams:
            teams[team] = {"count": 0, "pulsing": 0, "agents": []}
        teams[team]["count"] += 1
        if agent.get("cycles", 0) > 0:
            teams[team]["pulsing"] += 1
            pulsing += 1
        if agent.get("satellite_active"):
            active_satellites += 1
        teams[team]["agents"].append({
            "career": agent["career"],
            "title": agent["title"],
            "cycles": agent["cycles"],
            "coherence": agent["coherence"],
            "satellite_active": agent.get("satellite_active", False),
            "last_ok": (agent.get("last") or {}).get("result", {}).get("ok"),
        })
    return {
        "organization": "NOVA",
        "size": raw["count"],
        "expected": NOVA_ORG_SIZE,
        "pulsing": pulsing,
        "satellites_active": active_satellites,
        "teams": teams,
        "agents": raw["agents"],
        "ts": raw["ts"],
    }