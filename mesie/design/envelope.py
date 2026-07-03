"""Reality Engine envelope — seals design briefs across cores and protocols."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

PHI = 0.6180339887498948
PROTOCOL = "MESIE-REALITY-ENGINE-ENVELOPE/1.0"
ROOT = Path(__file__).resolve().parents[2]
REALITY_FEED = ROOT / "deliverables" / "design" / "REALITY_ENGINE_FEED.jsonl"


@dataclass
class RealityEngineEnvelope:
    agent_id: str
    core_id: str
    brief: Dict[str, Any] = field(default_factory=dict)
    paradigm_id: Optional[str] = None
    language_id: Optional[str] = None
    protocol_ids: List[str] = field(default_factory=list)
    envelope_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prior_hash: Optional[str] = None

    def body_hash(self) -> str:
        body = json.dumps(
            {"core_id": self.core_id, "brief": self.brief, "paradigm_id": self.paradigm_id},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(body.encode()).hexdigest()

    def seal(self) -> Dict[str, Any]:
        rec = {
            "protocol": PROTOCOL,
            "envelope_id": self.envelope_id,
            "agent_id": self.agent_id,
            "core_id": self.core_id,
            "paradigm_id": self.paradigm_id,
            "language_id": self.language_id,
            "protocol_ids": self.protocol_ids,
            "brief": self.brief,
            "phi_route": PHI,
            "body_hash": self.body_hash(),
            "prior_hash": self.prior_hash,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        REALITY_FEED.parent.mkdir(parents=True, exist_ok=True)
        with REALITY_FEED.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
        return rec

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RealityEngineEnvelope":
        return cls(
            agent_id=str(data.get("agent_id", "reality-agent")),
            core_id=str(data["core_id"]),
            brief=dict(data.get("brief") or {}),
            paradigm_id=data.get("paradigm_id"),
            language_id=data.get("language_id"),
            protocol_ids=list(data.get("protocol_ids") or []),
            envelope_id=str(data.get("envelope_id", uuid.uuid4())),
            prior_hash=data.get("prior_hash"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
