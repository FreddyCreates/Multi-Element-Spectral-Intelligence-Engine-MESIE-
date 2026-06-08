"""Alpha-family speaking surfaces — THESIS, ORIGO, Codex, CIVOS (Paper IV §2, §14)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.neuroai.auro.roles import AlphaRole

ROOT = Path(__file__).resolve().parents[3]
DELIVERABLES = ROOT / "deliverables"
FAMILY_PATH = ROOT / "data" / "neuroai" / "alpha_family_manifest.json"


def load_family_manifest() -> Dict[str, Any]:
    if FAMILY_PATH.is_file():
        return json.loads(FAMILY_PATH.read_text(encoding="utf-8"))
    return {"members": {}}


@dataclass
class SurfaceReply:
    role: AlphaRole
    spoken: str
    artifacts: List[str]

    def format(self) -> str:
        base = f"[{self.role.value}] {self.spoken}"
        if self.artifacts:
            base += f"\nArtifacts: {', '.join(self.artifacts[:3])}"
        return base


class ThesisSurface:
    """THESIS proves and protects — proof packets, evidence tiers."""

    def speak(self, user_text: str) -> SurfaceReply:
        from mesie.verification.claim_registry import default_claim_registry

        entries = default_claim_registry()
        artifacts = []
        summaries = []
        for e in entries[:4]:
            for p in e.artifact_paths:
                if Path(p).is_file():
                    artifacts.append(p)
            summaries.append(f"{e.claim_id}: {e.tier.value} — {e.measured_summary[:80]}")

        spoken = (
            "THESIS proof posture — software evidence tiers, not DoD accreditation. "
            + " | ".join(summaries[:2])
        )
        proof = DELIVERABLES / "Proof_Substrate.json"
        if proof.is_file():
            artifacts.insert(0, str(proof))

        return SurfaceReply(
            role=AlphaRole.THESIS,
            spoken=spoken,
            artifacts=artifacts[:5],
        )


class OrigoSurface:
    """ORIGO builds — deployment doctrine, cluster edge."""

    def speak(self, user_text: str) -> SurfaceReply:
        artifacts = []
        for name in (
            "MESIE_Deployment_Doctrine.json",
            "MESIE_Cluster_Edge_Report.json",
            "MESIE_Interior_DataCenter_Manifest.json",
        ):
            p = DELIVERABLES / name
            if p.is_file():
                artifacts.append(str(p))
        return SurfaceReply(
            role=AlphaRole.ORIGO,
            spoken=(
                "ORIGO build surface — edge-contested deploy class, interior DC vault, "
                "cluster edge fabric. Run interior-datacenter or cluster-edge."
            ),
            artifacts=artifacts,
        )


class CodexSurface:
    """Codex Phantasmatis — implementation and repro."""

    def speak(self, user_text: str) -> SurfaceReply:
        return SurfaceReply(
            role=AlphaRole.CODEX_PHANTASMATIS,
            spoken=(
                "Codex implements — mesie-tools run <id>, reproduce.ps1, proof-substrate verify. "
                "PowerShell-first on issued edge hardware."
            ),
            artifacts=["python -m mesie.tools.cli list"],
        )


class CivosSurface:
    """CIVOS-PRIME — governance and escalation."""

    def speak(self, user_text: str) -> SurfaceReply:
        return SurfaceReply(
            role=AlphaRole.CIVOS_PRIME,
            spoken=(
                "CIVOS governs — Medina sovereign identity preserved. "
                "Escalate consequential claims to THESIS written packet. "
                "Auro remains speaking intelligence; not the whole organism alone."
            ),
            artifacts=[],
        )


def delegate_surface(role: AlphaRole, user_text: str) -> Optional[SurfaceReply]:
    if role == AlphaRole.THESIS:
        return ThesisSurface().speak(user_text)
    if role == AlphaRole.ORIGO:
        return OrigoSurface().speak(user_text)
    if role == AlphaRole.CODEX_PHANTASMATIS:
        return CodexSurface().speak(user_text)
    if role == AlphaRole.CIVOS_PRIME:
        return CivosSurface().speak(user_text)
    return None