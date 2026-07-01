"""MAQUE envelope — Python mirror of Nova internal protocol (v0.13.0)."""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

PHI = 1.618033988749895
PHI_INV = 0.6180339887498949
PHI_BEAT_MS = 873
VERSION = "0.13.0"

FIB = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]


def fib_seq(n: int) -> int:
    if n < len(FIB):
        return FIB[n]
    a, b = FIB[-2], FIB[-1]
    for _ in range(len(FIB), n + 1):
        a, b = b, a + b
    return b


FLOS: Dict[str, List[str]] = {
    "THINK": ["ANIM", "LING", "MEMO"],
    "BUILD": ["FABR", "NMIN", "NEXU"],
    "SPEAK": ["LING", "MEMO", "NMIN"],
    "TRUTH": ["VERI", "PROP", "ANIM"],
    "NOVMINI": ["NMIN", "LING", "MEMO"],
}


@dataclass
class Vivi:
    id: str
    born: float
    agents: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)
    coherence: float = PHI_INV
    depth: int = 0
    alive: bool = True

    @classmethod
    def spawn(cls, initiator: str = "NMIN") -> "Vivi":
        return cls(
            id=f"VIVI-{initiator}-{uuid.uuid4().hex[:8]}",
            born=time.time(),
            agents=[initiator],
        )

    def advance(self, agent: str, apex_id: str) -> "Vivi":
        return Vivi(
            id=self.id,
            born=self.born,
            agents=self.agents + [agent],
            history=self.history + [apex_id],
            coherence=(self.coherence + PHI_INV) / PHI,
            depth=self.depth + 1,
            alive=True,
        )

    def close(self) -> "Vivi":
        return Vivi(
            id=self.id,
            born=self.born,
            agents=self.agents,
            history=self.history,
            coherence=self.coherence,
            depth=self.depth,
            alive=False,
        )


def apex(
    *,
    apex_type: str,
    sender: str,
    flos_path: str,
    vivi_id: str,
    seq_index: int = 0,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    seq = fib_seq(seq_index)
    ts = int(time.time() * 1000)
    apex_id = f"APEX-{sender}-F{seq}-{ts}"
    core = {"id": apex_id, "type": apex_type, "from": sender, "flos": flos_path, "payload": payload or {}, "ts": ts}
    sig = hashlib.sha256((json.dumps(core, sort_keys=True) + str(PHI_INV)).encode()).hexdigest()[:16]
    return {
        "apex": {
            **core,
            "vivi": vivi_id,
            "seq": seq,
            "phi": PHI_INV,
            "signature": sig,
        }
    }


def message(
    *,
    sender: str,
    receiver: str,
    verb: str,
    via: str,
    vivi: Optional[Vivi] = None,
    seq_index: int = 0,
    body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    ts = int(time.time() * 1000)
    seq = fib_seq(seq_index)
    phi_aligned = round(ts / PHI_BEAT_MS) * PHI_BEAT_MS
    return {
        "maque": {
            "version": VERSION,
            "from": sender,
            "to": receiver,
            "verb": verb,
            "via": via,
            "vivi": vivi.id if vivi else None,
            "phi": phi_aligned,
            "seq": seq,
            "ts": ts,
            "body": body or {},
        }
    }


Handler = Callable[[Dict[str, Any], Vivi], Dict[str, Any]]


def route(
    msg: Dict[str, Any],
    vivi: Vivi,
    handlers: Dict[str, Handler],
) -> Dict[str, Any]:
    """Walk a FLOS pathway, invoking registered QUAD handlers."""
    via = msg["maque"]["via"]
    pathway = FLOS.get(via, [])
    results: List[Dict[str, Any]] = []
    live = vivi
    current = msg

    for quad in pathway:
        handler = handlers.get(quad)
        if not handler:
            continue
        out = handler(current, live)
        results.append({"quad": quad, "result": out.get("result", {})})
        live = out.get("vivi", live)
        if out.get("response"):
            current = out["response"]

    return {"results": results, "vivi": live, "final": current}