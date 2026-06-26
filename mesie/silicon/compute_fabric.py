"""Compute fabric orchestrator — certify all chip SKUs + export deploy manifest."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from mesie.silicon.chip_registry import deploy_manifest, list_chips
from mesie.silicon.virtual_chip import VirtualSiliconChip

FABRIC_DIR = Path(__file__).resolve().parents[2] / "deliverables" / "virtual_silicon"


def certify_all_chips() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for sku in list_chips():
        chip = VirtualSiliconChip.from_sku(sku.chip_id)
        cert = chip.certify()
        out = FABRIC_DIR / "chips" / f"{sku.chip_id}_Certification.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = cert.to_dict()
        chip.attach_content_hash(payload)
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        results.append({
            "chip_id": sku.chip_id,
            "certified": cert.certified,
            "path": str(out),
            "threat_fast_p50_ms": cert.benchmark_lane.threat_fast_p50_ms,
            "ann_p50_ms": cert.benchmark_lane.ann_p50_ms,
            "ann_p95_ms": cert.benchmark_lane.ann_p95_ms,
            "ann_backend": cert.benchmark_lane.ann_backend,
        })
    return results


def export_deploy_manifest(*, certified: List[Dict[str, Any]]) -> Path:
    payload = deploy_manifest(certified_chips=certified)
    FABRIC_DIR.mkdir(parents=True, exist_ok=True)
    out = FABRIC_DIR / "MESIE_Chip_Deploy_Manifest.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def run_compute_fabric_suite() -> Dict[str, Any]:
    from mesie.library.domain_corpus import load_domain_corpus
    from mesie.sdk.fast_compute import FastSpectralCompute

    t0 = time.perf_counter()
    refs = load_domain_corpus()
    fc = FastSpectralCompute()
    lib_n = fc.load_library_index()
    if lib_n == 0:
        fc.build_index(refs)
    ann = fc.benchmark_ann_p50(refs[0], n_trials=100)

    certified = certify_all_chips()
    manifest_path = export_deploy_manifest(certified=certified)

    # VS1 legacy paths for backward compat
    vs1 = VirtualSiliconChip.from_sku("MESIE-VS1")
    cert_path = vs1.export_certification()
    narrative_path = FABRIC_DIR / "MESIE_Virtual_Silicon_Narrative.md"
    narrative_path.write_text(vs1.narrative_md(), encoding="utf-8")

    report = {
        "suite": "compute_fabric",
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "fast_compute": ann.to_dict(),
        "chips_certified": certified,
        "all_certified": all(c["certified"] for c in certified),
        "deploy_manifest": str(manifest_path),
        "vs1_cert_path": str(cert_path),
        "narrative_path": str(narrative_path),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = FABRIC_DIR / "MESIE_Compute_Fabric_Report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
