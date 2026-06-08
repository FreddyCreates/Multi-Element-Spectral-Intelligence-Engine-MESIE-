"""SOLUS Formal Stack — composition of our four own models (zero third-party)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional, Sequence

from mesie.sdk.solus.adaptation_model import SolusAdaptationModel
from mesie.sdk.solus.constants import FORMAL_COMPOSITION, LOCAL_ENGINE, OWN_MODELS_ONLY, SOLUS_BRAND
from mesie.sdk.solus.emergence_model import SolusEmergenceModel
from mesie.sdk.solus.formal_models import composition_manifest
from mesie.sdk.solus.logic_prover import SolusLogicProver
from mesie.sdk.solus.pattern_forge import SolusPatternForge
from mesie.sdk.solus.reasoning_model import SolusReasoningModel


class SolusFormalStack:
    """What SOLUS is made of: Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation."""

    def __init__(self) -> None:
        self.logic = SolusLogicProver()
        self.reasoning = SolusReasoningModel()
        self.emergence = SolusEmergenceModel()
        self.adaptation = SolusAdaptationModel()
        self.pattern = SolusPatternForge()

    @property
    def formula(self) -> str:
        return FORMAL_COMPOSITION

    def manifest(self) -> Dict[str, Any]:
        return composition_manifest()

    def _composition_hash(self, layers: Dict[str, Any]) -> str:
        payload = json.dumps(layers, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:32]

    def compose_cycle(
        self,
        frequencies: Sequence[float],
        amplitudes: Sequence[float],
        *,
        cycle_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run all four own models over one spectral cycle."""
        ctx = dict(cycle_context or {})
        record_id = str(ctx.get("record_id", "spectral_cycle"))

        theorem = (
            f"formal_cycle {record_id}: logic→reasoning→emergence→adaptation "
            f"— own models only, zero third-party"
        )
        logic_r = self.logic.caretaker_run("prove", theorem=theorem)
        xray = self.pattern.caretaker_run("xray", values=list(amplitudes))

        signal_ratio = float(xray.data.get("signal_ratio", 0))
        ctx.setdefault("signal_ratio", signal_ratio)

        reasoning_r = self.reasoning.run(
            logic_data=logic_r.data,
            signal_ratio=signal_ratio,
            cycle_context=ctx,
        )
        emergence_r = self.emergence.run(amplitudes)
        adaptation_r = self.adaptation.run(
            ctx,
            composite_score=reasoning_r.data.get("composite_score", 0),
            emergence_score=emergence_r.data.get("emergence_score", 0),
        )

        layers = {
            "logic": logic_r.data,
            "reasoning": reasoning_r.data,
            "emergence": emergence_r.data,
            "adaptation": adaptation_r.data,
        }
        models = {
            "logic": {"model_id": self.logic.caretaker_id, "ok": logic_r.ok, "brain": logic_r.brain},
            "reasoning": {"model_id": reasoning_r.model_id, "ok": reasoning_r.ok, "brain": reasoning_r.brain},
            "emergence": {"model_id": emergence_r.model_id, "ok": emergence_r.ok, "brain": emergence_r.brain},
            "adaptation": {"model_id": adaptation_r.model_id, "ok": adaptation_r.ok, "brain": adaptation_r.brain},
        }

        conclusion = reasoning_r.brain.get("conclusion", "")
        if emergence_r.data.get("emerged"):
            conclusion = f"{conclusion} | emergence={emergence_r.data.get('emergence_score', 0):.4f}"
        if adaptation_r.data.get("recalibrated"):
            conclusion = f"{conclusion} | adapted thresholds"

        return {
            "formula": self.formula,
            "brand": SOLUS_BRAND,
            "engine": LOCAL_ENGINE,
            "sovereign": True,
            "third_party": False,
            "own_models_only": OWN_MODELS_ONLY,
            "record_id": record_id,
            "cycle_id": str(ctx.get("cycle_id", record_id)),
            "conclusion": conclusion,
            "logic_confidence": float(logic_r.brain.get("confidence", 0)),
            "signal_ratio": signal_ratio,
            "proof_steps": int(logic_r.data.get("total_steps", 1)),
            "composite_score": reasoning_r.data.get("composite_score", 0),
            "emergence_score": emergence_r.data.get("emergence_score", 0),
            "adapted": adaptation_r.data.get("adapted", False),
            "composition_hash": self._composition_hash(layers),
            "formal_models": models,
            "formal_layers": layers,
            "pattern_xray": xray.data,
            "cycle_context": ctx,
        }