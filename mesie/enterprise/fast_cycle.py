"""Fast enterprise cycle — agentic path without full Octopus overhead."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence

from mesie import match_records, validate_record
from mesie.enterprise.agent_memory import EnterpriseAgentMemory
from mesie.io.loaders import RecordInput, load_record
from mesie.sdk.fast_compute import FastSpectralCompute
from mesie.sovereign.field_access import get_field_access_engine


@dataclass
class FastEnterpriseReport:
    latency_ms: float
    neighbors: List[Dict[str, Any]]
    match_score: float
    field_coherence: float
    memory_hits: int
    threat: bool
    sla_fast_ms: float
    sla_ok: bool
    path: str = "enterprise_fast"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FastEnterpriseCycle:
    """Validate → ANN → match → memory recall → field bridge — no movement/control arms."""

    def __init__(self, *, sla_fast_ms: float = 5.0) -> None:
        self.sla_fast_ms = sla_fast_ms
        self.fc = FastSpectralCompute()
        self.memory = EnterpriseAgentMemory()
        self.fa = get_field_access_engine()
        self._indexed = False

    def index_corpus(self, records: Sequence[RecordInput]) -> int:
        n = self.fc.build_index(records)
        self.memory.index_corpus(records)
        self._indexed = True
        return n

    def run(
        self,
        record: RecordInput,
        *,
        candidate: Optional[RecordInput] = None,
        session_id: str = "fast-enterprise",
    ) -> FastEnterpriseReport:
        if not self._indexed:
            raise RuntimeError("Call index_corpus() first")
        q = load_record(record)
        cand = load_record(candidate) if candidate else q
        t0 = time.perf_counter()
        validate_record(q)
        hits = self.fc.cosine_search(q, top_k=3)
        score = match_records(q, cand).composite_score
        recall = self.memory.recall(q, top_k=3, session_id=session_id)
        br = self.fa.bridge(q)
        ms = (time.perf_counter() - t0) * 1000
        neighbors = [{"id": h[0], "score": round(h[1], 4)} for h in hits]
        return FastEnterpriseReport(
            latency_ms=round(ms, 4),
            neighbors=neighbors,
            match_score=round(score, 4),
            field_coherence=round(br.field_coherence, 4),
            memory_hits=len(recall.get("corpus_hits", [])),
            threat=score >= 0.5,
            sla_fast_ms=self.sla_fast_ms,
            sla_ok=ms <= self.sla_fast_ms,
        )