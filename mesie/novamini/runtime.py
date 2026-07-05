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
        turn_hits = self.memory.recall(query)
        artifact_hits = self.memory.recall_artifacts(query)
        for h in turn_hits:
            h["source"] = "turn"
        for h in artifact_hits:
            h["source"] = "artifact"
        hits = turn_hits + artifact_hits
        apex_id = apex(
            apex_type="memory.recall",
            sender="MEMO",
            flos_path=msg["maque"]["via"],
            vivi_id=vivi.id,
            seq_index=self._turn_count,
            payload={"hits": len(hits), "turn_hits": len(turn_hits), "artifact_hits": len(artifact_hits)},
        )["apex"]["id"]
        live = vivi.advance("MEMO", apex_id)
        return {"result": {"memory_hits": hits}, "vivi": live}

    def _handler_ling(self, msg: Dict[str, Any], vivi: Vivi) -> Dict[str, Any]:
        body = msg["maque"]["body"]
        user_text = body.get("text", "")
        memory_hits = body.get("memory_hits", [])
        context = self._build_context(memory_hits)

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

    @staticmethod
    def _build_context(memory_hits: List[Dict[str, Any]], max_turns: int = 2, max_artifacts: int = 3) -> str:
        """Build the LM's grounding context, distinguishing recalled conversation
        from recalled artifact chunks so the LM reasons off real ingested content,
        not just what was previously said."""
        turn_parts = [h["spoken"][:80] for h in memory_hits if h.get("source") != "artifact"][:max_turns]
        artifact_parts = [
            f"[{h['artifact_name']}#{h['chunk_index']}] {h['text'][:160]}"
            for h in memory_hits if h.get("source") == "artifact"
        ][:max_artifacts]
        pieces = []
        if turn_parts:
            pieces.append(" | ".join(turn_parts))
        if artifact_parts:
            pieces.append(" || ".join(artifact_parts))
        return " ".join(pieces)

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

    def learn(self, source: "str | Path", name: Optional[str] = None) -> Dict[str, Any]:
        """Ingest a whole artifact (file on disk or raw text) into spectral memory
        so future chat() calls can recall and reason off pieces of it.
        Real files: NOVAMINI gets better the more it has actually read, not just
        what was said to it."""
        path = Path(source) if isinstance(source, (str, Path)) else None
        if path is not None and path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            artifact_name = name or path.name
        else:
            text = str(source)
            artifact_name = name or f"text-{int(time.time())}"

        result = self.memory.ingest_artifact(artifact_name, text)
        apex(
            apex_type="artifact.ingested",
            sender=QUAD,
            flos_path="NOVMINI",
            vivi_id=self.vivi.id,
            seq_index=self._turn_count,
            payload={"name": artifact_name, "ok": result.get("ok"), "chunks": result.get("chunks_indexed", 0)},
        )
        return result

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