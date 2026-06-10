"""Paper 04 suite — simulated spacetime agent embedding architecture."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.spacetime.eval import run_spacetime_eval


def main() -> None:
    result = run_spacetime_eval(ticks=24)
    deliverable = ROOT / "deliverables" / "Paper04_Spacetime_Architecture_Report.json"
    deliverable.parent.mkdir(parents=True, exist_ok=True)
    deliverable.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("=== Paper 04 — Simulated Spacetime Architecture ===")
    print(f"Authority: {result['authority_state']}")
    print(f"Claim boundary: {result['claim_boundary']}")
    print(f"Eval: {result['passed']}/{result['total']} — Ready: {result['ready']}")
    sim = result["simulation"]
    print(f"Ticks: {sim['ticks_run']} | Routes: {sim['routes_total']} | Containment: {sim['containment_ok']}")
    print(f"Mean tick: {sim['mean_tick_ms']} ms")
    print(f"Deliverable: {deliverable}")
    sys.exit(0 if result["ready"] else 1)


if __name__ == "__main__":
    main()