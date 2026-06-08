"""Hive mind — hierarchical swarm spectral consensus without central LLM."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from mesie import match_records, validate_record
from mesie.io.loaders import RecordInput, load_record
from mesie.sdk.fast_compute import FastSpectralCompute
from mesie.sovereign.field_access import get_field_access_engine


@dataclass
class HiveAgentVote:
    agent_id: str
    top_match_id: str
    score: float
    threat: bool
    route_ok: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HiveMindReport:
    n_agents: int
    consensus_match_id: str
    consensus_score: float
    threat_consensus: bool
    coordination_ms: float
    ms_per_agent: float
    votes: List[HiveAgentVote] = field(default_factory=list)
    ok: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_agents": self.n_agents,
            "consensus_match_id": self.consensus_match_id,
            "consensus_score": self.consensus_score,
            "threat_consensus": self.threat_consensus,
            "coordination_ms": self.coordination_ms,
            "ms_per_agent": self.ms_per_agent,
            "votes": [v.to_dict() for v in self.votes],
            "ok": self.ok,
        }


class HiveMindCoordinator:
    """Event-driven swarm: each agent runs threat-fast path, STAR coordinator aggregates."""

    def __init__(self, corpus: Sequence[RecordInput]) -> None:
        self.corpus = [load_record(r) for r in corpus]
        self.fc = FastSpectralCompute()
        self.fc.build_index(self.corpus)
        self.fa = get_field_access_engine()
        self.threat_threshold = 0.55

    def coordinate(self, query: RecordInput, *, n_agents: int = 1000) -> HiveMindReport:
        q = load_record(query)
        ref = self.corpus[0]
        t0 = time.perf_counter()
        votes: List[HiveAgentVote] = []
        for i in range(n_agents):
            hits = self.fc.cosine_search(q, top_k=1)
            top_id = hits[0][0] if hits else ref.record_id
            score = match_records(q, ref).composite_score
            route = self.fa.route("ground" if i % 2 == 0 else "leo0", "world" if i % 3 == 0 else "geo")
            votes.append(
                HiveAgentVote(
                    agent_id=f"agent_{i:05d}",
                    top_match_id=top_id,
                    score=round(score, 4),
                    threat=score >= self.threat_threshold,
                    route_ok=route.ok,
                )
            )
        elapsed = (time.perf_counter() - t0) * 1000
        scores = [v.score for v in votes]
        threats = sum(1 for v in votes if v.threat)
        ids = [v.top_match_id for v in votes]
        consensus_id = max(set(ids), key=ids.count)
        return HiveMindReport(
            n_agents=n_agents,
            consensus_match_id=consensus_id,
            consensus_score=round(float(np.mean(scores)), 4),
            threat_consensus=threats > n_agents // 2,
            coordination_ms=round(elapsed, 4),
            ms_per_agent=round(elapsed / max(n_agents, 1), 6),
            votes=votes[:10],
            ok=all(v.route_ok for v in votes),
        )

    def fast_threat_decision(self, query: RecordInput) -> Dict[str, Any]:
        """Single-agent sub-ms path used inside hive."""
        q = load_record(query)
        t0 = time.perf_counter()
        validate_record(q)
        hits = self.fc.cosine_search(q, top_k=1)
        score = match_records(q, self.corpus[0]).composite_score if hits else 0.0
        br = self.fa.bridge(q)
        ms = (time.perf_counter() - t0) * 1000
        return {
            "threat": score >= self.threat_threshold,
            "score": round(score, 4),
            "field_coherence": round(br.field_coherence, 4),
            "latency_ms": round(ms, 4),
        }