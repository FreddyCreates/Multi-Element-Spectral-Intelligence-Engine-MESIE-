"""Task allocation — particle swarm optimization + lightweight MARL assignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

import numpy as np


@dataclass
class SwarmTask:
    task_id: str
    task_type: str
    priority: float
    position: np.ndarray
    spectral_urgency: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "priority": self.priority,
            "position": self.position.tolist(),
            "spectral_urgency": self.spectral_urgency,
        }


@dataclass
class TaskAssignment:
    agent_id: str
    task_id: str
    cost: float
    method: str

    def to_dict(self) -> Dict[str, Any]:
        return {"agent_id": self.agent_id, "task_id": self.task_id, "cost": self.cost, "method": self.method}


@dataclass
class AllocationReport:
    n_agents: int
    n_tasks: int
    assignments: List[TaskAssignment]
    total_cost: float
    method: str
    coverage: float
    ok: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_agents": self.n_agents,
            "n_tasks": self.n_tasks,
            "assignments": [a.to_dict() for a in self.assignments],
            "total_cost": self.total_cost,
            "method": self.method,
            "coverage": self.coverage,
            "ok": self.ok,
        }


def _agent_positions(n: int, rng: np.random.Generator) -> np.ndarray:
    side = int(np.ceil(np.sqrt(n)))
    pts = []
    for i in range(n):
        pts.append([(i % side) * 10.0, (i // side) * 10.0, rng.uniform(0, 5)])
    return np.asarray(pts, dtype=np.float64)


class ParticleSwarmAllocator:
    """PSO assigns agents to tasks by minimizing distance + spectral urgency."""

    def __init__(self, *, n_particles: int = 30, iterations: int = 25, seed: int = 42) -> None:
        self.n_particles = n_particles
        self.iterations = iterations
        self.rng = np.random.default_rng(seed)

    def allocate(
        self,
        n_agents: int,
        tasks: Sequence[SwarmTask],
    ) -> AllocationReport:
        if not tasks or n_agents == 0:
            return AllocationReport(0, 0, [], 0.0, "pso", 0.0, False)
        agents = _agent_positions(n_agents, self.rng)
        task_pos = np.stack([t.position for t in tasks])
        urg = np.array([t.spectral_urgency * t.priority for t in tasks])
        n_t = len(tasks)
        dim = n_agents * n_t
        lo, hi = 0.0, 1.0
        particles = self.rng.uniform(lo, hi, (self.n_particles, dim))
        velocities = self.rng.uniform(-0.1, 0.1, (self.n_particles, dim))
        pbest = particles.copy()
        pbest_cost = np.array([self._cost(p, agents, task_pos, urg, n_agents, n_t) for p in particles])
        gbest_idx = int(np.argmin(pbest_cost))
        gbest = pbest[gbest_idx].copy()
        gbest_cost = float(pbest_cost[gbest_idx])

        for _ in range(self.iterations):
            r1 = self.rng.random((self.n_particles, dim))
            r2 = self.rng.random((self.n_particles, dim))
            velocities = 0.7 * velocities + 1.4 * r1 * (pbest - particles) + 1.4 * r2 * (gbest - particles)
            particles = np.clip(particles + velocities, lo, hi)
            costs = np.array([self._cost(p, agents, task_pos, urg, n_agents, n_t) for p in particles])
            improved = costs < pbest_cost
            pbest[improved] = particles[improved]
            pbest_cost[improved] = costs[improved]
            if costs.min() < gbest_cost:
                gbest_idx = int(np.argmin(costs))
                gbest = particles[gbest_idx].copy()
                gbest_cost = float(costs[gbest_idx])

        matrix = gbest.reshape(n_agents, n_t)
        assignments: List[TaskAssignment] = []
        used_tasks: set[int] = set()
        for i in range(n_agents):
            order = np.argsort(-matrix[i])
            for j in order:
                if j not in used_tasks:
                    used_tasks.add(j)
                    dist = float(np.linalg.norm(agents[i] - task_pos[j]))
                    cost = dist + (1.0 - urg[j]) * 10.0
                    assignments.append(
                        TaskAssignment(f"agent_{i:05d}", tasks[j].task_id, round(cost, 3), "pso")
                    )
                    break
        total = sum(a.cost for a in assignments)
        coverage = len(assignments) / min(n_agents, n_t)
        return AllocationReport(
            n_agents=n_agents,
            n_tasks=n_t,
            assignments=assignments,
            total_cost=round(total, 3),
            method="particle_swarm",
            coverage=round(coverage, 4),
            ok=coverage >= 0.8,
        )

    @staticmethod
    def _cost(
        particle: np.ndarray,
        agents: np.ndarray,
        task_pos: np.ndarray,
        urg: np.ndarray,
        n_a: int,
        n_t: int,
    ) -> float:
        m = particle.reshape(n_a, n_t)
        cost = 0.0
        for j in range(n_t):
            i = int(np.argmax(m[:, j]))
            cost += float(np.linalg.norm(agents[i] - task_pos[j])) + (1.0 - urg[j]) * 5.0
        return cost


class MARLTaskAllocator:
    """Lightweight decentralized Q-table assignment — no external RL lib."""

    def __init__(self, *, seed: int = 42) -> None:
        self.rng = np.random.default_rng(seed)
        self.q: Dict[str, float] = {}

    def allocate(self, n_agents: int, tasks: Sequence[SwarmTask]) -> AllocationReport:
        agents = _agent_positions(n_agents, self.rng)
        assignments: List[TaskAssignment] = []
        for i in range(min(n_agents, len(tasks))):
            best_j, best_cost = 0, 1e18
            for j, task in enumerate(tasks):
                key = f"{i}:{task.task_id}"
                q = self.q.get(key, 0.0)
                dist = float(np.linalg.norm(agents[i] - task.position))
                cost = dist - q * 2.0 + (1.0 - task.spectral_urgency) * 5.0
                if cost < best_cost:
                    best_j, best_cost = j, cost
            task = tasks[best_j]
            reward = task.priority * task.spectral_urgency
            self.q[f"{i}:{task.task_id}"] = self.q.get(f"{i}:{task.task_id}", 0.0) + 0.1 * reward
            assignments.append(
                TaskAssignment(f"agent_{i:05d}", task.task_id, round(best_cost, 3), "marl_local")
            )
        total = sum(a.cost for a in assignments)
        coverage = len(assignments) / max(len(tasks), 1)
        return AllocationReport(
            n_agents=n_agents,
            n_tasks=len(tasks),
            assignments=assignments,
            total_cost=round(total, 3),
            method="marl_local",
            coverage=round(coverage, 4),
            ok=coverage >= 0.5,
        )