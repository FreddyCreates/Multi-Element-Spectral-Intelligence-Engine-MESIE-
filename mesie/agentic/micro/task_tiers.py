"""Task tiers — light pulse on boot, heavy work on long intervals."""

from __future__ import annotations

from enum import Enum

from mesie.agentic.micro.career import MicroCareer


class TaskTier(str, Enum):
    LIGHT = "light"      # <50ms typical — safe on simultaneous boot
    MEDIUM = "medium"    # subprocess / HTTP
    HEAVY = "heavy"      # pytest, full benchmark, embed library


CAREER_TIERS: dict[MicroCareer, TaskTier] = {
    MicroCareer.LINGUIST: TaskTier.LIGHT,
    MicroCareer.TRANSLATOR: TaskTier.LIGHT,
    MicroCareer.COGNITIVE: TaskTier.LIGHT,
    MicroCareer.EMBEDDER: TaskTier.MEDIUM,
    MicroCareer.MATCHER: TaskTier.MEDIUM,
    MicroCareer.FINGERPRINT_GUARD: TaskTier.LIGHT,
    MicroCareer.RETRIEVER: TaskTier.LIGHT,
    MicroCareer.SALIENCE_ROUTER: TaskTier.LIGHT,
    MicroCareer.RELEASE_SENTINEL: TaskTier.HEAVY,
    MicroCareer.VERSION_AUDITOR: TaskTier.LIGHT,
    MicroCareer.MANIFEST_WRITER: TaskTier.MEDIUM,
    MicroCareer.SCHEMA_VALIDATOR: TaskTier.LIGHT,
    MicroCareer.READINESS_GATE: TaskTier.MEDIUM,
    MicroCareer.DETERMINISM_CHECKER: TaskTier.MEDIUM,
    MicroCareer.SATELLITE_WATCH: TaskTier.LIGHT,
    MicroCareer.HEALTH_MONITOR: TaskTier.LIGHT,
    MicroCareer.PORT_WATCH: TaskTier.LIGHT,
    MicroCareer.LOG_TRIAGE: TaskTier.LIGHT,
    MicroCareer.BENCHMARK_RUNNER: TaskTier.HEAVY,
    MicroCareer.SLA_WATCHER: TaskTier.LIGHT,
    MicroCareer.ROBOTICS_SATELLITE: TaskTier.LIGHT,
    MicroCareer.SCHEMA_DESIGNER: TaskTier.LIGHT,
    MicroCareer.API_CONTRACT_AUDITOR: TaskTier.LIGHT,
    MicroCareer.SURFACE_MAPPER: TaskTier.MEDIUM,
    MicroCareer.DOC_SYNTHESIZER: TaskTier.LIGHT,
    MicroCareer.ARCHITECTURE_REVIEWER: TaskTier.LIGHT,
    MicroCareer.DOCTRINE_CURATOR: TaskTier.LIGHT,
    MicroCareer.SURFACE_BRIDGE: TaskTier.LIGHT,
    MicroCareer.MCP_WIRING: TaskTier.LIGHT,
    MicroCareer.REPO_SCANNER: TaskTier.LIGHT,
    MicroCareer.BUS_ROUTER: TaskTier.LIGHT,
    MicroCareer.LOOM_BRIDGE: TaskTier.LIGHT,
    MicroCareer.CODING_LAB_BRIDGE: TaskTier.LIGHT,
    MicroCareer.MEMORY_DESK_BRIDGE: TaskTier.LIGHT,
    MicroCareer.PROCESSOR_BRIDGE: TaskTier.LIGHT,
    MicroCareer.PYTHON_ARM: TaskTier.MEDIUM,
    MicroCareer.RUST_ARM: TaskTier.MEDIUM,
    MicroCareer.JULIA_ARM: TaskTier.MEDIUM,
    MicroCareer.TYPESCRIPT_ARM: TaskTier.MEDIUM,
    MicroCareer.MOTOKO_ARM: TaskTier.MEDIUM,
    MicroCareer.ORBITAL_ANALYST: TaskTier.LIGHT,
    MicroCareer.SEISMIC_WATCH: TaskTier.LIGHT,
    MicroCareer.ROBOTICS_COORD: TaskTier.LIGHT,
    MicroCareer.POWER_GRID: TaskTier.LIGHT,
    MicroCareer.TERRAIN_MAPPER: TaskTier.LIGHT,
    MicroCareer.ENTERPRISE_MONTE: TaskTier.LIGHT,
    MicroCareer.LOGIC_PROVER_CARETAKER: TaskTier.LIGHT,
    MicroCareer.PATTERN_FORGE_CARETAKER: TaskTier.LIGHT,
    MicroCareer.EMERGENCE_WATCHER: TaskTier.LIGHT,
    MicroCareer.ADAPTATION_TUNER: TaskTier.LIGHT,
    MicroCareer.VAULT_CURATOR: TaskTier.LIGHT,
    MicroCareer.RECEIPT_CHAIN: TaskTier.LIGHT,
    MicroCareer.KNOWLEDGE_INDEXER: TaskTier.MEDIUM,
    MicroCareer.SOVEREIGN_GATE: TaskTier.LIGHT,
    MicroCareer.INTERIOR_DATACENTER: TaskTier.LIGHT,
    # Infrastructure IT — new careers
    MicroCareer.ENGINE_REGISTRY_KEEPER: TaskTier.LIGHT,
    MicroCareer.PROTOCOL_EXECUTOR: TaskTier.MEDIUM,
    MicroCareer.LAW_COMPILER: TaskTier.LIGHT,
    MicroCareer.CHARTER_KEEPER: TaskTier.LIGHT,
    MicroCareer.LIBRARY_FEEDER: TaskTier.HEAVY,
    MicroCareer.SIGNAL_ROUTER: TaskTier.MEDIUM,
    MicroCareer.PHYSICS_FOUNDATION: TaskTier.MEDIUM,
    MicroCareer.EDGE_PROTOCOL_OPS: TaskTier.MEDIUM,
    MicroCareer.OCTOPUS_CONTROLLER: TaskTier.MEDIUM,
    MicroCareer.WORKFLOW_ORCHESTRATOR: TaskTier.MEDIUM,
    MicroCareer.DOMAIN_SIGNAL_HUB: TaskTier.MEDIUM,
    MicroCareer.TRAINING_CORPUS_CURATOR: TaskTier.HEAVY,
    MicroCareer.SHOWCASE_BROADCASTER: TaskTier.HEAVY,
    MicroCareer.DEVKIT_PACKAGER: TaskTier.MEDIUM,
    MicroCareer.PROCESSOR_RELEASE_GATE: TaskTier.MEDIUM,
}


def tier_for(career: MicroCareer) -> TaskTier:
    return CAREER_TIERS.get(career, TaskTier.MEDIUM)