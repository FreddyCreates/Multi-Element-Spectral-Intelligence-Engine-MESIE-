"""Sync Auro substrate from GPTREPO + NeuroAI packet into MESIE vendored fallback."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mesie.neuroai.auro.substrate_loader import gptrepo_root, neuroai_packet_root

VENDORED = ROOT / "data" / "neuroai" / "substrate"


def main() -> None:
    gpt = gptrepo_root()
    pkt = neuroai_packet_root()
    VENDORED.mkdir(parents=True, exist_ok=True)
    copied = []

    pairs = [
        (pkt / "manifests" / "lineage_record.json", VENDORED / "lineage_record.json"),
        (pkt / "matrices" / "citation_to_claim_matrix.json", VENDORED / "citation_to_claim_matrix.json"),
        (pkt / "papers" / "p4-auro-dynamics-speaking-intelligence.md", VENDORED / "p4-auro-dynamics-speaking-intelligence.md"),
        (pkt / "README.md", VENDORED / "neuroai_packet_README.md"),
        (gpt / "protocols" / "sovereign-offline-cognition-protocol.js", VENDORED / "sovereign-offline-cognition-protocol.js"),
        (gpt / "protocols" / "auro-guardian-intelligence-protocol.js", VENDORED / "auro-guardian-intelligence-protocol.js"),
        (gpt / "protocols" / "auro-absorption-charter-protocol.js", VENDORED / "auro-absorption-charter-protocol.js"),
    ]

    for src, dst in pairs:
        if src.is_file():
            shutil.copy2(src, dst)
            copied.append(str(dst.relative_to(ROOT)))

    manifest = {
        "synced_from": {"gptrepo": str(gpt), "neuroai_packet": str(pkt)},
        "copied": copied,
        "native_model": "PROTO-183-SOCP",
    }
    (VENDORED / "sync_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("=== Auro Substrate Sync ===")
    print(f"GPTREPO: {gpt} ({'OK' if gpt.is_dir() else 'MISSING'})")
    print(f"NeuroAI: {pkt} ({'OK' if pkt.is_dir() else 'MISSING'})")
    print(f"Copied {len(copied)} files to {VENDORED}")
    for c in copied:
        print(f"  {c}")
    sys.exit(0 if copied else 1)


if __name__ == "__main__":
    main()