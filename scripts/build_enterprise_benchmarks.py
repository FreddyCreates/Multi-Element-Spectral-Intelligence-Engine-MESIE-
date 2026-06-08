"""Build per-industry enterprise benchmark slices from spectral classification data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data import load_benchmark

USE_CASE_SLICES = [
    ("mfg_predictive", "machinery", 20, 0.45),
    ("energy_grid", "ambient", 20, 0.40),
    ("aerospace_orbital", "earthquake", 20, 0.45),
    ("insurance_seismic", "earthquake", 15, 0.45),
    ("structural_civil", "structural", 20, 0.45),
    ("health_device", "ambient", 15, 0.40),
    ("robotics_fleet", "machinery", 20, 0.45),
    ("telecom_compliance", "blast", 15, 0.40),
    ("rd_lab", None, 40, 0.45),
    ("ai_copilot_rag", None, 20, 0.50),
]


def main() -> None:
    src = load_benchmark("spectral_classification_benchmark")
    all_samples = src.get("samples", [])
    by_class: dict[str, list] = {}
    for s in all_samples:
        by_class.setdefault(s["class"], []).append(s)

    use_cases = []
    for case_id, cls, n_take, min_score in USE_CASE_SLICES:
        if cls:
            pool = by_class.get(cls, [])
            taken = pool[:n_take]
        else:
            taken = all_samples[:n_take]
        use_cases.append(
            {
                "use_case_id": case_id,
                "benchmark_class": cls,
                "n_samples": len(taken),
                "min_rank_score": min_score,
                "samples": taken,
            }
        )

    payload = {
        "dataset_id": "mesie-enterprise-benchmark-v2",
        "version": "2.0",
        "description": "Per-industry benchmark slices for 10 enterprise Monte Carlo use cases",
        "source_benchmark": "spectral_classification_benchmark",
        "generated_from": src.get("dataset_id", "mesie-benchmark-v1"),
        "use_cases": use_cases,
    }

    out = ROOT / "data" / "benchmarks" / "enterprise_use_cases_benchmark.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    total = sum(uc["n_samples"] for uc in use_cases)
    print(f"Wrote {out} ({len(use_cases)} use cases, {total} samples)")


if __name__ == "__main__":
    main()