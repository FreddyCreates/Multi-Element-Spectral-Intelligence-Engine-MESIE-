#!/usr/bin/env python3
"""Export MININOVA production manifest."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.mininova.sphere import MiniNovaSphere
from mesie.version_info import MININOVA_VERSION, MESIE_VERSION

DELIVERABLES = ROOT / "deliverables" / "mininova"


def main() -> int:
    sphere = MiniNovaSphere(session_id="mininova-export")
    payload = {
        "product": "MININOVA",
        "version": MININOVA_VERSION,
        "mesie_version": MESIE_VERSION,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": sphere.status(),
        "sample": sphere.process("What is MININOVA and how does it wrap MESIE?").to_dict(),
    }
    DELIVERABLES.mkdir(parents=True, exist_ok=True)
    out = DELIVERABLES / "MININOVA_Sphere_Manifest.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())