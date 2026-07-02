"""Multi-user tenant and agent registry for enterprise federation."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "deliverables" / "enterprise" / "FEDERATION_REGISTRY.json"


@dataclass
class FederationAgent:
    agent_id: str
    org_id: str
    tenant_id: str
    roles: List[str] = field(default_factory=list)
    runtimes: List[str] = field(default_factory=lambda: ["python", "julia"])
    healthy: bool = True
    last_seen: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FederationTenant:
    tenant_id: str
    org_id: str
    name: str
    max_agents: int = 100
    agents: List[str] = field(default_factory=list)
    airgapped: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FederationRegistry:
    """File-backed multi-tenant registry — local sovereign default."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or REGISTRY_PATH
        self._tenants: Dict[str, FederationTenant] = {}
        self._agents: Dict[str, FederationAgent] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.is_file():
            self.register_tenant("default", org_id="mesie-enterprise", name="Sovereign Local")
            self.register_agent("mesie-orchestrator", tenant_id="default", roles=["admin", "compute"])
            self._save()
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        for t in data.get("tenants", []):
            self._tenants[t["tenant_id"]] = FederationTenant(**t)
        for a in data.get("agents", []):
            self._agents[a["agent_id"]] = FederationAgent(**a)

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "tenants": [t.to_dict() for t in self._tenants.values()],
            "agents": [a.to_dict() for a in self._agents.values()],
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def register_tenant(self, tenant_id: str, *, org_id: str, name: str, airgapped: bool = True) -> FederationTenant:
        t = FederationTenant(tenant_id=tenant_id, org_id=org_id, name=name, airgapped=airgapped)
        self._tenants[tenant_id] = t
        return t

    def register_agent(
        self,
        agent_id: str,
        *,
        tenant_id: str,
        org_id: str = "mesie-enterprise",
        roles: Optional[List[str]] = None,
        runtimes: Optional[List[str]] = None,
    ) -> FederationAgent:
        if tenant_id not in self._tenants:
            self.register_tenant(tenant_id, org_id=org_id, name=tenant_id)
        agent = FederationAgent(
            agent_id=agent_id,
            org_id=org_id,
            tenant_id=tenant_id,
            roles=roles or ["agent"],
            runtimes=runtimes or ["python", "julia", "haskell"],
            last_seen=time.time(),
        )
        self._agents[agent_id] = agent
        if agent_id not in self._tenants[tenant_id].agents:
            self._tenants[tenant_id].agents.append(agent_id)
        self._save()
        return agent

    def authorize(self, *, agent_id: str, tenant_id: str, org_id: str) -> bool:
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        return agent.tenant_id == tenant_id and agent.org_id == org_id and agent.healthy

    def status(self) -> Dict[str, Any]:
        return {
            "tenants": len(self._tenants),
            "agents": len(self._agents),
            "tenant_ids": sorted(self._tenants.keys()),
            "registry_path": str(self.path),
        }
