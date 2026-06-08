"""Public claim registry — maps NeuroSwarm/MESIE claims to evidence artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.verification.evidence_tiers import EvidenceTier

ROOT = Path(__file__).resolve().parents[2]
DELIVERABLES = ROOT / "deliverables"


@dataclass
class ClaimEntry:
    claim_id: str
    public_claim: str
    critique_source: str
    tier: EvidenceTier
    artifact_paths: List[str]
    measured_summary: str
    honest_limit: str
    remediation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "public_claim": self.public_claim,
            "critique_source": self.critique_source,
            "tier": self.tier.value,
            "artifact_paths": self.artifact_paths,
            "measured_summary": self.measured_summary,
            "honest_limit": self.honest_limit,
            "remediation": self.remediation,
        }


def default_claim_registry() -> List[ClaimEntry]:
    return [
        ClaimEntry(
            claim_id="sub_ms_threat",
            public_claim="Sub-12ms threat-fast spectral decisions",
            critique_source="Grok/X self-reported timing",
            tier=EvidenceTier.MEASURED_LOCAL,
            artifact_paths=[
                str(DELIVERABLES / "NeuroSwarmAI_Audit_Evidence.json"),
                str(DELIVERABLES / "MAESI_SDK_Major_Benchmarks.json"),
            ],
            measured_summary="p50 threat-fast ~0.85ms on Qualcomm ARM64 laptop harness",
            honest_limit="Single-machine Python harness; not independent lab audit",
            remediation="Publish reproducible harness + hardware profile JSON",
        ),
        ClaimEntry(
            claim_id="swarm_10k",
            public_claim="10K decentralized swarm coordination",
            critique_source="Grok/X scalability vs simulation",
            tier=EvidenceTier.SIMULATED_VALIDATED,
            artifact_paths=[
                str(DELIVERABLES / "NeuroSwarmAI_Drone_Swarm_Report.json"),
                str(DELIVERABLES / "MESIE_Scenario_Simulation_Report.json"),
            ],
            measured_summary="~0.05-0.11 ms/agent cluster-optimized in software sim",
            honest_limit="In-process simulation; not 10K physical drones or multi-host mesh at scale",
            remediation="Multi-machine LAN/OTA mesh soak + published node count methodology",
        ),
        ClaimEntry(
            claim_id="jam_failover",
            public_claim="Jamming failover to orbital routing",
            critique_source="Grok/X no actual jammed environment",
            tier=EvidenceTier.SIMULATED_VALIDATED,
            artifact_paths=[str(DELIVERABLES / "MESIE_Enterprise_Drone_Defense_Offense_Thesis.json")],
            measured_summary="jam_ground=True scenarios pass orbital_preferred access modes",
            honest_limit="Spectral jam profile reference; no RF anechoic or live EW range",
            remediation="Virtual silicon HIL certified; physical SDR range test is gap",
        ),
        ClaimEntry(
            claim_id="real_drone_hw",
            public_claim="Real drone hardware integration",
            critique_source="Grok/X no physical drone proof",
            tier=EvidenceTier.GAP,
            artifact_paths=[str(ROOT / "mesie" / "swarm" / "drone_adapter.py")],
            measured_summary="PX4/MAVSDK sim adapter dispatches commands; SIM platform only",
            honest_limit="No published flight test video or cleared contractor validation",
            remediation="PX4 SITL + hardware-in-loop gate in CI when available",
        ),
        ClaimEntry(
            claim_id="sovereign_airgap",
            public_claim="Sovereign air-gapped on-prem appliance",
            critique_source="Grok/X closed-source trust",
            tier=EvidenceTier.MEASURED_LOCAL,
            artifact_paths=[
                str(DELIVERABLES / "MESIE_Appliance_Manifest.json"),
                str(DELIVERABLES / "MESIE_Production_Tiers_Report.json"),
            ],
            measured_summary="field_access reports airgapped=true, third_party=false",
            honest_limit="Self-reported engine status; not third-party penetration test",
            remediation="Tier-1 appliance manifest + customer deploy checklist",
        ),
        ClaimEntry(
            claim_id="mission_critical_100",
            public_claim="100/100 mission-critical defense scenarios",
            critique_source="Grok/X 100/100 unproven publicly",
            tier=EvidenceTier.SIMULATED_VALIDATED,
            artifact_paths=[
                str(DELIVERABLES / "MESIE_Scenario_Simulation_Report.json"),
                str(DELIVERABLES / "mission_worlds"),
            ],
            measured_summary="12 scenario sim + 7-day theater week ticks (software)",
            honest_limit="Not DoD accreditation; scenario pass != combat validation",
            remediation="Rename public copy to 'software scenario validation' not 'mission-critical certified'",
        ),
        ClaimEntry(
            claim_id="external_corroboration",
            public_claim="Independent validation of NeuroSwarm/Chimeria deployment",
            critique_source="Grok/X no web corroboration chimeradefense.com",
            tier=EvidenceTier.GAP,
            artifact_paths=[],
            measured_summary="No independent public audit found in open sources",
            honest_limit="Defense tech often opaque; we cannot claim external proof",
            remediation="Publish evidence pack + invite reproducible third-party harness runs",
        ),
        ClaimEntry(
            claim_id="connectome_44_region",
            public_claim="44-region connectome spectral intelligence",
            critique_source="Grok/X biologically-inspired substrate",
            tier=EvidenceTier.MEASURED_LOCAL,
            artifact_paths=[str(ROOT / "mesie" / "connectome" / "brain_regions.py")],
            measured_summary="Connectome modules present; used in routing/cognitive paths",
            honest_limit="Inspired architecture; not neuroscience certification",
            remediation="Document which regions are active in threat-fast vs full Octopus paths",
        ),
    ]