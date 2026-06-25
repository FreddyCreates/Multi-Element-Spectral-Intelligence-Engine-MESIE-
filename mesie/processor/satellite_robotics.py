"""Persistent robotics / NeuroSwarm satellite — background compute loop."""

from __future__ import annotations

import json
import time
from pathlib import Path

from mesie.processor.virtual_processor import VirtualProcessor

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "deliverables" / "processor" / "robotics_satellite.jsonl"


def run_satellite(*, interval_s: float = 300.0, max_cycles: int = 0) -> None:
    """Run until max_cycles or Ctrl+C. Default 5 min interval."""
    proc = VirtualProcessor()
    LOG.parent.mkdir(parents=True, exist_ok=True)
    cycles = 0
    print(f"[robotics-satellite] interval={interval_s}s log={LOG}")
    try:
        while max_cycles == 0 or cycles < max_cycles:
            cycles += 1
            result = proc.robotics_pulse()
            entry = {"cycle": cycles, "ts": time.time(), "result": result.to_dict()}
            with LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            print(f"[robotics-satellite] cycle={cycles} threat_p50={result.output.get('threat_p50_ms')} LRC={result.lrc.get('lrc_id')}")
            if max_cycles and cycles >= max_cycles:
                break
            time.sleep(interval_s)
    except KeyboardInterrupt:
        print("[robotics-satellite] stopped")


if __name__ == "__main__":
    run_satellite()