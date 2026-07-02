"""Enterprise federation envelope — multi-user fields on MESIE-FEDERATED-ENVELOPE/1.0."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.mcp.envelope_protocol import FEDERATION_NODES, FederatedEnvelope, PHI, PROTOCOL

ROOT = Path(__file__).resolve().parents[3]
ENTERPRISE_FEED = ROOT / "deliverables" / "enterprise" / "FEDERATION_ENTERPRISE_FEED.jsonl"
MANIFEST = ROOT / "deliverables" / "enterprise" / "ENTERPRISE_FEDERATION_MANIFEST.json"


@dataclass
class EnterpriseFederationEnvelope(FederatedEnvelope):
    """Multi-user / multi-org envelope for enterprise AI federation."""

    org_id: str = "mesie-enterprise"
    tenant_id: str = "default"
    user_id: str = "system"
    delegation_chain: List[str] = field(default_factory=list)
    runtime: str = "python"  # python|julia|haskell|rust|motoko
    pillar_id: Optional[str] = None
    arm_id: Optional[str] = None
    hand_command: Optional[Dict[str, Any]] = None
    policy_hash: Optional[str] = None

    def seal_enterprise(self) -> Dict[str, Any]:
        base = self.seal()
        rec = {
            **base,
            "enterprise": {
                "org_id": self.org_id,
                "tenant_id": self.tenant_id,
                "user_id": self.user_id,
                "delegation_chain": self.delegation_chain,
                "runtime": self.runtime,
                "pillar_id": self.pillar_id,
                "arm_id": self.arm_id,
                "hand_command": self.hand_command,
                "policy_hash": self.policy_hash,
            },
        }
        ENTERPRISE_FEED.parent.mkdir(parents=True, exist_ok=True)
        with ENTERPRISE_FEED.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
        return rec

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnterpriseFederationEnvelope":
        ent = data.get("enterprise") or {}
        base = FederatedEnvelope.from_dict(data)
        return cls(
            agent_id=base.agent_id,
            tool=base.tool,
            payload=base.payload,
            topic=base.topic,
            source=base.source,
            target=base.target,
            envelope_id=base.envelope_id,
            correlation_id=base.correlation_id,
            prior_hash=base.prior_hash,
            phi_route=base.phi_route,
            federation_nodes=base.federation_nodes,
            org_id=str(ent.get("org_id", data.get("org_id", "mesie-enterprise"))),
            tenant_id=str(ent.get("tenant_id", data.get("tenant_id", "default"))),
            user_id=str(ent.get("user_id", data.get("user_id", "system"))),
            delegation_chain=list(ent.get("delegation_chain") or data.get("delegation_chain") or []),
            runtime=str(ent.get("runtime", data.get("runtime", "python"))),
            pillar_id=ent.get("pillar_id") or data.get("pillar_id"),
            arm_id=ent.get("arm_id") or data.get("arm_id"),
            hand_command=ent.get("hand_command") or data.get("hand_command"),
            policy_hash=ent.get("policy_hash") or data.get("policy_hash"),
        )


def build_enterprise_federation_manifest() -> Dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "enterprise_extension": "MESIE-ENTERPRISE-FEDERATION/1.0",
        "phi_route": PHI,
        "federation_nodes": FEDERATION_NODES,
        "multi_user_fields": ["org_id", "tenant_id", "user_id", "delegation_chain"],
        "polyglot_runtimes": ["python", "julia", "haskell", "rust", "motoko", "typescript"],
        "octopus_arms": ["sense", "embed", "match", "move", "control", "workflow", "logic", "memory"],
        "hands_commands": ["reach", "grip", "release", "rotate", "pulse"],
        "http_surface": {
            "status": "GET /processor/federation/status",
            "envelope": "POST /processor/federation/envelope",
            "invoke": "POST /processor/federation/invoke",
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def export_enterprise_federation_manifest() -> Path:
    payload = build_enterprise_federation_manifest()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return MANIFEST
