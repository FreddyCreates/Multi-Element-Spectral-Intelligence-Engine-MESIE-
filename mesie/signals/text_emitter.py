"""Generate text from any signal — SOLUS reasoning + optional native voice."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from mesie.signals.universal_reader import SignalReadResult, UniversalSignalReader


@dataclass
class TextEmission:
    text: str
    format: str
    signal_fingerprint: str
    sovereign: bool
    model: str
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "format": self.format,
            "signal_fingerprint": self.signal_fingerprint,
            "sovereign": self.sovereign,
            "model": self.model,
            "meta": self.meta,
        }


class SignalTextEmitter:
    """Turn unified signals into analyst prose, briefs, or native spoken output."""

    def __init__(self) -> None:
        self._reader = UniversalSignalReader()

    def generate(
        self,
        payload: Any,
        *,
        style: str = "analyst_brief",
        max_chars: int = 1200,
        use_native_voice: bool = False,
        hint: Optional[str] = None,
    ) -> TextEmission:
        signal = self._reader.read(payload, hint=hint)
        if use_native_voice:
            return self._native_voice(signal, max_chars=max_chars)
        return self._solus_brief(signal, style=style, max_chars=max_chars)

    def generate_from_signal(self, signal: SignalReadResult, *, style: str = "analyst_brief", max_chars: int = 1200) -> TextEmission:
        return self._solus_brief(signal, style=style, max_chars=max_chars)

    def _solus_brief(self, signal: SignalReadResult, *, style: str, max_chars: int) -> TextEmission:
        from mesie.sdk.solus import SDKSolusOrganism

        org = SDKSolusOrganism()
        amps = signal.spectral_signature or [0.1, 0.3, 0.5]
        freqs = [float(i + 1) for i in range(len(amps))]
        cycle = org.formal_stack.compose_cycle(
            freqs,
            amps,
            cycle_context={
                "record_id": signal.record_id,
                "modality": signal.modality.value,
                "text_excerpt": signal.text[:500],
            },
        )
        logic = cycle.get("models", {}).get("logic", {})
        reasoning = cycle.get("models", {}).get("reasoning", {})
        emergence = cycle.get("models", {}).get("emergence", {})
        conclusion = reasoning.get("brain", {}).get("conclusion", "signal observed")
        conf = reasoning.get("brain", {}).get("confidence", 0.0)
        em = emergence.get("brain", {}).get("emergence", emergence.get("data", {}).get("emergence_score", 0.0))

        if style == "executive":
            body = (
                f"Signal ({signal.modality.value}): {signal.text[:300]}\n"
                f"Assessment: {conclusion} (confidence {conf:.2f}, emergence {em:.4f}).\n"
                f"Fingerprint {signal.fingerprint[:12]}… — sovereign local analysis."
            )
        elif style == "technical":
            body = (
                f"## Signal envelope\n"
                f"- modality: {signal.modality.value}\n"
                f"- record_id: {signal.record_id}\n"
                f"- spectral_dims: {len(signal.spectral_signature)}\n"
                f"- logic: {(logic.get('brain') or {}).get('conclusion', 'ok')}\n"
                f"- reasoning: {conclusion}\n"
                f"- excerpt: {signal.text[:400]}"
            )
        else:
            body = (
                f"MESIE read [{signal.modality.value}] → {conclusion}. "
                f"Coherence {conf:.2f}. Signal: {signal.text[:280]}"
            )

        return TextEmission(
            text=body[:max_chars],
            format=style,
            signal_fingerprint=signal.fingerprint,
            sovereign=True,
            model="SOLUS-Logic⊗Reasoning⊗Emergence",
            meta={
                "logic_ok": logic.get("ok", True),
                "confidence": conf,
                "emergence": em,
                "composition_hash": cycle.get("composition_hash"),
                "latency_note": "local-only",
            },
        )

    def _native_voice(self, signal: SignalReadResult, *, max_chars: int) -> TextEmission:
        from mesie.neuroai.auro.native_lm import AuroNativeLanguageModel

        lm = AuroNativeLanguageModel(session_id=f"sig-{uuid.uuid4().hex[:8]}")
        prompt = f"Interpret this {signal.modality.value} signal for a sovereign analyst: {signal.text[:800]}"
        out = lm.generate(prompt[:2000])
        return TextEmission(
            text=out.spoken[:max_chars],
            format="native_voice",
            signal_fingerprint=signal.fingerprint,
            sovereign=True,
            model=out.native_model,
            meta={"role": out.role, "trajectory_id": out.trajectory_id},
        )