"""Delay-tolerant store — contested comms buffer for swarm event replay."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

DTN_DIR = Path(__file__).resolve().parents[2] / "library" / "swarm_dtn"


@dataclass
class DTNBundle:
    bundle_id: str
    sender_id: str
    payload: Dict[str, Any]
    created_at: float
    ttl_s: float
    delivered: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "sender_id": self.sender_id,
            "payload": self.payload,
            "created_at": self.created_at,
            "ttl_s": self.ttl_s,
            "delivered": self.delivered,
        }


class DelayTolerantStore:
    """Store-and-forward for jammed/intermittent swarm links."""

    def __init__(self, store_dir: Optional[Path] = None) -> None:
        self.dir = store_dir or DTN_DIR
        self.dir.mkdir(parents=True, exist_ok=True)
        self._seq = 0

    def enqueue(self, sender_id: str, payload: Dict[str, Any], *, ttl_s: float = 300.0) -> DTNBundle:
        self._seq += 1
        bundle = DTNBundle(
            bundle_id=f"dtn-{self._seq:08d}",
            sender_id=sender_id,
            payload=payload,
            created_at=time.time(),
            ttl_s=ttl_s,
        )
        path = self.dir / f"{bundle.bundle_id}.json"
        path.write_text(json.dumps(bundle.to_dict()), encoding="utf-8")
        return bundle

    def dequeue(self, limit: int = 50) -> List[DTNBundle]:
        now = time.time()
        out: List[DTNBundle] = []
        for p in sorted(self.dir.glob("dtn-*.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            if now - data["created_at"] > data["ttl_s"]:
                p.unlink(missing_ok=True)
                continue
            if data.get("delivered"):
                continue
            bundle = DTNBundle(**{k: data[k] for k in ("bundle_id", "sender_id", "payload", "created_at", "ttl_s")})
            bundle.delivered = True
            p.write_text(json.dumps(bundle.to_dict()), encoding="utf-8")
            out.append(bundle)
            if len(out) >= limit:
                break
        return out

    def pending_count(self) -> int:
        return len(list(self.dir.glob("dtn-*.json")))