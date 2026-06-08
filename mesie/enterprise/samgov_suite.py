"""Sam.gov / GSA contractor edition — proof, readiness, opportunity alignment (bundled refs)."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "samgov"
DELIVERABLES = ROOT / "deliverables"


@dataclass
class SamGovWorkflow:
    workflow_id: str
    title: str
    command: str
    deliverable: str
    compliance_note: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SamGovReport:
    edition: str
    company: str
    mesie_version: str
    sdk_version: str
    workflows: List[SamGovWorkflow]
    opportunity_refs: List[Dict[str, Any]]
    proof_artifacts: List[str]
    honest_limits: List[str]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["workflows"] = [w.to_dict() for w in self.workflows]
        return d


class SamGovSuite:
    """Full Sam.gov-aligned contractor harness — sovereign proof + repro, not live classified feeds."""

    EDITION = "samgov-full-v1"

    WORKFLOWS = [
        SamGovWorkflow(
            "proof_substrate",
            "Sealed proof substrate",
            "python scripts/run_proof_substrate.py",
            "deliverables/Proof_Substrate.json",
            "Hash-linked evidence for proposal attachment",
        ),
        SamGovWorkflow(
            "readiness",
            "NeuroSwarm readiness pack",
            "python scripts/run_neuroswarm_readiness.py",
            "deliverables/neuroswarmai_com/evidence_manifest.json",
            "Gap-closure plan with honest tier labels",
        ),
        SamGovWorkflow(
            "interior_dc",
            "Interior data center manifest",
            "python scripts/run_interior_datacenter.py",
            "deliverables/MESIE_Interior_DataCenter_Manifest.json",
            "Sovereign corpus vault — no public cloud dependency",
        ),
        SamGovWorkflow(
            "cluster_edge",
            "Cluster edge fabric",
            "python scripts/run_cluster_edge.py",
            "deliverables/MESIE_Cluster_Edge_Report.json",
            "LAN/OTA edge scale without hyperscale DC",
        ),
        SamGovWorkflow(
            "production_tiers",
            "Production tier 1+2",
            "python scripts/run_production_tiers.py --tier both",
            "deliverables/MESIE_Production_Tiers_Report.json",
            "Edge appliance + cluster moat validation",
        ),
        SamGovWorkflow(
            "scenario_sim",
            "Defense + enterprise scenarios",
            "python scripts/run_scenario_simulation_suite.py",
            "deliverables/MESIE_Scenario_Simulation_Report.json",
            "Software scenario validation — not combat certification",
        ),
    ]

    def _load_opportunities(self) -> List[Dict[str, Any]]:
        path = DATA / "gsa_opportunity_reference.json"
        if not path.is_file():
            return []
        return json.loads(path.read_text(encoding="utf-8")).get("opportunities", [])

    def build_report(self) -> SamGovReport:
        import mesie
        from mesie.sdk import __sdk_version__
        from mesie.sdk.terminal import default_session

        session = default_session()
        workflows = []
        for w in self.WORKFLOWS:
            workflows.append(
                SamGovWorkflow(
                    w.workflow_id,
                    w.title,
                    session.format_command(w.command),
                    w.deliverable,
                    w.compliance_note,
                )
            )

        artifacts = [
            "Proof_Substrate.json",
            "MESIE_Deployment_Doctrine.json",
            "MESIE_Appliance_Manifest.json",
            "neuroswarmai_com/evidence_manifest.json",
        ]
        present = [a for a in artifacts if (DELIVERABLES / a).is_file()]

        return SamGovReport(
            edition=self.EDITION,
            company="NeuroSwarmAI",
            mesie_version=mesie.__version__,
            sdk_version=__sdk_version__,
            workflows=workflows,
            opportunity_refs=self._load_opportunities(),
            proof_artifacts=present,
            honest_limits=[
                "Bundled opportunity reference — configure SAM_API_KEY for live SAM.gov pull",
                "Software evidence tiers — not DoD accreditation",
                "Edge deploy class — reproducible on contractor program hardware",
            ],
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def export(self, path: Optional[Path] = None) -> Path:
        report = self.build_report()
        out = path or DELIVERABLES / "MESIE_SamGov_Contractor_Edition.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        return out

    def answer(self, question: str) -> str:
        """Contractor copilot quick answers — routes to workflows."""
        q = question.lower()
        if "proof" in q or "substrate" in q:
            return "Run proof-substrate — sealed SHA256 evidence graph for proposals."
        if "readiness" in q or "evidence" in q:
            return "Run neuroswarm-readiness — website evidence pack + gap plan."
        if "gsa" in q or "sam" in q or "opportunit" in q:
            n = len(self._load_opportunities())
            return f"SamGov edition: {n} bundled opportunity refs. Set SAM_API_KEY for live feed."
        if "repro" in q:
            return "PowerShell: .\\deliverables\\neuroswarmai_com\\reproduce.ps1"
        return (
            "SamGov contractor edition — proof substrate, readiness, interior DC, "
            "cluster edge, production tiers. Type 'workflows' for list."
        )