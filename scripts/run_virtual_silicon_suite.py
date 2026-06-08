"""Virtual silicon certification — RF HIL, OTA mesh, MLPerf lane."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.evaluation.mlperf_submit import MLPerfSubmissionPack
from mesie.silicon.virtual_chip import VirtualSiliconChip


def main() -> None:
    t0 = time.perf_counter()
    chip = VirtualSiliconChip()
    cert_path = chip.export_certification()
    narrative_path = ROOT / "deliverables" / "virtual_silicon" / "MESIE_Virtual_Silicon_Narrative.md"
    narrative_path.write_text(chip.narrative_md(), encoding="utf-8")
    mlperf_path = MLPerfSubmissionPack.export(MLPerfSubmissionPack().generate(n_trials=100))

    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    payload = {
        "chip": cert["spec"]["chip_name"],
        "certified": cert["certified"],
        "rf_hil_certified": cert["rf_hil"]["certified"],
        "ota_mesh_ok": cert["ota_mesh"]["ok"],
        "ota_frames_received": cert["ota_mesh"]["frames_received"],
        "threat_fast_p50_ms": cert["benchmark_lane"]["threat_fast_p50_ms"],
        "cert_path": str(cert_path),
        "narrative_path": str(narrative_path),
        "mlperf_path": mlperf_path,
        "gaps_resolved": cert["gaps_resolved"],
        "gaps_remaining": cert["gaps_remaining"],
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    out = ROOT / "deliverables" / "virtual_silicon" / "MESIE_Virtual_Silicon_Report.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== MESIE Virtual Silicon ===")
    print(f"Certified: {payload['certified']}")
    print(f"RF HIL: {payload['rf_hil_certified']}")
    print(f"OTA mesh: {payload['ota_mesh_ok']} ({payload['ota_frames_received']} frames)")
    print(f"Report: {out}")
    sys.exit(0 if payload["certified"] else 1)


if __name__ == "__main__":
    main()