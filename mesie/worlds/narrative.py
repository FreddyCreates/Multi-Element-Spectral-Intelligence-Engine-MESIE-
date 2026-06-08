"""Operational narrative — system-internal mission log (real to the engine)."""

from __future__ import annotations

from typing import Any, Dict, List

from mesie.worlds.state import MissionWorldState, TickRecord


def tick_narrative(
    *,
    theater: str,
    campaign: str,
    day: int,
    hour: int,
    phase: str,
    doctrine: str,
    metrics: Dict[str, Any],
) -> str:
    jam = "JAMMED" if metrics.get("jam_ground") else "CLEAR"
    consensus = metrics.get("threat_consensus", "hold")
    ms = metrics.get("ms_per_agent", 0)
    agents = metrics.get("n_agents", 0)
    return (
        f"[THEATER {theater} | {campaign}] D+{day} T+{hour:02d}00Z | {phase} | "
        f"doctrine={doctrine} | RF={jam} | agents={agents} | consensus={consensus} | "
        f"coord={ms:.4f}ms/agent | mission_ok={metrics.get('mission_ok')}"
    )


def week_narrative_md(state: MissionWorldState, hierarchy_label: str) -> str:
    lines = [
        f"# Mission World Narrative — {hierarchy_label}",
        "",
        f"**Theater:** {state.theater}",
        f"**Campaign:** {state.campaign}",
        f"**Operational mode:** {state.operational_mode} (engine treats ticks as live ops)",
        f"**Sim span:** Day 1–{state.sim_day}, {len(state.ticks)} ticks",
        f"**Peak agents:** {state.agents_deployed_peak}",
        f"**Cumulative attrition:** {state.attrition_cumulative:.1%}",
        "",
        "## Day-by-day operational log",
        "",
    ]
    by_day: Dict[int, List[TickRecord]] = {}
    for t in state.ticks:
        by_day.setdefault(t.sim_day, []).append(t)

    for day in sorted(by_day.keys()):
        ticks = by_day[day]
        op = ticks[0].operation_id if ticks else "—"
        lines.append(f"### Day {day} — {ticks[0].phase if ticks else op}")
        lines.append("")
        for t in ticks:
            status = "OK" if t.ok else "DEGRADED"
            lines.append(f"- **T+{t.sim_hour:02d}00** [{status}] {t.narrative}")
        lines.append("")

    ok_n = sum(1 for t in state.ticks if t.ok)
    lines.extend([
        "## Findings",
        "",
        f"- Ticks OK: **{ok_n}/{len(state.ticks)}**",
        f"- Jam peak level: **{state.jam_level:.0%}**",
        f"- Operations completed: **{state.operations_completed}**",
        "",
        "*This narrative is generated from engine state — not marketing copy.*",
    ])
    return "\n".join(lines)