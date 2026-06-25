"""Shared manifest shape for deployable MESIE services."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]


def build_service_manifest(
    *,
    product: str,
    version: str,
    status: Dict[str, Any],
    sample: Optional[Dict[str, Any]] = None,
    deploy_artifacts: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    from mesie.version_info import MESIE_VERSION

    return {
        "product": product,
        "version": version,
        "mesie_version": MESIE_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": status,
        "sample": sample or status,
        "deploy_artifacts": deploy_artifacts or {},
    }


def write_manifest(path: Path, payload: Dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def export_service_manifest(service_id: str, path: Path) -> Path:
    """Build manifest via service-specific exporter registered in registry."""
    from mesie.deploy.registry import get_service

    svc = get_service(service_id)
    if svc.manifest_exporter:
        payload = svc.manifest_exporter()
    else:
        payload = build_service_manifest(
            product=svc.name,
            version=svc.version,
            status={"service_id": service_id, "ready": True},
        )
    return write_manifest(path, payload)
