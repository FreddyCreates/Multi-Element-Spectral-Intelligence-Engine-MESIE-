"""Full scenario simulation — real reference data → mission/enterprise pipeline."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from data import load_enterprise_benchmark, load_library, load_reference_record
from mesie import match_records
from mesie.enterprise.fast_cycle import FastEnterpriseCycle
from mesie.evaluation.neuroswarm_audit import NeuroSwarmClaimsVerifier
from mesie.library.domain_corpus import load_domain_corpus
from mesie.scenarios.catalog import enterprise_scenarios, load_catalog, military_scenarios
from mesie.sdk.fast_compute import FastSpectralCompute
from mesie.sovereign.field_access import get_field_access_engine


@dataclass
class ScenarioRunReport:
    scenario_id: str
    label: str
    domain: str
    doctrine: str
    data_sources: List[str]
    ok: bool
    metrics: Dict[str, Any]
    criteria_results: Dict[str, bool]
    elapsed_ms: float
    plain_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScenarioSimulator:
    """Run military drone or enterprise civilian scenarios on real bundled data."""

    def __init__(self) -> None:
        self._corpus = load_domain_corpus()
        self._fc = FastSpectralCompute()
        self._fc.build_index(self._corpus)
        self._fast = FastEnterpriseCycle()
        self._fast.index_corpus(self._corpus)
        self._fa = get_field_access_engine()

    def _resolve_records(self, spec: Dict[str, Any]) -> tuple[List[str], Any, Optional[Any]]:
        sources: List[str] = []
        primary = load_reference_record(spec["primary_data"])
        sources.append(f"reference:{spec['primary_data']}")
        secondary = None
        if spec.get("secondary_data"):
            secondary = load_reference_record(spec["secondary_data"])
            sources.append(f"reference:{spec['secondary_data']}")
        for lib in spec.get("library_refs", []):
            data = load_library(lib)
            sources.append(f"library:{lib} ({data.get('source', 'bundled')})")
        return sources, primary, secondary

    def _library_signal_hz(self, spec: Dict[str, Any]) -> Optional[float]:
        sig = spec.get("library_signal")
        if not sig or not spec.get("library_refs"):
            return None
        lib_name = spec["library_refs"][0]
        data = load_library(lib_name)
        parts = sig.split(".")
        node = data
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            elif isinstance(node, dict) and "constellations" in node:
                node = node["constellations"].get(p, node.get(p))
            else:
                return None
        if isinstance(node, dict) and "center_frequency_Hz" in node:
            return float(node["center_frequency_Hz"])
        if isinstance(node, dict) and "signals" in node:
            first = next(iter(node["signals"].values()), {})
            return float(first.get("center_frequency_Hz", 0)) or None
        return None

    def _check_criteria(self, criteria: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        for key, val in criteria.items():
            if key == "mission_ok":
                results[key] = bool(metrics.get("mission_ok"))
            elif key == "coordination_ok":
                results[key] = bool(metrics.get("coord_ok"))
            elif key == "jam_failover_or_orbital":
                results[key] = bool(metrics.get("jam_failover_ok") or metrics.get("access_orbital"))
            elif key == "ms_per_agent_max":
                results[key] = metrics.get("ms_per_agent", 999) <= val
            elif key == "threat_fast_p50_max_ms":
                results[key] = metrics.get("threat_fast_p50_ms", 999) <= val
            elif key == "e2e_p50_max_ms":
                results[key] = metrics.get("e2e_p50_ms", 999) <= val
            elif key == "spectral_match_min":
                results[key] = metrics.get("match_score", 0) >= val
            elif key == "route_ok":
                results[key] = bool(metrics.get("route_ok"))
            elif key == "tasks_allocated_min":
                results[key] = metrics.get("tasks_allocated", 0) >= val
            elif key == "platform_commands_min":
                results[key] = metrics.get("platform_commands", 0) >= val
            elif key == "formation_ok":
                results[key] = bool(metrics.get("formation_ok"))
            elif key == "consensus_required":
                results[key] = metrics.get("threat_consensus") not in (None, "", "hold")
            elif key == "enterprise_fast_sla_ms":
                results[key] = metrics.get("enterprise_fast_ms", 999) <= val
            elif key == "anomaly_separation_min":
                results[key] = metrics.get("anomaly_separation", 0) >= val
            elif key == "cross_match_score_max":
                results[key] = metrics.get("cross_match_score", 1) <= val
            elif key == "match_ok":
                results[key] = metrics.get("match_score", 0) > 0
            elif key == "field_coherence_min":
                results[key] = metrics.get("field_coherence", 0) >= val
            elif key == "cross_match_score_range":
                lo, hi = val
                s = metrics.get("cross_match_score", 0)
                results[key] = lo <= s <= hi
            elif key == "sovereign":
                results[key] = bool(metrics.get("sovereign"))
            elif key == "mission_or_coord_ok":
                results[key] = bool(metrics.get("mission_ok") or metrics.get("coord_ok"))
            elif key == "task_coverage_min":
                results[key] = metrics.get("task_coverage", 0) >= val
            elif key == "library_loaded":
                results[key] = bool(metrics.get("library_loaded"))
            elif key == "ann_top_k_ok":
                results[key] = len(metrics.get("ann_neighbors", [])) >= 1
            else:
                results[key] = True
        return results

    def run_military(self, spec: Dict[str, Any]) -> ScenarioRunReport:
        t0 = time.perf_counter()
        sources, primary, secondary = self._resolve_records(spec)
        query = primary
        if secondary and spec.get("jam_ground"):
            query = secondary

        from mesie.swarm.drone_coordination import DecentralizedSwarmCoordinator
        from mesie.swarm.mission_planner import SwarmMissionPlanner

        corpus = load_domain_corpus(["defense", "libraries"])
        coord = DecentralizedSwarmCoordinator(corpus)
        planner = SwarmMissionPlanner(corpus)

        preset = spec.get("preset", "ew")
        n = spec.get("n_agents", 500)
        jam = spec.get("jam_ground", False)
        attr = spec.get("attrition_rate", 0.05)

        mission = planner.execute_mission(
            query, preset_id=preset, n_agents=n, jam_ground=jam, attrition_rate=attr,
        )
        coord_rep = coord.coordinate(
            primary, n_agents=n, jam_ground=jam, attrition_rate=attr, cluster_optimized=True,
        )

        m_score = match_records(primary, secondary or primary)
        threat = NeuroSwarmClaimsVerifier(n_latency_trials=100).benchmark_threat_response_fast_path()
        lib_hz = self._library_signal_hz(spec)
        match_val = float(getattr(m_score, "composite_score", getattr(m_score, "score", 0.5)))

        metrics = {
            "mission_ok": mission.ok,
            "coord_ok": coord_rep.ok,
            "ms_per_agent": coord_rep.ms_per_agent,
            "e2e_p50_ms": coord_rep.e2e_p50_ms,
            "threat_consensus": mission.threat_consensus,
            "jam_failover_ok": coord_rep.jamming_failover_ok,
            "access_orbital": any(
                m in {"orbital_hz_ladder", "mixed"} for m in coord_rep.access_modes
            ),
            "tasks_allocated": mission.tasks_allocated,
            "platform_commands": mission.platform_commands,
            "formation_ok": mission.formation_ok,
            "route_ok": mission.route_ok,
            "match_score": match_val,
            "threat_fast_p50_ms": threat.p50_ms,
            "library_signal_hz": lib_hz,
            "spectral_score": mission.spectral_score,
            "coordination_ms": mission.coordination_ms,
        }

        criteria = self._check_criteria(spec.get("criteria", {}), metrics)
        ok = all(criteria.values())
        elapsed = (time.perf_counter() - t0) * 1000

        return ScenarioRunReport(
            scenario_id=spec["id"],
            label=spec["label"],
            domain="military_drone",
            doctrine=spec.get("doctrine", "defense"),
            data_sources=sources,
            ok=ok,
            metrics=metrics,
            criteria_results=criteria,
            elapsed_ms=round(elapsed, 2),
            plain_summary=(
                f"{spec['label']}: mission={mission.ok}, {coord_rep.ms_per_agent:.4f} ms/agent, "
                f"data={len(sources)} sources, pass={ok}"
            ),
        )

    def _enterprise_sample(self, use_case_id: str) -> Optional[Dict[str, Any]]:
        bench = load_enterprise_benchmark()
        for uc in bench.get("use_cases", []):
            if uc["use_case_id"] == use_case_id:
                return uc["samples"][0] if uc.get("samples") else None
        return None

    def run_enterprise(self, spec: Dict[str, Any]) -> ScenarioRunReport:
        t0 = time.perf_counter()
        sources, primary, secondary = self._resolve_records(spec)

        ent_rep = self._fast.run(primary, candidate=secondary or self._corpus[0])
        br = self._fa.bridge(primary)
        ann = self._fc.cosine_search(primary, top_k=5)

        cross_score = 0.5
        if secondary:
            m = match_records(primary, secondary)
            cross_score = float(getattr(m, "composite_score", getattr(m, "score", 0.5)))

        anomaly_sep = abs(cross_score - 0.5)
        threat = NeuroSwarmClaimsVerifier(n_latency_trials=50).benchmark_threat_response_fast_path()

        metrics: Dict[str, Any] = {
            "enterprise_fast_ms": ent_rep.latency_ms,
            "enterprise_sla_ok": ent_rep.sla_ok,
            "match_score": ent_rep.match_score,
            "field_coherence": br.field_coherence,
            "cross_match_score": cross_score,
            "anomaly_separation": anomaly_sep,
            "sovereign": br.sovereign,
            "threat_fast_p50_ms": threat.p50_ms,
            "ann_neighbors": ann,
            "library_loaded": bool(spec.get("library_refs")),
            "enterprise_benchmark_sample": spec.get("enterprise_use_case"),
        }

        bench_sample = self._enterprise_sample(spec.get("enterprise_use_case", ""))
        if bench_sample:
            sources.append(f"benchmark:{spec['enterprise_use_case']}/{bench_sample['sample_id']}")
            metrics["benchmark_class"] = bench_sample.get("class")

        if spec.get("preset"):
            from mesie.swarm.mission_planner import SwarmMissionPlanner
            from mesie.swarm.task_allocation import ParticleSwarmAllocator, SwarmTask

            planner = SwarmMissionPlanner(self._corpus)
            mission = planner.execute_mission(
                primary,
                preset_id=spec["preset"],
                n_agents=spec.get("n_agents", 64),
                jam_ground=spec.get("jam_ground", False),
                attrition_rate=spec.get("attrition_rate", 0.05),
            )
            metrics["mission_ok"] = mission.ok
            metrics["coord_ok"] = mission.ok
            tasks = [
                SwarmTask("scan", "scan", 0.9, np.array([50, 30, 10]), 0.85),
                SwarmTask("relay", "relay", 0.7, np.array([80, 50, 15]), 0.8),
            ]
            pso = ParticleSwarmAllocator().allocate(min(spec.get("n_agents", 64), 128), tasks)
            metrics["task_coverage"] = pso.coverage

        criteria = self._check_criteria(spec.get("criteria", {}), metrics)
        ok = all(criteria.values())
        elapsed = (time.perf_counter() - t0) * 1000

        return ScenarioRunReport(
            scenario_id=spec["id"],
            label=spec["label"],
            domain="enterprise_civilian",
            doctrine=spec.get("industry", "enterprise"),
            data_sources=sources,
            ok=ok,
            metrics=metrics,
            criteria_results=criteria,
            elapsed_ms=round(elapsed, 2),
            plain_summary=(
                f"{spec['label']}: enterprise_fast={ent_rep.latency_ms:.2f}ms, "
                f"industry={spec.get('industry')}, pass={ok}"
            ),
        )

    def run_all(self) -> Dict[str, Any]:
        mil = [self.run_military(s) for s in military_scenarios()]
        ent = [self.run_enterprise(s) for s in enterprise_scenarios()]
        mil_ok = sum(1 for r in mil if r.ok)
        ent_ok = sum(1 for r in ent if r.ok)
        return {
            "military": {
                "catalog": load_catalog("military_drone_scenarios"),
                "passed": mil_ok,
                "total": len(mil),
                "runs": [r.to_dict() for r in mil],
            },
            "enterprise": {
                "catalog": load_catalog("enterprise_civilian_scenarios"),
                "passed": ent_ok,
                "total": len(ent),
                "runs": [r.to_dict() for r in ent],
            },
            "all_pass": mil_ok == len(mil) and ent_ok == len(ent),
        }