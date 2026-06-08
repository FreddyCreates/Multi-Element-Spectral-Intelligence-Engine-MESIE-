"""Intelligence engine — reasoning and memory objects."""

from __future__ import annotations

from typing import Optional

from mesie.ai.intelligence_protocols import IntelligenceConfig, IntelligenceProtocol
from mesie.cognitive.memory_adapter import SpectralMemoryAdapter
from mesie.engines.base import Engine
from mesie.embeddings.vectorizers import SpectralVectorizer
from mesie.internal_api.messages import EngineResponse, MessageEnvelope
from mesie.io.loaders import load_record


class IntelligenceEngine(Engine):
    name = "intelligence"
    capabilities = ["reason", "memory", "observe", "agent_session", "spectral_cycle"]

    def __init__(self, *, use_solus: bool = True) -> None:
        self._protocol = IntelligenceProtocol(IntelligenceConfig())
        self._memory = SpectralMemoryAdapter()
        self._vectorizer = SpectralVectorizer()
        self._organism = None
        if use_solus:
            from mesie.sdk.solus import SDKSolusOrganism

            self._organism = SDKSolusOrganism()

    def handle(self, message: MessageEnvelope) -> Optional[EngineResponse]:
        if message.target not in (self.name, "*"):
            return None
        action = message.action
        if action not in self.capabilities:
            return EngineResponse(False, self.name, action, error=f"Unknown action: {action}")

        try:
            if action == "spectral_cycle":
                if not self._organism:
                    return EngineResponse(False, self.name, action, error="SOLUS organism not enabled")
                rec = load_record(message.payload["record"])
                comp = rec.components[0]
                ctx = message.payload.get("cycle_context", {})
                ctx.setdefault("record_id", rec.record_id)
                result = self._organism.reason_spectral_cycle(
                    comp.frequency.tolist(),
                    comp.amplitude.tolist(),
                    cycle_context=ctx,
                )
                return EngineResponse(True, self.name, action, result)

            rec = load_record(message.payload["record"])
            amp = rec.components[0].amplitude

            if action == "observe":
                self._protocol.observe(amp)
                return EngineResponse(True, self.name, action, {"observed": True, "record_id": rec.record_id})

            if action == "reason":
                emb = self._vectorizer.transform(rec)
                result = self._protocol.reason(emb)
                data: dict = {
                    "conclusion": result.conclusion,
                    "confidence": result.confidence,
                    "evidence": getattr(result, "evidence", {}),
                }
                if self._organism:
                    comp = rec.components[0]
                    ctx = message.payload.get("cycle_context", {"record_id": rec.record_id})
                    solus = self._organism.reason_spectral_cycle(
                        comp.frequency.tolist(),
                        comp.amplitude.tolist(),
                        cycle_context=ctx,
                    )
                    data["solus"] = solus
                    data["conclusion"] = solus.get("conclusion", data["conclusion"])
                    data["sovereign"] = True
                    data["enterprise_ai"] = True
                return EngineResponse(True, self.name, action, data)

            if action == "memory":
                obj = self._memory.to_memory_object(rec)
                data = {"keys": list(obj.keys()), "semantic_id": obj.get("semantic_id")}
                if self._organism:
                    comp = rec.components[0]
                    ctx = message.payload.get("cycle_context", {"record_id": rec.record_id})
                    solus = self._organism.reason_spectral_cycle(
                        comp.frequency.tolist(),
                        comp.amplitude.tolist(),
                        cycle_context=ctx,
                    )
                    data["solus_memory"] = solus
                    data["sovereign"] = True
                    data["enterprise_ai"] = True
                return EngineResponse(True, self.name, action, data)

            if action == "agent_session":
                if not self._organism:
                    return EngineResponse(False, self.name, action, error="SOLUS organism not enabled")
                tended = self._organism.tend_agent_session(message.payload.get("session", {}))
                return EngineResponse(True, self.name, action, tended)
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            return EngineResponse(False, self.name, action, error=str(exc))

        return EngineResponse(False, self.name, action, error="Unhandled")