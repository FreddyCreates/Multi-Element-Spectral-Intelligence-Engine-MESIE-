# phantom_native/neurocore.py
"""SovereignNeuroCore — Native MESIE NeuroCore with resonance attention.

Provides a self-contained neural processing core that combines:
- Resonance-weighted attention (no external ML libraries)
- Helix-encoded weight initialization from MESIE primitives
- TAURUS working memory integration for temporal context

Zero heavy dependencies — built entirely on Python standard library + MESIE
framework primitives.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from phantom_native.sovereign_tensor import SovereignTensor


class SovereignNeuroCore:
    """Native MESIE NeuroCore — resonance + helix + TAURUS aware.

    Args:
        config: Configuration dictionary with keys:
            - ``d_model`` (int): Internal dimension (default 128).
            - ``n_heads`` (int): Number of attention heads (default 8).
            - ``memory_cap`` (int): TAURUS working memory capacity (default 32).
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        config = config or {}
        self.d_model: int = config.get("d_model", 128)
        self.n_heads: int = config.get("n_heads", 8)
        self.memory_cap: int = config.get("memory_cap", 32)
        self.weights: Dict[str, List[float]] = self._init_helix_weights()
        self.taurus_memory: List[SovereignTensor] = []  # working memory

    # ------------------------------------------------------------------
    # Weight initialization
    # ------------------------------------------------------------------

    def _init_helix_weights(self) -> Dict[str, List[float]]:
        """Helix-encoded initial weights from MESIE primitives.

        Uses sinusoidal patterns inspired by helix encoding to generate
        deterministic initial projections for Q, K, V.
        """
        return {
            "query": [math.sin(i * 0.1) for i in range(self.d_model)],
            "key": [math.cos(i * 0.1) for i in range(self.d_model)],
            "value": [1.0 / math.sqrt(self.d_model) for _ in range(self.d_model)],
        }

    # ------------------------------------------------------------------
    # Resonance attention kernel
    # ------------------------------------------------------------------

    def _resonance_attention(
        self, q: List[float], k: List[float]
    ) -> List[float]:
        """Custom resonance-weighted attention kernel.

        Computes attention scores by combining dot-product similarity
        with an exponential resonance decay factor, then applies a
        native softmax approximation.

        Args:
            q: Query vector (length d_model).
            k: Key vector (length d_model).

        Returns:
            Attention weights after resonance-weighted softmax.
        """
        n = len(q)
        scores: List[float] = []
        for i in range(n):
            dot = q[i] * k[i]  # element-wise attention score
            resonance = math.exp(-abs(dot) * 0.5)  # resonance decay
            scores.append(dot * resonance)

        # Native softmax
        if not scores:
            return []
        max_s = max(scores)
        exp_s = [math.exp(s - max_s) for s in scores]
        total = sum(exp_s)
        if total == 0.0:
            return [1.0 / n for _ in range(n)]
        return [e / total for e in exp_s]

    # ------------------------------------------------------------------
    # Forward pass
    # ------------------------------------------------------------------

    def forward(self, tensor: SovereignTensor) -> SovereignTensor:
        """Full forward pass with resonance, helix, and TAURUS.

        Args:
            tensor: Input SovereignTensor.

        Returns:
            Processed SovereignTensor after resonance attention + TAURUS update.
        """
        d = self.d_model
        data = tensor.data

        # Project to Q, K, V (native)
        q = [
            data[i % len(data)] * self.weights["query"][i % d]
            for i in range(d)
        ]
        k = [
            data[i % len(data)] * self.weights["key"][i % d]
            for i in range(d)
        ]
        v = [
            data[i % len(data)] * self.weights["value"][i % d]
            for i in range(d)
        ]

        # Compute attention weights
        attn = self._resonance_attention(q, k)

        # Weighted sum of values → broadcast to output shape
        weighted_sum = sum(attn[j] * v[j] for j in range(len(v)))
        output_data = [weighted_sum for _ in range(len(data))]

        out_tensor = SovereignTensor(output_data, tensor.shape, tensor.spectral_meta)

        # TAURUS working memory update
        self.taurus_memory.append(out_tensor)
        if len(self.taurus_memory) > self.memory_cap:
            self.taurus_memory.pop(0)

        return out_tensor

    # ------------------------------------------------------------------
    # Memory utilities
    # ------------------------------------------------------------------

    def memory_size(self) -> int:
        """Current number of entries in working memory."""
        return len(self.taurus_memory)

    def clear_memory(self) -> None:
        """Reset TAURUS working memory."""
        self.taurus_memory.clear()

    def recall_recent(self, n: int = 5) -> List[SovereignTensor]:
        """Retrieve the *n* most recent working memory entries."""
        return self.taurus_memory[-n:]

    def __repr__(self) -> str:
        return (
            f"SovereignNeuroCore(d_model={self.d_model}, n_heads={self.n_heads}, "
            f"memory={self.memory_size()}/{self.memory_cap})"
        )
