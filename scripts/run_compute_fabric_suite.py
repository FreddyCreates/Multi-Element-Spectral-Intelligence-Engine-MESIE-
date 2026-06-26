"""Unified compute fabric suite — certify all chip SKUs + deploy manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.silicon.compute_fabric import run_compute_fabric_suite


def main() -> None:
    report = run_compute_fabric_suite()
    print("=== MESIE Compute Fabric ===")
    print(f"All certified: {report['all_certified']}")
    for row in report["chips_certified"]:
        print(
            f"  {row['chip_id']}: certified={row['certified']} "
            f"threat_p50={row['threat_fast_p50_ms']}ms ann_p50={row['ann_p50_ms']}ms"
        )
    print(f"Deploy manifest: {report['deploy_manifest']}")
    print(f"Report: deliverables/virtual_silicon/MESIE_Compute_Fabric_Report.json")
    sys.exit(0 if report["all_certified"] else 1)


if __name__ == "__main__":
    main()
