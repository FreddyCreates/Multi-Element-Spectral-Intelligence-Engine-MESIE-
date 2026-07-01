"""Micro-agent careers — 55-role NOVA production organization."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple


class MicroTeam(str, Enum):
    INTELLIGENCE = "intelligence"
    RELEASE = "release"
    OPERATIONS = "operations"
    DESIGN = "design"
    INTEGRATION = "integration"
    POLYGLOT = "polyglot"
    DOMAINS = "domains"
    SOLUS = "solus"
    MEMORY = "memory"
    INFRASTRUCTURE = "infrastructure"  # IT — runs the whole stack
    FOUNDATIONS = "foundations"        # laws, physics, protocols, signals


class MicroCareer(str, Enum):
    # Intelligence — spectral cognition
    LINGUIST = "linguist"
    TRANSLATOR = "translator"
    COGNITIVE = "cognitive"
    EMBEDDER = "embedder"
    MATCHER = "matcher"
    FINGERPRINT_GUARD = "fingerprint_guard"
    RETRIEVER = "retriever"
    SALIENCE_ROUTER = "salience_router"
    # Release — ship gates
    RELEASE_SENTINEL = "release_sentinel"
    VERSION_AUDITOR = "version_auditor"
    MANIFEST_WRITER = "manifest_writer"
    SCHEMA_VALIDATOR = "schema_validator"
    READINESS_GATE = "readiness_gate"
    DETERMINISM_CHECKER = "determinism_checker"
    # Operations — keep the lab alive
    SATELLITE_WATCH = "satellite_watch"
    HEALTH_MONITOR = "health_monitor"
    PORT_WATCH = "port_watch"
    LOG_TRIAGE = "log_triage"
    BENCHMARK_RUNNER = "benchmark_runner"
    SLA_WATCHER = "sla_watcher"
    ROBOTICS_SATELLITE = "robotics_satellite"
    # Design — systems thinking
    SCHEMA_DESIGNER = "schema_designer"
    API_CONTRACT_AUDITOR = "api_contract_auditor"
    SURFACE_MAPPER = "surface_mapper"
    DOC_SYNTHESIZER = "doc_synthesizer"
    ARCHITECTURE_REVIEWER = "architecture_reviewer"
    DOCTRINE_CURATOR = "doctrine_curator"
    # Integration — wiring
    SURFACE_BRIDGE = "surface_bridge"
    MCP_WIRING = "mcp_wiring"
    REPO_SCANNER = "repo_scanner"
    BUS_ROUTER = "bus_router"
    LOOM_BRIDGE = "loom_bridge"
    CODING_LAB_BRIDGE = "coding_lab_bridge"
    MEMORY_DESK_BRIDGE = "memory_desk_bridge"
    PROCESSOR_BRIDGE = "processor_bridge"
    # Polyglot — language arms
    PYTHON_ARM = "python_arm"
    RUST_ARM = "rust_arm"
    JULIA_ARM = "julia_arm"
    TYPESCRIPT_ARM = "typescript_arm"
    MOTOKO_ARM = "motoko_arm"
    # Domains — field specialists
    ORBITAL_ANALYST = "orbital_analyst"
    SEISMIC_WATCH = "seismic_watch"
    ROBOTICS_COORD = "robotics_coord"
    POWER_GRID = "power_grid"
    TERRAIN_MAPPER = "terrain_mapper"
    ENTERPRISE_MONTE = "enterprise_monte"
    # SOLUS — formal organism
    LOGIC_PROVER_CARETAKER = "logic_prover_caretaker"
    PATTERN_FORGE_CARETAKER = "pattern_forge_caretaker"
    EMERGENCE_WATCHER = "emergence_watcher"
    ADAPTATION_TUNER = "adaptation_tuner"
    # Memory — sovereign vault
    VAULT_CURATOR = "vault_curator"
    RECEIPT_CHAIN = "receipt_chain"
    KNOWLEDGE_INDEXER = "knowledge_indexer"
    SOVEREIGN_GATE = "sovereign_gate"
    INTERIOR_DATACENTER = "interior_datacenter"
    # Infrastructure IT — orchestrate engines, laws, library, release
    ENGINE_REGISTRY_KEEPER = "engine_registry_keeper"
    PROTOCOL_EXECUTOR = "protocol_executor"
    LAW_COMPILER = "law_compiler"
    CHARTER_KEEPER = "charter_keeper"
    LIBRARY_FEEDER = "library_feeder"
    SIGNAL_ROUTER = "signal_router"
    PHYSICS_FOUNDATION = "physics_foundation"
    EDGE_PROTOCOL_OPS = "edge_protocol_ops"
    OCTOPUS_CONTROLLER = "octopus_controller"
    WORKFLOW_ORCHESTRATOR = "workflow_orchestrator"
    DOMAIN_SIGNAL_HUB = "domain_signal_hub"
    TRAINING_CORPUS_CURATOR = "training_corpus_curator"
    SHOWCASE_BROADCASTER = "showcase_broadcaster"
    DEVKIT_PACKAGER = "devkit_packager"
    PROCESSOR_RELEASE_GATE = "processor_release_gate"


@dataclass
class CareerSpec:
    career: MicroCareer
    team: MicroTeam
    title: str
    mission: str
    default_interval_s: float = 60.0
    engines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "career": self.career.value,
            "team": self.team.value,
            "title": self.title,
            "mission": self.mission,
            "default_interval_s": self.default_interval_s,
            "engines": self.engines,
        }


_CAREER_DEFS: List[Tuple[MicroCareer, MicroTeam, str, str, float, List[str]]] = [
    (MicroCareer.LINGUIST, MicroTeam.INTELLIGENCE, "Linguistic Analyst",
     "Coherence, doctrine attractors, φ-weighted language geometry.", 45.0, ["lingua", "auro"]),
    (MicroCareer.TRANSLATOR, MicroTeam.INTELLIGENCE, "Modality Translator",
     "Map text/spectral/state into unified MESIE records.", 30.0, ["translator", "embed"]),
    (MicroCareer.COGNITIVE, MicroTeam.INTELLIGENCE, "Adaptive Cognitive Router",
     "Intent routing, salience, adaptive policy on MESIE bus.", 20.0, ["cognitive", "match"]),
    (MicroCareer.EMBEDDER, MicroTeam.INTELLIGENCE, "Spectral Embed Guard",
     "Vectorize and fingerprint incoming knowledge fragments.", 90.0, ["embed", "fingerprint"]),
    (MicroCareer.MATCHER, MicroTeam.INTELLIGENCE, "Spectral Matcher",
     "Composite-score match pairs from bundled reference library.", 75.0, ["match"]),
    (MicroCareer.FINGERPRINT_GUARD, MicroTeam.INTELLIGENCE, "Fingerprint Sentinel",
     "TF → salient → LSH pipeline health on library index.", 120.0, ["fingerprint", "lsh"]),
    (MicroCareer.RETRIEVER, MicroTeam.INTELLIGENCE, "Top-K Retriever",
     "Rank query spectrum against candidate pool.", 80.0, ["rank", "retrieval"]),
    (MicroCareer.SALIENCE_ROUTER, MicroTeam.INTELLIGENCE, "Salience Router",
     "Route intent by domain salience and policy.", 25.0, ["cognitive", "salience"]),
    (MicroCareer.RELEASE_SENTINEL, MicroTeam.RELEASE, "Release Sentinel",
     "Run pytest gates and readiness checks on timer.", 300.0, ["test", "readiness"]),
    (MicroCareer.VERSION_AUDITOR, MicroTeam.RELEASE, "Version Auditor",
     "Verify canonical version_info vs pyproject vs tests.", 180.0, ["version"]),
    (MicroCareer.MANIFEST_WRITER, MicroTeam.RELEASE, "Manifest Writer",
     "Export NOVA/MININOVA/MESIE/Surface production manifests.", 120.0, ["manifest"]),
    (MicroCareer.SCHEMA_VALIDATOR, MicroTeam.RELEASE, "Schema Validator",
     "Validate bundled references against MESIE schema levels.", 150.0, ["validate"]),
    (MicroCareer.READINESS_GATE, MicroTeam.RELEASE, "Readiness Gate",
     "Full MESIE release readiness check — bootstrap, copilot, auro.", 240.0, ["readiness"]),
    (MicroCareer.DETERMINISM_CHECKER, MicroTeam.RELEASE, "Determinism Checker",
     "Verify seeded PSD/FAS generation is reproducible.", 200.0, ["determinism", "benchmark"]),
    (MicroCareer.SATELLITE_WATCH, MicroTeam.OPERATIONS, "Fleet Watch",
     "Heartbeat + health telemetry for full micro organization.", 15.0, ["health"]),
    (MicroCareer.HEALTH_MONITOR, MicroTeam.OPERATIONS, "Health Monitor",
     "MESIE bootstrap, SDK import, engine registry alive.", 30.0, ["health"]),
    (MicroCareer.PORT_WATCH, MicroTeam.OPERATIONS, "Port Watch",
     "Probe lab services: Memory Desk, Surface, Coding Lab, Processor.", 20.0, ["ports"]),
    (MicroCareer.LOG_TRIAGE, MicroTeam.OPERATIONS, "Log Triage",
     "Scan lab run logs and recent deliverable failures.", 60.0, ["logs"]),
    (MicroCareer.BENCHMARK_RUNNER, MicroTeam.OPERATIONS, "Benchmark Runner",
     "Run fast-compute / major benchmark slice.", 360.0, ["benchmark"]),
    (MicroCareer.SLA_WATCHER, MicroTeam.OPERATIONS, "SLA Watcher",
     "Read major benchmark deliverable — threat p50, win rate.", 180.0, ["sla"]),
    (MicroCareer.ROBOTICS_SATELLITE, MicroTeam.OPERATIONS, "Robotics Satellite",
     "Processor robotics satellite loop evidence on disk.", 120.0, ["robotics"]),
    (MicroCareer.SCHEMA_DESIGNER, MicroTeam.DESIGN, "Schema Designer",
     "Audit MESIE schema levels and record shape contracts.", 300.0, ["schema", "design"]),
    (MicroCareer.API_CONTRACT_AUDITOR, MicroTeam.DESIGN, "API Contract Auditor",
     "Surface + lab HTTP contract consistency.", 240.0, ["api", "design"]),
    (MicroCareer.SURFACE_MAPPER, MicroTeam.DESIGN, "Surface Mapper",
     "Map systems, papers, deliverables into agent catalog.", 150.0, ["surface"]),
    (MicroCareer.DOC_SYNTHESIZER, MicroTeam.DESIGN, "Doc Synthesizer",
     "Index papers and docs for agent retrieval.", 200.0, ["docs"]),
    (MicroCareer.ARCHITECTURE_REVIEWER, MicroTeam.DESIGN, "Architecture Reviewer",
     "Nine-engine registry + octopus arm topology.", 270.0, ["engines"]),
    (MicroCareer.DOCTRINE_CURATOR, MicroTeam.DESIGN, "Doctrine Curator",
     "φ-weighted doctrine attractors and world doctrine refs.", 180.0, ["doctrine"]),
    (MicroCareer.SURFACE_BRIDGE, MicroTeam.INTEGRATION, "Surface Bridge",
     "HTTP invoke Medina Surface status + manifest.", 45.0, ["surface", "http"]),
    (MicroCareer.MCP_WIRING, MicroTeam.INTEGRATION, "MCP Wiring",
     "Loom MCP descriptors + skills map integrity.", 90.0, ["mcp", "loom"]),
    (MicroCareer.REPO_SCANNER, MicroTeam.INTEGRATION, "Repo Fleet Scanner",
     "Scan Medina repo fleet — git + workspace roots.", 120.0, ["repos"]),
    (MicroCareer.BUS_ROUTER, MicroTeam.INTEGRATION, "Internal Bus Router",
     "Engine bus routing — validate + match envelope.", 60.0, ["bus"]),
    (MicroCareer.LOOM_BRIDGE, MicroTeam.INTEGRATION, "Loom Vault Bridge",
     "Medina vault .medina tier health.", 75.0, ["loom", "vault"]),
    (MicroCareer.CODING_LAB_BRIDGE, MicroTeam.INTEGRATION, "Coding Lab Bridge",
     "Medina Coding Lab API health + repo count.", 30.0, ["coding-lab"]),
    (MicroCareer.MEMORY_DESK_BRIDGE, MicroTeam.INTEGRATION, "Memory Desk Bridge",
     "Sovereign Memory Desk API health.", 35.0, ["memory-desk"]),
    (MicroCareer.PROCESSOR_BRIDGE, MicroTeam.INTEGRATION, "Processor Bridge",
     "Virtual Processor HTTP :8750 health.", 40.0, ["processor"]),
    (MicroCareer.PYTHON_ARM, MicroTeam.POLYGLOT, "Python Arm",
     "AISVectorPolyglot Python runtime — embed/match/validate.", 50.0, ["python", "polyglot"]),
    (MicroCareer.RUST_ARM, MicroTeam.POLYGLOT, "Rust Arm",
     "Rust polyglot arm — match parity lane.", 55.0, ["rust", "polyglot"]),
    (MicroCareer.JULIA_ARM, MicroTeam.POLYGLOT, "Julia Arm",
     "Julia polyglot arm — spectral compute lane.", 55.0, ["julia", "polyglot"]),
    (MicroCareer.TYPESCRIPT_ARM, MicroTeam.POLYGLOT, "TypeScript Arm",
     "TypeScript polyglot arm — edge/API lane.", 60.0, ["typescript", "polyglot"]),
    (MicroCareer.MOTOKO_ARM, MicroTeam.POLYGLOT, "Motoko Arm",
     "Motoko polyglot arm — validate/canister lane.", 65.0, ["motoko", "polyglot"]),
    (MicroCareer.ORBITAL_ANALYST, MicroTeam.DOMAINS, "Orbital Analyst",
     "50-day orbital edge analysis deliverable freshness.", 400.0, ["orbital"]),
    (MicroCareer.SEISMIC_WATCH, MicroTeam.DOMAINS, "Seismic Watch",
     "Seismic domain suite reference integrity.", 400.0, ["seismic"]),
    (MicroCareer.ROBOTICS_COORD, MicroTeam.DOMAINS, "Robotics Coordinator",
     "Robotics domain + drone swarm evidence.", 350.0, ["robotics", "swarm"]),
    (MicroCareer.POWER_GRID, MicroTeam.DOMAINS, "Power Grid Analyst",
     "Power domain spectral suite health.", 400.0, ["power"]),
    (MicroCareer.TERRAIN_MAPPER, MicroTeam.DOMAINS, "Terrain Mapper",
     "Terrain domain analysis references.", 400.0, ["terrain"]),
    (MicroCareer.ENTERPRISE_MONTE, MicroTeam.DOMAINS, "Monte Carlo Sentinel",
     "Enterprise Monte Carlo deliverable win rate.", 300.0, ["monte-carlo"]),
    (MicroCareer.LOGIC_PROVER_CARETAKER, MicroTeam.SOLUS, "Logic Prover Caretaker",
     "SOLUS Logic formal model pulse.", 240.0, ["logic-prover"]),
    (MicroCareer.PATTERN_FORGE_CARETAKER, MicroTeam.SOLUS, "Pattern Forge Caretaker",
     "Pattern Forge φ-harmonics + spectral decompose.", 240.0, ["pattern-forge"]),
    (MicroCareer.EMERGENCE_WATCHER, MicroTeam.SOLUS, "Emergence Watcher",
     "SOLUS Emergence model organism pulse.", 200.0, ["emergence"]),
    (MicroCareer.ADAPTATION_TUNER, MicroTeam.SOLUS, "Adaptation Tuner",
     "SOLUS Adaptation policy tuning evidence.", 200.0, ["adaptation"]),
    (MicroCareer.VAULT_CURATOR, MicroTeam.MEMORY, "Vault Curator",
     "Medina vault tiers + skill count.", 90.0, ["vault"]),
    (MicroCareer.RECEIPT_CHAIN, MicroTeam.MEMORY, "Receipt Chain",
     "Enterprise receipt chain deliverable integrity.", 150.0, ["receipt"]),
    (MicroCareer.KNOWLEDGE_INDEXER, MicroTeam.MEMORY, "Knowledge Indexer",
     "Research + technical catalog search pulse.", 120.0, ["knowledge"]),
    (MicroCareer.SOVEREIGN_GATE, MicroTeam.MEMORY, "Sovereign Gate",
     "Sovereign local 120 report existence + third_party=false.", 300.0, ["sovereign"]),
    (MicroCareer.INTERIOR_DATACENTER, MicroTeam.MEMORY, "Interior DC Curator",
     "Interior datacenter corpus manifest freshness.", 240.0, ["interior-datacenter"]),
    # Infrastructure IT
    (MicroCareer.ENGINE_REGISTRY_KEEPER, MicroTeam.INFRASTRUCTURE, "Engine Registry Keeper",
     "Register and health-check all nine MESIE engines on the internal bus.", 45.0, ["engines", "internal-bus"]),
    (MicroCareer.PROTOCOL_EXECUTOR, MicroTeam.INFRASTRUCTURE, "Protocol Executor",
     "Run intelligence + edge protocols — everything is a signal.", 60.0, ["protocols"]),
    (MicroCareer.LAW_COMPILER, MicroTeam.FOUNDATIONS, "Law Compiler",
     "Compile φ-laws and release bootstrap rules into runtime checks.", 120.0, ["solus", "laws"]),
    (MicroCareer.CHARTER_KEEPER, MicroTeam.FOUNDATIONS, "Charter Keeper",
     "Maintain NOVA/MESIE production charter and agent entrypoints.", 150.0, ["charter", "surface"]),
    (MicroCareer.LIBRARY_FEEDER, MicroTeam.INFRASTRUCTURE, "Library Feeder",
     "Index and embed spectral library — train the corpus (bytes on disk).", 600.0, ["embed-library", "library"]),
    (MicroCareer.SIGNAL_ROUTER, MicroTeam.FOUNDATIONS, "Signal Router",
     "Route all modalities through spectral records — text/state/physics unified.", 35.0, ["translator", "signal"]),
    (MicroCareer.PHYSICS_FOUNDATION, MicroTeam.FOUNDATIONS, "Physics Foundation",
     "Hz-ladder, spacetime bridge, cosmology modules — science base pulse.", 180.0, ["physics", "edge"]),
    (MicroCareer.EDGE_PROTOCOL_OPS, MicroTeam.INFRASTRUCTURE, "Edge Protocol Ops",
     "Edge spectral protocol + field routing health.", 90.0, ["edge", "field-route"]),
    (MicroCareer.OCTOPUS_CONTROLLER, MicroTeam.INFRASTRUCTURE, "Octopus Controller",
     "Eight-arm polyglot controller — default EMBED/MATCH arms.", 75.0, ["octopus"]),
    (MicroCareer.WORKFLOW_ORCHESTRATOR, MicroTeam.INFRASTRUCTURE, "Workflow Orchestrator",
     "Workflow engine on internal bus — chain validate→embed→match.", 55.0, ["workflow", "bus"]),
    (MicroCareer.DOMAIN_SIGNAL_HUB, MicroTeam.DOMAINS, "Domain Signal Hub",
     "Terrain, seismic, orbital, power, robotics — all domains as signals.", 200.0, ["domains"]),
    (MicroCareer.TRAINING_CORPUS_CURATOR, MicroTeam.INFRASTRUCTURE, "Training Corpus Curator",
     "Feed references, benchmarks, swarm DTN library into index.", 480.0, ["data", "training"]),
    (MicroCareer.SHOWCASE_BROADCASTER, MicroTeam.RELEASE, "Showcase Broadcaster",
     "Run showcase benchmark workflow and export public proof JSON.", 360.0, ["showcase", "benchmark"]),
    (MicroCareer.DEVKIT_PACKAGER, MicroTeam.RELEASE, "DevKit Packager",
     "Package Virtual Processor + NOVA runtime developer kit manifest.", 300.0, ["devkit", "processor"]),
    (MicroCareer.PROCESSOR_RELEASE_GATE, MicroTeam.RELEASE, "Processor Release Gate",
     "Virtual Processor production readiness — LRC, ops, devkit.", 240.0, ["processor", "release"]),
]

CAREER_REGISTRY: Dict[MicroCareer, CareerSpec] = {
    c: CareerSpec(c, team, title, mission, interval, engines)
    for c, team, title, mission, interval, engines in _CAREER_DEFS
}

TEAM_REGISTRY: Dict[MicroTeam, List[MicroCareer]] = {}
for spec in CAREER_REGISTRY.values():
    TEAM_REGISTRY.setdefault(spec.team, []).append(spec.career)

NOVA_ORG_SIZE = len(CAREER_REGISTRY)