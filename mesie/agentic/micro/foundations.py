"""NOVA foundations map — laws, protocols, engines, physics, library, signals."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]


def engine_names() -> List[str]:
    from mesie.engines.registry import build_default_registry

    return sorted(build_default_registry().names())


def protocol_modules() -> List[str]:
    mods = [
        "mesie.ai.intelligence_protocols",
        "mesie.edge.edge_protocol",
        "mesie.internal_api.bus",
    ]
    return [m for m in mods if _importable(m)]


def physics_modules() -> List[str]:
    mods = [
        "mesie.edge.hz_ladder",
        "mesie.cosmology.teotl_flow",
        "mesie.worlds.spacetime_bridge",
    ]
    return [m for m in mods if _importable(m)]


def library_stats() -> Dict[str, Any]:
    lib = ROOT / "library"
    if not lib.is_dir():
        return {"ok": False, "bytes": 0, "files": 0}
    files = list(lib.rglob("*"))
    file_paths = [p for p in files if p.is_file()]
    total_bytes = sum(p.stat().st_size for p in file_paths)
    return {
        "ok": True,
        "root": str(lib),
        "files": len(file_paths),
        "bytes": total_bytes,
        "mb": round(total_bytes / 1_048_576, 2),
        "swarm_dtn": len(list((lib / "swarm_dtn").glob("*.json"))) if (lib / "swarm_dtn").is_dir() else 0,
        "lan_gossip": len(list((lib / "lan_gossip").glob("*.json"))) if (lib / "lan_gossip").is_dir() else 0,
        "spectral_index": (lib / "spectral_index.json").is_file(),
    }


def deliverable_bytes() -> Dict[str, Any]:
    d = ROOT / "deliverables"
    if not d.is_dir():
        return {"ok": False, "bytes": 0}
    files = [p for p in d.rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    return {"ok": True, "files": len(files), "bytes": total, "mb": round(total / 1_048_576, 2)}


def tool_count() -> int:
    from mesie.tools.registry import TOOLS

    return len(TOOLS)


def _importable(module: str) -> bool:
    try:
        __import__(module)
        return True
    except Exception:
        return False


def foundations_snapshot() -> Dict[str, Any]:
    """Single snapshot for IT careers + showcase."""
    lib = library_stats()
    return {
        "engines": engine_names(),
        "engine_count": len(engine_names()),
        "protocols": protocol_modules(),
        "physics": physics_modules(),
        "library": lib,
        "deliverables": deliverable_bytes(),
        "tools": tool_count(),
        "mesie_root": str(ROOT),
        "doctrine": "Everything is a signal — spectral records unify text, state, physics, domains.",
    }