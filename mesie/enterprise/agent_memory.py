"""Spectral agent memory for enterprise copilots — local RAG without third-party inference."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from mesie.io.loaders import RecordInput, load_record
from mesie.sdk.fast_compute import FastSpectralCompute


@dataclass
class AgentMemoryTurn:
    """One copilot turn stored as spectral memory."""

    turn_id: str
    session_id: str
    record_id: str
    neighbors: List[Dict[str, Any]]
    research_hits: List[str]
    technical_hits: List[str]
    solus_conclusion: str
    elapsed_ms: float
    sovereign: bool = True


@dataclass
class EnterpriseAgentMemory:
    """On-prem agent memory index — embed, recall, and audit copilot sessions."""

    max_turns: int = 512
    _turns: List[AgentMemoryTurn] = field(default_factory=list)
    _compute: FastSpectralCompute = field(default_factory=FastSpectralCompute)
    _indexed: bool = False

    def index_corpus(self, records: Sequence[RecordInput]) -> int:
        n = self._compute.build_index(records)
        self._indexed = True
        return n

    def store_turn(
        self,
        session_id: str,
        record: RecordInput,
        *,
        neighbors: List[Dict[str, Any]],
        research_hits: List[str],
        technical_hits: List[str],
        solus_conclusion: str,
        elapsed_ms: float,
    ) -> AgentMemoryTurn:
        rec = load_record(record)
        turn = AgentMemoryTurn(
            turn_id=f"{session_id}_{len(self._turns)}",
            session_id=session_id,
            record_id=rec.record_id,
            neighbors=neighbors,
            research_hits=research_hits,
            technical_hits=technical_hits,
            solus_conclusion=solus_conclusion,
            elapsed_ms=elapsed_ms,
        )
        self._turns.append(turn)
        if len(self._turns) > self.max_turns:
            self._turns = self._turns[-self.max_turns :]
        return turn

    def recall(self, record: RecordInput, *, top_k: int = 5, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Recall nearest corpus neighbors and prior session turns."""
        t0 = time.perf_counter()
        rec = load_record(record)
        corpus_hits: List[Dict[str, Any]] = []
        if self._indexed and self._compute._matrix is not None:
            for rid, sim in self._compute.cosine_search(rec, top_k=top_k):
                corpus_hits.append({"record_id": rid, "similarity": round(sim, 4), "source": "corpus"})

        session_turns = [t for t in self._turns if session_id is None or t.session_id == session_id]
        turn_hits: List[Dict[str, Any]] = []
        if session_turns and self._indexed:
            emb = self._compute.embed_one(rec)
            for turn in reversed(session_turns[-top_k * 2 :]):
                for n in turn.neighbors[:1]:
                    sim = float(n.get("similarity", 0))
                    turn_hits.append({
                        "turn_id": turn.turn_id,
                        "record_id": turn.record_id,
                        "similarity": sim,
                        "solus_conclusion": turn.solus_conclusion[:120],
                        "source": "session",
                    })
            turn_hits.sort(key=lambda x: -x["similarity"])
            turn_hits = turn_hits[:top_k]

        ms = (time.perf_counter() - t0) * 1000
        return {
            "ok": True,
            "record_id": rec.record_id,
            "corpus_hits": corpus_hits,
            "session_hits": turn_hits,
            "session_turns": len(session_turns),
            "latency_ms": round(ms, 2),
            "sovereign": True,
        }

    def session_summary(self, session_id: str) -> Dict[str, Any]:
        turns = [t for t in self._turns if t.session_id == session_id]
        if not turns:
            return {"session_id": session_id, "turns": 0, "sovereign": True}
        latencies = [t.elapsed_ms for t in turns]
        return {
            "session_id": session_id,
            "turns": len(turns),
            "mean_latency_ms": round(float(np.mean(latencies)), 2),
            "last_conclusion": turns[-1].solus_conclusion[:160],
            "sovereign": True,
        }