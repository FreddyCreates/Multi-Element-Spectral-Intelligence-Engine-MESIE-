"""Week-long mission world engine — real data, hierarchical ops, live-to-system clock."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from data import load_reference_record
from mesie.scenarios.catalog import enterprise_scenarios
from mesie.scenarios.simulator import ScenarioSimulator
from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator
from mesie.swarm.mission_planner import SwarmMissionPlanner
from mesie.library.domain_corpus import load_domain_corpus
from mesie.worlds.hierarchy import WorldHierarchy, load_world
from mesie.worlds.narrative import tick_narrative, week_narrative_md
from mesie.worlds.state import MissionWorldState, TickRecord


@dataclass
class WeekWorldReport:
    world_id: str
    days_simulated: int
    ticks_total: int
    ticks_ok: int
    peak_agents: int
    state_path: str
    narrative_path: str
    findings: List[str]
    enterprise_parallels: List[Dict[str, Any]]
    ok: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MissionWorldWeekEngine:
    """Run a full week; each tick uses real reference data and updates world state."""

    def __init__(self, world: Optional[WorldHierarchy] = None) -> None:
        self.world = world or load_world()
        self._corpus = load_domain_corpus(["defense", "libraries"])
        self._coord = DecentralizedSwarmCoordinator(self._corpus)
        self._planner = SwarmMissionPlanner(self._corpus)
        self._scenario_sim = ScenarioSimulator()

    def _run_tick(
        self,
        state: MissionWorldState,
        op,
        tick_idx: int,
    ) -> TickRecord:
        primary = load_reference_record(op.primary_data)
        secondary = load_reference_record(op.secondary_data) if op.secondary_data else None
        query = secondary if op.jam_ground and secondary else primary

        mission = self._planner.execute_mission(
            query,
            preset_id=op.preset,
            n_agents=op.n_agents,
            jam_ground=op.jam_ground,
            attrition_rate=op.attrition_rate,
        )
        coord = self._coord.coordinate(
            primary,
            n_agents=op.n_agents,
            jam_ground=op.jam_ground,
            attrition_rate=op.attrition_rate,
            cluster_optimized=True,
        )

        if op.jam_ground:
            state.jam_level = max(state.jam_level, 0.3 + 0.1 * op.day)
        state.attrition_cumulative = min(0.95, state.attrition_cumulative + op.attrition_rate * 0.15)
        state.agents_deployed_peak = max(state.agents_deployed_peak, op.n_agents)
        if mission.ok:
            state.operations_completed += 1

        metrics = {
            "mission_ok": mission.ok,
            "threat_consensus": mission.threat_consensus,
            "ms_per_agent": coord.ms_per_agent,
            "jam_ground": op.jam_ground,
            "n_agents": op.n_agents,
            "jam_failover_ok": coord.jamming_failover_ok,
        }
        hour = tick_idx * (24 // self.world.ticks_per_day)
        nar = tick_narrative(
            theater=state.theater,
            campaign=state.campaign,
            day=op.day,
            hour=hour,
            phase=op.phase,
            doctrine=op.doctrine,
            metrics=metrics,
        )
        ok = mission.ok and coord.ok and (not op.jam_ground or coord.jamming_failover_ok)
        return TickRecord(
            sim_day=op.day,
            tick=tick_idx,
            sim_hour=hour,
            operation_id=op.id,
            phase=op.phase,
            threat_consensus=mission.threat_consensus,
            ms_per_agent=coord.ms_per_agent,
            jam_active=op.jam_ground,
            attrition_cumulative=state.attrition_cumulative,
            agents_active=int(op.n_agents * (1 - state.attrition_cumulative)),
            narrative=nar,
            ok=ok,
        )

    def run_week(self, *, days: int = 7) -> tuple[MissionWorldState, WeekWorldReport]:
        t0 = time.perf_counter()
        w = self.world
        state = MissionWorldState(
            world_id=w.world_id,
            theater=w.theater,
            campaign=w.campaign,
            mission_clock_started=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            operational_mode="LIVE_SIM" if w.sim_mission_real_to_system else "DRILL",
        )
        enterprise_runs: List[Dict[str, Any]] = []

        for day in range(1, min(days, 7) + 1):
            op = w.operation_for_day(day)
            if not op:
                continue
            for tick in range(w.ticks_per_day):
                rec = self._run_tick(state, op, tick)
                state.ticks.append(rec)
                state.advance_hour(24 // w.ticks_per_day)
            if op.enterprise_parallel:
                ent_spec = next(
                    (s for s in enterprise_scenarios() if s["id"] == op.enterprise_parallel),
                    None,
                )
                if ent_spec:
                    ent_rep = self._scenario_sim.run_enterprise(ent_spec)
                    enterprise_runs.append(ent_rep.to_dict())

        state_path = state.save()
        from pathlib import Path

        nar_path = Path(__file__).resolve().parents[2] / "deliverables" / "mission_worlds" / f"{w.world_id}_narrative.md"
        nar_path.parent.mkdir(parents=True, exist_ok=True)
        nar_path.write_text(week_narrative_md(state, w.label), encoding="utf-8")

        ticks_ok = sum(1 for t in state.ticks if t.ok)
        findings = [
            f"Week sim: {ticks_ok}/{len(state.ticks)} ticks operational OK",
            f"Peak theater agents: {state.agents_deployed_peak}",
            f"Day 6 10K surge ms/agent: {next((t.ms_per_agent for t in state.ticks if '10k' in t.operation_id), 0):.4f}",
            f"Jam escalation peak: {state.jam_level:.0%}",
            f"Enterprise parallels run: {len(enterprise_runs)}",
        ]

        report = WeekWorldReport(
            world_id=w.world_id,
            days_simulated=days,
            ticks_total=len(state.ticks),
            ticks_ok=ticks_ok,
            peak_agents=state.agents_deployed_peak,
            state_path=str(state_path),
            narrative_path=str(nar_path),
            findings=findings,
            enterprise_parallels=enterprise_runs,
            ok=ticks_ok >= len(state.ticks) * 0.85,
        )
        return state, report