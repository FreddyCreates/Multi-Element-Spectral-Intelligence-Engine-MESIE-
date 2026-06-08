"""Formation control — flocking rules, collision avoidance, attrition reform."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

import numpy as np


@dataclass
class DronePose:
    agent_id: str
    position: np.ndarray
    velocity: np.ndarray
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "position": self.position.tolist(),
            "velocity": self.velocity.tolist(),
            "active": self.active,
        }


@dataclass
class FormationReport:
    formation: str
    n_agents: int
    n_active: int
    min_separation_m: float
    collisions_avoided: int
    reform_after_attrition: bool
    cohesion: float
    ok: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "formation": self.formation,
            "n_agents": self.n_agents,
            "n_active": self.n_active,
            "min_separation_m": self.min_separation_m,
            "collisions_avoided": self.collisions_avoided,
            "reform_after_attrition": self.reform_after_attrition,
            "cohesion": self.cohesion,
            "ok": self.ok,
        }


class FormationController:
    """Boids-inspired local rules — separation, alignment, cohesion."""

    def __init__(
        self,
        *,
        separation_radius_m: float = 5.0,
        min_sep_m: float = 2.0,
        seed: int = 42,
    ) -> None:
        self.separation_radius = separation_radius_m
        self.min_sep = min_sep_m
        self.rng = np.random.default_rng(seed)

    def spawn_grid(self, n: int, *, spacing_m: float = 10.0) -> List[DronePose]:
        side = int(np.ceil(np.sqrt(n)))
        poses: List[DronePose] = []
        for i in range(n):
            x = (i % side) * spacing_m
            y = (i // side) * spacing_m
            poses.append(
                DronePose(
                    agent_id=f"drone_{i:05d}",
                    position=np.array([x, y, 0.0]),
                    velocity=self.rng.normal(0, 0.5, 3),
                )
            )
        return poses

    def step(
        self,
        poses: List[DronePose],
        *,
        target: np.ndarray | None = None,
        dt: float = 0.1,
    ) -> Tuple[List[DronePose], int]:
        target = target if target is not None else np.zeros(3)
        collisions = 0
        active = [p for p in poses if p.active]
        for p in active:
            sep = np.zeros(3)
            ali = np.zeros(3)
            coh = np.zeros(3)
            neighbors = 0
            for q in active:
                if q.agent_id == p.agent_id:
                    continue
                d = q.position - p.position
                dist = float(np.linalg.norm(d))
                if dist < self.separation_radius:
                    neighbors += 1
                    if dist < self.min_sep:
                        collisions += 1
                        sep -= d / max(dist, 1e-6)
                    ali += q.velocity
                    coh += q.position
            if neighbors > 0:
                ali /= neighbors
                coh = (coh / neighbors) - p.position
            to_target = target - p.position
            steer = 0.4 * sep + 0.2 * ali + 0.15 * coh + 0.25 * to_target
            p.velocity = 0.8 * p.velocity + 0.2 * steer
            p.position = p.position + p.velocity * dt
        return poses, collisions

    def apply_attrition(self, poses: List[DronePose], rate: float) -> List[DronePose]:
        n = len(poses)
        drop = int(n * rate)
        if drop <= 0:
            return poses
        idx = set(self.rng.choice(n, size=drop, replace=False).tolist())
        for i in idx:
            poses[i].active = False
        return poses

    def reform_v_shape(self, poses: List[DronePose]) -> FormationReport:
        active = [p for p in poses if p.active]
        n = len(poses)
        if not active:
            return FormationReport("v_shape", n, 0, 0.0, 0, False, 0.0, False)
        leader = active[0]
        for i, p in enumerate(active[1:], 1):
            wing = 1 if i % 2 else -1
            row = (i + 1) // 2
            p.position = leader.position + np.array([row * 8.0, wing * row * 6.0, 0.0])
            p.velocity = leader.velocity * 0.9
        mins = []
        for i, a in enumerate(active):
            for b in active[i + 1 :]:
                mins.append(float(np.linalg.norm(a.position - b.position)))
        min_sep = min(mins) if mins else 999.0
        center = np.mean([p.position for p in active], axis=0)
        cohesion = float(np.mean([np.linalg.norm(p.position - center) for p in active]))
        return FormationReport(
            formation="v_shape",
            n_agents=n,
            n_active=len(active),
            min_separation_m=round(min_sep, 3),
            collisions_avoided=0,
            reform_after_attrition=len(active) < n,
            cohesion=round(cohesion, 3),
            ok=min_sep >= self.min_sep and len(active) >= max(1, n // 2),
        )

    def simulate(
        self,
        n_agents: int,
        *,
        steps: int = 20,
        attrition_rate: float = 0.0,
    ) -> FormationReport:
        poses = self.spawn_grid(n_agents)
        target = np.array([100.0, 50.0, 20.0])
        total_collisions = 0
        for _ in range(steps // 2):
            poses, c = self.step(poses, target=target)
            total_collisions += c
        if attrition_rate > 0:
            poses = self.apply_attrition(poses, attrition_rate)
        for _ in range(steps // 2):
            poses, c = self.step(poses, target=target)
            total_collisions += c
        rep = self.reform_v_shape(poses)
        rep.collisions_avoided = max(0, total_collisions)
        return rep