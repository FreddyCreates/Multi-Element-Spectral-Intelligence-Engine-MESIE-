# phantom_native/sovereign_tensor.py
"""SovereignTensor — Pure native tensor engine integrated with MESIE spectral primitives.

Zero external dependencies beyond the Python standard library.
Supports deterministic binary serialization for QSHA + Vault workflows,
direct ingestion from MESIE SpectralComponent objects, and resonance-weighted
linear algebra.
"""

from __future__ import annotations

import math
import struct
from typing import Any, Dict, List, Optional, Tuple


class SovereignTensor:
    """Pure native tensor engine integrated with MESIE spectral primitives."""

    def __init__(
        self,
        data: List[float],
        shape: Tuple[int, ...],
        spectral_meta: Optional[Dict[str, Any]] = None,
    ):
        self.shape = shape
        self.data = data[:]  # flattened copy
        self.spectral_meta = spectral_meta or {}
        expected = self._compute_size(shape)
        if len(data) != expected:
            raise ValueError(
                f"Shape / data mismatch: shape {shape} expects {expected} elements, "
                f"got {len(data)}"
            )

        # MESIE-native metadata
        self.resonance_score: float = self.spectral_meta.get("resonance", 1.0)
        self.helix_params: Dict[str, Any] = self.spectral_meta.get("helix", {})
        self.lineage: Any = self.spectral_meta.get("lineage", [])

    # ------------------------------------------------------------------
    # Size helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_size(shape: Tuple[int, ...]) -> int:
        """Return the number of elements implied by *shape*."""
        p = 1
        for d in shape:
            p *= d
        return p

    @property
    def size(self) -> int:
        """Total number of elements."""
        return self._compute_size(self.shape)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_bytes(self) -> bytes:
        """Deterministic binary representation for QSHA + Vault."""
        return struct.pack(f"{len(self.data)}f", *self.data)

    @classmethod
    def from_bytes(cls, raw: bytes, shape: Tuple[int, ...]) -> "SovereignTensor":
        """Reconstruct a tensor from its deterministic binary form."""
        n = cls._compute_size(shape)
        data = list(struct.unpack(f"{n}f", raw))
        return cls(data, shape)

    # ------------------------------------------------------------------
    # MESIE integration
    # ------------------------------------------------------------------

    @classmethod
    def from_mesie_component(cls, component: Dict[str, Any]) -> "SovereignTensor":
        """Direct ingestion from a MESIE SpectralComponent dict.

        Expects keys like ``frequency``, ``amplitude``, ``element_weight``,
        and optionally ``node_id``.
        """
        freq = component.get("frequency", [])
        amp = component.get("amplitude", [])
        data = list(amp) if amp else list(freq)
        if not data:
            data = [0.0]
        shape = (len(data),)
        meta: Dict[str, Any] = {
            "resonance": component.get("element_weight", 1.0),
            "helix": {"turns": 8, "dimensions": len(data)},
            "lineage": component.get("node_id"),
        }
        return cls(data, shape, meta)

    @classmethod
    def zeros(cls, shape: Tuple[int, ...]) -> "SovereignTensor":
        """Create a zero-filled tensor of given shape."""
        n = cls._compute_size(shape)
        return cls([0.0] * n, shape)

    @classmethod
    def ones(cls, shape: Tuple[int, ...]) -> "SovereignTensor":
        """Create a one-filled tensor of given shape."""
        n = cls._compute_size(shape)
        return cls([1.0] * n, shape)

    # ------------------------------------------------------------------
    # Core operations — fully unrolled for fixed shapes
    # ------------------------------------------------------------------

    def add(self, other: "SovereignTensor") -> "SovereignTensor":
        """Element-wise addition."""
        if self.shape != other.shape:
            raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
        result = [a + b for a, b in zip(self.data, other.data)]
        return SovereignTensor(result, self.shape, self.spectral_meta)

    def sub(self, other: "SovereignTensor") -> "SovereignTensor":
        """Element-wise subtraction."""
        if self.shape != other.shape:
            raise ValueError(f"Shape mismatch: {self.shape} vs {other.shape}")
        result = [a - b for a, b in zip(self.data, other.data)]
        return SovereignTensor(result, self.shape, self.spectral_meta)

    def scale(self, scalar: float) -> "SovereignTensor":
        """Scalar multiplication."""
        result = [x * scalar for x in self.data]
        return SovereignTensor(result, self.shape, self.spectral_meta)

    def dot(self, other: "SovereignTensor") -> float:
        """Dot product for 1-D tensors."""
        if len(self.shape) != 1 or len(other.shape) != 1:
            raise ValueError("dot requires 1-D tensors")
        if self.shape[0] != other.shape[0]:
            raise ValueError(f"Length mismatch: {self.shape[0]} vs {other.shape[0]}")
        return sum(a * b for a, b in zip(self.data, other.data))

    def matmul(self, other: "SovereignTensor") -> "SovereignTensor":
        """Resonance-weighted matrix multiplication for 2-D tensors."""
        if len(self.shape) != 2 or len(other.shape) != 2:
            raise ValueError("matmul requires 2-D tensors")
        if self.shape[1] != other.shape[0]:
            raise ValueError(
                f"Inner dimension mismatch: {self.shape[1]} vs {other.shape[0]}"
            )
        m, k = self.shape
        _, n = other.shape
        result = [0.0] * (m * n)

        resonance = self.resonance_score * other.resonance_score

        for i in range(m):
            for j in range(n):
                acc = 0.0
                for p in range(k):
                    acc += self.data[i * k + p] * other.data[p * n + j]
                result[i * n + j] = acc * resonance  # resonance weighting
        return SovereignTensor(result, (m, n), self.spectral_meta)

    def norm(self) -> float:
        """L2 norm."""
        return math.sqrt(sum(x * x for x in self.data))

    # ------------------------------------------------------------------
    # Quantization for edge deployment
    # ------------------------------------------------------------------

    def quantize_int8(self) -> "SovereignTensor":
        """Native int8 quantization for edge deployment.

        Stores quantized values as floats for interoperability.
        The quantization scale is recorded in ``spectral_meta["quant_scale"]``.
        """
        scale = max(abs(x) for x in self.data) if self.data else 1.0
        if scale == 0.0:
            scale = 1.0
        qdata = [float(int((x / scale) * 127)) for x in self.data]
        meta = dict(self.spectral_meta)
        meta["quant_scale"] = scale
        return SovereignTensor(qdata, self.shape, meta)

    def dequantize(self) -> "SovereignTensor":
        """Reverse int8 quantization using stored scale."""
        scale = self.spectral_meta.get("quant_scale")
        if scale is None:
            raise ValueError("No quant_scale in spectral_meta; not a quantized tensor")
        data = [(x / 127.0) * scale for x in self.data]
        meta = dict(self.spectral_meta)
        meta.pop("quant_scale", None)
        return SovereignTensor(data, self.shape, meta)

    # ------------------------------------------------------------------
    # Representations
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        preview = self.data[:6]
        suffix = ", ..." if len(self.data) > 6 else ""
        return (
            f"SovereignTensor(shape={self.shape}, "
            f"data=[{', '.join(f'{x:.4f}' for x in preview)}{suffix}])"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SovereignTensor):
            return NotImplemented
        return self.shape == other.shape and self.data == other.data
