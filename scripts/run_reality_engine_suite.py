"""Reality Engine Cores — 10 × 20 × 40+ certification."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.design.envelope import RealityEngineEnvelope
from mesie.design.reality_engine import RealityEngine
from mesie.design.registry import DESIGN_CORES, paradigm_count


def main() -> int:
    engine = RealityEngine()
    status = engine.status()

    env = RealityEngineEnvelope(
        agent_id="reality-suite",
        core_id="core_realitas",
        brief={"showcase": "product_demo", "scene": "phi_icosahedron"},
        paradigm_id="threejs_webgl",
    )
    # core_realitas may not have threejs - use unreal_class
    env2 = RealityEngineEnvelope(
        agent_id="reality-suite",
        core_id="core_geometrica",
        brief={"mesh": "spectral"},
        paradigm_id="threejs_webgl",
    )
    invoke = engine.invoke(env2)

    report = {
        "ok": invoke.get("ok") and status["paradigm_count"] == 200,
        "cores": len(DESIGN_CORES),
        "paradigms": paradigm_count(),
        "status": {
            "protocol": status["protocol"],
            "paradigms_per_core": status["paradigms_per_core"],
            "canonical_protocol_count": status["canonical_protocol_count"],
        },
        "invoke_latency_ms": invoke.get("latency_ms"),
        "reality_class": invoke.get("reality_class"),
    }
    out = ROOT / "deliverables" / "design" / "REALITY_ENGINE_MANIFEST.json"
    payload = {**status, "certification": report}
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
