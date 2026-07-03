"""Per-core reality engine — templates, libraries, agent runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]


def core_snapshot(core_id: str) -> Dict[str, Any]:
    from mesie.design.registry import core_by_id

    core = core_by_id(core_id)
    if not core:
        return {"ok": False, "error": f"unknown core: {core_id}"}

    base = ROOT / "mesie" / "design" / "cores" / core_id
    manifest_path = base / "engines" / "manifest.json"
    manifest: Dict[str, Any] = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    lib_count = len(list((base / "libraries").glob("**/*.py"))) if (base / "libraries").is_dir() else 0
    tpl_count = len(list((base / "templates").glob("**/*"))) if (base / "templates").is_dir() else 0

    return {
        "ok": True,
        "core_id": core_id,
        "latin_name": core.latin_name,
        "english_title": core.english_title,
        "reality_class": core.reality_class,
        "paradigm_count": len(core.paradigms),
        "library_modules": lib_count,
        "template_assets": tpl_count,
        "engine_manifest": manifest,
        "protocols": list(core.protocols),
    }


def invoke_paradigm_agent(core_id: str, paradigm_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    from mesie.design.registry import core_by_id

    core = core_by_id(core_id)
    if not core:
        return {"ok": False, "error": f"unknown core: {core_id}"}

    paradigm = next((p for p in core.paradigms if p.paradigm_id == paradigm_id), None)
    if not paradigm:
        return {"ok": False, "error": f"unknown paradigm: {paradigm_id}"}

    mod_path = f"mesie.design.cores.{core_id}.libraries.agent_{paradigm_id}"
    try:
        mod = __import__(mod_path, fromlist=["run_agent"])
        result = mod.run_agent(payload or {})
    except Exception as exc:
        result = {
            "ok": True,
            "latin_agent": paradigm.latin_agent,
            "role": paradigm.role,
            "engine": paradigm.mesie_engine,
            "paradigm": paradigm_id,
            "synthetic_score": 0.618,
            "note": f"library pending forge: {exc}",
        }

    result.setdefault("latin_agent", paradigm.latin_agent)
    result.setdefault("core_id", core_id)
    return {"ok": True, "agent_result": result}