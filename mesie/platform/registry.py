"""Platform service registry — web apps offering native model services."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from mesie.version_info import MESIE_VERSION

PROTOCOL = "MESIE-MODEL-PLATFORM-REGISTRY/1.0"


@dataclass(frozen=True)
class PlatformService:
    service_id: str
    title: str
    category: str
    models: Tuple[str, ...]
    protocol_id: str
    worker_role: str
    worker_action: str
    processor_route: str
    web_surface: str
    port: Optional[int]
    description: str


PLATFORM_SERVICES: List[PlatformService] = [
    PlatformService(
        "model-hub",
        "Unified Model Hub",
        "catalog",
        ("NOVA-50B-VIRTUAL", "NOVAMINI-8B-VIRTUAL", "MININOVA-3B-VIRTUAL", "ST-φ-128", "ST-φ-256", "ST-φ-512"),
        "P36",
        "worker",
        "platform_models",
        "GET /processor/models",
        "websites/model-hub/index.html",
        8750,
        "Browse all sovereign models — encode, forge, benchmark.",
    ),
    PlatformService(
        "nova-studio",
        "NOVA Virtual Studio",
        "forge",
        ("NOVA-50B-VIRTUAL", "NOVAMINI-8B-VIRTUAL", "MININOVA-3B-VIRTUAL"),
        "P33",
        "creator",
        "platform_forge",
        "POST /processor/platform/nova-studio/invoke",
        "websites/model-hub/index.html#nova",
        8750,
        "Forge 50B/8B/3B virtual models from corpus probe text.",
    ),
    PlatformService(
        "st-phi-encode",
        "ST-φ Edge Encoder",
        "encode",
        ("ST-φ-128", "ST-φ-256", "ST-φ-512"),
        "P36",
        "worker",
        "platform_encode",
        "POST /processor/compute/encode",
        "websites/model-hub/index.html#encode",
        8750,
        "Sub-ms spectral embedding — no torch, φ-harmonic attention.",
    ),
    PlatformService(
        "solus-console",
        "SOLUS Formal Console",
        "intelligence",
        ("solus-logic-model", "solus-reasoning-model", "solus-emergence-model", "solus-adaptation-model"),
        "P35",
        "orchestrator",
        "platform_solus",
        "POST /processor/platform/solus-console/invoke",
        "websites/solus-console/index.html",
        8750,
        "Logic ⊗ Reasoning ⊗ Emergence ⊗ Adaptation over spectral cycles.",
    ),
    PlatformService(
        "auro-speak",
        "Auro Native Speaking",
        "speaking",
        ("AuroNativeLM-v1",),
        "P08",
        "creator",
        "platform_auro",
        "GET /processor/platform/auro-speak/invoke",
        "websites/auro-studio/index.html",
        8750,
        "Sovereign speaking intelligence — 32 knowledge entries, Paper IV.",
    ),
    PlatformService(
        "producer-pipeline",
        "ML Producer Pipeline",
        "large_data",
        ("MESIE-Producer",),
        "P07",
        "worker",
        "platform_producer",
        "POST /processor/platform/producer-pipeline/invoke",
        "websites/producer-lab/index.html",
        8750,
        "932+ corpus records — harvest, encode, auto-forge NOVA.",
    ),
    PlatformService(
        "st-phi-benchmark",
        "ST-φ Benchmark Suite",
        "benchmark",
        ("ST-φ-128", "ST-φ-256", "ST-φ-512"),
        "P36",
        "worker",
        "platform_benchmark",
        "POST /processor/compute/benchmark",
        "websites/model-hub/index.html#benchmark",
        8750,
        "Full hub benchmark — ST-φ + Fast ANN + virtual processor.",
    ),
    PlatformService(
        "auro-studio",
        "Auro Studio",
        "speaking",
        ("AuroNativeLM-v1",),
        "P08",
        "creator",
        "platform_auro",
        "POST /processor/platform/auro-speak/invoke",
        "websites/auro-studio/index.html",
        8750,
        "Dedicated speaking intelligence surface — eval matrix + alpha family.",
    ),
    PlatformService(
        "producer-lab",
        "Producer Lab",
        "large_data",
        ("MESIE-Producer",),
        "P07",
        "worker",
        "platform_producer",
        "POST /processor/platform/producer-pipeline/invoke",
        "websites/producer-lab/index.html",
        8750,
        "Dedicated ML producer — corpus harvest, pulse, NOVA auto-forge.",
    ),
    PlatformService(
        "computing-family",
        "MESIE Computing Family",
        "products",
        ("ST-φ-256", "ST-φ-512", "MESIE-COMPUTE-EDGE"),
        "P07",
        "helper",
        "platform_compute",
        "GET /processor/compute/products",
        "websites/computing-family/index.html",
        8750,
        "8 virtual products + tri-agent squads + live latency.",
    ),
    PlatformService(
        "virtual-silicon",
        "Virtual Silicon VS1",
        "silicon",
        ("MESIE-VS1", "MESIE-VS2-ANN", "MESIE-VS3-EDGE", "MESIE-VS4-ORBITAL"),
        "P07",
        "helper",
        "virtual_silicon_catalog",
        "GET /processor/virtual-silicon",
        "websites/virtual-silicon/index.html",
        8750,
        "Baseline sovereign virtual chip — 256-bit ALU, single RF, 4-node OTA mesh.",
    ),
    PlatformService(
        "platform-hub",
        "Platform Command Hub",
        "orchestration",
        ("ALL",),
        "P32",
        "orchestrator",
        "platform_status",
        "GET /processor/platform",
        "websites/platform-hub/index.html",
        8750,
        "MVP launcher — workers, protocols, all model services.",
    ),
    PlatformService(
        "reality-engine",
        "Design Reality Engine",
        "design",
        ("LatinDesignAgents-100",),
        "P16",
        "creator",
        "platform_design",
        "GET /processor/design",
        "websites/reality-engine/index.html",
        8750,
        "10 cores × 100 paradigms — Three.js φ-icosahedron showcase.",
    ),
    PlatformService(
        "hermes-fleet",
        "HERMES Cloudflare Fleet",
        "edge_execution",
        ("HERMES-12", "NOVA-PROTOCOL"),
        "P43",
        "executioner",
        "platform_hermes",
        "GET /processor/hermes",
        "websites/hermes-fleet/index.html",
        8750,
        "12 Cloudflare workers — wrangler, ICP CLI, SDK, clean internet. ItsnotAILabs.",
    ),
    PlatformService(
        "enterprise-4k",
        "Enterprise 4K Command",
        "enterprise",
        ("SOLUS", "NOVA", "MESIE"),
        "P30",
        "orchestrator",
        "processor_status",
        "GET /processor/harness",
        "websites/enterprise-4k/index.html",
        8770,
        "4K ops desk — five businesses, dual-chain tokens, live ports.",
    ),
]


def service_by_id(service_id: str) -> Optional[PlatformService]:
    for svc in PLATFORM_SERVICES:
        if svc.service_id == service_id:
            return svc
    return None


def platform_manifest() -> Dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "service_count": len(PLATFORM_SERVICES),
        "third_party_inference": False,
        "bridge": "MESIE-MVP-PROTOCOL-BRIDGE/1.0",
        "worker_bus": "MESIE-WORKER-BUS-GROK/1.0",
        "services": [
            {
                "service_id": s.service_id,
                "title": s.title,
                "category": s.category,
                "models": list(s.models),
                "protocol_id": s.protocol_id,
                "worker_role": s.worker_role,
                "worker_action": s.worker_action,
                "processor_route": s.processor_route,
                "web_surface": s.web_surface,
                "port": s.port,
                "description": s.description,
            }
            for s in PLATFORM_SERVICES
        ],
        "surfaces": {
            "platform_hub": "websites/platform-hub/index.html",
            "model_hub": "websites/model-hub/index.html",
            "solus_console": "websites/solus-console/index.html",
            "auro_studio": "websites/auro-studio/index.html",
            "producer_lab": "websites/producer-lab/index.html",
            "computing_family": "websites/computing-family/index.html",
            "virtual_silicon": "websites/virtual-silicon/index.html",
            "reality_engine": "websites/reality-engine/index.html",
            "enterprise_4k": "websites/enterprise-4k/index.html",
            "hermes_fleet": "websites/hermes-fleet/index.html",
            "market_hub": "websites/market-hub/index.html",
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }