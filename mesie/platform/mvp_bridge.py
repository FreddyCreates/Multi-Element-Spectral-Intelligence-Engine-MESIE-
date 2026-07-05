"""MVP ↔ Protocol ↔ Worker bridge — envelopes web apps to native backends."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Optional

from mesie.design.protocols import DESIGN_PROTOCOLS, PROTOCOL_BUS_VERSION
from mesie.platform.registry import PLATFORM_SERVICES, service_by_id
from mesie.version_info import MESIE_VERSION

BRIDGE_PROTOCOL = "MESIE-MVP-PROTOCOL-BRIDGE/1.0"


def _protocol_lookup(protocol_id: str) -> Optional[Dict[str, Any]]:
    for p in DESIGN_PROTOCOLS:
        if p["id"] == protocol_id:
            return p
    return None


def bridge_envelope(
    service_id: str,
    *,
    action: str = "invoke",
    payload: Optional[Dict[str, Any]] = None,
    mission_id: str = "mvp-default",
) -> Dict[str, Any]:
    """Wrap a platform service call in a federated envelope for workers + protocols."""
    svc = service_by_id(service_id)
    if not svc:
        return {"ok": False, "error": f"unknown service: {service_id}"}

    body = payload or {}
    proto = _protocol_lookup(svc.protocol_id)
    envelope = {
        "protocol": BRIDGE_PROTOCOL,
        "envelope_id": hashlib.sha256(
            json.dumps({"svc": service_id, "ts": time.time()}, sort_keys=True).encode()
        ).hexdigest()[:16],
        "mission_id": mission_id,
        "service_id": service_id,
        "action": action,
        "mvp_surface": svc.web_surface,
        "processor_route": svc.processor_route,
        "payload": body,
        "routing": {
            "worker_role": svc.worker_role,
            "worker_action": svc.worker_action,
            "models": list(svc.models),
        },
        "protocol_binding": {
            "protocol_id": svc.protocol_id,
            "protocol_name": proto["name"] if proto else None,
            "protocol_layer": proto["layer"] if proto else None,
            "protocol_bus": PROTOCOL_BUS_VERSION,
        },
        "sovereign": True,
        "third_party_inference": False,
        "mesie_version": MESIE_VERSION,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return {"ok": True, "envelope": envelope}


def bridge_manifest() -> Dict[str, Any]:
    """How MVP surfaces connect to the 42-protocol bus and worker roles."""
    bindings = []
    for svc in PLATFORM_SERVICES:
        proto = _protocol_lookup(svc.protocol_id)
        bindings.append({
            "service_id": svc.service_id,
            "web_surface": svc.web_surface,
            "protocol_id": svc.protocol_id,
            "protocol_name": proto["name"] if proto else None,
            "worker_role": svc.worker_role,
            "worker_action": svc.worker_action,
        })
    return {
        "protocol": BRIDGE_PROTOCOL,
        "mesie_version": MESIE_VERSION,
        "protocol_bus": PROTOCOL_BUS_VERSION,
        "protocol_count": len(DESIGN_PROTOCOLS),
        "service_count": len(PLATFORM_SERVICES),
        "bindings": bindings,
        "flow": [
            "web_app → bridge_envelope",
            "envelope → WorkerBus.dispatch(role, action)",
            "worker → native backend (compute, SOLUS, forge, producer)",
            "receipt → processor JSON response",
        ],
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }