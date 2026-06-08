"""7-day mission world simulation — theater hierarchy, real data, operational narrative."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.worlds.week_engine import MissionWorldWeekEngine


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()

    t0 = time.perf_counter()
    engine = MissionWorldWeekEngine()
    state, report = engine.run_week(days=args.days)

    payload = {
        "suite": "mission_world_week",
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "state": state.to_dict(),
        "report": report.to_dict(),
    }
    out = ROOT / "deliverables" / "mission_worlds" / f"{report.world_id}_week_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== Mission World Week ===")
    print(f"Theater: {state.theater} | Campaign: {state.campaign}")
    print(f"Ticks: {report.ticks_ok}/{report.ticks_total} OK")
    print(f"Peak agents: {report.peak_agents}")
    print(f"Narrative: {report.narrative_path}")
    print(f"Report: {out}")
    sys.exit(0 if report.ok else 1)


if __name__ == "__main__":
    main()