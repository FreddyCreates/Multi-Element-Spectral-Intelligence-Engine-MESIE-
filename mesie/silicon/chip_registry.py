"""Deployable virtual chip SKUs — registry for systems and AIs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from mesie.silicon.virtual_chip import VirtualChipSpec


@dataclass(frozen=True)
class ChipSKU:
    chip_id: str
    name: str
    description: str
    spec: VirtualChipSpec
    ann_trials: int = 200
    ota_nodes: int = 4
    threat_trials: int = 200
    deploy_profile: str = "sovereign_local"
    ota_propagation_tier: int = 3
    processor_ops: List[str] = field(default_factory=list)
    sku_family_rank: int = 1
    family_role: str = "general"
    baseline_sovereign: bool = False
    tagline: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chip_id": self.chip_id,
            "name": self.name,
            "description": self.description,
            "spec": self.spec.to_dict(),
            "ann_trials": self.ann_trials,
            "ota_nodes": self.ota_nodes,
            "threat_trials": self.threat_trials,
            "deploy_profile": self.deploy_profile,
            "ota_propagation_tier": self.ota_propagation_tier,
            "processor_ops": self.processor_ops,
            "sku_family_rank": self.sku_family_rank,
            "family_role": self.family_role,
            "baseline_sovereign": self.baseline_sovereign,
            "tagline": self.tagline,
        }


CHIP_REGISTRY: Dict[str, ChipSKU] = {
    "MESIE-VS1": ChipSKU(
        chip_id="MESIE-VS1",
        name="MESIE Virtual Silicon VS1",
        description="Baseline sovereign chip — single RF front-end, 256-bit spectral ALU, 4-node NSOT OTA MAC.",
        spec=VirtualChipSpec(),
        processor_ops=["virtual_chip", "benchmark", "embed", "match"],
        sku_family_rank=1,
        family_role="baseline_sovereign",
        baseline_sovereign=True,
        tagline="Foundational virtual chip for autonomous, decentralized AI",
    ),
    "MESIE-VS2-ANN": ChipSKU(
        chip_id="MESIE-VS2-ANN",
        name="MESIE Virtual Silicon VS2-ANN",
        description="ANN-optimized SKU — 512-bit ALU, library-backed index, statistical p50 ANN lane.",
        spec=VirtualChipSpec(
            chip_name="MESIE-VS2-ANN",
            spectral_alu_width=512,
            rf_frontends=1,
        ),
        ann_trials=500,
        threat_trials=300,
        deploy_profile="appliance_ann",
        processor_ops=["virtual_chip", "benchmark", "embed", "match", "exec_tool"],
        sku_family_rank=2,
        family_role="ann_optimized",
        tagline="Wider ALU + statistical ANN lane for neural workloads",
    ),
    "MESIE-VS3-EDGE": ChipSKU(
        chip_id="MESIE-VS3-EDGE",
        name="MESIE Virtual Silicon VS3-EDGE",
        description="Edge contested SKU — dual RF front-ends, widened OTA mesh, threat-fast SLA profile.",
        spec=VirtualChipSpec(
            chip_name="MESIE-VS3-EDGE",
            rf_frontends=2,
            spectral_alu_width=384,
            ota_mac="NSOT_multicast_v2_edge",
        ),
        ota_nodes=8,
        ann_trials=200,
        threat_trials=500,
        deploy_profile="edge_contested",
        processor_ops=["virtual_chip", "benchmark", "robotics_pulse", "embed"],
        sku_family_rank=3,
        family_role="contested_edge",
        tagline="Dual RF + larger mesh for adversarial edge environments",
    ),
    "MESIE-VS4-ORBITAL": ChipSKU(
        chip_id="MESIE-VS4-ORBITAL",
        name="MESIE Virtual Silicon VS4-ORBITAL",
        description="Orbital edge SKU — SHF/Satellite Hz-ladder tier, 12-node constellation mesh, robotics pulse lane.",
        spec=VirtualChipSpec(
            chip_name="MESIE-VS4-ORBITAL",
            rf_frontends=1,
            spectral_alu_width=448,
            ota_mac="NSOT_multicast_orbital_v1",
            airgapped=False,
        ),
        ota_nodes=12,
        ota_propagation_tier=4,
        ann_trials=250,
        threat_trials=300,
        deploy_profile="orbital_edge",
        processor_ops=["virtual_chip", "benchmark", "robotics_pulse", "embed"],
        sku_family_rank=4,
        family_role="orbital_edge",
        tagline="Satellite-tier mesh for orbital and long-haul edge",
    ),
}


def get_chip(chip_id: str) -> ChipSKU:
    if chip_id not in CHIP_REGISTRY:
        known = ", ".join(sorted(CHIP_REGISTRY))
        raise KeyError(f"unknown chip_id: {chip_id}. known: {known}")
    return CHIP_REGISTRY[chip_id]


def list_chips() -> List[ChipSKU]:
    return list(CHIP_REGISTRY.values())


def deploy_manifest(*, certified_chips: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Production manifest — how systems and AIs invoke virtual chips."""
    import time

    from mesie.version_info import MESIE_VERSION, VIRTUAL_CHIP_VERSION

    return {
        "product": "MESIE Virtual Silicon Compute Fabric",
        "fabric_version": VIRTUAL_CHIP_VERSION,
        "mesie_version": MESIE_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "instruction_for_agents": (
            "Virtual chips are software-defined spectral processors on commodity CPU — NOT fab RTL. "
            "Invoke via HTTP :8750 POST /processor/virtual-chip {\"chip_id\": \"MESIE-VS1\"} "
            "or run scripts/run_compute_fabric_suite.py for certification."
        ),
        "http_surface": {
            "base": "http://127.0.0.1:8750",
            "catalog": "GET /processor/virtual-silicon",
            "certify": "POST /processor/virtual-chip",
            "chips": "GET /processor/chips",
            "benchmark": "POST /processor/benchmark",
            "fast_compute": "POST /processor/embed",
        },
        "skus": [sku.to_dict() for sku in list_chips()],
        "certified": certified_chips or [],
        "deploy_profiles": {
            "sovereign_local": {"airgapped": True, "sla_threat_p50_ms": 12.0},
            "appliance_ann": {"airgapped": True, "sla_ann_p50_ms": 2.0},
            "edge_contested": {"airgapped": False, "sla_threat_p50_ms": 8.0},
            "orbital_edge": {"airgapped": False, "sla_propagation_tier": "SHF/Satellite", "sla_latency_ms": 5.0},
        },
    }
