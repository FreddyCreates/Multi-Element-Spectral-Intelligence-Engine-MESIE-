"""Export NOVAMINI (MESIE-LM) manifest + smoke session."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.novamini.runtime import NovaMiniRuntime, VERSION

DELIVERABLES = ROOT / "deliverables" / "novamini"


def main() -> int:
    runtime = NovaMiniRuntime(session_id="novamini-export")
    manifest_path = DELIVERABLES / "NOVAMINI_MESIE_LM_Manifest.json"
    runtime.export_manifest(manifest_path)

    smoke = [
        "What is NOVAMINI?",
        "Who are you in the Alpha family?",
        "What is the speaking loop?",
    ]
    session = []
    for q in smoke:
        r = runtime.chat(q)
        session.append({"q": q, "spoken": r.spoken, "latency_ms": r.latency_ms})

    session_path = DELIVERABLES / "NOVAMINI_Smoke_Session.json"
    session_path.write_text(
        json.dumps({"version": VERSION, "turns": session, "ts": time.time()}, indent=2),
        encoding="utf-8",
    )

    print("=== NOVAMINI (MESIE-LM) ===")
    print(f"Version: {VERSION}")
    print(f"Manifest: {manifest_path}")
    print(f"Smoke: {session_path}")
    print(f"Turns: {len(session)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())