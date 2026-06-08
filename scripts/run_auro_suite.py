"""Export Auro native speaking intelligence manifest + voice session."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.neuroai.auro import AuroSpeakingEngine
from mesie.neuroai.auro.eval import AuroEvalSuite
from mesie.neuroai.auro.manifest import load_auro_manifest

DELIVERABLES = ROOT / "deliverables"


def main() -> None:
    engine = AuroSpeakingEngine(session_id="auro-gov-export")
    manifest = load_auro_manifest()
    eval_report = AuroEvalSuite().run(engine)
    session_path = engine.export_session()

    out = DELIVERABLES / "Auro_Native_Speaking_Manifest.json"
    payload = {
        "edition": engine.edition,
        "packet_id": engine.packet_id,
        "identity": "Auro — Medina native speaking intelligence",
        "native_model": "AuroNativeComposer-v1",
        "third_party_inference": False,
        "manifest": manifest,
        "status": engine.status(),
        "eval": eval_report.to_dict(),
        "session_export": str(session_path),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== Auro Native Speaking Intelligence ===")
    print(f"Edition: {engine.edition}")
    print(f"Eval: {eval_report.passed}/{len(eval_report.cases)} passed")
    print(f"Manifest: {out}")
    print(f"Session: {session_path}")
    sys.exit(0 if eval_report.ok else 1)


if __name__ == "__main__":
    main()