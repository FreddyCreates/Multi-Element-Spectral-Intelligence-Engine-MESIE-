"""External-style benchmark comparisons — MQTT, vector RAG, cloud LLM baselines."""

from __future__ import annotations

import platform
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Sequence

import numpy as np

from data import list_references, load_reference_record
from mesie import match_records
from mesie.embeddings.vectorizers import SpectralVectorizer
from mesie.enterprise.fast_cycle import FastEnterpriseCycle
from mesie.evaluation.neuroswarm_audit import NeuroSwarmClaimsVerifier, _latency_stats
from mesie.io.loaders import load_record
from mesie.sdk.fast_compute import FastSpectralCompute
from mesie.swarm.hive_mind import HiveMindCoordinator


@dataclass
class ComparisonRow:
    system: str
    metric: str
    value_ms: float
    mesie_value_ms: float
    mesie_wins: bool
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExternalBenchmarkReport:
    version: str
    hardware: Dict[str, Any]
    comparisons: List[ComparisonRow]
    positioning: Dict[str, Any]
    gaps_named: List[str]
    tier1_ready: List[str]
    tier2_ready: List[str]
    latency: Dict[str, Any]
    overall: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "hardware": self.hardware,
            "comparisons": [c.to_dict() for c in self.comparisons],
            "positioning": self.positioning,
            "gaps_named": self.gaps_named,
            "tier1_ready": self.tier1_ready,
            "tier2_ready": self.tier2_ready,
            "latency": self.latency,
            "overall": self.overall,
        }


class ExternalBenchmarkPack:
    """Run MESIE vs documented third-party baselines on this machine."""

    VERSION = "1.0.0"

    def __init__(self, *, n_trials: int = 200) -> None:
        self.n_trials = n_trials
        self.refs = [load_reference_record(n) for n in list_references()]

    def _naive_vector_rag_ms(self) -> float:
        vec = SpectralVectorizer(n_bands=8)
        embs = [vec.transform(r) for r in self.refs]
        q = embs[0]
        samples = []
        for _ in range(self.n_trials):
            t0 = time.perf_counter()
            for e in embs:
                _ = float(np.dot(q, e) / (np.linalg.norm(q) * max(np.linalg.norm(e), 1e-12)))
            samples.append((time.perf_counter() - t0) * 1000)
        return _latency_stats(samples).p50_ms

    def _mesie_ann_ms(self) -> float:
        fc = FastSpectralCompute()
        fc.build_index(self.refs)
        q = self.refs[0]
        samples = []
        for _ in range(self.n_trials):
            t0 = time.perf_counter()
            fc.cosine_search(q, top_k=5)
            samples.append((time.perf_counter() - t0) * 1000)
        return _latency_stats(samples).p50_ms

    def _mesie_match_ms(self) -> float:
        a, b = self.refs[0], self.refs[1]
        samples = []
        for _ in range(self.n_trials):
            t0 = time.perf_counter()
            match_records(a, b)
            samples.append((time.perf_counter() - t0) * 1000)
        return _latency_stats(samples).p50_ms

    def run(self) -> ExternalBenchmarkReport:
        audit = NeuroSwarmClaimsVerifier(n_latency_trials=min(500, self.n_trials))
        threat = audit.benchmark_threat_response_fast_path()
        fast_ent = FastEnterpriseCycle()
        fast_ent.index_corpus(self.refs)
        ent_samples = []
        for _ in range(min(200, self.n_trials)):
            t0 = time.perf_counter()
            fast_ent.run(self.refs[0], candidate=self.refs[1])
            ent_samples.append((time.perf_counter() - t0) * 1000)
        ent_stats = _latency_stats(ent_samples)
        hive = HiveMindCoordinator(self.refs)
        hive_1k = hive.coordinate(self.refs[0], n_agents=1000)
        hive_10k = hive.coordinate(self.refs[0], n_agents=10000)

        naive_rag = self._naive_vector_rag_ms()
        mesie_ann = self._mesie_ann_ms()
        mesie_match = self._mesie_match_ms()

        comparisons = [
            ComparisonRow(
                "naive_python_vector_rag",
                "retrieval_p50",
                naive_rag,
                mesie_ann,
                mesie_ann < naive_rag,
                "Loop cosine over corpus vs FastSpectralCompute ANN",
            ),
            ComparisonRow(
                "typical_mqtt_broker_rtt",
                "round_trip_p50",
                25.0,
                threat.p50_ms,
                threat.p50_ms < 25.0,
                "Industry MQTT RTT ~10-50ms (documented); MESIE threat-fast local",
            ),
            ComparisonRow(
                "cloud_llm_tool_call",
                "agent_step_p50",
                800.0,
                ent_stats.p50_ms,
                ent_stats.p50_ms < 800.0,
                "Cloud LLM+tool round-trip ~500-2000ms; MESIE fast enterprise",
            ),
            ComparisonRow(
                "full_octopus_enterprise",
                "cycle_p50",
                637.0,
                ent_stats.p50_ms,
                ent_stats.p50_ms < 637.0,
                "Prior measured full Octopus vs new fast enterprise path",
            ),
            ComparisonRow(
                "centralized_swarm_coordinator",
                "10k_agents_ms_per_agent",
                0.5,
                hive_10k.ms_per_agent,
                hive_10k.ms_per_agent < 0.5,
                "Hive mind hierarchical routing vs naive centralized polling",
            ),
        ]

        positioning = {
            "reasoning_breadth": {
                "general_llm": "open-domain chat, massive training corpus",
                "mesie_solus": "spectral + formal SOLUS — specialized general within signal domains",
            },
            "tool_ecosystem": {
                "general_llm": "massive plugin marketplace",
                "mesie": "growing sovereign copilot tools + native CLI (20+ post-pro-update)",
            },
            "latency_posture": {
                "threat_fast_p50_ms": threat.p50_ms,
                "enterprise_fast_p50_ms": ent_stats.p50_ms,
                "enterprise_fast_sub_ms": ent_stats.p50_ms < 1.0,
                "threat_fast_sub_ms": threat.p50_ms < 1.0,
            },
        }

        gaps = [
            "Live RF/Schumann hardware ingest (CSV/UDP adapters shipped; coil/modem pending)",
            "Distributed P2P mesh between machines (LAN file-drop shipped; live sync pending)",
            "General open-domain language AI (SOLUS spectral+formal only)",
            "Production PyPI/Cloudflare hardened deploy",
            "Silicon hardware certification",
            "Independent third-party leaderboard submission",
        ]

        tier1 = [
            "Airgapped enterprise spectral copilot appliance",
            "Field Access API: bridge_to_field + route_field + CSV/UDP ingest",
        ]
        tier2 = [
            "Anchor calibration against Schumann/geomag libraries",
            "Sovereign mesh LAN peer export",
            "Hive mind 10K swarm coordination",
            "External benchmark pack for customer SLA trust",
        ]

        wins = sum(1 for c in comparisons if c.mesie_wins)
        overall = "mesie_competitive" if wins >= 4 else "mesie_partial"

        return ExternalBenchmarkReport(
            version=self.VERSION,
            hardware={
                "platform": platform.platform(),
                "processor": platform.processor() or platform.machine(),
            },
            comparisons=comparisons,
            positioning=positioning,
            gaps_named=gaps,
            tier1_ready=tier1,
            tier2_ready=tier2,
            latency={
                "threat_fast": threat.to_dict(),
                "enterprise_fast": ent_stats.to_dict(),
                "hive_1k": hive_1k.to_dict(),
                "hive_10k": {"ms_per_agent": hive_10k.ms_per_agent, "coordination_ms": hive_10k.coordination_ms},
                "mesie_match_p50": mesie_match,
                "mesie_ann_p50": mesie_ann,
            },
            overall=overall,
        )