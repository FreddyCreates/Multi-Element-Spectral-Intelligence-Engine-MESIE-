"""SOLUS formal model registry — what our AI is made of, not what it does."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from mesie.sdk.solus.constants import FORMAL_COMPOSITION, LOCAL_ENGINE, SOLUS_BRAND


@dataclass(frozen=True)
class FormalModelSpec:
    """One own-model layer in the SOLUS stack."""

    model_id: str
    layer: str
    description: str
    operators: List[str]
    sovereign: bool = True
    third_party: bool = False
    engine: str = LOCAL_ENGINE


FORMAL_MODEL_REGISTRY: List[FormalModelSpec] = [
    FormalModelSpec(
        "solus-logic-model",
        "logic",
        "Formal proof and symbolic structure — the logic substrate.",
        ["prove", "verify", "parse", "complexity"],
    ),
    FormalModelSpec(
        "solus-reasoning-model",
        "reasoning",
        "Inference chains over logic + signal context — local conclusion synthesis.",
        ["infer", "chain", "weigh", "conclude"],
    ),
    FormalModelSpec(
        "solus-emergence-model",
        "emergence",
        "Phi-harmonic pattern emergence from spectral interaction — no external model.",
        ["resonate", "harmonic_lift", "cross_couple", "lift"],
    ),
    FormalModelSpec(
        "solus-adaptation-model",
        "adaptation",
        "Cycle-to-cycle local adaptation — thresholds and coherence drift.",
        ["adapt", "drift", "recalibrate", "remember"],
    ),
]


@dataclass
class FormalModelReport:
    model_id: str
    layer: str
    ok: bool
    data: Dict[str, Any]
    heart: Dict[str, Any]
    brain: Dict[str, Any]
    sovereign: bool = True
    third_party: bool = False
    engine: str = LOCAL_ENGINE


def composition_manifest() -> Dict[str, Any]:
    """Return the formula of what SOLUS is made of."""
    return {
        "brand": SOLUS_BRAND,
        "formula": FORMAL_COMPOSITION,
        "sovereign": True,
        "third_party": False,
        "engine": LOCAL_ENGINE,
        "models": [
            {
                "model_id": m.model_id,
                "layer": m.layer,
                "operators": m.operators,
                "sovereign": m.sovereign,
                "third_party": m.third_party,
            }
            for m in FORMAL_MODEL_REGISTRY
        ],
    }