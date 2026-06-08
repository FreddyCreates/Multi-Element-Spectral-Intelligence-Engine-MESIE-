"""Build interior data center manifest — sovereign corpus vault inside the org."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.production.deployment_doctrine import build_deployment_doctrine
from mesie.production.interior_datacenter import InteriorDataCenter


def main() -> None:
    dc = InteriorDataCenter()
    path = dc.export()
    report = dc.catalog()
    doctrine = build_deployment_doctrine()
    doctrine_path = ROOT / "deliverables" / "MESIE_Deployment_Doctrine.json"
    doctrine_path.write_text(json.dumps(doctrine.to_dict(), indent=2), encoding="utf-8")

    print("=== MESIE Interior Data Center ===")
    print(f"Shards: {report.total_shards} | Records: {report.total_records}")
    print(f"Bytes: {report.total_bytes:,} | Sovereign: {report.sovereign}")
    print(f"Manifest: {path}")
    print(f"Doctrine: {doctrine_path}")
    print(f"Primary deployment: {doctrine.primary_deployment}")
    sys.exit(0 if report.total_shards > 0 else 1)


if __name__ == "__main__":
    main()