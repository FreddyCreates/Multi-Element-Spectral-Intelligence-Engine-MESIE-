"""Production Tier 1 + Tier 2 validation — appliance manifest, cluster RF MLPerf."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.production.appliance import ProductionAppliance


def _md(payload: dict) -> str:
    lines = [
        "# MESIE Production — Tier 1 + Tier 2",
        "",
        f"**SDK:** {payload['sdk_version']}",
        f"**Ready to ship (T1):** {payload['tier1']['ready_to_ship']}",
        f"**Tier 2 ready:** {payload['tier2']['ready']}",
        "",
        "## Tier 1 — On-prem appliance",
        "",
        f"- Health: {'PASS' if payload['tier1']['health_ok'] else 'FAIL'}",
        f"- Threat SLA p50: {payload['tier1']['sla']['measured_threat_p50']} ms",
        f"- Enterprise SLA p50: {payload['tier1']['sla']['measured_enterprise_p50']} ms",
        f"- Major benchmark win rate: {payload['tier1']['benchmarks']['major_win_rate']}%",
        f"- Manifest: `{payload['tier1']['manifest_path']}`",
        f"- Narrative: `{payload['tier1'].get('narrative_path', '')}`",
        "",
        "## Tier 2 — Moat",
        "",
        f"- Cluster optimized ms/agent: **{payload['tier2']['cluster_optimized_ms_per_agent']}** (target <0.5)",
        f"- Cluster win vs centralized: **{payload['tier2']['cluster_optimized_win']}**",
        f"- Virtual silicon certified: **{payload['tier2'].get('virtual_silicon_certified')}**",
        f"- RF HIL: **{payload['tier2'].get('rf_silicon_certified')}** (coherence {payload['tier2']['rf_field_coherence']})",
        f"- OTA mesh: **{payload['tier2'].get('ota_mesh_ok')}** ({payload['tier2'].get('ota_frames_received', 0)} frames)",
        f"- MLPerf: `{payload['tier2']['mlperf_submission']}` ({payload['tier2'].get('mlperf_credibility_tier', 'n/a')})",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=["1", "2", "both"], default="both")
    args = parser.parse_args()

    t0 = time.perf_counter()
    appliance = ProductionAppliance()
    payload: dict = {"sdk_version": appliance.client.version}

    if args.tier in ("1", "both"):
        t1 = appliance.run_tier1_validation()
        manifest_path = appliance.export_manifest()
        narrative_path = appliance.export_narrative()
        payload["tier1"] = {
            **t1,
            "manifest_path": str(manifest_path),
            "narrative_path": str(narrative_path),
            "sla": t1["manifest"]["sla"],
            "benchmarks": t1["manifest"]["benchmarks"],
        }

    if args.tier in ("2", "both"):
        payload["tier2"] = appliance.run_tier2_validation()

    payload["elapsed_s"] = round(time.perf_counter() - t0, 2)
    payload["production_ready"] = (
        payload.get("tier1", {}).get("ready_to_ship", True)
        and payload.get("tier2", {}).get("ready", True)
    )

    out_json = ROOT / "deliverables" / "MESIE_Production_Tiers_Report.json"
    out_md = ROOT / "deliverables" / "MESIE_Production_Tiers_Report.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(_md(payload), encoding="utf-8")

    print(f"=== MESIE Production Tiers ===")
    if "tier1" in payload:
        print(f"T1 ship ready: {payload['tier1']['ready_to_ship']}")
    if "tier2" in payload:
        print(f"T2 cluster ms/agent: {payload['tier2']['cluster_optimized_ms_per_agent']}")
        print(f"T2 ready: {payload['tier2']['ready']}")
    print(f"Report: {out_json}")
    sys.exit(0 if payload["production_ready"] else 1)


if __name__ == "__main__":
    main()