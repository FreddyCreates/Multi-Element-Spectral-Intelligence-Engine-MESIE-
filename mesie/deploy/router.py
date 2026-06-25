"""Deploy router — dry-run by default."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from mesie.deploy.registry import DEPLOY_TARGETS, get_service
from mesie.deploy.targets.cursor_mcp import apply_cursor_mcp, plan_cursor_mcp
from mesie.deploy.targets.local_http import apply_local_http, plan_local_http
from mesie.deploy.targets.powershell import apply_powershell, plan_powershell

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class DeployResult:
    service_id: str
    target: str
    dry_run: bool
    plan: Dict[str, Any]
    applied: bool = False
    detail: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_id": self.service_id,
            "target": self.target,
            "dry_run": self.dry_run,
            "applied": self.applied,
            "plan": self.plan,
            "detail": self.detail,
        }


def _plan(service_id: str, target: str) -> Dict[str, Any]:
    svc = get_service(service_id)
    if target == "local-http":
        return plan_local_http(svc)
    if target == "powershell":
        return plan_powershell(svc)
    if target == "cursor-mcp":
        return plan_cursor_mcp(svc)
    if target == "docker":
        return {
            "action": "placeholder",
            "note": "docker target not implemented — stub for future packaging",
            "service_id": service_id,
        }
    raise ValueError(f"unknown target: {target}. known: {', '.join(DEPLOY_TARGETS)}")


def _apply(service_id: str, target: str) -> Dict[str, Any]:
    svc = get_service(service_id)
    if target == "local-http":
        return apply_local_http(svc)
    if target == "powershell":
        return apply_powershell(svc)
    if target == "cursor-mcp":
        return apply_cursor_mcp(svc)
    if target == "docker":
        raise NotImplementedError("docker deploy target is a future placeholder")
    raise ValueError(f"unknown target: {target}")


def deploy_service(
    service_id: str,
    target: str,
    *,
    dry_run: bool = True,
) -> DeployResult:
    target = target.lower().strip()
    plan = _plan(service_id, target)
    if dry_run:
        return DeployResult(
            service_id=service_id,
            target=target,
            dry_run=True,
            plan=plan,
            applied=False,
            detail="dry-run — pass --apply to execute",
        )
    outcome = _apply(service_id, target)
    return DeployResult(
        service_id=service_id,
        target=target,
        dry_run=False,
        plan=plan,
        applied=bool(outcome.get("applied", True)),
        detail=json.dumps(outcome, indent=2)[:2000],
    )
