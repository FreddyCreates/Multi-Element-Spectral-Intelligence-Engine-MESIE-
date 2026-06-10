"""Influence and communication modeled through force analogies."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from mesie.spacetime.agents import SpatialAgent


def gravitational_influence(source: SpatialAgent, target: SpatialAgent, *, G: float = 1.0, eps: float = 0.5) -> Tuple[float, Tuple[float, float, float]]:
    """Attraction magnitude and unit direction — authority/influence analogy."""
    a = np.array(source.position, dtype=float)
    b = np.array(target.position, dtype=float)
    delta = a - b
    r = float(np.linalg.norm(delta) + eps)
    magnitude = G * source.influence_mass * target.influence_mass / (r * r)
    direction = tuple((delta / r).tolist())
    return magnitude, direction  # type: ignore[return-value]


def communication_reach(source: SpatialAgent, target: SpatialAgent, *, range_limit: float = 20.0) -> bool:
    return source.distance_to(target) <= range_limit


def influence_matrix(agents: List[SpatialAgent]) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    for s in agents:
        out[s.agent_id] = {}
        for t in agents:
            if s.agent_id == t.agent_id:
                continue
            mag, _ = gravitational_influence(s, t)
            out[s.agent_id][t.agent_id] = round(mag, 6)
    return out