"""SOLUS Adaptation Model — local cycle-to-cycle recalibration, no external learning."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from mesie.sdk.solus.constants import LOCAL_ENGINE, PHI
from mesie.sdk.solus.formal_models import FormalModelReport
from mesie.sdk.solus.mini_brain import MiniBrain
from mesie.sdk.solus.mini_heart import MiniHeart


class SolusAdaptationModel:
    """Own adaptation layer — drift thresholds and coherence from prior cycles."""

    model_id = "solus-adaptation-model"
    layer = "adaptation"

    def __init__(self) -> None:
        self.heart = MiniHeart(self.model_id)
        self.brain = MiniBrain("adaptation")
        self._history: List[Dict[str, float]] = []
        self._thresholds = {"match": 0.65, "anomaly": 2.5, "signal": 0.3}

    def adapt(self, cycle_context: Dict[str, Any], *, composite_score: float) -> Dict[str, Any]:
        snapshot = {
            "match_score": float(cycle_context.get("match_score", 0)),
            "anomaly": float(cycle_context.get("anomaly", 0)),
            "signal_ratio": float(cycle_context.get("signal_ratio", 0)),
            "composite": composite_score,
        }
        self._history.append(snapshot)
        if len(self._history) > 128:
            self._history.pop(0)

        drift = {}
        if len(self._history) >= 3:
            recent = np.array([h["composite"] for h in self._history[-8:]])
            mean_c = float(np.mean(recent))
            std_c = float(np.std(recent))
            drift["composite_mean"] = round(mean_c, 4)
            drift["composite_std"] = round(std_c, 4)
            self._thresholds["match"] = round(min(0.9, max(0.4, mean_c * 0.85)), 4)
            self._thresholds["signal"] = round(min(0.6, max(0.15, mean_c / PHI)), 4)

        adapted = snapshot["match_score"] >= self._thresholds["match"]
        recalibrated = len(self._history) % 8 == 0 and len(self._history) >= 8

        return {
            "adapted": adapted,
            "recalibrated": recalibrated,
            "thresholds": dict(self._thresholds),
            "drift": drift,
            "cycles_seen": len(self._history),
            "engine": LOCAL_ENGINE,
        }

    def run(
        self,
        cycle_context: Dict[str, Any],
        *,
        composite_score: float,
        emergence_score: float = 0.0,
    ) -> FormalModelReport:
        ctx = {**cycle_context, "signal_ratio": cycle_context.get("signal_ratio", 0)}
        data = self.adapt(ctx, composite_score=composite_score)
        vitals = self.heart.pulse(data.get("thresholds", {}).get("match", 0.5))
        thought = self.brain.reason({
            "score": composite_score,
            "metric": emergence_score,
            "complexity": 0.2 if data["adapted"] else 0.6,
        })
        return FormalModelReport(
            model_id=self.model_id,
            layer=self.layer,
            ok=True,
            data=data,
            heart={"bpm": vitals.bpm, "coherence": vitals.coherence, "sdk_health": vitals.sdk_health, **self.heart.to_dict()},
            brain={"conclusion": thought.conclusion, "confidence": thought.confidence, "evidence": thought.evidence},
        )