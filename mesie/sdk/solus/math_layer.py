"""SOLUS formal stack entry — default own-model layer for MAESI (zero third-party)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Sequence

from mesie.sdk.solus.constants import FORMAL_COMPOSITION, LOCAL_ENGINE, SOLUS_BRAND
from mesie.sdk.solus.formal_stack import SolusFormalStack
from mesie.sdk.solus.organism import SDKSolusOrganism


@dataclass
class SolusMathLayer:
    """Default MAESI AI substrate — Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation."""

    organism: SDKSolusOrganism = field(default_factory=SDKSolusOrganism)
    formal_stack: SolusFormalStack = field(default_factory=SolusFormalStack)
    sovereign: bool = True
    third_party: bool = False
    brand: str = SOLUS_BRAND
    engine: str = LOCAL_ENGINE
    formula: str = FORMAL_COMPOSITION

    def manifest(self) -> Dict[str, Any]:
        return self.formal_stack.manifest()

    def prove(self, theorem: str) -> Dict[str, Any]:
        r = self.organism.logic_action("prove", theorem=theorem)
        return {
            "ok": r.ok,
            "caretaker": r.caretaker,
            "model": "solus-logic-model",
            "layer": "logic",
            "conclusion": r.brain.get("conclusion", ""),
            "confidence": r.brain.get("confidence", 0),
            "sovereign": True,
            "third_party": False,
            "engine": LOCAL_ENGINE,
        }

    def analyze_values(self, values: Sequence[float]) -> Dict[str, Any]:
        emergence = self.formal_stack.emergence.run(values)
        xray = self.organism.pattern_action("xray", values=list(values))
        return {
            "ok": xray.ok and emergence.ok,
            "xray": xray.data,
            "emergence": emergence.data,
            "signal_ratio": xray.data.get("signal_ratio"),
            "sovereign": True,
            "third_party": False,
            "engine": LOCAL_ENGINE,
        }

    def complexity(self, problem: str) -> Dict[str, Any]:
        r = self.organism.logic_action("complexity", problem=problem)
        return {
            "ok": r.ok,
            "complexity": r.data,
            "model": "solus-logic-model",
            "conclusion": r.brain.get("conclusion", ""),
            "confidence": r.brain.get("confidence", 0),
            "sovereign": True,
        }

    def reason_spectral_cycle(
        self,
        frequencies: Sequence[float],
        amplitudes: Sequence[float],
        *,
        cycle_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Full formal stack over one spectral cycle — all four own models."""
        return self.formal_stack.compose_cycle(
            frequencies,
            amplitudes,
            cycle_context=cycle_context or {},
        )