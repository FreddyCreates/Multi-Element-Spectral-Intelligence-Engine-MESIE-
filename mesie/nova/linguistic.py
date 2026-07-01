"""NOVA linguistic layer — φ-weighted language geometry (Liquid Language patterns)."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Dict, List

PHI = 1.618033988749895
PHI_INV = 0.6180339887498949


@dataclass
class LinguisticAnalysis:
    tokens: List[str]
    coherence: float
    center_index: int
    weights: List[float]
    attractors: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tokens": self.tokens[:24],
            "coherence": round(self.coherence, 4),
            "center_index": self.center_index,
            "attractors": self.attractors[:6],
        }


class LinguisticEngine:
    """Adaptive linguistic intelligence — doctrine attractors + φ-Gaussian focus."""

    def analyze(self, text: str) -> LinguisticAnalysis:
        tokens = text.split()
        n = len(tokens) or 1
        center = int(round(n / PHI)) if n > 1 else 0
        weights = self._phi_gaussian(n, center)
        coherence = self._coherence_score(text)
        attractors = [self._doctrine_attractor(t) for t in tokens[:8]]
        return LinguisticAnalysis(
            tokens=tokens,
            coherence=coherence,
            center_index=center,
            weights=weights,
            attractors=attractors,
        )

    @staticmethod
    def _phi_gaussian(n: int, center: int) -> List[float]:
        raw = [math.exp(-PHI * abs(i - center)) for i in range(n)]
        z = sum(raw) or 1.0
        return [w / z for w in raw]

    @staticmethod
    def _coherence_score(text: str) -> float:
        words = [w.lower() for w in re.split(r"\W+", text) if w]
        if not words:
            return 0.0
        ttr = len(set(words)) / len(words)
        norm = min(len(words) / 200.0, 1.0)
        return PHI_INV * ttr + (1.0 - PHI_INV) * norm

    @staticmethod
    def _doctrine_attractor(word: str, vocab: int = 50000) -> Dict[str, Any]:
        h = 0
        for c in word:
            h = (h * 31 + ord(c)) % vocab
        angle = (h / vocab) * 2 * math.pi * PHI
        return {
            "word": word,
            "angle_rad": round(angle, 4),
            "phi_weight": round(math.exp(-PHI_INV * (h / vocab)), 4),
        }