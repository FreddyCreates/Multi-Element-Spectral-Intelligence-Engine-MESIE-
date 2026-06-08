"""Build MERSD — MESIE Edge Robotics Spectral Dataset for Zenodo release."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.robotics.zenodo_dataset import build_mersd, DEFAULT_OUT


def main() -> None:
    out, manifest = build_mersd()
    print("=== MERSD — Zenodo Robotics Dataset ===")
    print(f"Title: {manifest.title}")
    print(f"Episodes: {manifest.episode_count}")
    print(f"Records: {manifest.record_count}")
    print(f"Splits: {manifest.splits}")
    print(f"Output: {out}")
    zip_name = f"MERSD_v{manifest.version}.zip"
    print(f"Archive: {out.parent / zip_name}")
    print("\nZenodo targets:")
    for t in manifest.zenodo_targets:
        print(f"  - {t}")
    print("\nGaps filled:")
    for g in manifest.gaps_filled:
        print(f"  - {g}")
    print(f"\nUpload: {out / 'zenodo_metadata.json'}")
    import json
    import shutil

    deliv = ROOT / "deliverables" / "MERSD_Zenodo_Release_Manifest.json"
    shutil.copy2(out / "manifest.json", deliv)
    print(f"Deliverable: {deliv}")
    sys.exit(0)


if __name__ == "__main__":
    main()