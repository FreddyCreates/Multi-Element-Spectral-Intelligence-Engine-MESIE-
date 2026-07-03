"""Design orchestrator — front ↔ middle intelligence ↔ back compute."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from mesie.design.registry import DESIGN_CORES, core_by_id

PHI = 0.6180339887498948


def orchestrate_design_brief(
    core_id: str,
    brief: Dict[str, Any],
    *,
    agent_id: str = "design-orchestrator",
) -> Dict[str, Any]:
    """Route a design brief through core paradigms → MESIE engines → surface manifest."""
    core = core_by_id(core_id)
    if not core:
        return {"ok": False, "error": f"unknown core: {core_id}"}

    from mesie.compute.hub import MESIEComputeHub

    hub = MESIEComputeHub()
    encoded = hub.encode({"core": core_id, "brief": brief})

    agents_invoked: List[Dict[str, Any]] = []
    for p in core.paradigms:
        agents_invoked.append(
            {
                "latin_agent": p.latin_agent,
                "role": p.role,
                "paradigm": p.paradigm_id,
                "engine": p.mesie_engine,
                "route_hash": hashlib.sha256(f"{core_id}:{p.paradigm_id}".encode()).hexdigest()[:12],
            }
        )

    body = json.dumps({"core": core_id, "brief": brief, "agent_id": agent_id}, sort_keys=True)
    receipt = {
        "protocol": "MESIE-DESIGN-ORCHESTRATOR/1.0",
        "core_id": core_id,
        "latin_name": core.latin_name,
        "agent_id": agent_id,
        "phi_route": PHI,
        "body_hash": hashlib.sha256(body.encode()).hexdigest(),
        "embedding_dims": encoded.get("dims"),
        "encode_latency_ms": encoded.get("latency_ms"),
        "agents_invoked": len(agents_invoked),
        "agents": agents_invoked,
        "middle_intelligence": "ST-φ encode + SOLUS formal stack",
        "back_compute": ":8750 processor + mesie engines",
        "front_surface": _surface_for_core(core_id),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return {"ok": True, "orchestration": receipt, "encode": encoded}


def _surface_for_core(core_id: str) -> str:
    mapping = {
        "core_geometrica": "websites/reality-engine/index.html",
        "core_realitas": "websites/reality-engine/index.html",
        "core_datavis": "websites/computing-family/index.html",
        "core_architectura": "websites/enterprise-4k/index.html",
        "core_spectralis": "websites/mesie-landing/index.html",
    }
    return mapping.get(core_id, f"mesie/design/cores/{core_id}/templates/")


def list_orchestrator_roles() -> Dict[str, Any]:
    return {
        "orchestrator": "Routes brief → ST-φ → all core agents → surface",
        "worker": "Builds paradigm-specific assets",
        "helper": "Assists token/motion/material subtasks",
        "executor": "Commits render/deploy/receipt",
        "cores": [c.core_id for c in DESIGN_CORES],
    }