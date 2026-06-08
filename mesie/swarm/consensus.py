"""Lightweight edge consensus — gossip plurality, no central leader."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

import numpy as np


@dataclass
class ConsensusResult:
    decision: str
    confidence: float
    votes_for: int
    votes_against: int
    quorum_met: bool
    rounds: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "confidence": self.confidence,
            "votes_for": self.votes_for,
            "votes_against": self.votes_against,
            "quorum_met": self.quorum_met,
            "rounds": self.rounds,
        }


def gossip_consensus(
    votes: Sequence[bool],
    *,
    quorum_ratio: float = 0.51,
    neighbor_fanout: int = 8,
) -> ConsensusResult:
    """Plurality consensus over local agent votes — Raft-inspired but leaderless."""
    n = len(votes)
    if n == 0:
        return ConsensusResult("hold", 0.0, 0, 0, False, 0)

    arr = np.asarray(votes, dtype=np.int8)
    rounds = max(1, int(np.ceil(np.log2(max(n, 2)) / np.log2(max(neighbor_fanout, 2)))))
    active = arr.copy()
    for _ in range(rounds):
        pooled: List[int] = []
        for i in range(n):
            neighbors = [(i + k) % n for k in range(1, neighbor_fanout + 1)]
            pooled.append(int(np.round(np.mean(np.concatenate([[active[i]], active[neighbors]])))))
        active = np.asarray(pooled, dtype=np.int8)

    votes_for = int(np.sum(active))
    votes_against = n - votes_for
    quorum = votes_for / n >= quorum_ratio
    decision = "engage" if quorum else "hold"
    confidence = round(votes_for / n, 4)
    return ConsensusResult(
        decision=decision,
        confidence=confidence,
        votes_for=votes_for,
        votes_against=votes_against,
        quorum_met=quorum,
        rounds=rounds,
    )