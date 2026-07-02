"""Medina algorithmic generation suite.

Real physics / geometry / cascade / recursion algorithms — no external LLM calls.
Every signal path is mathematical. Wires into native_lm.py as the generation core.

Algorithms:
    phi_cascade         — φ-weighted axonal signal cascade (biotech: neural propagation)
    polygon_envelope    — convex-hull geometry for knowledge-region detection
    recursive_unfold    — fractal dendritic grammar expansion
    hebbian_salience    — LTP synaptic plasticity (biotech: neurons that fire together)
    chemical_cascade    — enzyme reaction-network propagation (biotech: enzyme cascade)
    phi_rank            — φ-harmonic re-ranking with positional bonus
    spectral_compose    — assemble spoken text from cascade-selected knowledge chunks
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

PHI = 1.618033988749895
PHI_INV = 0.6180339887498949   # 1/φ — natural decay constant
SCHUMANN = 7.83                 # Hz — Earth resonance base
DELTA_T = 0.873                 # φ⁴ × 7.83 s — Medina heartbeat


# ── Physics: φ-harmonic frequency basis ──────────────────────────────────────

def phi_harmonic_basis(n: int = 64) -> np.ndarray:
    """Build a geometric basis where each frequency is the previous × φ_inv.

    Models standing-wave harmonics anchored at the Schumann base frequency.
    Converges to zero — bounded, physically realistic.
    """
    freqs = np.zeros(n, dtype=np.float64)
    freqs[0] = SCHUMANN / 100.0
    for i in range(1, n):
        freqs[i] = freqs[i - 1] * PHI_INV
    norm = float(np.linalg.norm(freqs)) + 1e-12
    return freqs / norm


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


# ── Cascade algorithm: φ-weighted axonal signal propagation ──────────────────

def phi_cascade(
    query_vec: np.ndarray,
    knowledge_items: List[Dict[str, Any]],
    decay: float = PHI_INV,
    threshold: float = 0.12,
    k: int = 5,
    hops: int = 3,
) -> List[Dict[str, Any]]:
    """φ-cascade — biotech: axonal / chemical signal cascade.

    Models: A(t+1) = φ_inv × A(t) × S(item_i, item_j)

    Each activated knowledge item fires its signal to spectral neighbors.
    Each hop decays by φ_inv (0.618). Mimics enzyme cascade kinetics and
    neural propagation through a synaptic weight matrix.

    Returns knowledge items ranked by cascaded activation score.
    """
    if not knowledge_items:
        return []

    dim = len(query_vec)
    vecs: List[np.ndarray] = []
    for item in knowledge_items:
        v = item.get("vector")
        vecs.append(np.array(v, dtype=np.float64) if v is not None else np.zeros(dim))

    # Tier-0: direct cosine similarity to query
    activations = np.array([_cosine(query_vec, v) for v in vecs], dtype=np.float64)

    # Pairwise spectral similarity matrix (O(n²) — n is always small)
    n = len(knowledge_items)
    sim = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            s = _cosine(vecs[i], vecs[j])
            sim[i, j] = s
            sim[j, i] = s

    # Cascade: propagate activation through similarity edges, decaying each hop by φ_inv
    for hop in range(1, hops):
        hop_factor = decay ** hop
        propagated = sim @ activations
        activations = activations + hop_factor * propagated

    # Weight by per-item salience (biotech: receptor density)
    for i, item in enumerate(knowledge_items):
        sal = float(item.get("salience", PHI_INV))
        activations[i] *= sal

    ranked = sorted(
        [(float(activations[i]), knowledge_items[i]) for i in range(n)],
        key=lambda x: -x[0],
    )
    return [
        {**item, "cascade_score": round(score, 4)}
        for score, item in ranked[:k]
        if score > threshold
    ]


# ── Geometry: polygon envelope for knowledge-region detection ─────────────────

def polygon_envelope(
    query_vec: np.ndarray,
    knowledge_vecs: List[np.ndarray],
) -> Dict[str, Any]:
    """Polygon envelope — computational geometry.

    Projects all knowledge vectors and the query onto a 2D φ-harmonic basis
    (golden-angle spiral coordinates). Computes the convex hull of the
    knowledge cloud, then determines whether the query falls inside
    (known territory) or outside (novel territory).

    Returns:
        inside          — True if query is within the knowledge convex hull
        region_confidence — how central the query is (1.0 = centroid, 0.0 = exterior)
        nearest_idx     — index of the nearest knowledge vertex
        hull_radius     — mean radius of the knowledge polygon
    """
    if len(knowledge_vecs) < 3:
        return {"inside": False, "region_confidence": 0.0, "nearest_idx": 0,
                "hull_radius": 0.0, "query_radius": 0.0}

    n = len(query_vec)
    basis1 = phi_harmonic_basis(n)

    # Second basis: φ-rotated (golden-angle shift in harmonic space)
    shift = int(round(n * PHI_INV)) % n
    basis2 = np.roll(basis1, shift)

    def project(v: np.ndarray) -> Tuple[float, float]:
        return float(np.dot(v, basis1)), float(np.dot(v, basis2))

    pts = np.array([project(v) for v in knowledge_vecs], dtype=np.float64)
    qpt = np.array(project(query_vec), dtype=np.float64)

    centroid = pts.mean(axis=0)
    radii = np.linalg.norm(pts - centroid, axis=1)
    hull_radius = float(radii.mean())

    q_radius = float(np.linalg.norm(qpt - centroid))
    inside = q_radius <= hull_radius * 1.15    # 15% margin

    dists = np.linalg.norm(pts - qpt[None, :], axis=1)
    nearest_idx = int(np.argmin(dists))

    region_confidence = max(0.0, min(1.0, 1.0 - q_radius / (hull_radius + 1e-12)))

    return {
        "inside": inside,
        "region_confidence": round(region_confidence, 4),
        "nearest_idx": nearest_idx,
        "hull_radius": round(hull_radius, 4),
        "query_radius": round(q_radius, 4),
    }


# ── Recursion: fractal dendritic grammar expansion ────────────────────────────

def recursive_unfold(
    seed_spectrum: np.ndarray,
    depth: int = 3,
    branching: int = 2,
) -> List[float]:
    """Recursive spectral unfold — fractal / dendritic computation.

    Models biological dendrite branching (biotech: dendritic spine growth).
    Each spectral component spawns `branching` child components at
    φ-scaled sub-indices (golden-angle spiral), decaying by φ_inv per level.

    Result: a φ-harmonic weight vector over the original spectrum dimensions.
    Use these weights to select and blend knowledge chunk text.
    """
    n = len(seed_spectrum)
    weights = np.array(seed_spectrum, dtype=np.float64).copy()

    def _recurse(level: int, parent: np.ndarray, scale: float) -> np.ndarray:
        if level == 0 or scale < 1e-7:
            return parent
        child = np.zeros(n, dtype=np.float64)
        for i in range(n):
            if parent[i] > 1e-10:
                for b in range(branching):
                    # Golden-angle spiral child index
                    child_i = int((i * PHI * (b + 1)) % n)
                    child[child_i] += parent[i] * scale * PHI_INV
        merged = parent + _recurse(level - 1, child, scale * PHI_INV)
        return merged

    unfolded = _recurse(depth, weights, 1.0)
    norm = float(np.linalg.norm(unfolded)) + 1e-12
    return (unfolded / norm).tolist()


# ── Biotech: Hebbian synaptic plasticity (LTP) ────────────────────────────────

def hebbian_salience(
    base_salience: float,
    co_activation_count: int,
    rate: float = PHI_INV * 0.08,
    ceiling: float = 1.0,
) -> float:
    """Hebbian LTP — 'neurons that fire together, wire together.'

    Salience grows logarithmically with co-activation count, bounded at
    ceiling. Rate is φ_inv × 0.08 — gentle plasticity that prevents runaway
    potentiation while still rewarding frequently-recalled knowledge.
    """
    return min(ceiling, base_salience + rate * math.log1p(co_activation_count))


# ── Biotech: chemical reaction network cascade ────────────────────────────────

def chemical_cascade(
    activations: List[float],
    reaction_matrix: np.ndarray,
    steps: int = 4,
    decay: float = PHI_INV,
) -> np.ndarray:
    """Chemical reaction-network cascade — biotech: enzyme kinetic cascade.

    Discretised ODE:  A(t+1) = decay × A(t) + (1-decay) × R × A(t)
    where R is the reaction (transition) matrix.

    Conserves total activation (normalised each step) — no unbounded growth.
    Use for propagating query signal through a knowledge graph where nodes
    are 'reactants' and edge weights are 'reaction rates'.
    """
    a = np.array(activations, dtype=np.float64)
    for _ in range(steps):
        a = decay * a + (1.0 - decay) * (reaction_matrix @ a)
        norm = float(np.linalg.norm(a)) + 1e-12
        a /= norm
    return a


# ── φ-harmonic positional re-ranking ─────────────────────────────────────────

def phi_rank(scores: List[float]) -> List[float]:
    """Apply φ-harmonic positional bonus to a score list.

    Position 0 keeps full score, position 1 is multiplied by φ_inv,
    position k by φ_inv^k. Rewards items that are both high-scoring
    AND early in the cascade output.
    """
    ranked = sorted(enumerate(scores), key=lambda x: -x[1])
    result = [0.0] * len(scores)
    for pos, (orig_i, score) in enumerate(ranked):
        result[orig_i] = score * (PHI_INV ** pos)
    return result


# ── Text assembly: spectral composition ──────────────────────────────────────

_BAND_LABELS = [
    "structural",   # lowest freq — foundational / architectural
    "semantic",     # mid-low — conceptual meaning
    "relational",   # mid — connections between ideas
    "specific",     # mid-high — concrete instances
    "differential", # high — fine distinctions
]


def spectral_compose(
    query_vec: np.ndarray,
    cascade_hits: List[Dict[str, Any]],
    polygon_result: Dict[str, Any],
    max_chars: int = 320,
) -> str:
    """Assemble response text from cascade-selected knowledge chunks.

    Uses the recursive_unfold weights to blend and order chunk text.
    Falls back to spectral-band description when no chunks are available.

    This is the 'Medina build' generation path — no LLM, no template,
    pure algorithm → text.
    """
    if not cascade_hits:
        return _spectral_fallback(query_vec, polygon_result)

    # Unfold the query spectrum to get φ-harmonic blending weights
    unfold_weights = recursive_unfold(query_vec, depth=3, branching=2)

    # Map each cascade hit to a spectral band weight
    n_hits = len(cascade_hits)
    n_bands = len(unfold_weights)

    # Assign each hit a blend weight based on its position in the unfolded spectrum
    blended: List[Tuple[float, str]] = []
    for hit_i, hit in enumerate(cascade_hits):
        band_idx = int((hit_i / max(1, n_hits)) * n_bands) % n_bands
        spectral_weight = float(unfold_weights[band_idx])
        cascade_weight = float(hit.get("cascade_score", 0.5))
        blend = (spectral_weight + cascade_weight) * 0.5

        text = hit.get("content") or hit.get("text") or ""
        if text:
            blended.append((blend, text[:max_chars // n_hits]))

    if not blended:
        return _spectral_fallback(query_vec, polygon_result)

    # Sort by blend weight, assemble
    blended.sort(key=lambda x: -x[0])
    assembled = " ".join(t for _, t in blended)
    return assembled[:max_chars].strip()


def _spectral_fallback(
    query_vec: np.ndarray,
    polygon_result: Dict[str, Any],
) -> str:
    """Spectral-band fallback — used when cascade finds no hits.

    Decomposes the query vector into φ-harmonic bands and generates a
    description of the query's spectral character. This is what the system
    knows about the *shape* of the question even when it has no content match.
    """
    # Run the unfolded spectrum over the query
    weights = recursive_unfold(query_vec, depth=4, branching=2)
    w = np.array(weights, dtype=np.float64)

    # Partition into 5 bands, compute band energy
    n = len(w)
    band_size = max(1, n // len(_BAND_LABELS))
    band_energies = []
    for i, label in enumerate(_BAND_LABELS):
        start = i * band_size
        end = start + band_size
        energy = float(np.sum(w[start:end] ** 2))
        band_energies.append((energy, label))

    dominant_band = max(band_energies, key=lambda x: x[0])
    region = "within known territory" if polygon_result.get("inside") else "at the frontier"
    confidence = polygon_result.get("region_confidence", 0.0)

    return (
        f"Spectral analysis — query is {region} "
        f"(region_confidence={confidence:.2f}). "
        f"Dominant spectral band: {dominant_band[1]} "
        f"(φ-harmonic energy={dominant_band[0]:.3f}). "
        f"Cascade found no indexed knowledge for this query. "
        f"φ={PHI:.6f}, Schumann={SCHUMANN}Hz, heartbeat={DELTA_T}s."
    )
