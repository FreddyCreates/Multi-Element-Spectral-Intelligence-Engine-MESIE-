"""Event-driven mesh gossip — low-bandwidth peer updates for swarm nodes."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class GossipEnvelope:
    sender_id: str
    seq: int
    threat: bool
    route_id: str
    score: float
    cluster_id: str
    payload_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "seq": self.seq,
            "threat": self.threat,
            "route_id": self.route_id,
            "score": self.score,
            "cluster_id": self.cluster_id,
            "payload_hash": self.payload_hash,
        }


@dataclass
class MeshGossipBus:
    """In-process event bus simulating ad-hoc peer exchange (no internet)."""

    fanout: int = 8
    _seq: int = 0
    _inbox: List[GossipEnvelope] = field(default_factory=list)
    _seen: Set[str] = field(default_factory=set)

    def publish(self, envelope: GossipEnvelope) -> int:
        key = f"{envelope.sender_id}:{envelope.seq}:{envelope.payload_hash}"
        if key in self._seen:
            return 0
        self._seen.add(key)
        self._inbox.append(envelope)
        return 1

    def fanout_publish(
        self,
        sender_id: str,
        *,
        threat: bool,
        route_id: str,
        score: float,
        cluster_id: str,
        n_peers: int,
    ) -> List[GossipEnvelope]:
        self._seq += 1
        payload_hash = hashlib.sha256(
            f"{sender_id}:{threat}:{route_id}:{score}".encode()
        ).hexdigest()[:12]
        env = GossipEnvelope(
            sender_id=sender_id,
            seq=self._seq,
            threat=threat,
            route_id=route_id,
            score=score,
            cluster_id=cluster_id,
            payload_hash=payload_hash,
        )
        delivered = []
        for _ in range(min(self.fanout, n_peers)):
            if self.publish(env):
                delivered.append(env)
        return delivered

    def drain(self, limit: int = 100) -> List[GossipEnvelope]:
        batch = self._inbox[:limit]
        self._inbox = self._inbox[limit:]
        return batch

    def bandwidth_bytes_estimate(self, n_messages: int) -> int:
        """Compressed spectral gossip — ~48 bytes per event envelope."""
        return n_messages * 48