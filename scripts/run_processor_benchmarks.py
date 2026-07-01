#!/usr/bin/env python3
"""Run processor benchmarks + export mint ledger for agent desks."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.processor.virtual_processor import VirtualProcessor


def main() -> int:
    proc = VirtualProcessor()
    results = []
    for op, fn in (
        ("benchmark", lambda: proc.benchmark(trials=200)),
        ("virtual_chip", proc.virtual_chip_certify),
        ("robotics_pulse", proc.robotics_pulse),
    ):
        results.append(fn().to_dict())

    out_dir = ROOT / "deliverables" / "processor"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "accounting": proc.status()["accounting"],
        "runs": results,
    }
    path = out_dir / "MESIE_Processor_Benchmarks.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["accounting"], indent=2))
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())