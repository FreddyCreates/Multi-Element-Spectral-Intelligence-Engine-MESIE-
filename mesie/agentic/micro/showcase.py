"""NOVA showcase — benchmark workflow proof for release."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[3]


def run_showcase(*, export: bool = True, quick: bool = False) -> Dict[str, Any]:
    from mesie.agentic.micro.foundations import foundations_snapshot
    from mesie.processor.virtual_processor import VirtualProcessor

    t0 = time.perf_counter()
    proc = VirtualProcessor()
    robotics = proc.robotics_pulse().to_dict()
    embed = proc.embed("ref-earthquake-psd-001").to_dict()
    signal_read = proc.read_signal("Everything is a signal — text and physics unify.", hint="text").to_dict()
    text_gen = proc.generate_text(
        {"event": "showcase", "domains": ["seismic", "orbital", "robotics"]},
        style="executive",
        max_chars=600,
    ).to_dict()
    bench = proc.benchmark(trials=50 if quick else 200).to_dict()
    chip = proc.virtual_chip_certify().to_dict() if not quick else {"skipped": True}
    foundations = foundations_snapshot()

    report: Dict[str, Any] = {
        "ok": robotics.get("ok") and embed.get("ok") and bench.get("ok") and signal_read.get("ok") and text_gen.get("ok"),
        "product": "NOVA_SHOWCASE",
        "mesie_version": __import__("mesie").__version__,
        "elapsed_s": round(time.perf_counter() - t0, 2),
        "foundations": foundations,
        "demos": {
            "robotics_pulse": robotics,
            "embed": embed,
            "read_signal": signal_read,
            "generate_text": text_gen,
            "benchmark": bench,
            "virtual_chip": chip,
        },
        "headline": {
            "threat_p50_ms": bench.get("output", {}).get("threat_p50_ms"),
            "fusion_dims": robotics.get("output", {}).get("fusion_dims"),
            "library_mb": foundations.get("library", {}).get("mb"),
            "engines": foundations.get("engine_count"),
            "doctrine": foundations.get("doctrine"),
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    out = ROOT / "deliverables" / "nova" / "NOVA_SHOWCASE.json"
    if export:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        report["path"] = str(out)
    return report