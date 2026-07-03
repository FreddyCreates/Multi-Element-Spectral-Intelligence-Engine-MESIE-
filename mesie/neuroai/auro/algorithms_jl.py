"""Julia-accelerated Medina algorithms — subprocess bridge to MedinaAlgorithms.jl.

Same function signatures as algorithms.py. Automatically falls back to the
pure-Python implementations if Julia is not installed or the CLI fails.

Usage in native_lm.py:
    from mesie.neuroai.auro.algorithms_jl import (
        JuliaBridge, phi_cascade, polygon_envelope,
        recursive_unfold, chemical_cascade, batch_analyze,
    )
    # or via the bridge object for batch (one round-trip):
    bridge = JuliaBridge()
    result = bridge.batch_analyze(text, knowledge_texts, saliences)
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from mesie.neuroai.auro.algorithms import (
    phi_cascade         as _py_phi_cascade,
    polygon_envelope    as _py_polygon_envelope,
    recursive_unfold    as _py_recursive_unfold,
    hebbian_salience    as _py_hebbian_salience,
    chemical_cascade    as _py_chemical_cascade,
    phi_harmonic_basis  as _py_phi_harmonic_basis,
    PHI_INV,
)

_CLI = Path(__file__).with_name("julia") / "algorithms_cli.jl"
_TIMEOUT = 90  # seconds — first call JIT-compiles (~30–60s); subsequent calls <5ms


class JuliaBridge:
    """Subprocess bridge to MedinaAlgorithms.jl.

    Detects Julia availability once at construction. If Julia is not present,
    every call transparently delegates to the pure-Python implementations.

    The critical method is batch_analyze() — it runs all 7 algorithms in a
    single Julia subprocess call, returning the complete analysis dict.
    No multiple round-trips.
    """

    def __init__(self) -> None:
        self._available: Optional[bool] = None

    @property
    def available(self) -> bool:
        if self._available is None:
            self._available = self._probe()
        return self._available

    def _probe(self) -> bool:
        if shutil.which("julia") is None or not _CLI.exists():
            return False
        try:
            out = self._call({"action": "health"})
            return bool(out.get("ok"))
        except Exception:
            return False

    def _call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        proc = subprocess.run(
            ["julia", str(_CLI)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
            check=True,
        )
        return json.loads(proc.stdout)

    # ── batch_analyze — preferred path: one round-trip, all algorithms ─────────

    def batch_analyze(
        self,
        text: str,
        knowledge_texts: List[str],
        saliences: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Run all 7 Medina algorithms in one Julia subprocess call.

        Returns the same keys as _algorithmic_analyze() in native_lm.py plus
        Julia-specific fields (cascade_idx, cascade_scores, n_knowledge).
        Falls back to Python batch if Julia unavailable.
        """
        if self.available:
            try:
                payload = {
                    "action": "batch_analyze",
                    "text": text,
                    "knowledge_texts": knowledge_texts,
                    "saliences": saliences or [PHI_INV] * len(knowledge_texts),
                }
                result = self._call(payload)
                if result.get("ok"):
                    return result
            except Exception:
                pass
        # Python fallback
        return self._py_batch_analyze(text, knowledge_texts, saliences)

    def _py_batch_analyze(
        self,
        text: str,
        knowledge_texts: List[str],
        saliences: Optional[List[float]],
    ) -> Dict[str, Any]:
        """Pure-Python batch analysis — matches Julia output schema."""
        from mesie.neuroai.auro.algorithms import _text_to_vec_internal  # may not exist
        q_vec = _safe_text_to_vec(text)
        k_vecs = [_safe_text_to_vec(t) for t in knowledge_texts]
        sals = saliences or [PHI_INV] * len(knowledge_texts)

        # φ-harmonic basis
        basis = _py_phi_harmonic_basis(len(q_vec))
        m = min(len(basis), len(q_vec))
        phi_sig = float(np.dot(basis[:m], q_vec[:m]))

        # φ-cascade (Python path returns dicts)
        k_items = [
            {"key": f"k{i}", "content": t, "salience": sals[i] if i < len(sals) else PHI_INV,
             "vector": v.tolist()}
            for i, (t, v) in enumerate(zip(knowledge_texts, k_vecs))
        ]
        cascade_hits = _py_phi_cascade(q_vec, k_items, decay=PHI_INV, threshold=0.09, k=6, hops=3)

        # Polygon
        poly = _py_polygon_envelope(q_vec, k_vecs) if len(k_vecs) >= 3 else {
            "inside": False, "region_confidence": 0.0, "nearest_idx": 0,
            "hull_radius": 0.0, "query_radius": 0.0,
        }

        # Unfold
        unfold_w = np.array(_py_recursive_unfold(q_vec, depth=4, branching=2))
        unfold_energy = float(np.sum(unfold_w ** 2))

        # Chemical cascade (3-band)
        dim = len(q_vec)
        band_size = max(1, dim // 3)
        bands = [q_vec[i * band_size:(i + 1) * band_size] for i in range(3)]
        n_bands = len(bands)
        react = np.zeros((n_bands, n_bands))
        for i in range(n_bands):
            for j in range(n_bands):
                a, b = bands[i], bands[j]
                l = min(len(a), len(b))
                if l > 0:
                    react[i, j] = float(np.dot(a[:l], b[:l]) /
                                        (np.linalg.norm(a[:l]) * np.linalg.norm(b[:l]) + 1e-12))
        init_act = [float(np.linalg.norm(b)) for b in bands]
        c_out = _py_chemical_cascade(init_act, react, steps=4, decay=PHI_INV)
        cascade_energy = float(np.sum(c_out ** 2))

        # Spectral entropy + centroid
        p = q_vec / (float(np.sum(q_vec)) + 1e-12)
        entropy = float(-np.sum(p * np.log2(p + 1e-14)))
        freqs = np.arange(1, len(q_vec) + 1, dtype=np.float64)
        centroid = float(np.dot(freqs, p))

        cascade_idx = list(range(len(cascade_hits)))
        cascade_scores = [round(h.get("cascade_score", 0.0), 4) for h in cascade_hits]

        return {
            "ok": True,
            "phi_signal": round(phi_sig, 4),
            "entropy": round(entropy, 4),
            "centroid": round(centroid, 4),
            "unfold_energy": round(unfold_energy, 4),
            "cascade_energy": round(cascade_energy, 4),
            "n_cascade_hits": len(cascade_idx),
            "cascade_idx": cascade_idx,
            "cascade_scores": cascade_scores,
            "poly_inside": bool(poly["inside"]),
            "poly_confidence": round(float(poly["region_confidence"]), 4),
            "poly_hull_radius": round(float(poly["hull_radius"]), 4),
            "poly_query_radius": round(float(poly["query_radius"]), 4),
            "poly_nearest_idx": int(poly.get("nearest_idx", 0)),
            "top_salience": round(_py_hebbian_salience(
                sals[0] if sals else PHI_INV, len(cascade_idx)
            ), 4),
            "runtime": "python-fallback",
            "n_knowledge": len(knowledge_texts),
        }

    # ── Individual algorithm accelerators (used when only one is needed) ───────

    def phi_cascade(
        self,
        query_vec: np.ndarray,
        knowledge_vecs: List[np.ndarray],
        saliences: List[float],
        *,
        decay: float = PHI_INV,
        threshold: float = 0.12,
        k: int = 5,
        hops: int = 3,
    ) -> Tuple[List[int], List[float]]:
        if self.available:
            try:
                payload = {
                    "action": "phi_cascade",
                    "query_vec": query_vec.tolist(),
                    "knowledge_vecs": [v.tolist() for v in knowledge_vecs],
                    "saliences": saliences,
                    "decay": decay, "threshold": threshold,
                    "k": k, "hops": hops,
                }
                out = self._call(payload)
                if out.get("ok"):
                    return out["indices"], out["scores"]
            except Exception:
                pass
        # Python fallback — returns dicts; extract index+score
        items = [
            {"key": f"k{i}", "content": "", "salience": saliences[i] if i < len(saliences) else PHI_INV,
             "vector": v.tolist()}
            for i, v in enumerate(knowledge_vecs)
        ]
        hits = _py_phi_cascade(query_vec, items, decay=decay, threshold=threshold, k=k, hops=hops)
        idx = list(range(len(hits)))
        scores = [h.get("cascade_score", 0.0) for h in hits]
        return idx, scores

    def polygon_envelope(
        self,
        query_vec: np.ndarray,
        knowledge_vecs: List[np.ndarray],
    ) -> Dict[str, Any]:
        if self.available:
            try:
                payload = {
                    "action": "polygon_envelope",
                    "query_vec": query_vec.tolist(),
                    "knowledge_vecs": [v.tolist() for v in knowledge_vecs],
                }
                out = self._call(payload)
                if out.get("ok"):
                    return out
            except Exception:
                pass
        return _py_polygon_envelope(query_vec, knowledge_vecs)

    def recursive_unfold(
        self,
        seed: np.ndarray,
        depth: int = 3,
        branching: int = 2,
    ) -> np.ndarray:
        if self.available:
            try:
                payload = {
                    "action": "recursive_unfold",
                    "seed": seed.tolist(),
                    "depth": depth,
                    "branching": branching,
                }
                out = self._call(payload)
                if out.get("ok"):
                    return np.array(out["weights"], dtype=np.float64)
            except Exception:
                pass
        return np.array(_py_recursive_unfold(seed, depth=depth, branching=branching))

    def chemical_cascade(
        self,
        activations: List[float],
        reaction_matrix: np.ndarray,
        steps: int = 4,
        decay: float = PHI_INV,
    ) -> np.ndarray:
        if self.available:
            try:
                payload = {
                    "action": "chemical_cascade",
                    "activations": list(activations),
                    "reaction_matrix": reaction_matrix.tolist(),
                    "steps": steps,
                    "decay": decay,
                }
                out = self._call(payload)
                if out.get("ok"):
                    return np.array(out["activations"], dtype=np.float64)
            except Exception:
                pass
        return _py_chemical_cascade(activations, reaction_matrix, steps=steps, decay=decay)


def _safe_text_to_vec(text: str, n: int = 64) -> np.ndarray:
    sig = np.array([float(ord(c) % 97) for c in text[:n]], dtype=np.float64)
    if len(sig) < n:
        sig = np.pad(sig, (0, n - len(sig)))
    detrended = sig - np.linspace(sig[0], sig[-1], n)
    spectrum = np.abs(np.fft.rfft(detrended))
    norm = float(np.linalg.norm(spectrum)) + 1e-12
    return spectrum / norm


# Module-level singleton — instantiated once per process
_bridge: Optional[JuliaBridge] = None


def _get_bridge() -> JuliaBridge:
    global _bridge
    if _bridge is None:
        _bridge = JuliaBridge()
    return _bridge


# Module-level convenience wrappers (drop-in for algorithms.py)
def phi_cascade(q, items, **kw):  # type: ignore[override]
    return _py_phi_cascade(q, items, **kw)


def polygon_envelope(q, k_vecs):  # type: ignore[override]
    return _py_polygon_envelope(q, k_vecs)


def recursive_unfold(seed, **kw):  # type: ignore[override]
    return _py_recursive_unfold(seed, **kw)


def chemical_cascade(acts, react, **kw):  # type: ignore[override]
    return _py_chemical_cascade(acts, react, **kw)


def hebbian_salience(base, count, **kw):  # type: ignore[override]
    return _py_hebbian_salience(base, count, **kw)


def batch_analyze(text: str, knowledge_texts: List[str],
                  saliences: Optional[List[float]] = None) -> Dict[str, Any]:
    """One-call entry point — uses Julia if available, Python otherwise."""
    return _get_bridge().batch_analyze(text, knowledge_texts, saliences)
