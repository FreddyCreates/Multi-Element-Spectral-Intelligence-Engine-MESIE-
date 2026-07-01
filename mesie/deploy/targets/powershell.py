"""Copy generated PowerShell launchers to repo root."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict

from mesie.deploy.registry import ServiceDefinition

ROOT = Path(__file__).resolve().parents[3]
SANDBOX = ROOT / "deliverables" / "deploy" / "sandbox"

_POWERSHELL_NAMES = {
    "virtual-processor": "Start-VirtualProcessor.ps1",
    "medina-surface": "Start-MedinaSurface.ps1",
    "novamini-http": "Start-NOVAMINI.ps1",
    "robotics-satellite": "Start-RoboticsSatellite.ps1",
    "vp-mesh": "Start-VPMesh.ps1",
}


def plan_powershell(svc: ServiceDefinition) -> Dict[str, Any]:
    src = SANDBOX / svc.id / "launcher.ps1"
    dest_name = _POWERSHELL_NAMES.get(svc.id, f"Start-{svc.id}.ps1")
    dest = ROOT / dest_name
    return {
        "action": "copy_launcher",
        "source": str(src),
        "destination": str(dest),
        "exists_source": src.is_file(),
    }


def apply_powershell(svc: ServiceDefinition) -> Dict[str, Any]:
    plan = plan_powershell(svc)
    src = Path(plan["source"])
    dest = Path(plan["destination"])
    if not src.is_file():
        raise FileNotFoundError(f"sandbox launcher missing: {src}. Run package_services --service {svc.id} first.")
    shutil.copy2(src, dest)
    return {**plan, "applied": True}
