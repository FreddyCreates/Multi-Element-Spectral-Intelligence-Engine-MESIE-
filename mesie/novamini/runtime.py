"""NOVAMINI runtime — MAQUE-routed sovereign speech on MESIE native LM."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.neuroai.auro.native_lm import AuroNativeLanguageModel, MODEL_ID as AURO_MODEL_ID
from mesie.novamini.maque import FLOS, Vivi, apex, message, route
from mesie.novamini.spectral_memory import SpectralMemory

try:
    from mesie.version_info import NOVAMINI_VERSION as VERSION
except ImportError:
    VERSION = "1.0.0"
MODEL_ID = "NOVAMINI-MESIE-LM-v0.1"
QUAD = "NMIN"


@dataclass
class NovaMiniResponse:
    spoken: str
    role: str
    claim_score: Dict[str, Any]
    loop_steps: List[str]
    maque: Dict[str, Any]
    apex: Dict[str, Any]
    memory_hits: List[Dict[str, Any]]
    latency_ms: float
    model_id: str = MODEL_ID
    native_lm: str = AURO_MODEL_ID
    sovereign: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spoken": self.spoken,
            "role": self.role,
            "claim_score": self.claim_score,
            "loop_steps": self.loop_steps,
            "maque": self.maque,
            "apex": self.apex,
            "memory_hits": self.memory_hits,
            "latency_ms": self.latency_ms,
            "model_id": self.model_id,
            "native_lm": self.native_lm,
            "sovereign": self.sovereign,
        }


@dataclass
class NovaMiniRuntime:
    """Lightweight Nova mini-runtime: MAQUE SPEAK pathway + MESIE-LM + spectral vault."""

    session_id: str = field(default_factory=lambda: f"novamini-{uuid.uuid4().hex[:10]}")
    vault_root: Optional[Path] = None
    lm: AuroNativeLanguageModel = field(init=False)
    memory: SpectralMemory = field(init=False)
    vivi: Vivi = field(init=False)
    _turn_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        root = self.vault_root or Path.cwd() / ".novamini_vault"
        self.lm = AuroNativeLanguageModel(session_id=self.session_id)
        self.memory = SpectralMemory(vault_dir=root / self.session_id)
        self.vivi = Vivi.spawn(QUAD)

    def status(self) -> Dict[str, Any]:
        lm_status = self.lm.status()
        return {
            "product": "NOVAMINI (MESIE-LM)",
            "version": VERSION,
            "model_id": MODEL_ID,
            "native_lm": AURO_MODEL_ID,
            "session_id": self.session_id,
            "quad": QUAD,
            "flos_pathways": list(FLOS.keys()),
            "third_party_inference": False,
            "turns": self._turn_count,
            "vivi": {
                "id": self.vivi.id,
                "depth": self.vivi.depth,
                "coherence": round(self.vivi.coherence, 4),
                "alive": self.vivi.alive,
            },
            "lm": lm_status,
            "memory": self.memory.status(),
        }

    def _handler_memo(self, msg: Dict[str, Any], vivi: Vivi) -> Dict[str, Any]:
        query = msg["maque"]["body"].get("text", "")
        hits = self.memory.recall(query)
        apex_id = apex(
            apex_type="memory.recall",
            sender="MEMO",
            flos_path=msg["maque"]["via"],
            vivi_id=vivi.id,
            seq_index=self._turn_count,
            payload={"hits": len(hits)},
        )["apex"]["id"]
        live = vivi.advance("MEMO", apex_id)
        return {"result": {"memory_hits": hits}, "vivi": live}

    def _handler_ling(self, msg: Dict[str, Any], vivi: Vivi) -> Dict[str, Any]:
        body = msg["maque"]["body"]
        user_text = body.get("text", "")
        memory_hits = body.get("memory_hits", [])
        context = ""
        if memory_hits:
            context = " | ".join(h["spoken"][:80] for h in memory_hits[:2])

        out = self.lm.generate(user_text, samgov_context=context)
        apex_id = apex(
            apex_type="speech.act",
            sender="LING",
            flos_path=msg["maque"]["via"],
            vivi_id=vivi.id,
            seq_index=self._turn_count,
            payload={"role": out.role, "trajectory": out.trajectory_id},
        )["apex"]["id"]
        live = vivi.advance("LING", apex_id)
        return {
            "result": {
                "spoken": out.spoken,
                "role": out.role,
                "claim_score": out.claim_score,
                "loop_steps": out.loop_steps,
                "defer_to": out.defer_to,
            },
            "vivi": live,
        }

    def _handler_nmin(self, msg: Dict[str, Any], vivi: Vivi) -> Dict[str, Any]:
        """NOVAMINI gate — packages ingress, no external routing."""
        apex_id = apex(
            apex_type="novamini.ingress",
            sender=QUAD,
            flos_path=msg["maque"]["via"],
            vivi_id=vivi.id,
            seq_index=self._turn_count,
            payload={"verb": msg["maque"]["verb"]},
        )["apex"]["id"]
        live = vivi.advance(QUAD, apex_id)
        return {"result": {"gate": "open"}, "vivi": live}

    def chat(self, user_text: str) -> NovaMiniResponse:
        """Full MAQUE NOVMINI pathway: NMIN → LING → MEMO (recall first via reorder in handlers)."""
        t0 = time.perf_counter()
        self._turn_count += 1

        # Phase 1: memory recall
        recall_msg = message(
            sender=QUAD,
            receiver="MEMO",
            verb="query",
            via="NOVMINI",
            vivi=self.vivi,
            seq_index=self._turn_count,
            body={"text": user_text},
        )
        memo_out = self._handler_memo(recall_msg, self.vivi)
        self.vivi = memo_out["vivi"]
        memory_hits = memo_out["result"]["memory_hits"]

        # Phase 2: native LM speech
        speak_msg = message(
            sender=QUAD,
            receiver="LING",
            verb="query",
            via="SPEAK",
            vivi=self.vivi,
            seq_index=self._turn_count,
            body={"text": user_text, "memory_hits": memory_hits},
        )
        ling_out = self._handler_ling(speak_msg, self.vivi)
        self.vivi = ling_out["vivi"]
        result = ling_out["result"]

        # Phase 3: store in spectral vault
        self.memory.store(user_text, result["spoken"], role=result["role"])

        respond_maque = message(
            sender="LING",
            receiver=QUAD,
            verb="respond",
            via="NOVMINI",
            vivi=self.vivi,
            seq_index=self._turn_count,
            body=result,
        )
        respond_apex = apex(
            apex_type="novamini.response",
            sender=QUAD,
            flos_path="NOVMINI",
            vivi_id=self.vivi.id,
            seq_index=self._turn_count,
            payload={"spoken_len": len(result["spoken"])},
        )

        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        return NovaMiniResponse(
            spoken=result["spoken"],
            role=result["role"],
            claim_score=result["claim_score"],
            loop_steps=result["loop_steps"],
            maque=respond_maque,
            apex=respond_apex,
            memory_hits=memory_hits,
            latency_ms=elapsed,
        )

    def export_manifest(self, path: Path) -> Path:
        payload = {
            "product": "NOVAMINI (MESIE-LM)",
            "version": VERSION,
            "model_id": MODEL_ID,
            "native_lm": AURO_MODEL_ID,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": self.status(),
            "sample": self.chat("What is NOVAMINI and the Alpha family speaking protocol?").to_dict(),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path