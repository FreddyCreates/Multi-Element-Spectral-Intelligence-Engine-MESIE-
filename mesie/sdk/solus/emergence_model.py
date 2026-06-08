"""SOLUS Emergence Model — phi-harmonic pattern lift from spectral interaction."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

import numpy as np

from mesie.sdk.solus.constants import GOLDEN_ANGLE, LOCAL_ENGINE, PHI
from mesie.sdk.solus.formal_models import FormalModelReport
from mesie.sdk.solus.mini_brain import MiniBrain
from mesie.sdk.solus.mini_heart import MiniHeart


class SolusEmergenceModel:
    """Own emergence layer — patterns that arise from local spectral coupling."""

    model_id = "solus-emergence-model"
    layer = "emergence"

    def __init__(self) -> None:
        self.heart = MiniHeart(self.model_id)
        self.brain = MiniBrain("emergence")
        self._emergent_events: List[Dict[str, Any]] = []

    def resonate(self, values: Sequence[float]) -> Dict[str, Any]:
        arr = np.asarray(values, dtype=np.float64)
        if arr.size < 4:
            return {"error": "need at least 4 values", "engine": LOCAL_ENGINE}

        centered = arr - np.mean(arr)
        n = arr.size
        lifts = []
        for k in range(1, min(n // 2, 8)):
            t = np.arange(n)
            phase = 2 * np.pi * k * t / n
            re = float(np.sum(centered * np.cos(phase)))
            im = float(-np.sum(centered * np.sin(phase)))
            mag = np.sqrt(re * re + im * im) / n
            phi_lift = float(mag * (PHI ** (k % 3)))
            golden_align = abs((k * GOLDEN_ANGLE) % 360 - 180) / 180
            lifts.append({
                "harmonic": k,
                "magnitude": round(float(mag), 6),
                "phi_lift": round(phi_lift, 6),
                "golden_align": round(golden_align, 4),
            })

        lifts.sort(key=lambda x: -x["phi_lift"])
        top = lifts[:3]
        emergence_score = float(np.mean([x["phi_lift"] for x in top])) if top else 0.0
        cross = float(np.corrcoef(arr[: n // 2], arr[n // 2 : n // 2 * 2][: n // 2])[0, 1]) if n >= 8 else 0.0

        event = {
            "emergence_score": round(emergence_score, 6),
            "harmonic_lifts": top,
            "cross_coupling": round(cross, 4),
            "emerged": emergence_score > 0.05,
            "engine": LOCAL_ENGINE,
        }
        if event["emerged"]:
            self._emergent_events.append(event)
            if len(self._emergent_events) > 32:
                self._emergent_events.pop(0)
        return event

    def run(self, values: Sequence[float]) -> FormalModelReport:
        data = self.resonate(values)
        ok = "error" not in data
        score = data.get("emergence_score", 0.0) if ok else 0.0
        vitals = self.heart.pulse(min(1.0, score * 10))
        thought = self.brain.reason({"score": min(1.0, score * 5), "metric": data.get("cross_coupling", 0)})
        return FormalModelReport(
            model_id=self.model_id,
            layer=self.layer,
            ok=ok,
            data=data,
            heart={"bpm": vitals.bpm, "coherence": vitals.coherence, "sdk_health": vitals.sdk_health, **self.heart.to_dict()},
            brain={"conclusion": thought.conclusion, "confidence": thought.confidence, "evidence": thought.evidence},
        )