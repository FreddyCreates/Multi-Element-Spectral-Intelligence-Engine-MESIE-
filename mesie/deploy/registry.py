"""Registry of packagable MESIE services."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable


def _processor_manifest() -> Dict[str, Any]:
    from mesie.deploy.manifest import build_service_manifest
    from mesie.processor import PROCESSOR_VERSION
    from mesie.processor.virtual_processor import VirtualProcessor

    proc = VirtualProcessor()
    return build_service_manifest(
        product="MESIE Virtual Processor",
        version=PROCESSOR_VERSION,
        status=proc.status(),
        sample=proc.status(),
        deploy_artifacts={"port": 8750, "health_path": "/processor/status"},
    )


def _surface_manifest() -> Dict[str, Any]:
    from mesie.deploy.manifest import build_service_manifest
    from mesie.surface.catalog import build_catalog

    cat = build_catalog(export=False)
    return build_service_manifest(
        product="Medina Surface",
        version="1.0.0",
        status={"systems": len(cat.systems), "services": len(cat.services), "deliverables": len(cat.deliverables)},
        sample={"counts": cat.to_dict()["counts"]},
        deploy_artifacts={"port": 8760, "health_path": "/surface/status"},
    )


def _novamini_manifest() -> Dict[str, Any]:
    from mesie.novamini.runtime import NovaMiniRuntime, VERSION

    runtime = NovaMiniRuntime()
    return {
        "product": "NOVAMINI (MESIE-LM)",
        "version": VERSION,
        "generated_at": runtime.status().get("generated_at", ""),
        "status": runtime.status(),
        "sample": runtime.status(),
        "deploy_artifacts": {"port": 6180, "health_path": "/status"},
    }


def _robotics_manifest() -> Dict[str, Any]:
    from mesie.deploy.manifest import build_service_manifest
    from mesie.processor import PROCESSOR_VERSION

    log = ROOT / "deliverables" / "processor" / "robotics_satellite.jsonl"
    return build_service_manifest(
        product="MESIE Robotics Satellite",
        version=PROCESSOR_VERSION,
        status={"background": True, "log": str(log), "interval_s": 300},
        sample={"note": "pairs with virtual-processor :8750"},
        deploy_artifacts={"log_path": str(log)},
    )


@dataclass
class ServiceDefinition:
    id: str
    name: str
    version: str
    port: Optional[int]
    host: str = "127.0.0.1"
    health_path: Optional[str] = None
    command: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    background: bool = False
    mcp_server_path: Optional[str] = None
    mcp_key: Optional[str] = None
    manifest_exporter: Optional[Callable[[], Dict[str, Any]]] = None
    powershell_title: Optional[str] = None

    def start_command(self) -> List[str]:
        return list(self.command)

    def health_url(self) -> Optional[str]:
        if self.port is None or not self.health_path:
            return None
        return f"http://{self.host}:{self.port}{self.health_path}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "port": self.port,
            "host": self.host,
            "health_path": self.health_path,
            "health_url": self.health_url(),
            "command": self.start_command(),
            "env": self.env,
            "dependencies": self.dependencies,
            "background": self.background,
            "mcp_key": self.mcp_key,
            "ready": True,
        }


def _base_env() -> Dict[str, str]:
    return {"MESIE_ROOT": str(ROOT)}


SERVICE_REGISTRY: Dict[str, ServiceDefinition] = {
    "virtual-processor": ServiceDefinition(
        id="virtual-processor",
        name="MESIE Virtual Processor",
        version="1.0.0",
        port=8750,
        health_path="/processor/status",
        command=[PYTHON, "-m", "mesie.processor", "--serve"],
        env=_base_env(),
        mcp_server_path=str(ROOT / "mesie" / "processor" / "mcp_server.py"),
        mcp_key="mesie-processor",
        manifest_exporter=_processor_manifest,
        powershell_title="MESIE Virtual Processor",
    ),
    "medina-surface": ServiceDefinition(
        id="medina-surface",
        name="Medina Surface",
        version="1.0.0",
        port=8760,
        health_path="/surface/status",
        command=[PYTHON, "scripts/medina_surface.py", "--serve"],
        env=_base_env(),
        manifest_exporter=_surface_manifest,
        powershell_title="Medina Surface",
    ),
    "novamini-http": ServiceDefinition(
        id="novamini-http",
        name="NOVAMINI HTTP Hub",
        version="1.0.0",
        port=6180,
        health_path="/status",
        command=[PYTHON, "-m", "mesie.novamini", "--serve", "6180"],
        env=_base_env(),
        manifest_exporter=_novamini_manifest,
        powershell_title="NOVAMINI HTTP",
    ),
    "vp-mesh": ServiceDefinition(
        id="vp-mesh",
        name="VP-MESH Supervisor",
        version="1.2.0",
        port=None,
        health_path=None,
        command=[PYTHON, "scripts/run_vp_mesh.py", "--supervise"],
        env=_base_env(),
        dependencies=["virtual-processor"],
        background=True,
        powershell_title="VP-MESH Supervisor",
    ),
    "robotics-satellite": ServiceDefinition(
        id="robotics-satellite",
        name="MESIE Robotics Satellite",
        version="1.0.0",
        port=None,
        health_path=None,
        command=[PYTHON, "-m", "mesie.processor.satellite_robotics"],
        env=_base_env(),
        dependencies=["virtual-processor"],
        background=True,
        manifest_exporter=_robotics_manifest,
        powershell_title="Robotics Satellite",
    ),
}

# External reference only — not packaged or deployed from MESIE.
LOOM_EXTERNAL = {
    "id": "loom",
    "name": "Loom MCP (GPTREPO)",
    "source": "gptrepo",
    "path": str(Path.home() / ".medina"),
    "note": "Configured in ~/.cursor/mcp.json — do not modify from MESIE deploy",
}

DEPLOY_TARGETS = ("local-http", "powershell", "cursor-mcp", "docker")

LOOM_PROTECTED_MCP_KEYS = frozenset({
    "loom", "loom-council", "loom-signal",
    "medina-vault", "medina-council", "medina-signal",
})


def get_service(service_id: str) -> ServiceDefinition:
    if service_id not in SERVICE_REGISTRY:
        known = ", ".join(sorted(SERVICE_REGISTRY))
        raise KeyError(f"unknown service: {service_id}. known: {known}")
    return SERVICE_REGISTRY[service_id]


def list_services() -> List[ServiceDefinition]:
    return list(SERVICE_REGISTRY.values())
