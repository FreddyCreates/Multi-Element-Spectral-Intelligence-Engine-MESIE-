"""Start HTTP services locally."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from mesie.deploy.registry import ServiceDefinition

ROOT = Path(__file__).resolve().parents[3]


def plan_local_http(svc: ServiceDefinition) -> Dict[str, Any]:
    cmd = svc.start_command()
    return {
        "action": "start_subprocess",
        "command": cmd,
        "cwd": str(ROOT),
        "env": svc.env,
        "health_url": svc.health_url(),
        "background": svc.background,
    }


def apply_local_http(svc: ServiceDefinition) -> Dict[str, Any]:
    plan = plan_local_http(svc)
    cmd: List[str] = plan["command"]
    env = {**dict(__import__("os").environ), **svc.env}
    if svc.background or svc.port is None:
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {**plan, "pid": proc.pid, "applied": True}
    # Foreground services block — use Popen detached for apply
    proc = subprocess.Popen(cmd, cwd=str(ROOT), env=env)
    return {**plan, "pid": proc.pid, "applied": True}
