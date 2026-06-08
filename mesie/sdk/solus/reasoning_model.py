"""SOLUS Reasoning Model — own formal inference layer (logic + context → conclusion)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mesie.sdk.solus.constants import LOCAL_ENGINE, PHI
from mesie.sdk.solus.formal_models import FormalModelReport
from mesie.sdk.solus.mini_brain import MiniBrain
from mesie.sdk.solus.mini_heart import MiniHeart


class SolusReasoningModel:
    """Chains logic proofs and signal context into sovereign local conclusions."""

    model_id = "solus-reasoning-model"
    layer = "reasoning"

    def __init__(self) -> None:
        self.heart = MiniHeart(self.model_id)
        self.brain = MiniBrain("reasoning")
        self._inference_chain: List[Dict[str, Any]] = []

    def infer(
        self,
        *,
        logic_data: Dict[str, Any],
        signal_ratio: float,
        cycle_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        steps: List[Dict[str, Any]] = []
        logic_conf = float(logic_data.get("average_confidence", 0.5))
        match_score = float(cycle_context.get("match_score", 0))
        anomaly = float(cycle_context.get("anomaly", 0))
        valid = bool(cycle_context.get("valid", True))

        steps.append({
            "step": 1,
            "operator": "weigh",
            "input": "logic_confidence",
            "value": round(logic_conf, 4),
        })
        steps.append({
            "step": 2,
            "operator": "chain",
            "input": "signal_ratio",
            "value": round(signal_ratio, 4),
        })
        composite = (logic_conf * PHI + signal_ratio + match_score) / (PHI + 2)
        if not valid:
            composite *= 0.7
        if anomaly > 2.0:
            composite *= 0.85
            steps.append({"step": 3, "operator": "conclude", "note": "anomaly dampening"})

        steps.append({
            "step": len(steps) + 1,
            "operator": "infer",
            "composite_score": round(composite, 4),
        })
        self._inference_chain.extend(steps[-3:])
        if len(self._inference_chain) > 64:
            self._inference_chain = self._inference_chain[-64:]

        return {
            "inference_chain": steps,
            "composite_score": round(composite, 4),
            "logic_confidence": logic_conf,
            "signal_ratio": signal_ratio,
            "engine": LOCAL_ENGINE,
        }

    def run(
        self,
        *,
        logic_data: Dict[str, Any],
        signal_ratio: float,
        cycle_context: Dict[str, Any],
    ) -> FormalModelReport:
        data = self.infer(
            logic_data=logic_data,
            signal_ratio=signal_ratio,
            cycle_context=cycle_context,
        )
        vitals = self.heart.pulse(data["composite_score"])
        thought = self.brain.reason({
            "score": data["composite_score"],
            "complexity": float(logic_data.get("complexity", {}).get("normalized", 0.3)
                                if isinstance(logic_data.get("complexity"), dict) else 0.3),
        })
        return FormalModelReport(
            model_id=self.model_id,
            layer=self.layer,
            ok=True,
            data=data,
            heart={"bpm": vitals.bpm, "coherence": vitals.coherence, "sdk_health": vitals.sdk_health, **self.heart.to_dict()},
            brain={"conclusion": thought.conclusion, "confidence": thought.confidence, "evidence": thought.evidence},
        )