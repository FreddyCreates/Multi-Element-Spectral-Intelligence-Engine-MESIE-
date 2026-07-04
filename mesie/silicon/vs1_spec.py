"""MESIE-VS1 baseline sovereign virtual chip — spec, SKU family, narrative."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mesie.version_info import MESIE_VERSION, VIRTUAL_CHIP_VERSION

BRAND = "ItsnotAILabs"
BASELINE_CHIP_ID = "MESIE-VS1"

COMPONENT_SPECS: List[Dict[str, str]] = [
    {
        "component": "ALU",
        "specification": "256-bit",
        "interpretation": (
            "Wide spectral Arithmetic Logic Unit. Processes 256-bit data paths in a single "
            "operation — strong for large-integer arithmetic (crypto, big-integer ML ops), "
            "high-precision compute, and efficient vector/matrix handling in AI workloads."
        ),
    },
    {
        "component": "RF",
        "specification": "Single RF",
        "interpretation": (
            "One radio-frequency front-end. Basic wireless connectivity to other nodes, sensors, "
            "or networks. Simpler and more power-efficient than the dual-RF profile in higher SKUs."
        ),
    },
    {
        "component": "OTA",
        "specification": "4-node",
        "interpretation": (
            "Over-the-air updates, configuration pushes, and coordination across a 4-node cluster. "
            "Enables remote firmware/model deltas and lightweight mesh collaboration without "
            "physical access."
        ),
    },
]

SKU_FAMILY: List[Dict[str, Any]] = [
    {
        "chip_id": "MESIE-VS1",
        "rank": 1,
        "role": "Baseline sovereign",
        "summary": (
            "Entry-level, general-purpose sovereign virtual chip — 256-bit ALU, single RF, "
            "4-node OTA. Minimal dependency, maximum independence."
        ),
        "deploy_profile": "sovereign_local",
    },
    {
        "chip_id": "MESIE-VS2-ANN",
        "rank": 2,
        "role": "ANN-optimized",
        "summary": (
            "Artificial Neural Network workloads — 512-bit ALU, statistical ANN lane, "
            "library-backed spectral index."
        ),
        "deploy_profile": "appliance_ann",
    },
    {
        "chip_id": "MESIE-VS3-EDGE",
        "rank": 3,
        "role": "Contested edge",
        "summary": (
            "Hardened for adversarial edge environments — dual RF, 8-node mesh, "
            "threat-fast SLA profile."
        ),
        "deploy_profile": "edge_contested",
    },
    {
        "chip_id": "MESIE-VS4-ORBITAL",
        "rank": 4,
        "role": "Orbital edge",
        "summary": (
            "Satellite/SHF Hz-ladder tier — 12-node constellation mesh, robotics pulse lane."
        ),
        "deploy_profile": "orbital_edge",
    },
]

SOVEREIGN_USE_CASES: List[str] = [
    "Standalone sovereign AI agents",
    "Small decentralized hive clusters",
    "Core nodes in recursive or living architecture systems",
    "Privacy-focused or air-gapped-leaning deployments",
]

INTEGRATION_CAPABILITIES: List[str] = [
    "Communicate via single RF interface (NSRF binary → field bridge)",
    "Receive OTA updates or model deltas across 4-node groups (NSOT multicast)",
    "Perform 256-bit-wide spectral compute locally",
    "Participate in larger recursive or hive-style AI systems",
]

ARCHITECTURAL_ROLE = {
    "abstraction": (
        "MESIE-VS1 is a virtualized hardware model — not physical silicon. It emulates or maps "
        "onto real substrates (edge devices, servers, microcontrollers) and exposes a consistent "
        "software-defined compute surface across heterogeneous hardware."
    ),
    "philosophy": (
        "Baseline sovereign configuration: minimal external dependency, self-contained AI compute "
        "suitable for autonomous decentralized systems without ANN-specific lanes or "
        "contested-environment hardening."
    ),
    "spectral_fabric": (
        "Part of the MESIE spectral compute fabric — graph-spectral methods, frequency-domain "
        "optimization, and multi-dimensional capability layering across virtual chip SKUs."
    ),
}


def baseline_sovereign_profile() -> Dict[str, Any]:
    """Canonical VS1 profile for APIs, certs, and docs."""
    return {
        "chip_id": BASELINE_CHIP_ID,
        "brand": BRAND,
        "fabric_version": VIRTUAL_CHIP_VERSION,
        "mesie_version": MESIE_VERSION,
        "position": "baseline_sovereign",
        "tagline": "Baseline sovereign — foundational virtual chip for decentralized AI",
        "baseline_sovereign": True,
        "sku_family_rank": 1,
        "components": COMPONENT_SPECS,
        "architectural_role": ARCHITECTURAL_ROLE,
        "sovereign_use_cases": SOVEREIGN_USE_CASES,
        "integration_capabilities": INTEGRATION_CAPABILITIES,
    }


def sku_family_catalog() -> List[Dict[str, Any]]:
    return list(SKU_FAMILY)


def virtual_silicon_catalog(*, include_cert_paths: bool = True) -> Dict[str, Any]:
    """Full catalog for GET /processor/virtual-silicon."""
    from mesie.silicon.chip_registry import deploy_manifest, list_chips

    manifest = deploy_manifest()
    chips = [sku.to_dict() for sku in list_chips()]
    out: Dict[str, Any] = {
        "product": "MESIE Virtual Silicon Compute Fabric",
        "brand": BRAND,
        "fabric_version": VIRTUAL_CHIP_VERSION,
        "mesie_version": MESIE_VERSION,
        "baseline": baseline_sovereign_profile(),
        "sku_family": sku_family_catalog(),
        "skus": chips,
        "http_surface": manifest.get("http_surface", {}),
        "deploy_profiles": manifest.get("deploy_profiles", {}),
        "instruction_for_agents": manifest.get("instruction_for_agents", ""),
    }
    if include_cert_paths:
        out["artifact_paths"] = {
            "baseline_narrative": "deliverables/virtual_silicon/MESIE_VS1_BASELINE_SOVEREIGN.md",
            "fabric_narrative": "deliverables/virtual_silicon/MESIE_Virtual_Silicon_Narrative.md",
            "deploy_manifest": "deliverables/virtual_silicon/MESIE_Chip_Deploy_Manifest.json",
            "vs1_certification": "deliverables/virtual_silicon/chips/MESIE-VS1_Certification.json",
        }
    return out


def vs1_narrative_md(*, cert: Optional[Dict[str, Any]] = None) -> str:
    """Polished baseline sovereign narrative — standalone deliverable."""
    profile = baseline_sovereign_profile()
    lines = [
        "# MESIE-VS1 — Baseline Sovereign Virtual Chip",
        "",
        f"**Brand:** {BRAND} · **Fabric:** v{VIRTUAL_CHIP_VERSION} · **MESIE:** v{MESIE_VERSION}",
        "",
        "MESIE-VS1 is the baseline virtual chip SKU in the spectral compute fabric. It is "
        "explicitly positioned as the **baseline sovereign** configuration — the foundational, "
        "minimal-yet-capable building block for autonomous, decentralized, self-contained AI systems.",
        "",
        "## Key specifications",
        "",
        "| Component | Specification | What it means |",
        "|-----------|---------------|---------------|",
    ]
    for row in COMPONENT_SPECS:
        lines.append(f"| {row['component']} | {row['specification']} | {row['interpretation']} |")

    lines.extend([
        "",
        "## Architectural role",
        "",
        "### Virtual chip abstraction",
        profile["architectural_role"]["abstraction"],
        "",
        "### Sovereign baseline philosophy",
        profile["architectural_role"]["philosophy"],
        "",
        "**Designed for:**",
    ])
    for use in SOVEREIGN_USE_CASES:
        lines.append(f"- {use}")

    lines.extend([
        "",
        "## SKU family position",
        "",
        "| Rank | Chip | Role |",
        "|------|------|------|",
    ])
    for sku in SKU_FAMILY:
        lines.append(f"| {sku['rank']} | `{sku['chip_id']}` | {sku['role']} |")
    lines.append("")
    lines.append(
        "VS1 is the simplest and most general-purpose starting point. Upgrade to VS2-ANN for "
        "dedicated ANN throughput, VS3-EDGE for contested environments, or VS4-ORBITAL for "
        "satellite-tier mesh."
    )

    lines.extend([
        "",
        "## System integration",
        "",
        "In the broader spectral compute fabric, MESIE-VS1 nodes can:",
    ])
    for cap in INTEGRATION_CAPABILITIES:
        lines.append(f"- {cap}")

    lines.extend([
        "",
        "## Spectral compute fabric",
        "",
        profile["architectural_role"]["spectral_fabric"],
        "",
        "## Summary",
        "",
        "**MESIE-VS1** = entry-level sovereign virtual chip.",
        "",
        "256-bit compute core + basic wireless connectivity + small-scale OTA management — "
        "everything needed to run independent AI workloads in a decentralized setup, without "
        "ANN-specific lanes or contested-environment hardening.",
        "",
        "## Invoke",
        "",
        "- `GET http://127.0.0.1:8750/processor/virtual-silicon` — full SKU catalog + baseline profile",
        "- `GET http://127.0.0.1:8750/processor/chips` — deploy manifest",
        f"- `POST http://127.0.0.1:8750/processor/virtual-chip` body `{{\"chip_id\": \"{BASELINE_CHIP_ID}\"}}`",
        "- Manifest: `deliverables/virtual_silicon/MESIE_Chip_Deploy_Manifest.json`",
    ])

    if cert:
        bench = cert.get("benchmark_lane", {})
        rf = cert.get("rf_hil", {})
        ota = cert.get("ota_mesh", {})
        lines.extend([
            "",
            "## Live certification (measured)",
            "",
            f"- **Certified:** {cert.get('certified', False)}",
            f"- RF path: `{rf.get('path', '—')}` · SNR {rf.get('snr_db', '—')} dB · "
            f"latency {rf.get('ingest_latency_ms', '—')} ms",
            f"- OTA mesh: {ota.get('nodes', 4)} nodes · {ota.get('frames_sent', 0)} sent / "
            f"{ota.get('frames_received', 0)} received",
            f"- Threat-fast p50: {bench.get('threat_fast_p50_ms', '—')} ms",
            f"- ANN p50 / p95: {bench.get('ann_p50_ms', '—')} / {bench.get('ann_p95_ms', '—')} ms",
            f"- Platform: {cert.get('platform', '—')}",
            f"- Generated: {cert.get('generated_at', '—')}",
        ])

    return "\n".join(lines) + "\n"