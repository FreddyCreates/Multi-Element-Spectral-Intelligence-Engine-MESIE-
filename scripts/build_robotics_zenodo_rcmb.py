"""Build RF-PDM — Robot Fleet Predictive Maintenance Benchmark for Zenodo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.robotics.zenodo_rcmb import build_rcmb


def main() -> None:
    out, manifest = build_rcmb()
    print("=== RF-PDM — Zenodo Production Dataset ===")
    print(f"Title: {manifest.title}")
    print(f"Samples: {manifest.sample_count:,}")
    print(f"Robots: {manifest.robot_count}")
    print(f"Splits: {manifest.splits}")
    print(f"Baseline: {manifest.baseline_accuracy:.1%} acc, {manifest.baseline_f1_macro:.3f} F1")
    print(f"Output: {out}")
    zip_name = f"RFPDM_v{manifest.version}.zip"
    print(f"Archive: {out.parent / zip_name}")
    print("\nGaps filled:")
    for g in manifest.gaps_filled:
        print(f"  - {g}")
    print(f"\nUpload: {out / 'zenodo_metadata.json'}")
    sys.exit(0)


if __name__ == "__main__":
    main()