"""Proof substrate — sealed, hash-linked evidence graph for honest public claims."""

from __future__ import annotations

import hashlib
import hmac
import json
import platform
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import mesie
from mesie.sdk import __sdk_version__
from mesie.verification.claim_registry import ClaimEntry, default_claim_registry
from mesie.verification.evidence_tiers import EvidenceTier, tier_summary
from mesie.verification.is_this_true import IsThisTrueEngine
from mesie.version_info import PROOF_SUBSTRATE_VERSION

ROOT = Path(__file__).resolve().parents[2]
DELIVERABLES = ROOT / "deliverables"
SITE_DIR = DELIVERABLES / "neuroswarmai_com"

CANONICAL_ARTIFACTS = [
    "Is_This_True_Response.json",
    "Proof_Substrate.json",
    "NeuroSwarmAI_Audit_Evidence.json",
    "MAESI_SDK_Major_Benchmarks.json",
    "MESIE_Production_Tiers_Report.json",
    "MESIE_Scenario_Simulation_Report.json",
    "NeuroSwarmAI_Drone_Swarm_Report.json",
    "MESIE_Enterprise_Drone_Defense_Offense_Thesis.json",
    "mission_worlds/theater_alpha_week_001_week_report.json",
    "MESIE_Appliance_Manifest.json",
    "virtual_silicon/MESIE_Virtual_Silicon_Certification.json",
    "neuroswarmai_com/evidence_manifest.json",
    "MESIE_Interior_DataCenter_Manifest.json",
    "MESIE_Cluster_Edge_Report.json",
    "MESIE_Deployment_Doctrine.json",
]

REPRODUCE_BY_CLAIM: Dict[str, str] = {
    "sub_ms_threat": "python scripts/run_neuroswarm_audit.py --trials 1000",
    "swarm_10k": "python scripts/run_drone_swarm_suite.py --agents 10000",
    "jam_failover": "python scripts/run_enterprise_drone_thesis.py",
    "real_drone_hw": "python scripts/run_drone_swarm_suite.py --agents 100",
    "sovereign_airgap": "python scripts/run_production_tiers.py --tier both",
    "mission_critical_100": "python scripts/run_scenario_simulation_suite.py && python scripts/run_mission_world_week.py --days 7",
    "external_corroboration": "python scripts/run_neuroswarm_readiness.py",
    "connectome_44_region": "python examples/08_3d_connectome_brain.py",
}

GENESIS = "MESIE-Proof-Substrate-v1"


def _canonical(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _seal(genesis: str, body: Dict[str, Any]) -> str:
    key = hashlib.sha256(f"{GENESIS}:{genesis}".encode("utf-8")).digest()
    return hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()


@dataclass
class ArtifactProof:
    path: str
    sha256: str
    bytes: int
    present: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClaimProof:
    claim_id: str
    public_claim: str
    tier: str
    tier_label: str
    artifacts: List[ArtifactProof]
    measured_summary: str
    honest_limit: str
    reproduce_command: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["artifacts"] = [a.to_dict() for a in self.artifacts]
        return d


@dataclass
class ProofSubstrateReport:
    substrate_version: str
    mesie_version: str
    sdk_version: str
    platform: str
    verdict: str
    confidence: str
    genesis_hash: str
    seal_digest: str
    claims: List[ClaimProof]
    artifact_index: Dict[str, ArtifactProof]
    tier_counts: Dict[str, int]
    gaps_open: int
    harness_commands: List[str]
    truth_summary: Dict[str, Any]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "substrate_version": self.substrate_version,
            "mesie_version": self.mesie_version,
            "sdk_version": self.sdk_version,
            "platform": self.platform,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "genesis_hash": self.genesis_hash,
            "seal_digest": self.seal_digest,
            "claims": [c.to_dict() for c in self.claims],
            "artifact_index": {k: v.to_dict() for k, v in self.artifact_index.items()},
            "tier_counts": self.tier_counts,
            "gaps_open": self.gaps_open,
            "harness_commands": self.harness_commands,
            "truth_summary": self.truth_summary,
            "generated_at": self.generated_at,
        }


class ProofSubstrateEngine:
    """Build hash-linked proof substrate from claims, artifacts, and harness paths."""

    HARNESS_COMMANDS = [
        "python scripts/run_proof_substrate.py",
        "python scripts/run_is_this_true.py",
        "python scripts/run_neuroswarm_readiness.py",
        "python scripts/run_sdk_major_benchmarks.py --trials 300 --agents 10000",
        "python scripts/run_production_tiers.py --tier both",
        "python scripts/run_mission_world_week.py --days 7",
        "python scripts/run_scenario_simulation_suite.py",
        "python scripts/run_drone_swarm_suite.py --agents 10000",
        "python scripts/run_neuroswarm_audit.py --trials 1000",
    ]

    def __init__(self, registry: Optional[List[ClaimEntry]] = None) -> None:
        self.registry = registry or default_claim_registry()

    def _normalize_rel(self, raw: str) -> str:
        p = Path(raw)
        if p.is_absolute():
            try:
                return str(p.relative_to(ROOT)).replace("\\", "/")
            except ValueError:
                return raw.replace("\\", "/")
        return raw.replace("\\", "/")

    def _resolve_path(self, raw: str) -> Path:
        rel = self._normalize_rel(raw)
        candidates = [ROOT / rel, DELIVERABLES / rel, DELIVERABLES / Path(rel).name]
        if rel.startswith("deliverables/"):
            candidates.insert(0, ROOT / rel)
        for c in candidates:
            if c.is_file():
                return c
        return ROOT / rel

    def _resolve_artifact(self, raw: str) -> ArtifactProof:
        rel = self._normalize_rel(raw)
        p = self._resolve_path(raw)
        if p.is_file():
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            return ArtifactProof(
                path=rel,
                sha256=_sha256_file(p),
                bytes=p.stat().st_size,
                present=True,
            )
        return ArtifactProof(path=rel, sha256="", bytes=0, present=False)

    def _artifact_index(self) -> Dict[str, ArtifactProof]:
        seen: Dict[str, ArtifactProof] = {}
        paths: set[str] = set(CANONICAL_ARTIFACTS)
        for c in self.registry:
            for ap in c.artifact_paths:
                paths.add(self._normalize_rel(ap))
        for rel in sorted(paths):
            proof = self._resolve_artifact(rel)
            seen[proof.path] = proof
        return seen

    def build(self) -> ProofSubstrateReport:
        truth = IsThisTrueEngine(self.registry).answer()
        index = self._artifact_index()
        claims: List[ClaimProof] = []

        for c in self.registry:
            arts: List[ArtifactProof] = []
            for ap in c.artifact_paths:
                rel = self._normalize_rel(ap)
                arts.append(index.get(rel, self._resolve_artifact(ap)))
            claims.append(
                ClaimProof(
                    claim_id=c.claim_id,
                    public_claim=c.public_claim,
                    tier=c.tier.value,
                    tier_label=tier_summary(c.tier),
                    artifacts=arts,
                    measured_summary=c.measured_summary,
                    honest_limit=c.honest_limit,
                    reproduce_command=REPRODUCE_BY_CLAIM.get(c.claim_id, "python scripts/run_is_this_true.py"),
                )
            )

        tier_counts: Dict[str, int] = {}
        for c in self.registry:
            tier_counts[c.tier.value] = tier_counts.get(c.tier.value, 0) + 1

        genesis_hash = _sha256(GENESIS.encode("utf-8"))
        body = {
            "substrate_version": PROOF_SUBSTRATE_VERSION,
            "mesie_version": mesie.__version__,
            "sdk_version": __sdk_version__,
            "verdict": truth.verdict,
            "claims": [c.to_dict() for c in claims],
            "artifact_hashes": {k: v.sha256 for k, v in index.items() if v.present},
        }
        seal = _seal(genesis_hash, body)

        return ProofSubstrateReport(
            substrate_version=PROOF_SUBSTRATE_VERSION,
            mesie_version=mesie.__version__,
            sdk_version=__sdk_version__,
            platform=platform.platform(),
            verdict=truth.verdict,
            confidence=truth.confidence,
            genesis_hash=genesis_hash,
            seal_digest=seal,
            claims=claims,
            artifact_index=index,
            tier_counts=tier_counts,
            gaps_open=sum(1 for c in self.registry if c.tier == EvidenceTier.GAP),
            harness_commands=self.HARNESS_COMMANDS,
            truth_summary={
                "measured_claims": tier_counts.get(EvidenceTier.MEASURED_LOCAL.value, 0),
                "simulated_claims": tier_counts.get(EvidenceTier.SIMULATED_VALIDATED.value, 0),
                "gap_claims": tier_counts.get(EvidenceTier.GAP.value, 0),
            },
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    def export(self, path: Optional[Path] = None) -> Path:
        report = self.build()
        out = path or DELIVERABLES / "Proof_Substrate.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = report.to_dict()
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        site_copy = SITE_DIR / "proof_substrate.json"
        SITE_DIR.mkdir(parents=True, exist_ok=True)
        site_copy.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        md = DELIVERABLES / "Proof_Substrate.md"
        md.write_text(self._to_md(report), encoding="utf-8")
        return out

    def verify_seal(self, payload: Dict[str, Any]) -> bool:
        """Recompute seal_digest for an exported substrate JSON."""
        body = {
            "substrate_version": payload["substrate_version"],
            "mesie_version": payload["mesie_version"],
            "sdk_version": payload["sdk_version"],
            "verdict": payload["verdict"],
            "claims": payload["claims"],
            "artifact_hashes": {
                k: v["sha256"]
                for k, v in payload.get("artifact_index", {}).items()
                if v.get("present") and v.get("sha256")
            },
        }
        expected = _seal(payload["genesis_hash"], body)
        return hmac.compare_digest(expected, payload.get("seal_digest", ""))

    def _to_md(self, report: ProofSubstrateReport) -> str:
        lines = [
            "# MESIE Proof Substrate",
            "",
            f"**Verdict:** `{report.verdict}` | **Seal:** `{report.seal_digest[:16]}…`",
            f"**MESIE:** {report.mesie_version} | **MAESI SDK:** {report.sdk_version}",
            "",
            "Hash-linked evidence graph — claims bound to artifacts with reproducible harness commands.",
            "",
            "## Tier summary",
            "",
        ]
        for tier, count in sorted(report.tier_counts.items()):
            lines.append(f"- **{tier}:** {count} claims")
        lines.extend(["", f"**Gaps open:** {report.gaps_open}", "", "## Claims → artifacts", ""])
        for c in report.claims:
            lines.append(f"### {c.claim_id}")
            lines.append(f"- **Claim:** {c.public_claim}")
            lines.append(f"- **Tier:** {c.tier_label}")
            lines.append(f"- **Measured:** {c.measured_summary}")
            lines.append(f"- **Limit:** {c.honest_limit}")
            lines.append(f"- **Reproduce:** `{c.reproduce_command}`")
            for a in c.artifacts:
                status = f"`{a.sha256[:12]}…` ({a.bytes} B)" if a.present else "_missing_"
                lines.append(f"  - `{a.path}` → {status}")
            lines.append("")
        lines.extend(["## Verify seal", "", "```bash", "python scripts/run_proof_substrate.py --verify", "```"])
        return "\n".join(lines)