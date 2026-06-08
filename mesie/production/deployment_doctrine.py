"""Deployment doctrine — edge contested, cluster edge, interior DC, industry contractor.

Not cloud-first. Not hobby-project. Operators already in defense/enterprise industries
use MESIE from whatever edge hardware they are issued (laptop, phone, toughbook).
The builder lab (LLC) runs the sovereign interior data center — not 'dev laptop vs independent lab'.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class DeploymentClass(str, Enum):
    EDGE_CONTESTED = "edge_contested"
    CLUSTER_EDGE = "cluster_edge"
    INTERIOR_DATACENTER = "interior_datacenter"
    BUILDER_LAB = "builder_lab"
    INDUSTRY_CONTRACTOR = "industry_contractor"
    BENCHMARK_REFERENCE_ONLY = "benchmark_reference_only"


DEPLOYMENT_LABELS: Dict[DeploymentClass, str] = {
    DeploymentClass.EDGE_CONTESTED: (
        "Field edge — issued laptop, phone, or tablet in contested environments"
    ),
    DeploymentClass.CLUSTER_EDGE: (
        "Cluster edge — 2–10 sovereign boxes on LAN/OTA, no cloud dependency"
    ),
    DeploymentClass.INTERIOR_DATACENTER: (
        "Interior data center — sovereign corpus vault inside your org (not public cloud)"
    ),
    DeploymentClass.BUILDER_LAB: (
        "Builder lab — LLC sovereign R&D floor (AI-assisted engineering is still a real lab)"
    ),
    DeploymentClass.INDUSTRY_CONTRACTOR: (
        "Industry contractor — GSA/gov drone & spectral work on customer programs"
    ),
    DeploymentClass.BENCHMARK_REFERENCE_ONLY: (
        "Cloud/datacenter — comparison baseline in benchmarks only, not a deploy target"
    ),
}


@dataclass
class OperatorProfile:
    profile_id: str
    label: str
    deployment_class: DeploymentClass
    typical_hardware: List[str]
    use_case: str
    proof_expectation: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["deployment_class"] = self.deployment_class.value
        return d


DEFAULT_OPERATOR_PROFILES: List[OperatorProfile] = [
    OperatorProfile(
        profile_id="field_operator",
        label="Contested field operator",
        deployment_class=DeploymentClass.EDGE_CONTESTED,
        typical_hardware=["issued laptop", "rugged tablet", "phone bridge", "powershell"],
        use_case="Launch/monitor drone ops from whatever edge device is available",
        proof_expectation="Threat-fast spectral path + swarm route on edge hardware",
    ),
    OperatorProfile(
        profile_id="cluster_edge_team",
        label="Cluster edge team",
        deployment_class=DeploymentClass.CLUSTER_EDGE,
        typical_hardware=["2–10 LAN nodes", "OTA multicast mesh"],
        use_case="Multi-box gossip + swarm without datacenter or cloud",
        proof_expectation="Multi-host OTA soak + cluster ms/agent on edge cluster",
    ),
    OperatorProfile(
        profile_id="interior_dc_ops",
        label="Interior DC operator",
        deployment_class=DeploymentClass.INTERIOR_DATACENTER,
        typical_hardware=["on-prem rack or appliance", "airgapped vault"],
        use_case="Corpus ingest, reference libraries, evidence vault for the org",
        proof_expectation="Shard catalog + byte counts + sovereign ingest lanes",
    ),
    OperatorProfile(
        profile_id="builder_lab_llc",
        label="Builder lab (LLC)",
        deployment_class=DeploymentClass.BUILDER_LAB,
        typical_hardware=["lab workstation", "edge appliance prototypes"],
        use_case="Ship production stack; researchers use REPL on same substrate",
        proof_expectation="Measured harness on lab edge class — same code path as field",
    ),
    OperatorProfile(
        profile_id="gsa_drone_contractor",
        label="GSA / gov drone contractor",
        deployment_class=DeploymentClass.INDUSTRY_CONTRACTOR,
        typical_hardware=["customer-site edge", "program laptop", "interior DC sync"],
        use_case="Spectral intelligence on government drone / EW programs",
        proof_expectation="Scenario sim + proof substrate + reproducible deliverables for customer",
    ),
]


@dataclass
class DeploymentDoctrineReport:
    company: str
    product: str
    mesie_version: str
    sdk_version: str
    primary_deployment: str
    not_a_deploy_target: List[str]
    operator_profiles: List[OperatorProfile]
    evidence_language: Dict[str, str]
    third_way_statement: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company": self.company,
            "product": self.product,
            "mesie_version": self.mesie_version,
            "sdk_version": self.sdk_version,
            "primary_deployment": self.primary_deployment,
            "not_a_deploy_target": self.not_a_deploy_target,
            "operator_profiles": [p.to_dict() for p in self.operator_profiles],
            "deployment_classes": {k.value: v for k, v in DEPLOYMENT_LABELS.items()},
            "evidence_language": self.evidence_language,
            "third_way_statement": self.third_way_statement,
        }


def build_deployment_doctrine() -> DeploymentDoctrineReport:
    import mesie
    from mesie.sdk import __sdk_version__

    return DeploymentDoctrineReport(
        company="NeuroSwarmAI",
        product="MESIE / MAESI SDK",
        mesie_version=mesie.__version__,
        sdk_version=__sdk_version__,
        primary_deployment=DeploymentClass.EDGE_CONTESTED.value,
        not_a_deploy_target=[
            "public cloud as primary runtime",
            "hyperscale datacenter dependency",
            "always-on internet for threat path",
        ],
        operator_profiles=list(DEFAULT_OPERATOR_PROFILES),
        evidence_language={
            "say_instead_of_dev_laptop": "edge deployment class (issued field hardware)",
            "say_instead_of_independent_lab": (
                "sovereign builder lab (LLC) or customer program repro — not a false dichotomy"
            ),
            "measured_local_means": (
                "Measured on edge-class hardware via reproducible harness in your environment"
            ),
            "gap_means": "Not yet demonstrated on named physical asset — gap is specific, not 'fake'",
        },
        third_way_statement=(
            "Users are already in the industries that require this — GSA contractors, defense "
            "integrators, enterprise spectral teams. They deploy from edge hardware on program "
            "sites. MESIE is production substrate for builders and their customers, not a "
            "science-fair REPL and not a cloud SaaS upsell."
        ),
    )